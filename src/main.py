import os
import sys
import time
import logging
import yaml
from typing import Dict, Any, Optional

from src.core.vision.capture import ScreenCapture
from src.core.vision.template import TemplateMatcher, MatchMethod
from src.core.state.manager import StateManager, GameState
from src.core.state.detection import StateDetector
from src.core.input.controller import InputController


class NikkeAutomation:
    """
    Main class for the NIKKE Automation Framework.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the NIKKE Automation system.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing NIKKE Automation Framework")
        
        # Initialize components
        self._init_components()
        
        self.logger.info("NIKKE Automation Framework initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading configuration from {config_path}: {str(e)}")
            print("Using default configuration")
            return {}
    
    def _setup_logging(self) -> None:
        """Set up logging based on configuration."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        log_dir = log_config.get('dir', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(
            log_dir, 
            log_config.get('file_pattern', 'nikke_auto_{date}.log').format(
                date=time.strftime('%Y%m%d_%H%M%S')
            )
        )
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler() if log_config.get('console_output', True) else logging.NullHandler()
            ]
        )
    
    def _init_components(self) -> None:
        """Initialize all system components."""
        # Initialize screen capture
        capture_config = self.config.get('vision', {}).get('capture', {})
        self.screen_capture = ScreenCapture(
            default_region=capture_config.get('default_region')
        )
        
        # Initialize template matcher
        template_config = self.config.get('vision', {}).get('template', {})
        self.template_matcher = TemplateMatcher(
            templates_dir=template_config.get('base_dir', 'resources/templates')
        )
        
        # Initialize state management
        self.state_manager = StateManager()
        
        # Initialize state detection
        self.state_detector = StateDetector(self.template_matcher)
        
        # Initialize input controller
        input_config = self.config.get('input', {})
        self.input_controller = InputController(
            min_delay=input_config.get('min_delay', 0.05),
            max_delay=input_config.get('max_delay', 0.2),
            move_duration_range=input_config.get('move_duration_range', (0.1, 0.3))
        )
    
    def update_state(self) -> GameState:
        """
        Update the current game state based on screen capture.
        
        Returns:
            GameState: The detected game state
        """
        # Capture the screen
        screen = self.screen_capture.capture()
        
        # Detect the state
        detected_state = self.state_detector.detect_state(screen)
        
        # Update the state manager
        state_changed = self.state_manager.update_state(detected_state)
        
        if state_changed:
            self.logger.info(f"State changed to: {detected_state}")
        
        return detected_state
    
    def navigate_to(self, target_state: GameState) -> bool:
        """
        Navigate to a target game state.
        
        Args:
            target_state: The target game state
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        # Update current state
        current_state = self.update_state()
        
        if current_state == target_state:
            self.logger.info(f"Already in target state: {target_state}")
            return True
        
        # Find path to target state
        path = self.state_manager.find_path(target_state)
        
        if not path:
            self.logger.error(f"No path found from {current_state} to {target_state}")
            return False
        
        self.logger.info(f"Navigating from {current_state} to {target_state} with {len(path)} steps")
        
        # Execute each transition in the path
        for transition in path:
            self.logger.info(f"Performing transition: {transition}")
            
            # Execute actions for this transition
            for action_name in transition.action_sequence:
                self._execute_action(action_name)
            
            # Wait for expected duration
            time.sleep(transition.expected_duration)
            
            # Verify that we reached the expected state
            new_state = self.update_state()
            
            if new_state != transition.to_state:
                self.logger.warning(
                    f"Expected to reach {transition.to_state}, but got {new_state} instead"
                )
                return False
        
        self.logger.info(f"Successfully navigated to {target_state}")
        return True
    
    def _execute_action(self, action_name: str) -> bool:
        """
        Execute a named action.
        
        Args:
            action_name: Name of the action to execute
            
        Returns:
            bool: True if action was executed successfully, False otherwise
        """
        self.logger.info(f"Executing action: {action_name}")
        
        try:
            # Capture the screen to find templates
            screen = self.screen_capture.capture()
            
            if action_name.startswith("click_"):
                # Extract the template name from the action
                template_name = action_name[6:]  # Remove 'click_' prefix
                
                # Find the template
                match = self.template_matcher.find_template(
                    screen, 
                    template_name,
                    method=MatchMethod.EXACT,
                    threshold=0.7
                )
                
                if match:
                    # Click on the template
                    self.input_controller.click_template(match)
                    return True
                else:
                    self.logger.warning(f"Template not found for action: {action_name}")
                    return False
            
            # Add more action types as needed
            
            else:
                self.logger.warning(f"Unknown action: {action_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing action {action_name}: {str(e)}")
            return False
    
    def run_test(self) -> None:
        """Run a simple test to verify that everything is working."""
        self.logger.info("Running test sequence")
        
        # Capture and display screen dimensions
        screen = self.screen_capture.capture()
        h, w = screen.shape[:2]
        self.logger.info(f"Screen dimensions: {w}x{h}")
        
        # Update state
        state = self.update_state()
        self.logger.info(f"Current state: {state}")
        
        # Log performance stats
        stats = self.screen_capture.get_performance_stats()
        self.logger.info(f"Screen capture performance: Avg time: {stats['avg_capture_time']:.3f}s")
        
        self.logger.info("Test completed successfully")


def main():
    """Main entry point."""
    print("NIKKE Automation Framework")
    print("-------------------------")
    
    # Create the automation system
    automation = NikkeAutomation()
    
    # Run a simple test
    automation.run_test()
    
    print("Initial test completed. See logs for details.")


if __name__ == "__main__":
    main()
