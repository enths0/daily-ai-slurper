#!/usr/bin/env python3
"""
Command Line Interface for NIKKE Automation Framework
This provides a single entry point for all functionality.
"""

import os
import sys
import argparse
import time

from src.utils.template_capture import capture_screenshot, interactive_region_select
from src.main import NikkeAutomation
from src.core.state.manager import GameState


def capture_template_command(args):
    """Handle template capture command"""
    print("=== Template Capture Tool ===")
    
    # Create output directory with category
    output_dir = os.path.join(args.output, args.category) if args.category else args.output
    os.makedirs(output_dir, exist_ok=True)
    
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


def run_test_command(args):
    """Handle test command"""
    print("=== NIKKE Automation Test ===")
    
    # Create automation instance
    automation = NikkeAutomation(config_path=args.config)
    
    # Run the test
    print("Running test sequence...")
    automation.run_test()
    
    print("Test completed. Check the logs for details.")


def run_automation_command(args):
    """Handle automation command"""
    print("=== NIKKE Automation ===")
    
    # Create automation instance
    automation = NikkeAutomation(config_path=args.config)
    
    # Update state
    state = automation.update_state()
    print(f"Current state: {state}")
    
    # If a target state is specified, navigate to it
    if args.navigate:
        try:
            target_state = GameState[args.navigate.upper()]
            print(f"Navigating to: {target_state}")
            result = automation.navigate_to(target_state)
            
            if result:
                print(f"Successfully navigated to {target_state}")
            else:
                print(f"Failed to navigate to {target_state}")
        except KeyError:
            print(f"Invalid state: {args.navigate}")
            print(f"Available states: {[s.name for s in GameState]}")
    
    print("Automation completed.")


def run_gui_command(args):
    """Launch the GUI interface"""
    try:
        from src.gui import NikkeAutomationGUI
        import tkinter as tk
        
        # Create the root window
        root = tk.Tk()
        
        # Create the GUI
        app = NikkeAutomationGUI(root)
        
        # Run the GUI
        root.mainloop()
    except ImportError as e:
        print(f"Error: {str(e)}")
        print("Failed to load the GUI. Make sure tkinter is installed.")
        sys.exit(1)


def setup_parser():
    """Set up the argument parser"""
    parser = argparse.ArgumentParser(
        description="NIKKE Automation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Launch the GUI:
    python -m src.cli gui
    
  Capture a template:
    python -m src.cli capture --name menu_button --category home
  
  Run a test:
    python -m src.cli test
  
  Run automation and navigate to shop:
    python -m src.cli run --navigate SHOP
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch the graphical user interface")
    
    # Template capture command
    capture_parser = subparsers.add_parser("capture", help="Capture template images")
    capture_parser.add_argument("--output", "-o", default="resources/templates",
                              help="Output directory for templates")
    capture_parser.add_argument("--name", "-n", required=True,
                              help="Name for the template file (without extension)")
    capture_parser.add_argument("--category", "-c", default="",
                              help="Category subdirectory for the template (e.g., 'home', 'battle')")
    capture_parser.add_argument("--interval", "-i", type=float, default=0,
                              help="Time interval between captures for multiple captures (in seconds)")
    capture_parser.add_argument("--count", type=int, default=1,
                              help="Number of templates to capture when using interval")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test the automation framework")
    test_parser.add_argument("--config", default="config.yaml",
                           help="Path to the configuration file")
    
    # Run automation command
    run_parser = subparsers.add_parser("run", help="Run automation")
    run_parser.add_argument("--config", default="config.yaml",
                          help="Path to the configuration file")
    run_parser.add_argument("--navigate", 
                          help="Navigate to a specific state (e.g., HOME_SCREEN, SHOP, BATTLE)")
    
    return parser


def main():
    """Main entry point for the CLI"""
    parser = setup_parser()
    args = parser.parse_args()
    
    # If no arguments, default to launching the GUI
    if len(sys.argv) == 1 or args.command is None:
        args.command = "gui"
    
    if args.command == "gui":
        run_gui_command(args)
    elif args.command == "capture":
        capture_template_command(args)
    elif args.command == "test":
        run_test_command(args)
    elif args.command == "run":
        run_automation_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 