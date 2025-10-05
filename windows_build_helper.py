#!/usr/bin/env python3
"""
Windows APK Build Helper
Since Buildozer doesn't work on Windows, this creates a package for building on other platforms
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

def create_build_package():
    """Create a complete build package for APK generation"""
    print("🔧 Creating Windows Build Package...")
    
    # Create dist directory
    dist_dir = Path("app/dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Package info
    package_name = "VoiceRecorder_BuildPackage"
    package_dir = dist_dir / package_name
    
    # Remove existing package
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    
    # Files to include in package
    source_files = {
        # App files
        "app/main.py": "app/main.py",
        "app/audio_utils.py": "app/audio_utils.py",
        "app/__init__.py": "app/__init__.py",
        
        # Service files
        "services/recording_service.py": "services/recording_service.py",
        "services/service.py": "services/service.py",
        "services/__init__.py": "services/__init__.py",
        
        # Build files
        "buildozer.spec": "buildozer.spec",
        "requirements.txt": "requirements.txt",
        "README.md": "README.md",
        "build_apk.py": "build_apk.py"
    }
    
    # Copy files
    copied_files = []
    for src, dst in source_files.items():
        src_path = Path(src)
        dst_path = package_dir / dst
        
        if src_path.exists():
            # Create destination directory
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            copied_files.append(dst)
            print(f"✓ {src}")
        else:
            print(f"✗ Missing: {src}")
    
    # Create build script for Linux/macOS
    linux_build_script = """#!/bin/bash
# APK Build Script for Linux/macOS
set -e

echo "Voice Recorder APK Builder (Linux/macOS)"
echo "========================================"

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "Installing buildozer..."
    pip3 install buildozer
fi

# Install other dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Initialize buildozer (first time only)
if [ ! -d ".buildozer" ]; then
    echo "Initializing buildozer..."
    buildozer android debug
else
    echo "Building APK..."
    buildozer android release
fi

echo "Build complete! Check the bin/ folder for your APK."
"""
    
    build_script_path = package_dir / "build_linux.sh"
    build_script_path.write_text(linux_build_script)
    
    # Create Windows instructions
    windows_instructions = """# APK Build Instructions for Windows Users

## Problem
Buildozer (the tool that converts Python to APK) doesn't work reliably on Windows.

## Solutions

### Option 1: WSL (Recommended)
1. Install Windows Subsystem for Linux:
   ```cmd
   wsl --install
   ```
2. Restart your computer
3. Open Ubuntu (from Start menu)
4. Copy this folder to WSL:
   ```bash
   cp -r /mnt/c/path/to/this/folder ~/voicerecorder
   cd ~/voicerecorder
   ```
5. Install Python and pip:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```
6. Run the build:
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```

### Option 2: Online Build (GitHub Actions)
1. Create a GitHub repository
2. Upload these files to the repo
3. Create `.github/workflows/build.yml`:
   ```yaml
   name: Build APK
   on: [push]
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: 3.8
         - name: Build APK
           run: |
             pip install buildozer
             pip install -r requirements.txt
             buildozer android debug
         - name: Upload APK
           uses: actions/upload-artifact@v2
           with:
             name: voice-recorder-apk
             path: bin/*.apk
   ```

### Option 3: Linux Virtual Machine
1. Install VirtualBox
2. Download Ubuntu ISO
3. Create Ubuntu VM
4. Install Python and dependencies
5. Copy files and build

### Option 4: Replit.com
1. Go to replit.com
2. Create new Python project
3. Upload these files
4. Install dependencies in shell:
   ```bash
   pip install buildozer
   pip install -r requirements.txt
   ```
5. Run: `buildozer android debug`

## What You'll Get
- APK file (8-25 MB)
- Ready to install on Android
- All permissions configured
- Background recording capability

## Need Help?
Check the main README.md for detailed instructions.
"""
    
    instructions_path = package_dir / "WINDOWS_BUILD_GUIDE.md"
    instructions_path.write_text(windows_instructions)
    
    # Create package info
    package_info = f"""# Voice Recorder Build Package

This package contains all files needed to build the Voice Recorder APK.

## Contents:
"""
    for file in copied_files:
        package_info += f"- {file}\n"
    
    package_info += f"""
## Created: {os.path.basename(__file__)}
## Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Build Instructions:
- Windows: See WINDOWS_BUILD_GUIDE.md
- Linux/macOS: Run ./build_linux.sh

## Expected Output:
- APK file in bin/ folder
- File size: 8-25 MB
- Compatible with Android 5.0+
"""
    
    info_path = package_dir / "PACKAGE_INFO.md"
    info_path.write_text(package_info)
    
    # Create ZIP file
    zip_path = dist_dir / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    # Results
    print(f"\n✅ Build package created successfully!")
    print(f"📁 Folder: {package_dir}")
    print(f"📦 ZIP file: {zip_path}")
    print(f"📄 Size: {zip_path.stat().st_size / 1024:.1f} KB")
    
    # Copy to desktop
    try:
        desktop_path = Path.home() / "Desktop" / zip_path.name
        shutil.copy2(zip_path, desktop_path)
        print(f"📥 Copied to desktop: {desktop_path}")
    except Exception as e:
        print(f"Note: Could not copy to desktop: {e}")
    
    print(f"\n🔍 Next Steps:")
    print(f"1. Open: {package_dir}")
    print(f"2. Read: WINDOWS_BUILD_GUIDE.md")
    print(f"3. Choose your preferred build method")
    print(f"4. Build the APK on Linux/macOS/WSL")
    
    return package_dir, zip_path

if __name__ == "__main__":
    print("Voice Recorder - Windows Build Helper")
    print("====================================")
    
    create_build_package()
    
    print("\nDone! 🎉")
    input("Press Enter to exit...")