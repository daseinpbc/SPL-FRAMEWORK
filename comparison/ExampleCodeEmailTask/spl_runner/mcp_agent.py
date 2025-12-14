"""MCP-based SPL orchestrator that routes all layer calls through MCP servers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import sys

SPL_FRAMEWORK_PATH = Path(__file__).resolve().parents[2] / "SPL-FRAMEWORK"
if str(SPL_FRAMEWORK_PATH) not in sys.path:
    sys.path.insert(0, str(SPL_FRAMEWORK_PATH))

from common.email_schema import ClassificationResult, EmailRecord, TokenUsage
from spl.world_state import world_state_from_json, world_state_to_json, default_world_state
from spl.mcp_integration import MCPClient
from spl_mcp.base import LocalMCPClient
from spl_mcp.resource_store import ResourceStore
from spl_mcp.reactive_server import ReactiveMCPServer
from spl_mcp.tactical_server import TacticalMCPServer
from spl_mcp.deliberative_server import DeliberativeMCPServer


@dataclass
class MCPDecision:
    category: str
    confidence: float
    final_layer: str
    explanation: Optional[str] = None
    pattern_name: Optional[str] = None
    token_usage: Optional[TokenUsage] = None
    cost_usd: float = 0.0
    suppressed: bool = False
    safety_violations: Optional[List[str]] = None


class SPLMCPAgent:
    """Single-agent MCP orchestrator for SPL."""

    def __init__(
        self,
        agent_id: str,
        settings: Dict[str, Any],
        providers: Dict[str, Any],
        labels_config: List[Dict[str, Any]],
        llm_client: MCPClient,
    ):
        self.agent_id = agent_id
        self.settings = settings
        self.providers = providers
        self.labels_config = labels_config
        spl_cfg = settings.get("spl", {})
        budget = spl_cfg.get("budget_usd")
        permissions = spl_cfg.get("permissions", {"can_classify_email": True})

        self.resource_store = ResourceStore()
        # Initialize world state resource upfront (reset to default each start)
        self.resource_store.write(
            f"world_state/{agent_id}",
            world_state_to_json(default_world_state(agent_id, budget_remaining=budget, permissions=permissions)),
        )
        # Start MCP servers and clients
        self.reactive_server = ReactiveMCPServer(self.resource_store, spl_cfg, agent_id, budget)
        self.tactical_server = TacticalMCPServer(self.resource_store, spl_cfg, agent_id)
        groq_cfg = providers.get("groq", {}).get("spl", {})
        model_name = groq_cfg.get("model") or groq_cfg.get("model_id") or "llama-3.1-8b-instant"
        self.deliberative_server = DeliberativeMCPServer(
            self.resource_store,
            agent_id=agent_id,
            model_name=model_name,
            labels_config=labels_config,
            mcp_client=llm_client,
            budget=budget,
        )

        self.reactive_client = LocalMCPClient(self.reactive_server)
        self.tactical_client = LocalMCPClient(self.tactical_server)
        self.deliberative_client = LocalMCPClient(self.deliberative_server)
        self.last_run_meta: Dict[str, Any] = {}

    def _world_state(self) -> Dict[str, Any]:
        return self.resource_store.read(f"world_state/{self.agent_id}")

    def process_email(self, email: EmailRecord) -> ClassificationResult:
        """Run L0 -> L1 -> L2 via MCP tools."""
        # L0
        l0_resp = self.reactive_client.call_tool(
            "reactive.validate_email",
            agent_id=self.agent_id,
            sender=email.from_address,
            recipient=email.to_address,
            subject=email.subject,
            body=email.body,
            user_id=email.from_address,
        )
        if not l0_resp.get("should_continue", False):
            decision = MCPDecision(
                category="invalid",
                confidence=1.0,
                final_layer="L0",
                explanation=l0_resp.get("reason"),
                suppressed=True,
            )
            return self._finalize(email, decision)

        # L1
        l1_resp = self.tactical_client.call_tool(
            "tactical.match_email",
            agent_id=self.agent_id,
            sender=email.from_address,
            recipient=email.to_address,
            subject=email.subject,
            body=email.body,
        )
        if l1_resp.get("suppress_layer2"):
            decision = MCPDecision(
                category=l1_resp.get("category") or "unknown",
                confidence=1.0,
                final_layer="L1",
                pattern_name=l1_resp.get("pattern_name"),
                explanation=l1_resp.get("explanation"),
                suppressed=True,
            )
            return self._finalize(email, decision)

        # Check world state suppression after L1
        state_summary = self.reactive_client.call_tool(
            "reactive.get_world_state_summary",
            agent_id=self.agent_id,
        )
        if "L2" in state_summary.get("suppressed_layers", []):
            decision = MCPDecision(
                category="suppressed",
                confidence=0.0,
                final_layer="L1",
                explanation="L2 suppressed by world state",
                suppressed=True,
            )
            return self._finalize(email, decision)

        # L2
        l2_resp = self.deliberative_client.call_tool(
            "deliberative.classify_email",
            agent_id=self.agent_id,
            sender=email.from_address,
            recipient=email.to_address,
            subject=email.subject,
            body=email.body,
        )
        if l2_resp.get("suppressed"):
            decision = MCPDecision(
                category=l2_resp.get("category") or "suppressed",
                confidence=float(l2_resp.get("confidence", 0.0)),
                final_layer="L1",
                explanation=l2_resp.get("reason"),
                suppressed=True,
            )
            return self._finalize(email, decision)

        token_usage = l2_resp.get("token_usage")
        tu_obj = TokenUsage(**token_usage) if token_usage else None
        decision = MCPDecision(
            category=l2_resp.get("category", "other"),
            confidence=float(l2_resp.get("confidence", 0.0)),
            final_layer="L2",
            explanation=l2_resp.get("reason"),
            token_usage=tu_obj,
            cost_usd=float(l2_resp.get("cost_usd", 0.0)),
        )
        # Pattern learning if confident
        if decision.confidence >= self.tactical_server.layer1_config.learn_pattern_min_confidence:
            self.tactical_client.call_tool(
                "tactical.learn_pattern_from_l2",
                agent_id=self.agent_id,
                sender=email.from_address,
                recipient=email.to_address,
                subject=email.subject,
                body=email.body,
                category=decision.category,
                confidence=decision.confidence,
                learned_by="L2",
            )

        return self._finalize(email, decision)

    def _finalize(self, email: EmailRecord, decision: MCPDecision) -> ClassificationResult:
        """Persist meta about the run and return ClassificationResult."""
        state = world_state_from_json(self._world_state())
        self.last_run_meta = {
            "final_layer": decision.final_layer,
            "l1_suppressed_l2": decision.suppressed and decision.final_layer == "L1",
            "budget_remaining": state.budget_remaining,
            "tokens_used": state.tokens_used,
            "safety_violations": list(state.safety_violations),
            "layers_used": self._layers_used(decision.final_layer),
            "cost_usd": decision.cost_usd,
            "token_usage": decision.token_usage.model_dump() if decision.token_usage else None,
        }
        return ClassificationResult(
            email_id=email.id,
            predicted_label=decision.category,
            method="spl",
            raw_response={"explanation": decision.explanation, "pattern": decision.pattern_name},
            explanation=decision.explanation,
        )

    def _layers_used(self, final_layer: str) -> List[int]:
        if final_layer == "L0":
            return [0]
        if final_layer == "L1":
            return [0, 1]
        return [0, 1, 2]
