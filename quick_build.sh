#!/bin/bash
# Simple APK Builder Script
echo "🚀 Voice Recorder APK Builder"
echo "============================"

# Check if we're on a supported platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "❌ This script requires Linux/macOS or WSL"
    echo "Please run this in:"
    echo "- WSL (Windows Subsystem for Linux)"
    echo "- Linux virtual machine"
    echo "- macOS terminal"
    echo "- Online Linux environment"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv git openjdk-8-jdk
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum install -y python3 python3-pip git java-1.8.0-openjdk-devel
elif command -v brew &> /dev/null; then
    # macOS
    brew install python3 git openjdk@8
fi

# Install Python packages
pip3 install --user buildozer cython kivy[base] pyaudio plyer pyjnius

# Build APK
echo "🔨 Building APK..."
if [ ! -f "buildozer.spec" ]; then
    echo "❌ buildozer.spec not found!"
    echo "Make sure you're in the correct directory"
    exit 1
fi

buildozer android debug

if [ $? -eq 0 ]; then
    echo "✅ APK build successful!"
    echo "📱 APK file location:"
    find . -name "*.apk" -type f
    
    # Copy to dist folder
    mkdir -p app/dist
    cp bin/*.apk app/dist/ 2>/dev/null || echo "No APK files to copy"
    
    echo ""
    echo "🎉 Your APK is ready!"
    echo "📁 Check the bin/ or app/dist/ folder"
else
    echo "❌ Build failed!"
    echo "Check the error messages above"
fi