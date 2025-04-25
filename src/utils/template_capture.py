import os
import sys
import time
import argparse
import cv2
import numpy as np
import pyautogui
from datetime import datetime


def capture_screenshot(output_dir: str, name: str = None, region: tuple = None) -> str:
    """
    Capture a screenshot and save it to the output directory.
    
    Args:
        output_dir: Directory to save the screenshot
        name: Name for the screenshot file (without extension)
        region: Region to capture (left, top, width, height)
        
    Returns:
        str: Path to the saved screenshot
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    if name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"template_{timestamp}.png"
    else:
        filename = f"{name}.png"
    
    filepath = os.path.join(output_dir, filename)
    
    # Capture screenshot
    screenshot = pyautogui.screenshot(region=region)
    
    # Save the screenshot
    screenshot.save(filepath)
    
    print(f"Screenshot saved to: {filepath}")
    return filepath


def interactive_region_select() -> tuple:
    """
    Allow the user to select a region on the screen.
    
    Returns:
        tuple: Selected region (left, top, width, height)
    """
    print("Please select a region on the screen...")
    print("1. Press and hold left mouse button to start selection")
    print("2. Drag to select the region")
    print("3. Release to confirm selection")
    print("4. Press ESC to cancel")
    
    # Wait for the user to prepare
    time.sleep(1)
    
    # Take a screenshot of the entire screen for display
    screenshot = pyautogui.screenshot()
    screen = np.array(screenshot)
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    
    # Create a window to show the screen
    window_name = "Select Region (Drag and release)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Variables to store selection
    start_point = None
    end_point = None
    selecting = False
    selection_complete = False
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal start_point, end_point, selecting, selection_complete, screen
        
        # Create a copy of the original screen
        img = screen.copy()
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Start selection
            selecting = True
            start_point = (x, y)
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if selecting:
                # Update end point while dragging
                end_point = (x, y)
                # Draw rectangle on the image
                cv2.rectangle(img, start_point, end_point, (0, 255, 0), 2)
                cv2.imshow(window_name, img)
        
        elif event == cv2.EVENT_LBUTTONUP:
            # Complete selection
            selecting = False
            end_point = (x, y)
            selection_complete = True
            # Draw final rectangle
            cv2.rectangle(img, start_point, end_point, (0, 255, 0), 2)
            cv2.imshow(window_name, img)
    
    cv2.setMouseCallback(window_name, mouse_callback)
    
    # Display the screen
    cv2.imshow(window_name, screen)
    
    # Wait for selection to complete or ESC to cancel
    while not selection_complete:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key
            cv2.destroyAllWindows()
            return None
    
    cv2.destroyAllWindows()
    
    # Calculate region (left, top, width, height)
    left = min(start_point[0], end_point[0])
    top = min(start_point[1], end_point[1])
    width = abs(end_point[0] - start_point[0])
    height = abs(end_point[1] - start_point[1])
    
    return (left, top, width, height)


def main():
    """Main entry point for the template capture utility."""
    parser = argparse.ArgumentParser(description="Capture template images for NIKKE Automation")
    parser.add_argument("--output", "-o", default="resources/templates",
                        help="Output directory for templates")
    parser.add_argument("--name", "-n", help="Name for the template file (without extension)")
    parser.add_argument("--category", "-c", default="",
                        help="Category subdirectory for the template (e.g., 'home', 'battle')")
    parser.add_argument("--interval", "-i", type=float, default=0,
                        help="Time interval between captures for multiple captures (in seconds, 0 for single capture)")
    parser.add_argument("--count", type=int, default=1,
                        help="Number of templates to capture when using interval")
    
    args = parser.parse_args()
    
    # Create output directory with category
    output_dir = os.path.join(args.output, args.category) if args.category else args.output
    
    if args.interval > 0 and args.count > 1:
        print(f"Capturing {args.count} templates with interval {args.interval}s")
        for i in range(args.count):
            if i > 0:
                print(f"Waiting {args.interval}s before next capture...")
                time.sleep(args.interval)
            
            # For multiple captures, append index to name
            name = f"{args.name}_{i+1}" if args.name else None
            region = interactive_region_select()
            
            if region:
                capture_screenshot(output_dir, name, region)
            else:
                print("Selection canceled.")
                break
    else:
        region = interactive_region_select()
        if region:
            capture_screenshot(output_dir, args.name, region)
        else:
            print("Selection canceled.")


if __name__ == "__main__":
    main() 