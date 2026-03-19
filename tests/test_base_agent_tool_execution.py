import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.base_agent import BaseAgent
from utils.llm.types import AgentResponse, ToolCall
from utils.llm.xml_formatter import parse_xml_agent_response


class EchoInput(BaseModel):
    text: str = Field(description="Text to echo")


class EchoTool(BaseTool):
    name: str = "echo"
    description: str = "Echo the input text."
    args_schema: type[BaseModel] = EchoInput

    def _run(self, text: str):
        return f"echo:{text}"


class AsyncEchoTool(BaseTool):
    name: str = "async_echo"
    description: str = "Echo asynchronously."
    args_schema: type[BaseModel] = EchoInput

    async def _run(self, text: str):
        return f"async:{text}"


class BaseAgentToolExecutionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.engine_patcher = patch("agents.base_agent.get_engine", return_value=object())
        self.logger_patcher = patch("agents.base_agent.SessionLogger.log_to_file", return_value=None)
        self.engine_patcher.start()
        self.logger_patcher.start()
        self.agent = BaseAgent(name="Interviewer", description="test", config={"model_name": "gpt-4o"})
        self.agent.tools = {
            "echo": EchoTool(),
            "async_echo": AsyncEchoTool(),
        }

    def tearDown(self) -> None:
        self.engine_patcher.stop()
        self.logger_patcher.stop()

    def test_get_tool_specs_uses_args_schema(self) -> None:
        tool_specs = self.agent.get_tool_specs(["echo"])
        self.assertEqual(len(tool_specs), 1)
        self.assertEqual(tool_specs[0].name, "echo")
        self.assertIn("text", tool_specs[0].json_schema["properties"])
        self.assertIn("text", tool_specs[0].required_fields)

    def test_validate_tool_call_raises_for_invalid_arguments(self) -> None:
        with self.assertRaises(ValueError):
            self.agent.validate_tool_call(
                ToolCall(
                    id="1",
                    name="echo",
                    arguments={},
                    source="native",
                )
            )

    def test_execute_tool_calls_runs_sync_tool(self) -> None:
        response = AgentResponse(
            text="",
            protocol="native",
            tool_calls=[
                ToolCall(id="1", name="echo", arguments={"text": "hello"}, source="native")
            ],
        )
        result = self.agent.execute_tool_calls(response)
        self.assertEqual(result, "echo:hello")
        self.assertEqual(self.agent.event_stream[-1].tag, "echo")

    async def test_execute_tool_calls_async_runs_async_tool(self) -> None:
        response = AgentResponse(
            text="",
            protocol="native",
            tool_calls=[
                ToolCall(id="1", name="async_echo", arguments={"text": "hello"}, source="native")
            ],
        )
        result = await self.agent.execute_tool_calls_async(response)
        self.assertEqual(result, "async:hello")
        self.assertEqual(self.agent.event_stream[-1].tag, "async_echo")

    def test_handle_tool_calls_uses_xml_compat_adapter(self) -> None:
        xml_response = """
<thinking>test</thinking>
<tool_calls>
    <echo>
        <text>hello</text>
    </echo>
</tool_calls>
"""
        result = self.agent.handle_tool_calls(xml_response)
        self.assertEqual(result, "echo:hello")

    def test_parse_xml_agent_response_extracts_tool_calls(self) -> None:
        xml_response = """
<tool_calls>
    <echo>
        <text>hello</text>
    </echo>
</tool_calls>
"""
        response = parse_xml_agent_response(xml_response)
        self.assertEqual(response.protocol, "xml")
        self.assertEqual(len(response.tool_calls), 1)
        self.assertEqual(response.tool_calls[0].name, "echo")
        self.assertEqual(response.tool_calls[0].arguments["text"], "hello")
