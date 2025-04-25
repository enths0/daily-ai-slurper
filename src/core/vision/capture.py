import numpy as np
import pyautogui
import cv2
import time
from typing import Tuple, Optional, Dict, Union


class ScreenCapture:
    """
    Screen capture module for the NIKKE Automation Framework.
    Provides fast and reliable screen capture with region of interest optimization.
    """
    
    def __init__(self, default_region: Optional[Tuple[int, int, int, int]] = None):
        """
        Initialize the screen capture module.
        
        Args:
            default_region: Optional default region to capture (left, top, width, height).
                            If None, captures the entire screen.
        """
        self.default_region = default_region
        self.last_capture_time = 0
        self.last_capture = None
        self.performance_stats: Dict[str, Union[float, int]] = {
            "total_captures": 0,
            "total_time": 0,
            "avg_capture_time": 0,
            "max_capture_time": 0,
        }
    
    def capture(self, region: Optional[Tuple[int, int, int, int]] = None, 
                grayscale: bool = False) -> np.ndarray:
        """
        Capture the screen or a region of the screen.
        
        Args:
            region: Optional region to capture (left, top, width, height).
                   If None, uses the default_region if set, otherwise captures the entire screen.
            grayscale: Whether to convert the image to grayscale.
            
        Returns:
            numpy.ndarray: The captured screen image.
        """
        start_time = time.time()
        
        # Determine the region to capture
        capture_region = region or self.default_region
        
        # Capture the screen
        if capture_region:
            left, top, width, height = capture_region
            screenshot = pyautogui.screenshot(region=capture_region)
        else:
            screenshot = pyautogui.screenshot()
        
        # Convert PIL Image to numpy array
        img = np.array(screenshot)
        
        # Convert BGR to RGB (PIL and OpenCV use different color formats)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale if requested
        if grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Update performance stats
        capture_time = time.time() - start_time
        self._update_performance_stats(capture_time)
        
        # Store the last capture
        self.last_capture = img
        self.last_capture_time = time.time()
        
        return img
    
    def capture_roi(self, x: int, y: int, width: int, height: int, 
                   grayscale: bool = False) -> np.ndarray:
        """
        Capture a specific region of interest (ROI) from the screen.
        
        Args:
            x: X-coordinate of the top-left corner of the ROI.
            y: Y-coordinate of the top-left corner of the ROI.
            width: Width of the ROI.
            height: Height of the ROI.
            grayscale: Whether to convert the image to grayscale.
            
        Returns:
            numpy.ndarray: The captured ROI image.
        """
        return self.capture(region=(x, y, width, height), grayscale=grayscale)
    
    def get_last_capture(self) -> Optional[np.ndarray]:
        """
        Get the last captured image.
        
        Returns:
            numpy.ndarray or None: The last captured image, or None if no image has been captured.
        """
        return self.last_capture
    
    def _update_performance_stats(self, capture_time: float) -> None:
        """
        Update performance statistics for the capture operation.
        
        Args:
            capture_time: Time taken for the capture operation.
        """
        self.performance_stats["total_captures"] += 1
        self.performance_stats["total_time"] += capture_time
        self.performance_stats["avg_capture_time"] = (
            self.performance_stats["total_time"] / self.performance_stats["total_captures"]
        )
        self.performance_stats["max_capture_time"] = max(
            self.performance_stats["max_capture_time"], capture_time
        )
    
    def get_performance_stats(self) -> Dict[str, Union[float, int]]:
        """
        Get the performance statistics for the capture module.
        
        Returns:
            Dict[str, Union[float, int]]: Dictionary containing performance statistics.
        """
        return self.performance_stats.copy()
