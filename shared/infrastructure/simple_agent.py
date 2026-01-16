"""SimpleAgent implementation with Observe-Think-Act-Reflect loop.

This module provides a basic agent implementation that follows the
Observe-Think-Act-Reflect (OTAR) loop pattern. This is a foundational
pattern for building AI agents from scratch.

The agent progresses through four states in order:
1. OBSERVE: Gather information from the environment
2. THINK: Analyze observations and plan actions
3. ACT: Execute the planned action
4. REFLECT: Evaluate the action's outcome

Example:
    >>> from src.agents import SimpleAgent
    >>> from src.services.llm import MockLLM
    >>> 
    >>> llm = MockLLM()
    >>> agent = SimpleAgent(llm=llm)
    >>> result = await agent.run("Estimate time for a CRUD API feature")
    >>> print(result)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, TypeVar

from src.services.llm import LLMProvider


# Configure logging for agent state transitions
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """States in the Observe-Think-Act-Reflect loop.
    
    The agent progresses through these states in order:
    IDLE -> OBSERVE -> THINK -> ACT -> REFLECT -> (back to OBSERVE or COMPLETE)
    
    Attributes:
        IDLE: Initial state before the agent starts
        OBSERVE: Gathering information from the environment
        THINK: Analyzing observations and planning
        ACT: Executing the planned action
        REFLECT: Evaluating the action's outcome
        COMPLETE: Final state when the task is done
        ERROR: Error state when something goes wrong
    """
    IDLE = auto()
    OBSERVE = auto()
    THINK = auto()
    ACT = auto()
    REFLECT = auto()
    COMPLETE = auto()
    ERROR = auto()


@dataclass
class AgentTransition:
    """Record of a state transition in the agent loop.
    
    Attributes:
        from_state: The state before the transition
        to_state: The state after the transition
        timestamp: When the transition occurred
        data: Optional data associated with the transition
        message: Optional message describing the transition
    """
    from_state: AgentState
    to_state: AgentState
    timestamp: datetime = field(default_factory=datetime.now)
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    
    def __str__(self) -> str:
        """Return a string representation of the transition."""
        msg = f"{self.from_state.name} -> {self.to_state.name}"
        if self.message:
            msg += f": {self.message}"
        return msg


@dataclass
class AgentContext:
    """Context maintained throughout the agent's execution.
    
    This holds all the information the agent accumulates during
    its Observe-Think-Act-Reflect loop.
    
    Attributes:
        task: The original task/query given to the agent
        observations: Information gathered during OBSERVE phase
        thoughts: Analysis and plans from THINK phase
        actions: Actions taken during ACT phase
        reflections: Evaluations from REFLECT phase
        iteration: Current iteration of the loop
        max_iterations: Maximum iterations before stopping
        metadata: Additional context data
    """
    task: str
    observations: List[str] = field(default_factory=list)
    thoughts: List[str] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    reflections: List[str] = field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_observation(self, observation: str) -> None:
        """Add an observation to the context."""
        self.observations.append(observation)
    
    def add_thought(self, thought: str) -> None:
        """Add a thought to the context."""
        self.thoughts.append(thought)
    
    def add_action(self, action: Dict[str, Any]) -> None:
        """Add an action to the context."""
        self.actions.append(action)
    
    def add_reflection(self, reflection: str) -> None:
        """Add a reflection to the context."""
        self.reflections.append(reflection)
    
    def increment_iteration(self) -> None:
        """Increment the iteration counter."""
        self.iteration += 1
    
    def should_continue(self) -> bool:
        """Check if the agent should continue iterating."""
        return self.iteration < self.max_iterations


class SimpleAgent:
    """A basic agent implementing the Observe-Think-Act-Reflect loop.
    
    This agent follows a state machine pattern where it progresses
    through four phases in each iteration:
    
    1. OBSERVE: Gather information about the current state
    2. THINK: Analyze observations and decide on an action
    3. ACT: Execute the chosen action
    4. REFLECT: Evaluate the outcome and decide whether to continue
    
    The agent logs all state transitions for debugging and analysis.
    
    Attributes:
        llm: The LLM provider for generating responses
        state: Current state of the agent
        transitions: History of state transitions
        context: Current execution context
        
    Example:
        >>> agent = SimpleAgent(llm=MockLLM())
        >>> result = await agent.run("What features are in the library?")
        >>> print(agent.transitions)  # See all state transitions
    """
    
    # Valid state transitions
    VALID_TRANSITIONS: Dict[AgentState, List[AgentState]] = {
        AgentState.IDLE: [AgentState.OBSERVE, AgentState.ERROR],
        AgentState.OBSERVE: [AgentState.THINK, AgentState.ERROR],
        AgentState.THINK: [AgentState.ACT, AgentState.ERROR],
        AgentState.ACT: [AgentState.REFLECT, AgentState.ERROR],
        AgentState.REFLECT: [AgentState.OBSERVE, AgentState.COMPLETE, AgentState.ERROR],
        AgentState.COMPLETE: [],  # Terminal state
        AgentState.ERROR: [],  # Terminal state
    }
    
    def __init__(
        self,
        llm: LLMProvider,
        max_iterations: int = 5,
        on_transition: Optional[Callable[[AgentTransition], None]] = None,
    ) -> None:
        """Initialize the SimpleAgent.
        
        Args:
            llm: The LLM provider for generating responses
            max_iterations: Maximum iterations of the OTAR loop
            on_transition: Optional callback for state transitions
        """
        self.llm = llm
        self.max_iterations = max_iterations
        self.on_transition = on_transition
        
        self._state = AgentState.IDLE
        self._transitions: List[AgentTransition] = []
        self._context: Optional[AgentContext] = None
    
    @property
    def state(self) -> AgentState:
        """Get the current state of the agent."""
        return self._state
    
    @property
    def transitions(self) -> List[AgentTransition]:
        """Get the history of state transitions."""
        return self._transitions.copy()
    
    @property
    def context(self) -> Optional[AgentContext]:
        """Get the current execution context."""
        return self._context
    
    def _transition_to(
        self,
        new_state: AgentState,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> None:
        """Transition to a new state.
        
        Args:
            new_state: The state to transition to
            data: Optional data associated with the transition
            message: Optional message describing the transition
            
        Raises:
            ValueError: If the transition is not valid
        """
        # Validate the transition
        valid_next_states = self.VALID_TRANSITIONS.get(self._state, [])
        if new_state not in valid_next_states:
            raise ValueError(
                f"Invalid transition: {self._state.name} -> {new_state.name}. "
                f"Valid transitions from {self._state.name}: {[s.name for s in valid_next_states]}"
            )
        
        # Create transition record
        transition = AgentTransition(
            from_state=self._state,
            to_state=new_state,
            data=data,
            message=message,
        )
        
        # Log the transition
        logger.info(f"Agent transition: {transition}")
        
        # Update state and record transition
        self._state = new_state
        self._transitions.append(transition)
        
        # Call the callback if provided
        if self.on_transition:
            self.on_transition(transition)
    
    async def _observe(self) -> str:
        """OBSERVE phase: Gather information about the current state.
        
        This phase collects information from the environment and
        the current context to inform the thinking phase.
        
        Returns:
            The observation as a string
        """
        self._transition_to(
            AgentState.OBSERVE,
            message="Gathering information from environment"
        )
        
        if self._context is None:
            raise RuntimeError("Agent context not initialized")
        
        # Build observation prompt
        prompt = f"""You are an AI agent in the OBSERVE phase.
