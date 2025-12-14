"""Reactive MCP server (Layer 0) that validates emails and updates world state."""

from __future__ import annotations

from typing import Any, Dict, Optional
import time
from pathlib import Path
import sys

SPL_FRAMEWORK_PATH = Path(__file__).resolve().parents[2] / "SPL-FRAMEWORK"
if str(SPL_FRAMEWORK_PATH) not in sys.path:
    sys.path.insert(0, str(SPL_FRAMEWORK_PATH))

from spl.layer0_reactive import Layer0Reactive, Layer0Config
from spl.world_state import WorldState, world_state_from_json, world_state_to_json, default_world_state
from .base import LocalMCPServer
from .resource_store import ResourceStore


class ReactiveMCPServer(LocalMCPServer):
    """MCP server exposing reactive tools."""

    def __init__(self, resource_store: ResourceStore, config: Dict[str, Any], agent_id: str, budget: Optional[float]):
        super().__init__(name="reactive")
        self.resource_store = resource_store
        self.agent_id = agent_id
        self.layer0_config = self._build_layer0_config(config.get("layer0", {}))
        self._layer0 = Layer0Reactive(config=self.layer0_config)
        self._ensure_world_state(budget, permissions=config.get("permissions"))
        self.register_tool("reactive.validate_email", self.validate_email)
        self.register_tool("reactive.get_world_state_summary", self.get_world_state_summary)

    def _build_layer0_config(self, cfg: Dict[str, Any]) -> Layer0Config:
        return Layer0Config(
            min_length=int(cfg.get("min_length", 5)),
            max_length=int(cfg.get("max_length", 1000)),
            max_requests_per_window=int(cfg.get("max_requests_per_window", 100)),
            window_seconds=int(cfg.get("window_seconds", 60)),
            blocked_senders=set(map(str.lower, cfg.get("blocked_senders", []))),
            allowed_domains=set(map(str.lower, cfg.get("allowed_domains", []))),
        )

    def _ensure_world_state(self, budget: Optional[float], permissions: Optional[Dict[str, bool]]) -> None:
        resource_id = f"world_state/{self.agent_id}"
        default_state = default_world_state(self.agent_id, budget, permissions=permissions)
        self.resource_store.ensure(resource_id, world_state_to_json(default_state))

    def _load_state(self) -> WorldState:
        resource_id = f"world_state/{self.agent_id}"
        payload = self.resource_store.read(resource_id)
        return world_state_from_json(payload)

    def _save_state(self, state: WorldState) -> None:
        resource_id = f"world_state/{self.agent_id}"
        self.resource_store.write(resource_id, world_state_to_json(state))

    def validate_email(
        self,
        agent_id: str,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Validate email inputs and update world state with any violations."""
        if agent_id != self.agent_id:
            raise ValueError(f"Unknown agent_id {agent_id}")
        state = self._load_state()
        content = f"Subject: {subject}\n\n{body}"
        result = self._layer0.validate(
            {"user_id": user_id or sender, "sender": sender, "content": content},
            state=state,
        )
        if not result.valid:
            state.suppressed_layers.append("L2")
        self._save_state(state)
        return {
            "should_continue": result.should_continue and result.valid,
            "reason": result.reason or "ok",
            "world_state": world_state_to_json(state),
        }

    def get_world_state_summary(self, agent_id: str) -> Dict[str, Any]:
        """Return a minimal world state summary for orchestration."""
        if agent_id != self.agent_id:
            raise ValueError(f"Unknown agent_id {agent_id}")
        state = self._load_state()
        return {
            "agent_id": state.agent_id,
            "budget_remaining": state.budget_remaining,
            "tokens_used": state.tokens_used,
            "safety_violations": list(state.safety_violations),
            "suppressed_layers": list(state.suppressed_layers),
            "rate_limit_reset_at": state.rate_limit_reset_at,
        }
