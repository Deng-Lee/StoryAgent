from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


ToolCallSource = Literal["native", "xml"]
ToolProtocol = Literal["native", "xml"]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    json_schema: Dict[str, Any]
    required_fields: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ToolCall:
    id: Optional[str]
    name: str
    arguments: Dict[str, Any]
    source: ToolCallSource
    raw_payload: Any = None


@dataclass
class AgentResponse:
    text: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    protocol: ToolProtocol = "xml"
    raw_content: Any = None
    response_metadata: Dict[str, Any] = field(default_factory=dict)
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