Your task is: {self._context.task}

Current iteration: {self._context.iteration + 1}/{self._context.max_iterations}

Previous observations: {self._context.observations if self._context.observations else 'None'}
Previous actions: {self._context.actions if self._context.actions else 'None'}
Previous reflections: {self._context.reflections if self._context.reflections else 'None'}

Observe the current state and gather relevant information.
What do you observe about this task?"""
        
        observation = await self.llm.complete(prompt)
        self._context.add_observation(observation)
        
        return observation
    
    async def _think(self) -> str:
        """THINK phase: Analyze observations and plan actions.
        
        This phase analyzes the gathered observations and decides
        what action to take next.
        
        Returns:
            The thought/plan as a string
        """
        self._transition_to(
            AgentState.THINK,
            message="Analyzing observations and planning"
        )
        
        if self._context is None:
            raise RuntimeError("Agent context not initialized")
        
        # Build thinking prompt
        latest_observation = self._context.observations[-1] if self._context.observations else "No observations"
        
        prompt = f"""You are an AI agent in the THINK phase.
Your task is: {self._context.task}

Latest observation: {latest_observation}

Based on your observations, analyze the situation and decide what action to take.
What is your analysis and what action do you plan to take?"""
        
        thought = await self.llm.complete(prompt)
        self._context.add_thought(thought)
        
        return thought
    
    async def _act(self) -> Dict[str, Any]:
        """ACT phase: Execute the planned action.
        
        This phase executes the action decided in the thinking phase.
        
        Returns:
            The action result as a dictionary
        """
        self._transition_to(
            AgentState.ACT,
            message="Executing planned action"
        )
        
        if self._context is None:
            raise RuntimeError("Agent context not initialized")
        
        # Build action prompt
        latest_thought = self._context.thoughts[-1] if self._context.thoughts else "No thoughts"
        
        prompt = f"""You are an AI agent in the ACT phase.
