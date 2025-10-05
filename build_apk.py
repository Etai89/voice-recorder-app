#!/usr/bin/env python3
"""
Voice Recorder APK Builder
This script creates an APK file for the Voice Recorder Scheduler app
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(step_num, text):
    """Print a formatted step"""
    print(f"\n[Step {step_num}] {text}")

def run_command(command, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=shell, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print_step(1, "Checking Prerequisites")
    
    # Check Python
    print(f"Python version: {sys.version}")
    
    # Check if we're on a supported platform
    if platform.system() not in ['Linux', 'Darwin', 'Windows']:
        print("Warning: Buildozer is primarily designed for Linux/macOS")
        print("For Windows, consider using WSL (Windows Subsystem for Linux)")
    
    # Check for Java (required for Android builds)
    java_check = run_command("java -version")
    if not java_check:
        print("WARNING: Java not found. Java 8 or higher is required for Android builds")
        print("Install Java from: https://adoptopenjdk.net/")
    
    # Check for Git
    git_check = run_command("git --version")
    if not git_check:
        print("WARNING: Git not found. Git is required for some dependencies")
    
    return True

def install_dependencies():
    """Install required Python packages"""
    print_step(2, "Installing Dependencies")
    
    dependencies = [
        'buildozer',
        'kivy[base]',
        'cython',
        'pyaudio',
        'plyer',
        'pyjnius'
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        success = run_command(f'"{sys.executable}" -m pip install {dep}')
        if not success:
            print(f"Warning: Failed to install {dep}")
    
    return True

def setup_android_environment():
    """Set up Android build environment"""
    print_step(3, "Setting up Android Environment")
    
    # Check if Android SDK/NDK are available
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home:
        print(f"Android SDK found at: {android_home}")
    else:
        print("Android SDK not found in environment variables")
        print("Buildozer will download Android SDK/NDK automatically")
    
    # Set environment variables for buildozer
    if platform.system() == 'Windows':
        # Windows-specific setup
        print("Setting up for Windows build environment...")
        print("WARNING: Buildozer has limited Windows support")
        print("Recommended alternatives:")
        print("1. Use WSL (Windows Subsystem for Linux)")
        print("2. Use a Linux virtual machine")
        print("3. Use GitHub Actions or cloud build service")
        print("4. Build on a Linux/macOS system")
        
        # Create dist folder structure
        dist_dir = Path("app/dist")
        dist_dir.mkdir(exist_ok=True)
        print(f"Created dist directory: {dist_dir.absolute()}")
    
    return True

def create_required_files():
    """Create any missing required files"""
    print_step(4, "Creating Required Files")
    
    app_dir = Path("app")
    services_dir = Path("services")
    
    # Ensure directories exist
    app_dir.mkdir(exist_ok=True)
    services_dir.mkdir(exist_ok=True)
    
    # Create __init__.py files if they don't exist
    init_files = [
        app_dir / "__init__.py",
        services_dir / "__init__.py"
    ]
    
    for init_file in init_files:
        if not init_file.exists():
            init_file.write_text("# Init file for Python package\n")
            print(f"Created: {init_file}")
    
    # Check if main.py exists
    main_file = app_dir / "main.py"
    if not main_file.exists():
        print(f"ERROR: {main_file} not found!")
        return False
    
    # Check if buildozer.spec exists
    spec_file = Path("buildozer.spec")
    if not spec_file.exists():
        print(f"ERROR: {spec_file} not found!")
        return False
    
    print("All required files are present")
    return True

def clean_build():
    """Clean previous build artifacts"""
    print_step(5, "Cleaning Previous Build")
    
    # Directories to clean
    clean_dirs = ['.buildozer', 'bin', '__pycache__']
    
    for dir_name in clean_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Removing {dir_path}")
            shutil.rmtree(dir_path, ignore_errors=True)
    
    return True

def create_windows_alternative(build_type):
    """Create Windows alternative for APK building"""
    print("\n📦 Creating Windows Build Package...")
    
    # Create dist directory
    dist_dir = Path("app/dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Create a deployment package
    package_name = f"VoiceRecorder_Windows_Package_{build_type}"
    package_dir = dist_dir / package_name
    package_dir.mkdir(exist_ok=True)
    
    # Copy all necessary files
    files_to_copy = [
        ("buildozer.spec", "buildozer.spec"),
        ("app/main.py", "app/main.py"),
        ("app/audio_utils.py", "app/audio_utils.py"),
        ("app/__init__.py", "app/__init__.py"),
        ("services/recording_service.py", "services/recording_service.py"),
        ("services/service.py", "services/service.py"),
        ("services/__init__.py", "services/__init__.py"),
        ("requirements.txt", "requirements.txt"),
        ("README.md", "README.md")
    ]
    
    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = package_dir / dst
        
        if src_path.exists():
            # Create destination directory if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"Copied: {src} -> {dst}")
    
    # Create build instructions for other platforms
    instructions = """# Voice Recorder APK - Build Instructions

