import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.core.vision.template import TemplateMatcher, MatchMethod
from .manager import GameState


class StateDetector:
    """
    Detects the current game state based on visual elements.
    """
    
    def __init__(self, template_matcher: TemplateMatcher):
        """
        Initialize the state detector.
        
        Args:
            template_matcher: Template matcher for finding UI elements
        """
        self.template_matcher = template_matcher
        self.logger = logging.getLogger(__name__)
        
        # Define state definitions with required templates and confidence thresholds
        self.state_definitions: Dict[GameState, Dict] = {
            GameState.HOME_SCREEN: {
                "required_templates": ["home/menu_button", "home/shop_button"],
                "confidence_threshold": 0.8,
                "match_all": True  # All templates must be matched
            },
            GameState.BATTLE: {
                "required_templates": ["battle/battle_ui", "battle/back_button"],
                "confidence_threshold": 0.7,
                "match_all": True
            },
            GameState.SHOP: {
                "required_templates": ["shop/shop_title", "shop/purchase_button"],
                "confidence_threshold": 0.75,
                "match_all": False  # Only one template needs to match
            },
            GameState.LOADING: {
                "required_templates": ["common/loading_indicator"],
                "confidence_threshold": 0.6,
                "match_all": True
            },
            GameState.ERROR: {
                "required_templates": ["common/error_icon", "common/error_message"],
                "confidence_threshold": 0.7,
                "match_all": False
            }
        }
    
    def detect_state(self, screen_image: np.ndarray) -> GameState:
        """
        Detect the current game state from a screen image.
        
        Args:
            screen_image: Screen image to analyze
            
        Returns:
            GameState: Detected game state
        """
        state_confidence: Dict[GameState, float] = {}
        
        # Check each defined state
        for state, definition in self.state_definitions.items():
            required_templates = definition["required_templates"]
            threshold = definition["confidence_threshold"]
            match_all = definition["match_all"]
            
            matched_templates = 0
            total_confidence = 0.0
            
            for template_name in required_templates:
                match = self.template_matcher.find_template(
                    screen_image, 
                    template_name, 
                    method=MatchMethod.EXACT,
                    threshold=threshold
                )
                
                if match:
                    matched_templates += 1
                    total_confidence += match.confidence
            
            # Calculate state confidence
            if matched_templates > 0:
                avg_confidence = total_confidence / matched_templates
                
                # Check if we need all templates to match or just one
                if (match_all and matched_templates == len(required_templates)) or \
                   (not match_all and matched_templates > 0):
                    state_confidence[state] = avg_confidence
        
        if not state_confidence:
            self.logger.warning("Could not detect any known state")
            return GameState.UNKNOWN
        
        # Find the state with the highest confidence
        best_state = max(state_confidence.items(), key=lambda x: x[1])[0]
        self.logger.info(f"Detected state: {best_state} with confidence {state_confidence[best_state]:.2f}")
        
        return best_state
    
    def verify_state(self, expected_state: GameState, screen_image: np.ndarray) -> bool:
        """
        Verify if the current screen matches an expected state.
        
        Args:
            expected_state: The expected game state
            screen_image: Screen image to analyze
            
        Returns:
            bool: True if the screen matches the expected state, False otherwise
        """
        detected_state = self.detect_state(screen_image)
        return detected_state == expected_state
    
    def register_state_definition(self, 
                                state: GameState, 
                                required_templates: List[str],
                                confidence_threshold: float = 0.7,
                                match_all: bool = True) -> None:
        """
        Register a new state definition.
        
        Args:
            state: The game state to define
            required_templates: List of template names required for this state
            confidence_threshold: Minimum confidence threshold for template matching
            match_all: Whether all templates must be matched (True) or just one (False)
        """
        self.state_definitions[state] = {
            "required_templates": required_templates,
            "confidence_threshold": confidence_threshold,
            "match_all": match_all
        }
        
        self.logger.info(f"Registered state definition for {state}")
    
    def get_visible_ui_elements(self, screen_image: np.ndarray, 
                              threshold: float = 0.7) -> Dict[str, List]:
        """
        Get all visible UI elements in the screen image.
        
        Args:
            screen_image: Screen image to analyze
            threshold: Confidence threshold for template matching
            
        Returns:
            Dict[str, List]: Dictionary mapping template names to match results
        """
        return self.template_matcher.find_all_templates(
            screen_image,
            method=MatchMethod.EXACT,
            threshold=threshold
        )
