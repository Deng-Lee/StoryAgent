# Python standard library imports
from datetime import datetime
from typing import Dict, List
import asyncio
from functools import partial
import os
import time

# Third-party imports
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

# Local imports
from utils.llm.engines import get_engine, invoke_engine, invoke_engine_response
from utils.llm.router import select_tool_call_protocol
from utils.llm.types import AgentResponse, ToolCall, ToolSpec
from utils.llm.xml_formatter import format_tool_as_xml_v2, parse_xml_agent_response
from utils.logger.session_logger import SessionLogger

# Load environment variables
load_dotenv(override=True)


class BaseAgent:
    """Base class for all agents. All agents inherits from this class."""

    # Class variable shared by all instances
    use_baseline: bool = False
    
    class Event(BaseModel):
        """Event class for all events. All events inherits from this class."""
        sender: str
        tag: str
        content: str
        timestamp: datetime
    
    def __init__(self, name: str, description: str, config: Dict):
        self.name = name
        self.description = description
        self.config = config
        
        # Initialize the LLM engine
        self.engine = get_engine(model_name= \
                                 config.get("model_name", 
                                            os.getenv("MODEL_NAME", "gpt-4o")))
        self.tools = {}

        # Each agent has an event stream. 
        # Contains all the events that have been sent by the agent.
        self.event_stream: list[BaseAgent.Event] = []
        
        # Setup environment variables
        self._max_consideration_iterations = \
            int(os.getenv("MAX_CONSIDERATION_ITERATIONS", "3"))
        self._max_events_len = int(os.getenv("MAX_EVENTS_LEN", 30))

    def workout(self):
        pass

    def _call_engine(self, prompt: str):
        '''Calls the LLM engine with the given prompt.'''
        for attempt in range(10):
            try:
                output = invoke_engine(self.engine, prompt)
                return output
            except Exception as e:
                # Calculate exponential backoff sleep time (1s, 2s, 4s, 8s, etc.)
                sleep_time = 2 ** attempt
                SessionLogger.log_to_file(
                    "execution_log", 
                    f"({self.name}) Failed to invoke the chain "
                    f"{attempt + 1} times.\n{type(e)} <{e}>\n"
                    f"Sleeping for {sleep_time} seconds before retrying...", 
                    log_level="error"
                )
                time.sleep(sleep_time)
                
        raise e
    
    async def call_engine_async(self, prompt: str) -> str:
        '''Asynchronously call the LLM engine with the given prompt.'''
        # Run call_engine in a thread pool since it's a blocking operation
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            partial(self._call_engine, prompt)
        )

    def get_tool_specs(self, selected_tools: List[str] = None) -> List[ToolSpec]:
        """Return structured tool specs for native Function Calling."""
        tool_specs = []
        for tool in self.tools.values():
            if selected_tools and tool.name not in selected_tools:
                continue

            args_schema = getattr(tool, "args_schema", None)
            json_schema = (
                args_schema.model_json_schema() if args_schema and issubclass(args_schema, BaseModel)
                else {"type": "object", "properties": {}}
            )
            required_fields = list(json_schema.get("required", []))
            tool_specs.append(
                ToolSpec(
                    name=tool.name,
                    description=tool.description,
                    json_schema=json_schema,
                    required_fields=required_fields,
                )
            )
        return tool_specs

    def _call_engine_response(
        self,
        prompt: str,
        selected_tools: List[str] = None,
        protocol: str = "auto",
        force_xml: bool = False,
    ) -> AgentResponse:
        tool_specs = self.get_tool_specs(selected_tools)
        if protocol == "auto":
            route = select_tool_call_protocol(
                model_name=self.config.get("model_name", os.getenv("MODEL_NAME", "gpt-4o")),
                agent_name=self.name,
                has_tools=bool(tool_specs),
                force_xml=force_xml,
            )
            protocol = route.protocol

        return invoke_engine_response(
            self.engine,
            prompt,
            tools=tool_specs,
            protocol=protocol,
        )

    async def call_engine_response_async(
        self,
        prompt: str,
        selected_tools: List[str] = None,
        protocol: str = "auto",
        force_xml: bool = False,
    ) -> AgentResponse:
        """Asynchronously call the LLM engine and return a structured response."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            partial(
                self._call_engine_response,
                prompt,
                selected_tools,
                protocol,
                force_xml,
            ),
        )
        
    def add_event(self, sender: str, tag: str, content: str):
        '''Adds an event to the event stream. 
        Args:
            sender: The sender of the event (interviewer, user, system)
            tag: The tag of the event 
                (interviewer_response, user_response, system_response, etc.)
            content: The content of the event.
        '''
        # Convert None content to empty string to satisfy Pydantic validation
        content = "" if content is None else str(content)
        
        self.event_stream.append(BaseAgent.Event(sender=sender, 
                                                 tag=tag,
                                                 content=content, 
                                                 timestamp=datetime.now()))
        # Log the event to the interviewer event stream file
        SessionLogger.log_to_file(f"{self.name}_event_stream", 
                                  f"({self.name}) Sender: {sender}, "
                                  f"Tag: {tag}\nContent: {content}")
        
    def get_event_stream_str(self, filter: List[Dict[str, str]] = None, as_list: bool = False):
        '''Gets the event stream that passes the filter. 
        Important for ensuring that the event stream only 
        contains events that are relevant to the agent.
        
        Args:
            filter: A list of dictionaries with sender and tag keys 
            to filter the events.
            as_list: Whether to return the events as a list of strings.
        '''
        events = []
        for event in self.event_stream:
            if self._passes_filter(event, filter):
                event_str = f"<{event.sender}>\n{event.content}\n</{event.sender}>"
                events.append(event_str)
        
        if as_list:
            return events
        return "\n".join(events)
    
    def _passes_filter(self, event: Event, filter: List[Dict[str, str]]):
        '''Helper function to check if an event passes the filter.
        
        Args:
            event: The event to check.
            filter: A list of dictionaries with sender 
            and tag keys to filter the events.
        '''
        if filter:
            for filter_item in filter:
                if not filter_item.get("sender", None) \
                      or event.sender == filter_item["sender"]:
                    if not filter_item.get("tag", None) \
                          or event.tag == filter_item["tag"]:
                        return True
            return False
        return True
    
    def get_tools_description(self, selected_tools: List[str] = None):
        '''Gets the tools description as a string.
        
        Args:
            selected_tools: A list of tool names to include a description for.
        '''
        if selected_tools:
            return "\n".join([format_tool_as_xml_v2(tool) \
                               for tool in self.tools.values() \
                               if tool.name in selected_tools])
        else:
            return "\n".join([format_tool_as_xml_v2(tool) \
                               for tool in self.tools.values()])

    def validate_tool_call(self, tool_call: ToolCall) -> tuple[object, dict]:
        """Validate tool arguments against the tool's args_schema."""
        if tool_call.name not in self.tools:
            raise ValueError(f"Tool {tool_call.name} not found")

        tool = self.tools[tool_call.name]
        args_schema = getattr(tool, "args_schema", None)

        if args_schema and issubclass(args_schema, BaseModel):
            try:
                validated = args_schema.model_validate(tool_call.arguments or {})
            except ValidationError as exc:
                raise ValueError(
                    f"Invalid arguments for tool {tool_call.name}: {exc}"
                ) from exc
            return tool, validated.model_dump()

        return tool, dict(tool_call.arguments or {})

    def execute_tool_calls(self, response: AgentResponse, raise_error: bool = False):
        """Structured synchronous tool handling for non-I/O bound operations."""
        result = None
        for tool_call in response.tool_calls:
            try:
                tool, arguments = self.validate_tool_call(tool_call)

                if asyncio.iscoroutinefunction(tool._run):
                    raise ValueError(
                        f"Tool {tool_call.name} is async and should use execute_tool_calls_async"
                    )

                result = tool._run(**arguments)
                self.add_event(sender="system", tag=tool_call.name, content=result)
            except Exception as e:
                error_msg = f"Error calling tool {tool_call.name}: {e}"
                self.add_event(sender="system", tag="error", content=error_msg)
                SessionLogger.log_to_file(
                    "execution_log",
                    f"({self.name}) {error_msg}",
                    log_level="error",
                )
                if raise_error:
                    raise RuntimeError(error_msg) from e
        return result

    async def execute_tool_calls_async(
        self,
        response: AgentResponse,
        raise_error: bool = False,
    ):
        """Structured async tool handling for AgentResponse objects."""
        result = None
        for tool_call in response.tool_calls:
            try:
                tool, arguments = self.validate_tool_call(tool_call)

                if asyncio.iscoroutinefunction(tool._run):
                    result = await tool._run(**arguments)
                else:
                    result = tool._run(**arguments)

                self.add_event(sender="system", tag=tool_call.name, content=result)
            except Exception as e:
                error_msg = f"Error calling tool {tool_call.name}: {e}"
                self.add_event(sender="system", tag="error", content=error_msg)
                SessionLogger.log_to_file(
                    "execution_log",
                    f"({self.name}) {error_msg}",
                    log_level="error",
                )
                if raise_error:
                    raise RuntimeError(error_msg) from e
        return result
    
    def handle_tool_calls(self, response: str, raise_error: bool = False):
        """Synchronous tool handling for non-I/O bound operations"""
        return self.execute_tool_calls(
            parse_xml_agent_response(response),
            raise_error=raise_error,
        )

    async def handle_tool_calls_async(self, response: str, raise_error: bool = False):
        """Asynchronous tool handling for I/O bound operations"""
        return await self.execute_tool_calls_async(
            parse_xml_agent_response(response),
            raise_error=raise_error,
        )
