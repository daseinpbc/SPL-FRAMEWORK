"""Minimal in-process MCP server/client primitives for the SPL POC."""

from __future__ import annotations

from typing import Any, Callable, Dict


class LocalMCPServer:
    """Registers tool handlers and dispatches tool invocations."""

    def __init__(self, name: str):
        self.name = name
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register_tool(self, name: str, handler: Callable[..., Any]) -> None:
        self._tools[name] = handler

    def call_tool(self, name: str, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool {name} not registered on server {self.name}")
        return self._tools[name](**kwargs)


class LocalMCPClient:
    """Simple client wrapper that calls into a LocalMCPServer."""

    def __init__(self, server: LocalMCPServer):
        self.server = server

    def call_tool(self, name: str, **kwargs: Any) -> Any:
        return self.server.call_tool(name, **kwargs)