## ⚠️ Windows Limitation
Buildozer (the APK build tool) does not work reliably on Windows.
This package contains all the source files needed to build the APK on a supported platform.

## 🔧 Build Options

### Option 1: Use WSL (Windows Subsystem for Linux)
1. Install WSL: https://docs.microsoft.com/en-us/windows/wsl/install
2. Install Ubuntu from Microsoft Store
3. Copy this package to WSL
4. Run: `python3 build_apk.py`

### Option 2: Use Linux Virtual Machine
1. Install VirtualBox or VMware
2. Create Ubuntu VM
3. Copy this package to VM
4. Install Python and dependencies
5. Run: `python3 build_apk.py`

### Option 3: Online Build Services
1. GitHub Actions (free for public repos)
2. GitLab CI/CD
3. Replit.com
4. Google Colab

### Option 4: Cloud Linux Server
1. Use AWS EC2, DigitalOcean, or similar
2. Copy files to server
3. Build remotely

## 📁 Package Contents
- `app/` - Main application code
- `services/` - Background recording services
- `buildozer.spec` - APK build configuration
- `requirements.txt` - Python dependencies
- `README.md` - Full documentation

## 🚀 Quick Build (on Linux/macOS)
```bash
# Install dependencies
pip install -r requirements.txt

# Build APK
python3 build_apk.py
```

## 📱 Expected Output
- APK file will be created in `bin/` folder
- File copied to `app/dist/` folder
- Size: ~15-25 MB (debug), ~8-15 MB (release)

## ℹ️ More Info
See README.md for complete build and installation instructions.
"""
    
    # Write instructions file
    instructions_file = package_dir / "BUILD_INSTRUCTIONS.md"
    instructions_file.write_text(instructions, encoding='utf-8')
    
    # Create a batch file for WSL users
    wsl_script = """@echo off
