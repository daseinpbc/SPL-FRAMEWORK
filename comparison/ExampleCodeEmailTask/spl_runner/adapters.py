"""Adapters that bridge the SPL framework to the POC email domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional

SPL_FRAMEWORK_PATH = Path(__file__).resolve().parents[2] / "SPL-FRAMEWORK"
if str(SPL_FRAMEWORK_PATH) not in sys.path:
    sys.path.insert(0, str(SPL_FRAMEWORK_PATH))

from spl.layer0_reactive import Layer0Reactive, ValidationResult, Layer0Config
from spl.layer1_tactical import (
    Layer1Tactical,
    PatternMatchResult,
    Layer1Config,
    PatternStore,
)
from spl.mcp_integration import MCPResponse

from common.cost_model import estimate_cost_usd
from common.email_schema import ClassificationResult, EmailRecord, TokenUsage
from spl_runner.groq_client import GroqMCPClient


@dataclass
class WorldState:
    """Mutable world state shared across SPL layers."""
    budget_remaining: Optional[float]
    tokens_used: int = 0
    safety_violations: List[str] = field(default_factory=list)
    suppressed_layers: set[str] = field(default_factory=set)
    rate_limit_counters: Dict[str, int] = field(default_factory=dict)
    rate_limit_reset_at: float = field(default_factory=time.time)
    permissions: Dict[str, bool] = field(default_factory=lambda: {"can_classify_email": True})
    learned_patterns: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Layer2Result:
    """Structured Layer 2 result."""
    category: str
    confidence: float
    raw_response: Dict[str, Any]
    token_usage: Optional[TokenUsage]
    cost_usd: float
    model: Optional[str] = None
    error: Optional[str] = None


def derive_key_from_email(email: EmailRecord) -> str:
    """First non-empty word in subject, lowercased, for pattern learning."""
    for word in email.subject.split():
        cleaned = word.strip().lower()
        if cleaned:
            return cleaned
    return "unknown"


class GroqEmailClient(GroqMCPClient):
    """Thin Groq client wrapper for legacy adapter compatibility."""

    def __init__(self, model: str, api_key: str, base_url: str):
        super().__init__(model=model, api_token=api_key, base_url=base_url)


class SplEmailWorld:
    """Encapsulates SPL state, configs, and MCP client for email classification."""

    def __init__(
        self,
        settings: Dict[str, Any],
        providers: Dict[str, Any],
        labels_config: List[Dict[str, Any]],
        mcp_client: Optional[GroqEmailClient] = None,
    ):
        self.settings = settings
        self.providers = providers
        self.labels_config = labels_config
        self.label_names = [item["name"] for item in labels_config]
        spl_cfg = settings.get("spl", {})

        l0_cfg = spl_cfg.get("layer0", {})
        self.layer0_config = Layer0Config(
            min_length=int(l0_cfg.get("min_length", 5)),
            max_length=int(l0_cfg.get("max_length", 1000)),
            max_requests_per_window=int(l0_cfg.get("max_requests_per_window", 100)),
            window_seconds=int(l0_cfg.get("window_seconds", 60)),
            blocked_senders=set(map(str.lower, l0_cfg.get("blocked_senders", []))),
            allowed_domains=set(map(str.lower, l0_cfg.get("allowed_domains", []))),
        )
        l1_cfg = spl_cfg.get("layer1", {})
        self.layer1_config = Layer1Config(
            high_confidence_threshold=float(l1_cfg.get("high_confidence_threshold", 0.85)),
            learn_pattern_min_confidence=float(l1_cfg.get("learn_pattern_min_confidence", 0.90)),
            min_accuracy_for_use=float(l1_cfg.get("min_accuracy_for_use", 0.80)),
            pattern_age_max_days=int(l1_cfg.get("pattern_age_max_days", 30)),
            require_revalidation=bool(l1_cfg.get("require_revalidation", True)),
        )

        budget = spl_cfg.get("budget_usd")
        self.state = WorldState(budget_remaining=float(budget) if budget is not None else None)
        self.pattern_store = PatternStore()
        self.shared_state: Dict[str, Any] = {"learned_patterns": self.state.learned_patterns}

        self.layer0 = Layer0Reactive(config=self.layer0_config)
        self.layer1 = Layer1Tactical(
            config=self.layer1_config,
            pattern_store=self.pattern_store,
            shared_state=self.shared_state,
        )

        groq_cfg = providers.get("groq", {}).get("spl", {})
        self.model_name = groq_cfg.get("model") or groq_cfg.get("model_id") or "llama-3.1-8b-instant"
        self.base_url = providers.get("groq", {}).get("base_url", "https://api.groq.com/openai/v1")
        self.mcp_client = mcp_client
        self.rate_limiter = None
        self.min_l2_cost = self._compute_min_l2_cost()
        self.last_run_meta: Dict[str, Any] = {}

    def _compute_min_l2_cost(self) -> float:
        """Compute minimum possible L2 cost from provider pricing for budget gating."""
        pricing = (
            self.providers.get("groq", {})
            .get("pricing", {})
            .get(self.model_name or "", {})
        )
        input_rate = float(pricing.get("input_cost_per_1k_tokens_usd", 0.0))
        output_rate = float(pricing.get("output_cost_per_1k_tokens_usd", 0.0))
        if input_rate == 0.0 and output_rate == 0.0:
            return 0.0
        return (input_rate + output_rate) / 1000.0

    def build_email_content(self, email: EmailRecord) -> str:
        """Compose the text that SPL layers inspect."""
        return f"Subject: {email.subject}\n\n{email.body}"

    def _build_system_prompt(self) -> str:
        """Construct system instructions with label definitions."""
        label_lines = [f'- "{item["name"]}": {item.get("description", "")}' for item in self.labels_config]
        labels_text = "\n".join(label_lines)
        return (
            "You are a classifier that labels emails using the provided categories.\n"
            "Respond ONLY with JSON using the schema {\"label\": \"<label>\", \"confidence\": <0-1>}.\n"
            "Allowed labels and descriptions:\n"
            f"{labels_text}"
        )

    def _build_user_prompt(self, content: str) -> str:
        """Build the user-facing prompt containing the email content."""
        return f"Classify the following email.\n\n{content}"

    def _normalize_label(self, raw_label: str) -> str:
        """Map model output to configured label names."""
        normalized = raw_label.strip().lower()
        if normalized in self.label_names:
            return normalized
        return self.label_names[0] if self.label_names else normalized

    def _extract_token_usage(
        self, response_text: str, system_prompt: str, user_prompt: str
    ) -> TokenUsage:
        """Heuristic token usage estimation when the provider does not supply metrics."""
        prompt_chars = len(system_prompt) + len(user_prompt)
        completion_chars = len(response_text)
        return TokenUsage(
            prompt_tokens=max(int(prompt_chars / 4), 1),
            completion_tokens=max(int(completion_chars / 4), 1),
        )

    def call_layer2_llm(self, content: str) -> Layer2Result:
        """Call Groq via the MCP client to align with SPL integration semantics."""
        if self.mcp_client is None:
            raise RuntimeError("MCP client is required for Layer 2 reasoning")
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(content)
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        if self.rate_limiter is not None:
            self.rate_limiter.acquire()

        response = self.mcp_client.reason(combined_prompt)  # type: ignore[union-attr]
        label = self._normalize_label(response.category or (self.label_names[0] if self.label_names else ""))
        confidence = float(response.confidence or 0.0)
        token_usage = self._extract_token_usage(response.content or "", system_prompt, user_prompt)
        cost_usd = estimate_cost_usd(token_usage, self.model_name or "")
        raw = {
            "response": response.content,
            "parsed": {
                "label": label,
                "confidence": confidence,
                "from_llm": True,
                "model": response.model,
            },
            "from_llm": True,
        }
        return Layer2Result(
            category=label,
            confidence=confidence,
            raw_response=raw,
            token_usage=token_usage,
            cost_usd=cost_usd,
            model=response.model,
        )

    def build_result_from_l0(
        self, l0_result: ValidationResult, state: WorldState, layers_used: List[int], email_id: str
    ) -> ClassificationResult:
        """Construct final result when Layer 0 halts processing."""
        self.last_run_meta = {
            "final_layer": "L0",
            "layers_used": layers_used,
            "l1_suppressed_l2": False,
            "budget_remaining": state.budget_remaining,
            "tokens_used": state.tokens_used,
            "safety_violations": list(state.safety_violations),
            "cost_usd": 0.0,
            "token_usage": None,
        }
        return ClassificationResult(
            email_id=email_id,
            predicted_label="invalid",
            method="spl",
            raw_response={"reason": l0_result.reason, "layer": "L0"},
            explanation=l0_result.reason,
        )

    def build_result_from_l1(
        self, l1_result: PatternMatchResult, state: WorldState, layers_used: List[int], email_id: str
    ) -> ClassificationResult:
        """Construct final result when Layer 1 suppresses Layer 2."""
        explanation = f"Suppressed Layer 2 via pattern '{l1_result.pattern_name}' (confidence={l1_result.confidence:.2f})"
        self.last_run_meta = {
            "final_layer": "L1",
            "layers_used": layers_used,
            "l1_suppressed_l2": True,
            "budget_remaining": state.budget_remaining,
            "tokens_used": state.tokens_used,
            "safety_violations": list(state.safety_violations),
            "cost_usd": 0.0,
            "pattern": l1_result.pattern_name,
            "token_usage": None,
        }
        return ClassificationResult(
            email_id=email_id,
            predicted_label=l1_result.category or "unknown",
            method="spl",
            raw_response={"pattern": l1_result.pattern_name, "layer": "L1"},
            explanation=explanation,
        )

    def build_result_for_suppressed_l2(
        self, state: WorldState, layers_used: List[int], email_id: str
    ) -> ClassificationResult:
        """Construct final result when L2 is suppressed for budget/safety reasons."""
        reason = "budget_exhausted" if "budget_exhausted" in state.safety_violations else "layer_suppressed"
        explanation = f"Layer 2 suppressed due to {reason}"
        self.last_run_meta = {
            "final_layer": "L1",
            "layers_used": layers_used,
            "l1_suppressed_l2": False,
            "budget_remaining": state.budget_remaining,
            "tokens_used": state.tokens_used,
            "safety_violations": list(state.safety_violations),
            "cost_usd": 0.0,
            "token_usage": None,
        }
        return ClassificationResult(
            email_id=email_id,
            predicted_label=reason,
            method="spl",
            raw_response={"reason": reason, "layer": "L1"},
            explanation=explanation,
        )

    def build_result_from_l2(
        self, l2_result: Layer2Result, state: WorldState, layers_used: List[int], email_id: str
    ) -> ClassificationResult:
        """Construct final result when Layer 2 produces the decision."""
        self.last_run_meta = {
            "final_layer": "L2",
            "layers_used": layers_used,
            "l1_suppressed_l2": False,
            "budget_remaining": state.budget_remaining,
            "tokens_used": state.tokens_used,
            "safety_violations": list(state.safety_violations),
            "cost_usd": l2_result.cost_usd,
            "token_usage": l2_result.token_usage.model_dump() if l2_result.token_usage else None,
        }
        return ClassificationResult(
            email_id=email_id,
            predicted_label=l2_result.category,
            method="spl",
            raw_response=l2_result.raw_response,
            explanation=l2_result.error,
        )


def run_layer0(email: EmailRecord, state: WorldState, world: SplEmailWorld) -> ValidationResult:
    """Execute Layer 0 validation for an email."""
    content = world.build_email_content(email)
    return world.layer0.validate(
        {"user_id": email.from_address, "sender": email.from_address, "content": content},
        state,
    )


def run_layer1(email: EmailRecord, state: WorldState, pattern_store: PatternStore, world: SplEmailWorld) -> PatternMatchResult:
    """Execute Layer 1 pattern matching using the world's pattern store."""
    content = world.build_email_content(email)
    return world.layer1.match(content, now=datetime.utcnow())