Your task is: {self._context.task}

Your plan: {latest_thought}

Execute the planned action and provide the result.
What is the result of your action?"""
        
        action_result = await self.llm.complete(prompt)
        
        action = {
            "iteration": self._context.iteration,
            "plan": latest_thought,
            "result": action_result,
            "timestamp": datetime.now().isoformat(),
        }
        self._context.add_action(action)
        
        return action
    
    async def _reflect(self) -> tuple[str, bool]:
        """REFLECT phase: Evaluate the action's outcome.
        
        This phase evaluates whether the action was successful
        and decides whether to continue or complete.
        
        Returns:
            Tuple of (reflection string, should_complete boolean)
        """
        self._transition_to(
            AgentState.REFLECT,
            message="Evaluating action outcome"
        )
        
        if self._context is None:
            raise RuntimeError("Agent context not initialized")
        
        # Build reflection prompt
        latest_action = self._context.actions[-1] if self._context.actions else {}
        
        prompt = f"""You are an AI agent in the REFLECT phase.
Your task is: {self._context.task}

Action taken: {latest_action.get('result', 'No action')}

Evaluate the outcome of your action.
1. Was the action successful?
2. Did it help accomplish the task?
3. Should we continue with more iterations or is the task complete?

Provide your reflection and end with either "CONTINUE" or "COMPLETE"."""
        
        reflection = await self.llm.complete(prompt)
        self._context.add_reflection(reflection)
        
        # Determine if we should complete
        should_complete = "COMPLETE" in reflection.upper() or not self._context.should_continue()
        
        return reflection, should_complete
    
    async def run(self, task: str) -> str:
        """Run the agent on a task.
        
        This executes the Observe-Think-Act-Reflect loop until
        the task is complete or max iterations is reached.
        
        Args:
            task: The task/query for the agent to work on
            
        Returns:
            The final result of the agent's work
        """
        # Initialize context
        self._context = AgentContext(
            task=task,
            max_iterations=self.max_iterations,
        )
        
        # Reset state
        self._state = AgentState.IDLE
        self._transitions = []
        
        logger.info(f"Starting agent with task: {task}")
        
        try:
            while True:
                # OBSERVE
                await self._observe()
                
                # THINK
                await self._think()
                
                # ACT
                await self._act()
                
                # REFLECT
                _, should_complete = await self._reflect()
                
                # Increment iteration
                self._context.increment_iteration()
                
                if should_complete:
                    self._transition_to(
                        AgentState.COMPLETE,
                        message="Task completed"
                    )
                    break
            
            # Return the final result
            if self._context.actions:
                return self._context.actions[-1].get("result", "No result")
            return "No actions taken"
            
        except Exception as e:
            logger.error(f"Agent error: {e}")
            self._transition_to(
                AgentState.ERROR,
                data={"error": str(e)},
                message=f"Error: {e}"
            )
            raise
    
    def get_state_history(self) -> List[AgentState]:
        """Get the sequence of states the agent has been in.
        
        Returns:
            List of states in order of occurrence
        """
        states = [AgentState.IDLE]
        for transition in self._transitions:
            states.append(transition.to_state)
        return states
    
    def reset(self) -> None:
        """Reset the agent to its initial state."""
        self._state = AgentState.IDLE
        self._transitions = []
        self._context = None
        logger.info("Agent reset to IDLE state")
