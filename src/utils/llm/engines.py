from __future__ import annotations

import json
from typing import Any, Iterable

from dotenv import load_dotenv

try:
    from langchain_together import ChatTogether
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ChatTogether = None

try:
    from langchain_openai import ChatOpenAI
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ChatOpenAI = None

from utils.llm.models.data import ModelResponse

try:
    from utils.llm.models.claude import ClaudeVertexEngine, claude_vertex_model_mapping
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ClaudeVertexEngine = None
    claude_vertex_model_mapping = {}

try:
    from utils.llm.models.gemini import GeminiVertexEngine, gemini_models
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    GeminiVertexEngine = None
    gemini_models = {}

try:
    from utils.llm.models.deepseek import DeepSeekEngine, deepseek_models
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    DeepSeekEngine = None
    deepseek_models = {}
from utils.llm.types import AgentResponse, ToolCall, ToolProtocol, ToolSpec

load_dotenv(override=True)


engine_constructor = {}
if ChatOpenAI is not None:
    engine_constructor.update({
        "gpt-4o-mini-2024-07-18": ChatOpenAI,
        "gpt-3.5-turbo-0125": ChatOpenAI,
        "gpt-4o": ChatOpenAI,
    })
if ChatTogether is not None:
    engine_constructor.update({
        "meta-llama/Llama-3.1-8B-Instruct": ChatTogether,
        "meta-llama/Llama-3.1-70B-Instruct": ChatTogether,
    })

def get_engine(model_name, **kwargs):
    """
    Creates and returns a language model engine based on the specified model name.

    Args:
        model_name (str): Name of the model to initialize. Supported models:
            - OpenAI models: gpt-4o-mini, gpt-3.5-turbo-0125, gpt-4o
            - Llama models: meta-llama/Llama-3.1-8B-Instruct, meta-llama/Llama-3.1-70B-Instruct
            - DeepSeek models: deepseek-ai/DeepSeek-V3 (671B parameter model)
            - Claude models: via Vertex AI
            - Gemini models: via Vertex AI
        **kwargs: Additional keyword arguments to pass to the model constructor.
            - temperature: Float between 0 and 1 (default: 0.0)
            - max_tokens/max_output_tokens: Maximum number of tokens in the response (default: 4096)
                Note: This will be mapped to the appropriate parameter name for each model:
                - OpenAI/Llama/DeepSeek: max_tokens
                - Gemini: max_output_tokens
                - Claude: max_tokens_to_sample

    Returns:
        LangChain chat model instance or custom engine configured with the specified parameters
    """
    # Set default temperature if not provided
    if "temperature" not in kwargs:
        kwargs["temperature"] = 0.0

    # Standardize max token handling
    max_tokens = kwargs.pop("max_tokens", None)
    max_output_tokens = kwargs.pop("max_output_tokens", None)
    max_tokens_to_sample = kwargs.pop("max_tokens_to_sample", None)
    
    # Use the first non-None value in order of precedence
    token_limit = max_output_tokens or max_tokens or max_tokens_to_sample or 4096
        
    if model_name == "gpt-4o-mini":
        model_name = "gpt-4o-mini-2024-07-18"
    
    # Handle Claude models via Vertex AI
    if model_name in claude_vertex_model_mapping or "claude" in model_name:
        if ClaudeVertexEngine is None:
            raise ValueError("Claude provider dependencies are not installed.")
        kwargs["max_tokens_to_sample"] = token_limit
        return ClaudeVertexEngine(model_name=model_name, **kwargs)
    
    # Handle Gemini models via Vertex AI
    if model_name in gemini_models or "gemini" in model_name:
        if GeminiVertexEngine is None:
            raise ValueError("Gemini provider dependencies are not installed.")
        kwargs["max_output_tokens"] = token_limit
        return GeminiVertexEngine(model_name=model_name, **kwargs)
        
    # Handle DeepSeek models
    if model_name in deepseek_models or "deepseek" in model_name.lower():
        if DeepSeekEngine is None:
            raise ValueError("DeepSeek provider dependencies are not installed.")
        kwargs["max_tokens"] = token_limit
        return DeepSeekEngine(model_name=model_name, **kwargs)
    
    # For other models (OpenAI, Llama), use max_tokens
    kwargs["max_tokens"] = token_limit
    kwargs["model_name"] = model_name
    if model_name not in engine_constructor:
        raise ValueError(
            f"Model {model_name} is not available. "
            "Required provider package may be missing."
        )
    return engine_constructor[model_name](**kwargs)

