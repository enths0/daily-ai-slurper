import logging
import random
import time
from typing import Tuple, Optional, List, Dict, Union, Callable

import pyautogui
from src.core.vision.template import TemplateMatch


class InputController:
    """
    Input controller for simulating human-like mouse/touch inputs.
    """
    
    def __init__(self, 
                min_delay: float = 0.05, 
                max_delay: float = 0.2,
                move_duration_range: Tuple[float, float] = (0.1, 0.3)):
        """
        Initialize the input controller.
        
        Args:
            min_delay: Minimum delay between actions in seconds
            max_delay: Maximum delay between actions in seconds
            move_duration_range: Range of durations for mouse movements (min, max) in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.move_duration_range = move_duration_range
        self.logger = logging.getLogger(__name__)
        self.last_action_time = 0.0
        
        # Configure pyautogui for safety
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1  # Default pause between pyautogui commands
    
    def _random_delay(self) -> None:
        """Add a random delay between actions to simulate human behavior."""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def _get_move_duration(self) -> float:
        """Get a random duration for mouse movement."""
        return random.uniform(self.move_duration_range[0], self.move_duration_range[1])
    
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """
        Move the mouse to the specified coordinates with human-like motion.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of the movement in seconds. If None, uses a random duration.
        """
        if duration is None:
            duration = self._get_move_duration()
        
        self._random_delay()
        pyautogui.moveTo(x, y, duration=duration)
        self.last_action_time = time.time()
        self.logger.debug(f"Moved mouse to ({x}, {y}) in {duration:.2f}s")
    
    def click(self, x: int, y: int, 
             duration: Optional[float] = None,
             button: str = 'left',
             clicks: int = 1) -> None:
        """
        Click at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of the movement in seconds. If None, uses a random duration.
            button: Mouse button to click ('left', 'right', 'middle')
            clicks: Number of clicks to perform
        """
        self.move_to(x, y, duration=duration)
        self._random_delay()
        pyautogui.click(x, y, clicks=clicks, button=button)
        self.last_action_time = time.time()
        self.logger.debug(f"Clicked at ({x}, {y}) with {button} button, {clicks} clicks")
    
    def double_click(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """
        Double-click at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of the movement in seconds. If None, uses a random duration.
        """
        self.click(x, y, duration=duration, clicks=2)
    
    def right_click(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """
        Right-click at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of the movement in seconds. If None, uses a random duration.
        """
        self.click(x, y, duration=duration, button='right')
    
    def drag(self, 
            start_x: int, start_y: int, 
            end_x: int, end_y: int,
            duration: Optional[float] = None) -> None:
        """
        Drag from start coordinates to end coordinates.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of the drag in seconds. If None, uses a random duration.
        """
        if duration is None:
            duration = self._get_move_duration() * 1.5  # Drags typically take longer
        
        self.move_to(start_x, start_y)
        self._random_delay()
        
        pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
        self.last_action_time = time.time()
        self.logger.debug(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y}) in {duration:.2f}s")
    
    def click_template(self, 
                      template_match: TemplateMatch, 
                      offset_x: int = 0, 
                      offset_y: int = 0) -> None:
        """
        Click on a template match object with optional offset from center.
        
        Args:
            template_match: The template match object to click on
            offset_x: X offset from the center of the match
            offset_y: Y offset from the center of the match
        """
        center_x, center_y = template_match.center
        click_x = center_x + offset_x
        click_y = center_y + offset_y
        
        self.click(click_x, click_y)
        self.logger.info(f"Clicked on template '{template_match.template_name}' at ({click_x}, {click_y})")
    
    def swipe(self, 
             start_x: int, start_y: int, 
             end_x: int, end_y: int,
             duration: Optional[float] = None) -> None:
        """
        Perform a swipe gesture (alias for drag, for touch-oriented terminology).
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of the swipe in seconds. If None, uses a random duration.
        """
        self.drag(start_x, start_y, end_x, end_y, duration=duration)
    
    def press_key(self, key: str) -> None:
        """
        Press a keyboard key.
        
        Args:
            key: Key to press (e.g., 'enter', 'esc', 'a', 'shift')
        """
        self._random_delay()
        pyautogui.press(key)
        self.last_action_time = time.time()
        self.logger.debug(f"Pressed key: {key}")
    
    def type_text(self, text: str, interval: Optional[float] = None) -> None:
        """
        Type text with human-like timing.
        
        Args:
            text: Text to type
            interval: Interval between keystrokes in seconds. If None, uses a random interval.
        """
        if interval is None:
            interval = random.uniform(0.05, 0.15)  # Human-like typing speed
        
        self._random_delay()
        pyautogui.write(text, interval=interval)
        self.last_action_time = time.time()
        self.logger.debug(f"Typed text: '{text}' with interval {interval:.2f}s")
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """
        Scroll the mouse wheel.
        
        Args:
            clicks: Number of "clicks" to scroll. Positive for up, negative for down.
            x: X coordinate to scroll at. If None, uses current mouse position.
            y: Y coordinate to scroll at. If None, uses current mouse position.
        """
        if x is not None and y is not None:
            self.move_to(x, y)
        
        self._random_delay()
        pyautogui.scroll(clicks)
        self.last_action_time = time.time()
        self.logger.debug(f"Scrolled {clicks} clicks")
    
    def perform_action_sequence(self, actions: List[Dict[str, Union[str, int, float, Tuple]]]) -> None:
        """
        Perform a sequence of actions.
        
        Args:
            actions: List of action dictionaries. Each dictionary must have a 'type' key
                   and additional parameters depending on the action type.
                   Examples:
                   - {'type': 'click', 'x': 100, 'y': 200}
                   - {'type': 'key', 'key': 'enter'}
                   - {'type': 'type', 'text': 'Hello world'}
        """
        for action in actions:
            action_type = action.get('type', '').lower()
            
            try:
                if action_type == 'click':
                    self.click(action['x'], action['y'])
                elif action_type == 'right_click':
                    self.right_click(action['x'], action['y'])
                elif action_type == 'double_click':
                    self.double_click(action['x'], action['y'])
                elif action_type == 'drag' or action_type == 'swipe':
                    self.drag(action['start_x'], action['start_y'], action['end_x'], action['end_y'])
                elif action_type == 'key':
                    self.press_key(action['key'])
                elif action_type == 'type':
                    self.type_text(action['text'])
                elif action_type == 'scroll':
                    self.scroll(action['clicks'], action.get('x'), action.get('y'))
                elif action_type == 'delay':
                    time.sleep(action['seconds'])
                else:
                    self.logger.warning(f"Unknown action type: {action_type}")
            except Exception as e:
                self.logger.error(f"Error performing action {action_type}: {str(e)}")
    
    def wait_after_action(self, seconds: float) -> None:
        """
        Wait a specified number of seconds after the last action.
        
        Args:
            seconds: Number of seconds to wait
        """
        time.sleep(seconds)
        self.logger.debug(f"Waited {seconds:.2f}s after action")
        
    def get_cursor_position(self) -> Tuple[int, int]:
        """
        Get the current cursor position.
        
        Returns:
            Tuple[int, int]: Current (x, y) coordinates of the cursor
        """
        return pyautogui.position()