def run_layer2(email: EmailRecord, state: WorldState, mcp_client: GroqEmailClient, world: SplEmailWorld) -> Layer2Result:
    """Execute Layer 2 deliberative reasoning via the MCP client with budget checks."""
    world.mcp_client = world.mcp_client or mcp_client
    if world.mcp_client is None:
        return Layer2Result(
            category="error",
            confidence=0.0,
            raw_response={"error": "missing_mcp_client"},
            token_usage=None,
            cost_usd=0.0,
            model=world.model_name,
            error="missing_mcp_client",
        )

    if state.budget_remaining is not None and world.min_l2_cost and state.budget_remaining < world.min_l2_cost:
        state.safety_violations.append("budget_exhausted")
        state.suppressed_layers.add("L2")
        return Layer2Result(
            category="error",
            confidence=0.0,
            raw_response={"error": "budget_exhausted"},
            token_usage=None,
            cost_usd=0.0,
            model=world.model_name,
            error="budget_exhausted",
        )

    content = world.build_email_content(email)
    l2_result = world.call_layer2_llm(content)
    if l2_result.token_usage:
        state.tokens_used += l2_result.token_usage.total_tokens
    if state.budget_remaining is not None:
        starting_budget = state.budget_remaining
        state.budget_remaining = max(starting_budget - l2_result.cost_usd, 0.0)
        if l2_result.cost_usd > starting_budget:
            state.safety_violations.append("budget_exhausted")
            state.suppressed_layers.add("L2")
            l2_result.error = l2_result.error or "budget_exhausted"
    return l2_result


def run_email_spl(email: EmailRecord, world: SplEmailWorld) -> ClassificationResult:
    """Deprecated in favor of MCP-based orchestration (see SPLMCPAgent)."""
    raise NotImplementedError("run_email_spl is deprecated; use SPLMCPAgent in spl_runner.mcp_agent instead.")
