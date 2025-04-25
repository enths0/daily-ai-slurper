#!/usr/bin/env python3
"""
Script to create the folder structure for NIKKE Automation project.
"""

import os
import sys

def create_directory(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_file(path):
    """Create an empty file if it doesn't exist."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass
        print(f"Created file: {path}")

def main():
    # Project root directory
    root_dir = "nikke_automation"
    
    # Create root directory
    create_directory(root_dir)
    
    # Define paths
    dirs = [
        # src directories
        f"{root_dir}/src/core/vision",
        f"{root_dir}/src/core/state",
        f"{root_dir}/src/core/input",
        f"{root_dir}/src/game/screens",
        f"{root_dir}/src/game/tasks",
        f"{root_dir}/src/utils",
        
        # resource directories
        f"{root_dir}/resources/templates/home",
        f"{root_dir}/resources/templates/battle",
        f"{root_dir}/resources/templates/shop",
        
        # test directory
        f"{root_dir}/tests"
    ]
    
    # Create all directories
    for dir_path in dirs:
        create_directory(dir_path)
    
    # Define files
    files = [
        # Init files
        f"{root_dir}/src/__init__.py",
        f"{root_dir}/src/core/__init__.py",
        f"{root_dir}/src/core/vision/__init__.py",
        f"{root_dir}/src/core/state/__init__.py",
        f"{root_dir}/src/core/input/__init__.py",
        f"{root_dir}/src/game/__init__.py",
        f"{root_dir}/src/game/screens/__init__.py",
        f"{root_dir}/src/game/tasks/__init__.py",
        f"{root_dir}/src/utils/__init__.py",
        f"{root_dir}/tests/__init__.py",
        
        # Core vision files
        f"{root_dir}/src/core/vision/capture.py",
        f"{root_dir}/src/core/vision/template.py",
        f"{root_dir}/src/core/vision/ocr.py",
        
        # Core state files
        f"{root_dir}/src/core/state/manager.py",
        f"{root_dir}/src/core/state/detection.py",
        f"{root_dir}/src/core/state/navigation.py",
        
        # Core input files
        f"{root_dir}/src/core/input/controller.py",
        f"{root_dir}/src/core/input/verification.py",
        
        # Game screen files
        f"{root_dir}/src/game/screens/home.py",
        f"{root_dir}/src/game/screens/battle.py",
        f"{root_dir}/src/game/screens/shop.py",
        
        # Game task files
        f"{root_dir}/src/game/tasks/daily.py",
        
        # Utils files
        f"{root_dir}/src/utils/logger.py",
        f"{root_dir}/src/utils/config.py",
        f"{root_dir}/src/utils/exceptions.py",
        
        # Main entry point
        f"{root_dir}/src/main.py",
        
        # Test files
        f"{root_dir}/tests/test_capture.py",
        f"{root_dir}/tests/test_template.py",
        f"{root_dir}/tests/test_state.py",
        
        # Root files
        f"{root_dir}/config.yaml",
        f"{root_dir}/requirements.txt",
        f"{root_dir}/setup.py",
        f"{root_dir}/README.md"
    ]
    
    # Create all files
    for file_path in files:
        create_file(file_path)
        
    print("\nProject structure created successfully!")
    print(f"Project location: {os.path.abspath(root_dir)}")

if __name__ == "__main__":
    main()