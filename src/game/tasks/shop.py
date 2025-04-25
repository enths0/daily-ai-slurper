"""
Shop automation tasks for NIKKE Automation Framework.
"""

import logging
import time
from typing import List, Optional, TYPE_CHECKING

from src.core.state.manager import GameState

# Use TYPE_CHECKING to prevent circular imports
if TYPE_CHECKING:
    from src.main import NikkeAutomation


class ShopTask:
    """Handles shopping-related automation tasks"""
    
    def __init__(self, automation: "NikkeAutomation"):
        """
        Initialize the shop task.
        
        Args:
            automation: NikkeAutomation instance
        """
        self.automation = automation
        self.logger = logging.getLogger(__name__)
    
    def purchase_credit_items(self) -> bool:
        """
        Purchase all available items for credits (NOT gems).
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info("Starting credit item purchase task")
        
        # Navigate to shop if not already there
        current_state = self.automation.update_state()
        if current_state != GameState.SHOP:
            self.logger.info("Navigating to shop")
            success = self.automation.navigate_to(GameState.SHOP)
            if not success:
                self.logger.error("Failed to navigate to shop")
                return False
        
        # Get the current screen
        screen = self.automation.capture_screen()
        
        # Find all credit items to purchase
        credit_items = self.automation.template_matcher.find_all_matches(
            screen, "shop/credit_items"
        )
        
        if not credit_items:
            self.logger.info("No credit items found to purchase")
            return True
        
        self.logger.info(f"Found {len(credit_items)} credit items to purchase")
        
        # For each item found
        for i, item in enumerate(credit_items):
            self.logger.info(f"Processing item {i+1}/{len(credit_items)}")
            
            # Click on the item
            center_x, center_y = item.center
            self.automation.input_controller.click(
                center_x, center_y, 
                randomize=True
            )
            
            # Wait for purchase confirmation
            time.sleep(1.0)
            
            # Verify we're using credits, not gems
            screen = self.automation.capture_screen()
            credits_found = self.automation.template_matcher.find_template(
                screen, "shop/currency_credits"
            )
            
            if not credits_found:
                self.logger.warning("Credits currency not found, skipping purchase")
                # Cancel the purchase by clicking outside
                self.automation.input_controller.click(100, 100)
                time.sleep(0.5)
                continue
            
            # Find and click the purchase button
            purchase_button = self.automation.template_matcher.find_template(
                screen, "shop/confirm_purchase"
            )
            
            if purchase_button:
                self.logger.info("Confirming purchase")
                center_x, center_y = purchase_button.center
                self.automation.input_controller.click(
                    center_x, center_y
                )
                time.sleep(1.5)  # Wait for purchase animation
                
                # Close any confirmation dialog
                screen = self.automation.capture_screen()
                confirm_button = self.automation.template_matcher.find_template(
                    screen, "common/confirm_button"
                )
                
                if confirm_button:
                    center_x, center_y = confirm_button.center
                    self.automation.input_controller.click(
                        center_x, center_y
                    )
                    time.sleep(0.5)
            else:
                self.logger.warning("Purchase button not found, skipping item")
                # Cancel by clicking outside
                self.automation.input_controller.click(100, 100)
            
            # Short delay before next item
            time.sleep(1.0)
        
        self.logger.info("Shop credit purchase task completed")
        
        # Navigate back to home
        return self.automation.navigate_to(GameState.HOME_SCREEN) 