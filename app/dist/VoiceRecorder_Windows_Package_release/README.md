# Voice Recorder Scheduler

A Python-based Android app that records audio in the background at scheduled times, even when the app is not running.

## Features

- 📅 **Scheduled Recording**: Set a specific time for recording to start
- ⏱️ **Custom Duration**: Set how long the recording should last (in minutes)
- 🎵 **Background Operation**: Records even when the app is closed or phone is locked
- 💾 **Local Storage**: Saves recordings directly to your device
- 🔴 **Manual Control**: Start, stop, or cancel recordings manually
- 📱 **Android Notifications**: Shows recording status in notification bar
- 📂 **Recording Management**: View list of recent recordings

## How It Works

1. **Set Recording Time**: Choose the hour and minute when you want recording to start
2. **Set Duration**: Specify how many minutes the recording should last
3. **Schedule**: The app sets up an Android alarm to trigger recording at the specified time
4. **Background Recording**: At the scheduled time, a background service starts recording
5. **Auto-Save**: When recording is complete, the audio file is saved to your device storage
6. **Notification**: You receive notifications about recording status

## Building the APK

### Prerequisites

- **Python 3.7+**: Download from [python.org](https://python.org)
- **Java 8+**: Download from [adoptopenjdk.net](https://adoptopenjdk.net)
- **Git**: Download from [git-scm.com](https://git-scm.com)
- **Internet Connection**: Required for downloading Android SDK/NDK

### Quick Build (Windows)

1. Double-click `build_apk.bat`
2. Follow the prompts
3. Wait for the build to complete (10-30 minutes for first build)
4. The APK will be created in the `bin/` folder and copied to your Desktop

### Manual Build

1. Open Command Prompt or PowerShell in the project directory
2. Run: `python build_apk.py`
3. Choose debug or release build when prompted
4. Wait for the build process to complete

### Build Output

- **Debug APK**: Larger file size, faster build, for testing
- **Release APK**: Smaller file size, slower build, for distribution
- Location: `bin/` folder and copied to Desktop

## Installing the APK

### Enable Installation from Unknown Sources

1. Go to **Settings** > **Security** (or **Privacy**)
2. Enable **"Unknown Sources"** or **"Install unknown apps"**
3. Or enable it per-app when prompted during installation

### Installation Methods

#### Method 1: ADB (Developer Method)
```bash
adb install path/to/voicerecorder-debug.apk
```

#### Method 2: File Transfer
1. Copy the APK file to your Android device
2. Use a file manager app to navigate to the APK
3. Tap the APK file and follow installation prompts

#### Method 3: Email/Cloud
1. Email the APK to yourself or upload to cloud storage
2. Download on your Android device
3. Open the downloaded APK to install

### Required Permissions

The app will request these permissions:
- **🎤 Microphone**: To record audio
- **💾 Storage**: To save recordings to device
- **⏰ Alarms**: To schedule recordings
- **🔋 Wake Lock**: To record while device is sleeping
- **📢 Notifications**: To show recording status

**Important**: Grant ALL permissions for the app to work properly.

## Using the App

### Basic Usage

1. **Open the app**
2. **Set recording time** using the hour and minute spinners
3. **Set duration** in minutes (how long to record)
4. **Tap "Schedule Recording"**
5. **The app will show countdown until recording time**
6. **At the scheduled time, recording starts automatically**
7. **Recording stops automatically after the set duration**

### Manual Controls

- **Schedule Recording**: Set up a new scheduled recording
- **Cancel Recording**: Cancel a scheduled recording
- **Stop Current Recording**: Immediately stop any active recording

### Finding Your Recordings

Recordings are saved to: `/storage/emulated/0/VoiceRecordings/`

Files are named with timestamp: `recording_YYYYMMDD_HHMMSS.wav`

You can access recordings through:
- Any file manager app
- Gallery app (audio section)
- Music player apps

## Technical Details

### Framework
- **Kivy**: Cross-platform Python framework for mobile apps
- **Buildozer**: Tool for packaging Python apps as Android APK
- **PyAudio**: Audio recording library
- **Plyer**: Platform-specific features (notifications, storage)

### Architecture
- **Main App**: User interface and scheduling logic
- **Background Service**: Handles actual audio recording
- **Android Alarms**: Triggers recording at scheduled times
- **Notifications**: Shows recording status to user

### File Structure
```
VoiceRecorderApp/
├── app/
│   ├── main.py              # Main application
│   ├── audio_utils.py       # Audio recording utilities
│   └── __init__.py
├── services/
│   ├── recording_service.py # Background recording service
│   ├── service.py          # Service entry point
│   └── __init__.py
├── buildozer.spec          # Build configuration
├── build_apk.py           # Build script
├── build_apk.bat          # Windows build launcher
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Build Issues

**"Java not found"**
- Install Java 8 or higher
- Ensure `java` command is available in PATH

**"Build failed with gradle error"**
- Check internet connection
- Try running build again (sometimes downloads fail)

**"NDK not found"**
- Buildozer will download NDK automatically
- Ensure sufficient disk space (2-3 GB)

### App Issues

**"Recording not starting"**
- Check if all permissions are granted
- Ensure microphone permission is granted
- Check if device has sufficient storage space

**"No audio recorded"**
- Verify microphone permission
- Check if other apps are using microphone
- Try recording manually first

**"App crashes on startup"**
- This is a debug build, some crashes are normal
- Check Android version compatibility (requires Android 5.0+)

### Performance Notes

- First build takes 10-30 minutes (downloads Android SDK/NDK)
- Subsequent builds are much faster (2-5 minutes)
- APK size: ~15-25 MB (debug), ~8-15 MB (release)
- Recording quality: 44.1 kHz, 16-bit, mono WAV format

## Limitations

- **Android Only**: This build process creates Android APK files
- **Microphone Access**: Requires exclusive microphone access
- **Battery Usage**: Background recording uses battery power
- **Storage Space**: Audio files can be large (1 MB per minute)
- **No Cloud Sync**: Recordings are stored locally only

## Legal and Privacy

- **Local Storage Only**: No recordings are sent to external servers
- **User Control**: User has full control over when recordings occur
- **Privacy**: Be aware of privacy laws in your jurisdiction
- **Permissions**: App only requests necessary permissions

## Support

This is an open-source project. For issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure permissions are granted on the device

## License

This project is provided as-is for educational and personal use.