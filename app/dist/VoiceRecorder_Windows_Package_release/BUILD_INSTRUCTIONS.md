# Voice Recorder APK - Build Instructions

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
