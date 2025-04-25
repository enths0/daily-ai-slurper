#!/usr/bin/env python3
"""
Script to build a standalone executable for the NIKKE Automation Framework.
Requires PyInstaller to be installed:
    pip install pyinstaller
"""

import os
import sys
import subprocess
import shutil
import platform

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building NIKKE Automation Framework executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Installing it now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Determine the system platform
    if platform.system() == "Windows":
        exe_name = "nikke-auto.exe"
    else:
        exe_name = "nikke-auto"
    
    # Create a spec file for PyInstaller
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/cli.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('config.yaml', '.'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.scrolledtext', 'tkinter.messagebox'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)
"""
    
    # Write the spec file
    with open("nikke-auto.spec", "w") as f:
        f.write(spec_content)
    
    # Ensure resources directory exists
    os.makedirs("resources/templates/home", exist_ok=True)
    os.makedirs("resources/templates/battle", exist_ok=True)
    os.makedirs("resources/templates/shop", exist_ok=True)
    
    # Run PyInstaller
    print("Running PyInstaller. This may take a few minutes...")
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "PyInstaller", 
        "nikke-auto.spec",
        "--clean"
    ])
    
    # Check if the executable was built successfully
    exe_path = os.path.join("dist", exe_name)
    if os.path.exists(exe_path):
        print(f"Executable built successfully: {exe_path}")
        print("You can now run the application by double-clicking on it or from command line.")
    else:
        print("Failed to build executable.")


if __name__ == "__main__":
    build_executable() 