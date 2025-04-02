from abc import ABC, abstractmethod
from typing import Optional

from pydantic import Field

from app.agent.base import BaseAgent
from app.llm import LLM
from app.schema import AgentState, Memory


class ReActAgent(BaseAgent, ABC):
    name: str
    description: Optional[str] = None

    system_prompt: Optional[str] = None
    next_step_prompt: Optional[str] = None

    llm: Optional[LLM] = Field(default_factory=LLM)
    memory: Memory = Field(default_factory=Memory)
    state: AgentState = AgentState.IDLE

    max_steps: int = 10
    current_step: int = 0

    @abstractmethod
    async def think(self) -> bool:
        """Process current state and decide next action"""

    @abstractmethod
    async def act(self) -> str:
        """Execute decided actions"""

    async def step(self) -> str:
        """Execute a single step: think and act."""
        should_act = await self.think()
        if not should_act:
            return "Thinking complete - no action needed"
        
        result = await self.act()

        if result and "Do you want me to terminate or stay ready for more?" in result:
            # Pause and ask the user for a decision
            print(result)  # show the result in terminal
            user_input = input("👉 Type 'terminate' to stop or 'continue' to keep going: ").strip().lower()
            if user_input == "terminate":
                self.state = AgentState.FINISHED
                return "🔚 Task terminated by user."
            else:
                self.state = AgentState.RUNNING
                return "🔄 Continuing task."

        return result