echo Starting APK build in WSL...
echo.
echo Make sure you have WSL installed and configured.
echo.
wsl python3 build_apk.py
pause
"""
    
    wsl_file = package_dir / "build_in_wsl.bat"
    wsl_file.write_text(wsl_script, encoding='utf-8')
    
    # Create ZIP package
    zip_file = dist_dir / f"{package_name}.zip"
    shutil.make_archive(str(zip_file).replace('.zip', ''), 'zip', package_dir)
    
    print(f"\n✅ Windows package created!")
    print(f"📁 Package location: {package_dir}")
    print(f"📦 ZIP file: {zip_file}")
    print(f"📋 Instructions: {instructions_file}")
    
    # Copy to desktop
    try:
        desktop_zip = Path.home() / "Desktop" / zip_file.name
        shutil.copy2(zip_file, desktop_zip)
        print(f"📥 ZIP copied to desktop: {desktop_zip}")
    except Exception as e:
        print(f"Could not copy to desktop: {e}")
    
    print("\n🔍 Next Steps:")
    print("1. Use WSL, Linux VM, or cloud service to build APK")
    print("2. Follow BUILD_INSTRUCTIONS.md in the package")
    print("3. Upload to online build service if needed")


def build_apk(build_type='debug'):
    """Build the APK file"""
    print_step(6, f"Building APK ({build_type})")
    
    # Check if we're on Windows
    if platform.system() == 'Windows':
        print("❌ Buildozer does not work reliably on Windows!")
        print("\n🔧 Windows Solutions:")
        print("1. Install WSL (Windows Subsystem for Linux)")
        print("2. Use a Linux virtual machine")
        print("3. Use online build services")
        print("4. Build on a Linux/macOS computer")
        
        # Create a Windows-compatible alternative
        print("\n🔄 Creating Windows alternative...")
        create_windows_alternative(build_type)
        return False
    
    # Build command for Linux/macOS
    if build_type == 'debug':
        command = "buildozer android debug"
    else:
        command = "buildozer android release"
    
    print(f"Starting build process...")
    print("This may take a while (10-30 minutes for first build)...")
    
    # Run buildozer
    success = run_command(command, shell=True)
    
    if success:
        print(f"\n✅ APK build completed successfully!")
        
        # Find the generated APK and copy to dist folder
        bin_dir = Path("bin")
        dist_dir = Path("app/dist")
        dist_dir.mkdir(exist_ok=True)
        
        if bin_dir.exists():
            apk_files = list(bin_dir.glob("*.apk"))
            if apk_files:
                apk_file = apk_files[0]
                apk_size = apk_file.stat().st_size / (1024 * 1024)  # Size in MB
                print(f"APK file: {apk_file}")
                print(f"APK size: {apk_size:.2f} MB")
                
                # Copy to app/dist folder
                dist_apk = dist_dir / apk_file.name
                shutil.copy2(apk_file, dist_apk)
                print(f"APK copied to: {dist_apk}")
                
                # Copy to desktop for easy access
                desktop_path = Path.home() / "Desktop" / apk_file.name
                try:
                    shutil.copy2(apk_file, desktop_path)
                    print(f"APK also copied to: {desktop_path}")
                except Exception as e:
                    print(f"Could not copy to desktop: {e}")
            else:
                print("No APK files found in bin directory")
        else:
            print("bin directory not found")
    else:
        print("❌ APK build failed!")
        print("\nCommon issues and solutions:")
        print("1. Make sure Java 8+ is installed")
        print("2. Check internet connection (downloads Android SDK/NDK)")
        print("3. On Windows, use WSL or Linux VM")
        print("4. Check buildozer logs for specific errors")
    
    return success

def show_installation_instructions():
    """Show instructions for installing the APK"""
    print_step(7, "Installation Instructions")
    
    print("""
To install the APK on your Android device:

1. ENABLE DEVELOPER OPTIONS:
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times
   - Developer options will be enabled

2. ENABLE USB DEBUGGING:
   - Go to Settings > Developer Options
   - Enable "USB Debugging"

3. ALLOW UNKNOWN SOURCES:
   - Go to Settings > Security
   - Enable "Unknown Sources" or "Install unknown apps"

4. INSTALL THE APK:
   Method 1 - ADB (if connected to computer):
   - Connect device via USB
   - Run: adb install path/to/your.apk
   
   Method 2 - File Transfer:
   - Copy APK to device storage
   - Use file manager to open and install
   
   Method 3 - Email/Cloud:
   - Email APK to yourself
   - Download and install on device

5. GRANT PERMISSIONS:
   - The app will request microphone and storage permissions
   - Grant all permissions for full functionality

IMPORTANT NOTES:
- This is a debug APK, not signed for Google Play Store
- Some devices may show security warnings - this is normal
- The app needs microphone permission to record audio
- Storage permission is needed to save recordings
""")

def main():
    """Main build process"""
    print_header("Voice Recorder APK Builder")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"Working directory: {project_dir.absolute()}")
    
    try:
        # Run build steps
        if not check_prerequisites():
            return False
        
        if not install_dependencies():
            return False
        
        if not setup_android_environment():
            return False
        
        if not create_required_files():
            return False
        
        if not clean_build():
            return False
        
        # Ask user for build type
        print("\nBuild type options:")
        print("1. Debug (faster, larger file, for testing)")
        print("2. Release (slower, smaller file, for distribution)")
        
        choice = input("Choose build type (1 or 2, default=1): ").strip()
        build_type = 'release' if choice == '2' else 'debug'
        
        if not build_apk(build_type):
            return False
        
        show_installation_instructions()
        
        print_header("Build Process Complete!")
        return True
        
    except KeyboardInterrupt:
        print("\n\nBuild process interrupted by user")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)