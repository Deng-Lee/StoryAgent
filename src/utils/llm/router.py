from __future__ import annotations

from dataclasses import dataclass

from utils.llm.types import ToolProtocol


NATIVE_TOOL_MODELS = {
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4o-mini-2024-07-18",
}

NATIVE_TOOL_AGENTS = {
    "Interviewer",
}


@dataclass(frozen=True)
class ProtocolRoute:
    protocol: ToolProtocol
    reason: str


def model_supports_native_tools(model_name: str | None) -> bool:
    if not model_name:
        return False

    normalized = model_name.strip()
    if normalized in NATIVE_TOOL_MODELS:
        return True

    return normalized.startswith("gpt-4o")


def select_tool_call_protocol(
    *,
    model_name: str | None,
    agent_name: str | None,
    has_tools: bool,
    force_xml: bool = False,
) -> ProtocolRoute:
    if force_xml:
        return ProtocolRoute(protocol="xml", reason="force_xml enabled")

    if not has_tools:
        return ProtocolRoute(protocol="xml", reason="no tools available")

    if agent_name not in NATIVE_TOOL_AGENTS:
        return ProtocolRoute(
            protocol="xml",
            reason=f"agent {agent_name} not enabled for native tool calling",
        )

    if not model_supports_native_tools(model_name):
        return ProtocolRoute(
            protocol="xml",
            reason=f"model {model_name} does not support native tool calling",
        )

    return ProtocolRoute(protocol="native", reason="native tool calling enabled")
