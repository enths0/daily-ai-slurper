import logging
import time
from typing import Dict, List, Optional, Set, Tuple, Type
from enum import Enum, auto


class GameState(Enum):
    """
    Enum representing different game states.
    These are high-level states that represent where the user is in the game.
    """
    UNKNOWN = auto()
    HOME_SCREEN = auto()
    BATTLE = auto()
    SHOP = auto()
    INVENTORY = auto()
    MAIL = auto()
    LOADING = auto()
    LOGIN = auto()
    ERROR = auto()
    POPUP = auto()  # Added for popup handling


class StateTransition:
    """Represents a transition from one state to another."""
    
    def __init__(self, 
                from_state: GameState, 
                to_state: GameState, 
                action_sequence: List[str],
                expected_duration: float = 2.0):
        """
        Initialize a state transition.
        
        Args:
            from_state: The starting state
            to_state: The target state
            action_sequence: List of actions (e.g., button clicks) to perform
            expected_duration: Expected time in seconds for the transition to complete
        """
        self.from_state = from_state
        self.to_state = to_state
        self.action_sequence = action_sequence
        self.expected_duration = expected_duration
    
    def __repr__(self) -> str:
        return f"StateTransition({self.from_state} -> {self.to_state})"


class StateManager:
    """
    Manages the game state and transitions between states.
    """
    
    def __init__(self):
        """Initialize the state manager."""
        self.current_state: GameState = GameState.UNKNOWN
        self.previous_state: Optional[GameState] = None
        self.state_history: List[Tuple[GameState, float]] = []
        self.transitions: Dict[Tuple[GameState, GameState], StateTransition] = {}
        self.stable_state_time: float = 0.0
        self.logger = logging.getLogger(__name__)
        
        # Register some common transitions
        self._register_default_transitions()
    
    def _register_default_transitions(self) -> None:
        """Register default state transitions."""
        # Home to Shop transition
        self.register_transition(
            from_state=GameState.HOME_SCREEN,
            to_state=GameState.SHOP,
            action_sequence=["click_template:home/shop_icon"],
            expected_duration=2.0
        )
        
        # Shop to Home transition
        self.register_transition(
            from_state=GameState.SHOP,
            to_state=GameState.HOME_SCREEN,
            action_sequence=["click_template:common/return_home"],
            expected_duration=1.5
        )
        
        # Handle popups from any state
        self.register_transition(
            from_state=GameState.POPUP,
            to_state=GameState.UNKNOWN,  # We don't know what state we'll be in after closing popup
            action_sequence=[
                "click_template:common/close_button", 
                "click_template:common/confirm_button",
                "click_template:common/empty_area"
            ],
            expected_duration=1.0
        )
        
        # Handle error state
        self.register_transition(
            from_state=GameState.ERROR,
            to_state=GameState.HOME_SCREEN,
            action_sequence=["click_template:common/confirm_button", "wait:2.0"],
            expected_duration=3.0
        )
        
        # Recovery from UNKNOWN state - try to get back to home
        self.register_transition(
            from_state=GameState.UNKNOWN,
            to_state=GameState.HOME_SCREEN,
            action_sequence=[
                "click_template:common/return_home",
                "wait:1.0",
                "click_template:common/close_button",
                "wait:0.5",
                "click_template:common/confirm_button",
                "wait:0.5"
            ],
            expected_duration=3.0
        )
    
    def register_transition(self, 
                           from_state: GameState, 
                           to_state: GameState, 
                           action_sequence: List[str],
                           expected_duration: float = 2.0) -> None:
        """
        Register a state transition.
        
        Args:
            from_state: The starting state
            to_state: The target state
            action_sequence: List of actions (e.g., button clicks) to perform
            expected_duration: Expected time in seconds for the transition to complete
        """
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            action_sequence=action_sequence,
            expected_duration=expected_duration
        )
        
        self.transitions[(from_state, to_state)] = transition
        self.logger.info(f"Registered transition: {from_state} -> {to_state}")
    
    def update_state(self, new_state: GameState) -> bool:
        """
        Update the current state.
        
        Args:
            new_state: The new game state
            
        Returns:
            bool: True if the state changed, False otherwise
        """
        if new_state == self.current_state:
            return False
        
        current_time = time.time()
        
        # Record previous state
        self.previous_state = self.current_state
        
        # Update state
        self.current_state = new_state
        self.state_history.append((new_state, current_time))
        self.stable_state_time = current_time
        
        self.logger.info(f"State changed: {self.previous_state} -> {self.current_state}")
        return True
    
    def get_current_state(self) -> GameState:
        """
        Get the current game state.
        
        Returns:
            GameState: The current game state
        """
        return self.current_state
    
    def get_state_duration(self) -> float:
        """
        Get the duration in seconds that the current state has been active.
        
        Returns:
            float: Duration in seconds
        """
        return time.time() - self.stable_state_time
    
    def find_path(self, target_state: GameState) -> Optional[List[StateTransition]]:
        """
        Find a path from the current state to the target state.
        Uses a simple breadth-first search for pathfinding.
        
        Args:
            target_state: The target game state
            
        Returns:
            Optional[List[StateTransition]]: List of transitions to reach the target state,
                                            or None if no path is found
        """
        if self.current_state == target_state:
            return []
        
        # BFS to find the shortest path
        queue = [(self.current_state, [])]
        visited = {self.current_state}
        
        while queue:
            state, path = queue.pop(0)
            
            # Check all possible transitions from this state
            for (from_s, to_s), transition in self.transitions.items():
                if from_s == state and to_s not in visited:
                    new_path = path + [transition]
                    
                    if to_s == target_state:
                        return new_path
                    
                    visited.add(to_s)
                    queue.append((to_s, new_path))
        
        self.logger.warning(f"No path found from {self.current_state} to {target_state}")
        return None
    
    def can_transition_to(self, target_state: GameState) -> bool:
        """
        Check if a transition to the target state is possible from the current state.
        
        Args:
            target_state: The target game state
            
        Returns:
            bool: True if transition is possible, False otherwise
        """
        return self.find_path(target_state) is not None
    
    def get_reachable_states(self) -> Set[GameState]:
        """
        Get all states that can be reached from the current state.
        
        Returns:
            Set[GameState]: Set of reachable game states
        """
        reachable = {self.current_state}
        
        # Find all states that have a direct transition from the current state
        for (from_s, to_s) in self.transitions.keys():
            if from_s == self.current_state:
                reachable.add(to_s)
        
        return reachable