def invoke_engine(engine, prompt, **kwargs) -> ModelResponse:
    """
    Simple wrapper to invoke a language model engine and return its response.

    Args:
        engine: The language model engine to use
        prompt: The input prompt to send to the model
        **kwargs: Additional keyword arguments for the model invocation

    Returns:
        str: The model's response text
    """
    return engine.invoke(prompt, **kwargs).content


def _coerce_tool_arguments(arguments: Any) -> dict[str, Any]:
    if arguments is None:
        return {}

    if isinstance(arguments, dict):
        return arguments

    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
            return parsed if isinstance(parsed, dict) else {"value": parsed}
        except json.JSONDecodeError:
            return {"value": arguments}

    return {"value": arguments}


def _normalize_tool_call(raw_call: Any, protocol: ToolProtocol) -> ToolCall:
    if isinstance(raw_call, ToolCall):
        return raw_call

    if not isinstance(raw_call, dict):
        raise TypeError(f"Unsupported tool call payload: {type(raw_call)}")

    function_payload = raw_call.get("function", {})
    name = raw_call.get("name") or function_payload.get("name")
    if not name:
        raise ValueError("Tool call payload is missing tool name")

    arguments = (
        raw_call.get("arguments")
        or raw_call.get("args")
        or function_payload.get("arguments")
    )

    return ToolCall(
        id=raw_call.get("id"),
        name=name,
        arguments=_coerce_tool_arguments(arguments),
        source=protocol,
        raw_payload=raw_call,
    )


def normalize_engine_response(
    raw_response: Any,
    *,
    protocol: ToolProtocol = "xml",
) -> AgentResponse:
    if isinstance(raw_response, AgentResponse):
        return raw_response

    if isinstance(raw_response, str):
        return AgentResponse(
            text=raw_response,
            tool_calls=[],
            protocol=protocol,
            raw_content=raw_response,
        )

    content = getattr(raw_response, "content", "")
    response_metadata = getattr(raw_response, "response_metadata", {}) or {}

    raw_tool_calls = getattr(raw_response, "tool_calls", None)
    if raw_tool_calls is None and hasattr(raw_response, "additional_kwargs"):
        raw_tool_calls = raw_response.additional_kwargs.get("tool_calls", [])

    normalized_tool_calls = [
        _normalize_tool_call(call, protocol)
        for call in (raw_tool_calls or [])
    ]

    return AgentResponse(
        text=content or "",
        tool_calls=normalized_tool_calls,
        protocol=protocol,
        raw_content=raw_response,
        response_metadata=response_metadata,
    )


def _serialize_tool_specs(tools: Iterable[ToolSpec] | None) -> list[dict[str, Any]]:
    serialized_tools = []
    for tool in tools or []:
        serialized_tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.json_schema,
                },
            }
        )
    return serialized_tools


def invoke_engine_response(
    engine: Any,
    prompt: str,
    *,
    tools: Iterable[ToolSpec] | None = None,
    protocol: ToolProtocol = "xml",
    **kwargs,
) -> AgentResponse:
    invoke_kwargs = dict(kwargs)
    if protocol == "native" and tools:
        invoke_kwargs["tools"] = _serialize_tool_specs(tools)

    raw_response = engine.invoke(prompt, **invoke_kwargs)
    return normalize_engine_response(raw_response, protocol=protocol)
