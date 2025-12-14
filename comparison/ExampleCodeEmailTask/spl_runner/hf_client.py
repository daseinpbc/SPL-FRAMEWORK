"""Hugging Face Inference MCP client."""

from __future__ import annotations

from typing import Any, Dict, Optional
import requests

from spl.mcp_integration import MCPClient, MCPResponse


class HFInferenceMCPClient(MCPClient):
    """MCP client that routes Layer 2 through Hugging Face Inference API."""

    def __init__(self, model_id: str, api_token: str, base_url: str = "https://api-inference.huggingface.co/models"):
        super().__init__(model=model_id, api_client=True, cost_per_call=0.0)
        self.model_id = model_id
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _call_api(self, content: str, context: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """Call Hugging Face Inference API."""
        endpoint = f"{self.base_url}/{self.model_id}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload: Dict[str, Any] = {"inputs": content, "options": {"wait_for_model": True}}
        if context:
            payload.update(context)
        response = self.session.post(endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        generated = ""
        if isinstance(data, list) and data:
            first = data[0]
            generated = first.get("generated_text") or first.get("summary_text") or str(first)
        elif isinstance(data, dict):
            generated = data.get("generated_text") or str(data)
        return MCPResponse(
            content=generated,
            category=(generated or "other").strip().split()[0].lower() if generated else "other",
            confidence=0.0,
            cost=self.cost_per_call,
            model=self.model_id,
        )
