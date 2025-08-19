#!/usr/bin/env python3
"""
Enhanced build script for creating Windows executables with reduced false positives
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")

def build_with_options():
    """Build with anti-virus friendly options"""
    
    # Additional PyInstaller options to reduce false positives
    build_args = [
        'pyinstaller', 
        'build.spec',
        '--clean',              # Clean cache
        '--noconfirm',          # Don't ask for confirmation
        '--log-level=INFO',     # Verbose logging
    ]
    
    # Windows-specific optimizations
    if sys.platform == "win32":
        build_args.extend([
            '--noupx',          # Don't use UPX (reduces false positives)
            '--strip',          # Strip debug symbols
        ])
    
    print("Building executable with anti-virus friendly settings...")
    print(f"Command: {' '.join(build_args)}")
    
    try:
        result = subprocess.run(build_args, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def post_build_cleanup():
    """Clean up after build to reduce executable size"""
    if sys.platform == "win32":
        exe_path = Path("dist/Mockachu.exe")
        if exe_path.exists():
            print(f"Executable created: {exe_path}")
            print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            # Create a simple installer script
            create_simple_installer()

def create_simple_installer():
    """Create a simple batch installer to help with deployment"""
    installer_content = '''@echo off
echo Installing Mockachu...
echo.
echo This is Mockachu - Mock Data Generator
echo Open source software under MIT License
echo Source: https://github.com/sahzudin/mockachu
echo.
echo If your antivirus flags this as a threat, it's a FALSE POSITIVE.
echo See WINDOWS_ANTIVIRUS_NOTICE.md for more information.
echo.
pause
echo.
echo Creating desktop shortcut...
set "target=%~dp0Mockachu.exe"
set "shortcut=%USERPROFILE%\\Desktop\\Mockachu.lnk"

powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut%'); $Shortcut.TargetPath = '%target%'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

echo Desktop shortcut created!
echo You can now run Mockachu from your desktop.
pause
'''
    
    with open("dist/install.bat", "w") as f:
        f.write(installer_content)
    
    print("Created install.bat for easy deployment")

if __name__ == "__main__":
    print("Enhanced Mockachu Build Script")
    print("==============================")
    
    # Step 1: Clean previous builds
    clean_build_dirs()
    
    # Step 2: Build executable
    if build_with_options():
        # Step 3: Post-build cleanup
        post_build_cleanup()
        print("\nBuild completed successfully!")
        print("\nTo reduce antivirus false positives:")
        print("1. The executable is built without UPX compression")
        print("2. Enhanced version information is included")
        print("3. Windows manifest file is embedded")
        print("4. See WINDOWS_ANTIVIRUS_NOTICE.md for user guidance")
    else:
        print("\nBuild failed. Please check the error messages above.")
        sys.exit(1)
