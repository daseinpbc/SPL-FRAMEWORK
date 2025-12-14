"""Deliberative MCP server (Layer 2) that wraps the LLM client and updates world state."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import sys

SPL_FRAMEWORK_PATH = Path(__file__).resolve().parents[2] / "SPL-FRAMEWORK"
if str(SPL_FRAMEWORK_PATH) not in sys.path:
    sys.path.insert(0, str(SPL_FRAMEWORK_PATH))

from spl.mcp_integration import MCPClient, MCPResponse
from spl.world_state import WorldState, world_state_from_json, world_state_to_json
from common.cost_model import estimate_cost_usd
from common.email_schema import TokenUsage
from .base import LocalMCPServer
from .resource_store import ResourceStore


@dataclass
class L2Result:
    category: str
    confidence: float
    raw_response: Dict[str, Any]
    token_usage: Optional[TokenUsage]
    cost_usd: float
    suppressed: bool = False
    reason: Optional[str] = None


class DeliberativeMCPServer(LocalMCPServer):
    """MCP server exposing deliberative classification tools."""

    def __init__(
        self,
        resource_store: ResourceStore,
        agent_id: str,
        model_name: str,
        labels_config: List[Dict[str, Any]],
        mcp_client: MCPClient,
        budget: Optional[float],
    ):
        super().__init__(name="deliberative")
        self.resource_store = resource_store
        self.agent_id = agent_id
        self.model_name = model_name
        self.labels_config = labels_config
        self.mcp_client = mcp_client
        self.default_budget = budget
        self.register_tool("deliberative.classify_email", self.classify_email)

    def _load_state(self) -> WorldState:
        payload = self.resource_store.read(f"world_state/{self.agent_id}")
        return world_state_from_json(payload)

    def _save_state(self, state: WorldState) -> None:
        self.resource_store.write(f"world_state/{self.agent_id}", world_state_to_json(state))

    def _build_system_prompt(self) -> str:
        label_lines = [f'- "{item["name"]}": {item.get("description", "")}' for item in self.labels_config]
        labels_text = "\n".join(label_lines)
        return (
            "You are a classifier that labels emails using the provided categories.\n"
            "Respond ONLY with JSON using the schema {\"label\": \"<label>\", \"confidence\": <0-1>}.\n"
            "Allowed labels and descriptions:\n"
            f"{labels_text}"
        )

    def _build_user_prompt(self, subject: str, body: str) -> str:
        return f"Classify the following email.\n\nSubject: {subject}\n\n{body}"

    def _normalize_label(self, raw_label: str) -> str:
        normalized = raw_label.strip().lower()
        label_names = [item["name"] for item in self.labels_config]
        if normalized in label_names:
            return normalized
        return label_names[0] if label_names else normalized

    def _estimate_tokens(self, prompt: str, completion: str) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=max(len(prompt) // 4, 1),
            completion_tokens=max(len(completion) // 4, 1),
        )

    def classify_email(
        self,
        agent_id: str,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        """Classify email with LLM, respecting budget and suppression rules."""
        if agent_id != self.agent_id:
            raise ValueError(f"Unknown agent_id {agent_id}")

        state = self._load_state()
        if "L2" in state.suppressed_layers:
            return {
                "category": "suppressed",
                "confidence": 0.0,
                "raw_response": {"reason": "suppressed_by_state"},
                "token_usage": None,
                "cost_usd": 0.0,
                "suppressed": True,
                "reason": "suppressed_by_state",
            }

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(subject, body)
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Simple budget guard: assume at least minimal cost of a tiny completion
        min_token_usage = TokenUsage(prompt_tokens=max(len(combined_prompt) // 4, 1), completion_tokens=1)
        min_cost = estimate_cost_usd(min_token_usage, self.model_name)
        if state.budget_remaining is not None and state.budget_remaining < min_cost:
            state.safety_violations.append("budget_exhausted")
            state.suppressed_layers.append("L2")
            self._save_state(state)
            return {
                "category": "budget_exhausted",
                "confidence": 0.0,
                "raw_response": {"reason": "budget_exhausted"},
                "token_usage": None,
                "cost_usd": 0.0,
                "suppressed": True,
                "reason": "budget_exhausted",
            }

        try:
            response: MCPResponse = self.mcp_client.reason(combined_prompt)
        except Exception as error:  # noqa: BLE001
            state.safety_violations.append("mcp_error_deliberative")
            self._save_state(state)
            return {
                "category": "error",
                "confidence": 0.0,
                "raw_response": {"error": str(error)},
                "token_usage": None,
                "cost_usd": 0.0,
                "suppressed": True,
                "reason": "mcp_error_deliberative",
            }

        label = self._normalize_label(response.category or "other")
        confidence = float(response.confidence or 0.0)
        token_usage = self._estimate_tokens(combined_prompt, response.content or "")
        cost_usd = estimate_cost_usd(token_usage, self.model_name)
        state.tokens_used += token_usage.total_tokens
        if state.budget_remaining is not None:
            state.budget_remaining = max(state.budget_remaining - cost_usd, 0.0)
        self._save_state(state)

        raw_response = {
            "response": response.content,
            "model": response.model,
            "from_llm": True,
        }
        return {
            "category": label,
            "confidence": confidence,
            "raw_response": raw_response,
            "token_usage": token_usage.model_dump(),
            "cost_usd": cost_usd,
            "suppressed": False,
            "reason": "ok",
        }
