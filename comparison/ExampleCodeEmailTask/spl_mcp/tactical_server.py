"""Tactical MCP server (Layer 1) that manages patterns via MCP resources."""

from __future__ import annotations

from typing import Any, Dict, Optional, Iterable
from datetime import datetime
import re
from pathlib import Path
import sys

SPL_FRAMEWORK_PATH = Path(__file__).resolve().parents[2] / "SPL-FRAMEWORK"
if str(SPL_FRAMEWORK_PATH) not in sys.path:
    sys.path.insert(0, str(SPL_FRAMEWORK_PATH))

from spl.layer1_tactical import (
    Layer1Config,
    Pattern,
    pattern_is_healthy,
)
from spl.world_state import WorldState, world_state_from_json, world_state_to_json
from .base import LocalMCPServer
from .resource_store import ResourceStore


def pattern_to_json(pattern: Pattern) -> Dict[str, Any]:
    """Serialize Pattern dataclass into JSON-friendly dict."""
    return {
        "name": pattern.name,
        "category": pattern.category,
        "regex": pattern.regex,
        "confidence": pattern.confidence,
        "learned_by": pattern.learned_by,
        "learned_at": pattern.learned_at.isoformat() if isinstance(pattern.learned_at, datetime) else str(pattern.learned_at),
        "last_validated": pattern.last_validated.isoformat() if isinstance(pattern.last_validated, datetime) else pattern.last_validated,
        "accuracy_on_holdout": pattern.accuracy_on_holdout,
        "match_count": pattern.match_count,
    }


def pattern_from_json(payload: Dict[str, Any]) -> Pattern:
    """Deserialize Pattern from JSON payload."""
    learned_at = payload.get("learned_at")
    if isinstance(learned_at, str):
        try:
            learned_at = datetime.fromisoformat(learned_at)
        except ValueError:
            learned_at = datetime.utcnow()
    last_validated = payload.get("last_validated")
    if isinstance(last_validated, str):
        try:
            last_validated = datetime.fromisoformat(last_validated)
        except ValueError:
            last_validated = None
    return Pattern(
        name=payload["name"],
        category=payload["category"],
        regex=payload["regex"],
        confidence=float(payload.get("confidence", 0.0)),
        learned_by=payload.get("learned_by", "unknown"),
        learned_at=learned_at,
        last_validated=last_validated,
        accuracy_on_holdout=payload.get("accuracy_on_holdout"),
        match_count=int(payload.get("match_count", 0)),
    )


class TacticalMCPServer(LocalMCPServer):
    """MCP server exposing tactical pattern tools."""

    def __init__(self, resource_store: ResourceStore, config: Dict[str, Any], agent_id: str):
        super().__init__(name="tactical")
        self.resource_store = resource_store
        self.agent_id = agent_id
        l1_cfg = config.get("layer1", {})
        self.layer1_config = Layer1Config(
            high_confidence_threshold=float(l1_cfg.get("high_confidence_threshold", 0.85)),
            learn_pattern_min_confidence=float(l1_cfg.get("learn_pattern_min_confidence", 0.90)),
            min_accuracy_for_use=float(l1_cfg.get("min_accuracy_for_use", 0.80)),
            pattern_age_max_days=int(l1_cfg.get("pattern_age_max_days", 30)),
            require_revalidation=bool(l1_cfg.get("require_revalidation", True)),
        )
        self.resource_store.ensure(f"patterns/{self.agent_id}", {})
        self.register_tool("tactical.match_email", self.match_email)
        self.register_tool("tactical.learn_pattern_from_l2", self.learn_pattern_from_l2)
        self.register_tool("tactical.list_patterns", self.list_patterns)

    def _load_state(self) -> WorldState:
        payload = self.resource_store.read(f"world_state/{self.agent_id}")
        return world_state_from_json(payload)

    def _save_state(self, state: WorldState) -> None:
        self.resource_store.write(f"world_state/{self.agent_id}", world_state_to_json(state))

    def _load_patterns(self) -> Dict[str, Pattern]:
        raw = self.resource_store.ensure(f"patterns/{self.agent_id}", {})
        return {name: pattern_from_json(data) for name, data in raw.items()}

    def _save_patterns(self, patterns: Dict[str, Pattern]) -> None:
        serialized = {name: pattern_to_json(pat) for name, pat in patterns.items()}
        self.resource_store.write(f"patterns/{self.agent_id}", serialized)

    def _derive_key_from_email(self, subject: str, body: str) -> str:
        for word in subject.split():
            cleaned = word.strip().lower()
            if cleaned:
                return cleaned
        for word in body.split():
            cleaned = word.strip().lower()
            if cleaned:
                return cleaned
        return "pattern"

    def match_email(
        self,
        agent_id: str,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        """Match email against healthy patterns, updating counts."""
        if agent_id != self.agent_id:
            raise ValueError(f"Unknown agent_id {agent_id}")
        state = self._load_state()
        patterns = self._load_patterns()
        content = f"Subject: {subject}\n\n{body}"
        now = datetime.utcnow()
        for pattern in patterns.values():
            if not pattern_is_healthy(pattern, self.layer1_config, now):
                continue
            try:
                if re.search(pattern.regex, content, re.IGNORECASE):
                    pattern.match_count += 1
                    suppress = pattern.confidence >= self.layer1_config.high_confidence_threshold
                    self._save_patterns(patterns)
                    explanation = (
                        f"Matched pattern '{pattern.name}' with confidence {pattern.confidence:.2f}"
                        f" (suppress_layer2={suppress})"
                    )
                    return {
                        "matched": True,
                        "category": pattern.category,
                        "pattern_name": pattern.name,
                        "suppress_layer2": suppress,
                        "explanation": explanation,
                    }
            except re.error:
                continue
        self._save_patterns(patterns)
        return {
            "matched": False,
            "category": None,
            "pattern_name": None,
            "suppress_layer2": False,
            "explanation": "No healthy pattern matched",
        }

    def learn_pattern_from_l2(
        self,
        agent_id: str,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        category: str,
        confidence: float,
        learned_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Learn a new pattern from L2 output if confidence is high enough."""
        if agent_id != self.agent_id:
            raise ValueError(f"Unknown agent_id {agent_id}")
        patterns = self._load_patterns()
        state = self._load_state()
        if confidence < self.layer1_config.learn_pattern_min_confidence:
            return {"learned": False, "reason": "confidence_below_threshold"}
        key = self._derive_key_from_email(subject, body)
        pattern_name = f"learned_{key}"
        now = datetime.utcnow()
        patterns[pattern_name] = Pattern(
            name=pattern_name,
            category=category,
            regex=re.escape(key),
            confidence=confidence,
            learned_by=learned_by or "L2",
            learned_at=now,
            last_validated=None,
            accuracy_on_holdout=None,
            match_count=0,
        )
        state.learned_patterns[pattern_name] = {
            "category": category,
            "regex": re.escape(key),
            "confidence": confidence,
            "learned_by": learned_by or "L2",
            "learned_at": now.isoformat(),
        }
        self._save_patterns(patterns)
        self._save_state(state)
        return {"learned": True, "pattern_name": pattern_name, "category": category}

    def list_patterns(self, agent_id: str) -> Dict[str, Any]:
        """List patterns and metadata for debugging."""
        if agent_id != self.agent_id:
            raise ValueError(f"Unknown agent_id {agent_id}")
        patterns = self._load_patterns()
        return {"patterns": [pattern_to_json(pat) for pat in patterns.values()]}
