"""SPL pipeline implementation that exercises the real SPL layers via MCP."""

from __future__ import annotations

from pathlib import Path
import sys
import os

# Ensure SPL framework package is on path when running from the POC tree.
SPL_FRAMEWORK_PATH = Path(__file__).resolve().parents[2] / "SPL-FRAMEWORK"
if str(SPL_FRAMEWORK_PATH) not in sys.path:
    sys.path.insert(0, str(SPL_FRAMEWORK_PATH))

from typing import Tuple

from common.dataset import load_labels
from common.email_schema import ClassificationResult, EmailRecord, PerEmailMetrics, TokenUsage
from common.io_utils import load_yaml
from common.timing import RateLimiter, measure_latency_ms
from spl.mcp_integration import MCPClient
from spl_runner.mcp_agent import SPLMCPAgent
from spl_runner.groq_client import GroqMCPClient


class SPLClassifier:
    """Classifier that drives SPL's MCP-based layered agent."""

    def __init__(self, config_dir: Path):
        """Load configuration, establish MCP clients, and initialize SPL agent."""
        self.config_dir = config_dir
        self.settings = load_yaml(config_dir / "settings.yaml")
        self.providers = load_yaml(config_dir / "providers.yaml")
        self.labels_config = load_labels(config_dir)
        self.label_names = [item["name"] for item in self.labels_config]
        groq_cfg = self.providers.get("groq", {}).get("spl", {})
        self.model_name = groq_cfg.get("model") or groq_cfg.get("model_id") or "llama-3.1-8b-instant"
        token_env = groq_cfg.get("env_var", "GROQ_API_KEY")
        api_token = os.getenv(token_env)
        if not api_token:
            raise EnvironmentError(f"Environment variable {token_env} must be set for Groq")
        base_url = self.providers.get("groq", {}).get("base_url", "https://api.groq.com/openai/v1")
        rpm = int(groq_cfg.get("max_requests_per_minute") or 0)
        rate_limiter = RateLimiter(rpm) if rpm else None
        llm_client: MCPClient = GroqMCPClient(
            model=self.model_name,
            api_token=api_token,
            base_url=base_url,
            rate_limiter=rate_limiter,
        )
        # Keep a handle to the client so we can surface wait vs runtime in metrics.
        self.llm_client = llm_client
        self.provider = f"groq:{self.model_name}"
        self.agent = SPLMCPAgent(
            agent_id="spl_agent",
            settings=self.settings,
            providers=self.providers,
            labels_config=self.labels_config,
            llm_client=llm_client,
        )

    def classify(self, email: EmailRecord) -> Tuple[ClassificationResult, PerEmailMetrics]:
        """Classify a single email through MCP-driven SPL layers."""
        with measure_latency_ms() as timer:
            classification = self.agent.process_email(email)

        latency_ms = timer.get("elapsed_ms", 0.0)
        meta = self.agent.last_run_meta
        wait_ms = 0.0
        if hasattr(self.llm_client, "last_wait_seconds"):
            wait_ms = getattr(self.llm_client, "last_wait_seconds") * 1000.0
        actual_runtime_ms = max(latency_ms - wait_ms, 0.0)
        token_usage_dict = meta.get("token_usage")
        token_usage = TokenUsage(**token_usage_dict) if token_usage_dict else None
        cost_usd = float(meta.get("cost_usd", 0.0))
        is_correct = classification.predicted_label == email.true_label
        layers_used = meta.get("layers_used")

        metrics = PerEmailMetrics(
            email_id=email.id,
            true_label=email.true_label,
            predicted_label=classification.predicted_label,
            method="spl",
            latency_ms=latency_ms,
            wait_ms=wait_ms,
            actual_runtime_ms=actual_runtime_ms,
            token_usage=token_usage,
            cost_usd=cost_usd,
            layers_used=layers_used,
            is_correct=is_correct,
            final_layer=meta.get("final_layer"),
            l1_suppressed_l2=meta.get("l1_suppressed_l2", False),
            budget_remaining=meta.get("budget_remaining"),
            tokens_used=int(meta.get("tokens_used", 0)),
            safety_violations=meta.get("safety_violations", []),
            explanation=classification.explanation,
        )
        return classification, metrics
