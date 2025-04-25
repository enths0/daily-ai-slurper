import unittest
import numpy as np
import os
import sys
import time

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.vision.capture import ScreenCapture


class TestScreenCapture(unittest.TestCase):
    """Test cases for the ScreenCapture module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.capture = ScreenCapture()
    
    def test_full_screen_capture(self):
        """Test capturing the full screen."""
        # Capture the full screen
        screen = self.capture.capture()
        
        # Check that the screen is not None
        self.assertIsNotNone(screen)
        
        # Check that the screen is a numpy array
        self.assertIsInstance(screen, np.ndarray)
        
        # Check that the screen has valid dimensions
        self.assertGreater(screen.shape[0], 0)  # Height
        self.assertGreater(screen.shape[1], 0)  # Width
        self.assertEqual(screen.shape[2], 3)    # BGR channels
    
    def test_region_capture(self):
        """Test capturing a specific region of the screen."""
        # Define a small region (100x100 at the top-left corner)
        region = (0, 0, 100, 100)
        
        # Capture the region
        screen = self.capture.capture(region=region)
        
        # Check that the screen is not None
        self.assertIsNotNone(screen)
        
        # Check that the screen has the expected dimensions
        self.assertEqual(screen.shape[0], 100)  # Height
        self.assertEqual(screen.shape[1], 100)  # Width
    
    def test_grayscale_capture(self):
        """Test capturing a grayscale image."""
        # Capture in grayscale
        screen = self.capture.capture(grayscale=True)
        
        # Check that the screen is not None
        self.assertIsNotNone(screen)
        
        # Check that the screen is a numpy array
        self.assertIsInstance(screen, np.ndarray)
        
        # Check that the screen has only one channel (grayscale)
        self.assertEqual(len(screen.shape), 2)
    
    def test_performance(self):
        """Test the performance of screen capture."""
        # Capture multiple times to get performance stats
        for _ in range(5):
            self.capture.capture()
        
        # Get performance stats
        stats = self.capture.get_performance_stats()
        
        # Check that stats are recorded
        self.assertGreaterEqual(stats["total_captures"], 5)
        self.assertGreater(stats["total_time"], 0)
        self.assertGreater(stats["avg_capture_time"], 0)
        
        # Check that capture time is reasonable (less than 200ms)
        self.assertLess(stats["avg_capture_time"], 0.2)
    
    def test_last_capture(self):
        """Test getting the last capture."""
        # Capture a screen
        screen1 = self.capture.capture()
        
        # Get the last capture
        last_capture = self.capture.get_last_capture()
        
        # Check that the last capture matches the captured screen
        self.assertTrue(np.array_equal(screen1, last_capture))
        
        # Capture another screen
        screen2 = self.capture.capture()
        
        # Get the last capture again
        last_capture = self.capture.get_last_capture()
        
        # Check that the last capture is updated
        self.assertTrue(np.array_equal(screen2, last_capture))


if __name__ == '__main__':
    unittest.main()
