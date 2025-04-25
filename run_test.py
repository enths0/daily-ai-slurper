#!/usr/bin/env python3
"""
Test script for the NIKKE Automation Framework.
This script runs a simple test to verify that the framework is working properly.
"""

import os
import sys
import time

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.main import NikkeAutomation


def main():
    """Run a simple test of the automation framework."""
    print("="*50)
    print("NIKKE Automation Framework Test")
    print("="*50)
    
    # Create the automation system
    print("Initializing automation system...")
    automation = NikkeAutomation()
    
    # Run the test
    print("\nRunning test sequence...")
    automation.run_test()
    
    print("\nTest completed. Check the logs for details.")
    print("="*50)


if __name__ == "__main__":
    main() 