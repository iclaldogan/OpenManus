import json
from typing import Any, List, Literal, Optional, Union

from pydantic import Field

from app.agent.react import ReActAgent
from app.logger import logger
from app.prompt.toolcall import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.schema import AgentState, Message, ToolCall
from app.tool import CreateChatCompletion, Terminate, ToolCollection

from app.agent.task_lifecycle import TaskLifecycleManager

TOOL_CALL_REQUIRED = "Tool calls required but none provided"


class ToolCallAgent(ReActAgent):
    """Base agent class for handling tool/function calls with enhanced abstraction"""

    name: str = "toolcall"
    description: str = "an agent that can execute tool calls."

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    lifecycle: TaskLifecycleManager = TaskLifecycleManager()
    
    available_tools: ToolCollection = ToolCollection(
        CreateChatCompletion(), Terminate()
    )
    tool_choices: Literal["none", "auto", "required"] = "auto"
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    tool_calls: List[ToolCall] = Field(default_factory=list)



    max_steps: int = 30
    max_observe: Optional[Union[int, bool]] = None

    async def think(self) -> bool:
        """Process current state and decide next actions using tools"""
        if self.next_step_prompt:
            user_msg = Message.user_message(self.next_step_prompt)
            self.messages += [user_msg]

        # Prevent infinite retries with no message
        if self.messages and self.messages[-1].role == "assistant" and not self.messages[-1].content:
            logger.warning("⚠️ Empty assistant message detected. Halting to avoid loop.")
            return False

        # Get response with tool options
        response = await self.llm.ask_tool(
            messages=self.messages,
            system_msgs=[Message.system_message(self.system_prompt)]
            if self.system_prompt
            else None,
            tools=self.available_tools.to_params(),
            tool_choice=self.tool_choices,
        )
        self.tool_calls = response.tool_calls

        # Log response info
        logger.info(f"✨ {self.name}'s thoughts: {response.content}")
        logger.info(
            f"🛠️ {self.name} selected {len(response.tool_calls) if response.tool_calls else 0} tools to use"
        )
        if response.tool_calls:
            logger.info(
                f"🧰 Tools being prepared: {[call.function.name for call in response.tool_calls]}"
            )

        try:
            # Handle different tool_choices modes
            if self.tool_choices == "none":
                if response.tool_calls:
                    logger.warning(
                        f"🤔 Hmm, {self.name} tried to use tools when they weren't available!"
                    )
                if response.content:
                    self.memory.add_message(Message.assistant_message(response.content))
                    return True
                return False
           
             # Skip if both content and tool_calls are missing (to avoid validation error)
            if not response.content and not self.tool_calls:
                logger.warning("⚠️ Skipping message: no content or tool calls.")
                return False

            # Create and add assistant message
            assistant_msg = (
                Message.from_tool_calls(
                    content=response.content, tool_calls=self.tool_calls
                )
                if self.tool_calls
                else Message.assistant_message(response.content)
            )
            self.memory.add_message(assistant_msg)


            if self.tool_choices == "required" and not self.tool_calls:
                return True  # Will be handled in act()

            # For 'auto' mode, continue with content if no commands but content exists
            if self.tool_choices == "auto" and not self.tool_calls:
                return bool(response.content)

            return bool(self.tool_calls)
        except Exception as e:
            logger.error(f"🚨 Oops! The {self.name}'s thinking process hit a snag: {e}")
            self.memory.add_message(
                Message.assistant_message(
                    f"Error encountered while processing: {str(e)}"
                )
            )
            return False

    async def act(self) -> str:
        """Execute tool calls and handle their results"""
        if not self.tool_calls:
            if self.tool_choices == "required":
                raise ValueError(TOOL_CALL_REQUIRED)

            return self.messages[-1].content or "No content or commands to execute"

        if not self.lifecycle.is_task_running():
            self.lifecycle.begin_task()

        results = []
        for command in self.tool_calls:
            result = await self.execute_tool(command)
            logger.info(
                f"🎯 Tool '{command.function.name}' completed its mission! Result: {result}"
            )

            if self.max_observe and isinstance(result, str):
                result = result[: self.max_observe]


            safe_result = result if isinstance(result, str) else str(result) if result else "No result"
            tool_msg = Message.tool_message(
            content=safe_result, tool_call_id=command.id, name=command.function.name
            )

            self.memory.add_message(tool_msg)
            results.append(result)

        # 🧠 After all tools have run, prepare to finish
        from app.agent.task_lifecycle import TaskLifecycleManager
        
        # ✅ Check for user confirmation commands
        if self.lifecycle.is_awaiting_user_input():
            if response.content:
                decision = response.content.strip().lower()
                if "terminate" in decision:
                    self.state = AgentState.FINISHED
                    self.lifecycle.clear_awaiting_user_input()
                    return False
                elif "continue" in decision:
                    self.lifecycle.clear_awaiting_user_input()
                    return False  # Think again next step (continue loop)
                else:
                    # Stay paused until valid input
                    logger.info(f"Awaiting user confirmation. Received: {decision}")
                    return False
            return (
                result_summary +
                "\n\n🧠 I've completed this task. Do you want me to terminate or stay ready for more?\n👉 Type 'terminate' to stop or 'continue' to keep going:"
            )



    async def execute_tool(self, command: ToolCall) -> str:
        """Execute a single tool call with robust error handling"""
        if not command or not command.function or not command.function.name:
            return "Error: Invalid command format"

        name = command.function.name
        if name not in self.available_tools.tool_map:
            return f"Error: Unknown tool '{name}'"

        try:
            # Parse arguments
            args = json.loads(command.function.arguments or "{}")

            # Execute the tool
            logger.info(f"🔧 Activating tool: '{name}'...")
            result = await self.available_tools.execute(name=name, tool_input=args)

            # Format result for display
            if result and getattr(result, "output", None) is not None:
                obs = result.output
                if isinstance(obs, list):
                    obs = "\n".join(str(x) for x in obs)
                else:
                    obs = str(obs)
                observation = f"Observed output of cmd `{name}` executed:\n{obs}"
            else:
                observation = f"Cmd `{name}` completed with no output"


            # Handle special tools like `finish`
            await self._handle_special_tool(name=name, result=result)

            return str(observation) if observation is not None else "No observation returned"

        except json.JSONDecodeError:
            error_msg = f"Error parsing arguments for {name}: Invalid JSON format"
            logger.error(
                f"📝 Oops! The arguments for '{name}' don't make sense - invalid JSON, arguments:{command.function.arguments}"
            )
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"⚠️ Tool '{name}' encountered a problem: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

    async def _handle_special_tool(self, name: str, result: Any, **kwargs):
        """Handle special tool execution and state changes"""
        if not self._is_special_tool(name):
            return

        if self._should_finish_execution(name=name, result=result, **kwargs):
            # Set agent state to finished
            logger.info(f"🏁 Special tool '{name}' has completed the task!")
            self.state = AgentState.FINISHED

    @staticmethod
    def _should_finish_execution(self, name: str, result: Any, **kwargs) -> bool:
        return name == "terminate" and self.lifecycle.ready_to_terminate()


    def _is_special_tool(self, name: str) -> bool:
        """Check if tool name is in special tools list"""
        return name.lower() in [n.lower() for n in self.special_tool_names]
