# 📱 APK Installation Guide

## Once your APK is ready, follow these steps:

### Step 1: Download APK from GitHub
1. Go to: https://github.com/Etai89/voice-recorder-app/actions
2. Click on the completed build (green checkmark)
3. Download "voice-recorder-apk" artifact
4. Extract the ZIP file to get the .apk file

### Step 2: Enable Unknown Sources on Android
1. Go to **Settings** > **Security** (or **Privacy & Security**)
2. Enable **"Unknown Sources"** or **"Install unknown apps"**
3. Or enable it when prompted during installation

### Step 3: Install APK on Your Phone

#### Method A: Direct Transfer
1. Connect phone to computer via USB
2. Copy the .apk file to your phone's Downloads folder
3. On phone: Open **File Manager** → **Downloads**
4. Tap the .apk file → **Install**

#### Method B: Email/Cloud
1. Email the .apk file to yourself
2. Open email on your phone
3. Download and tap the .apk file
4. Follow installation prompts

#### Method C: ADB (Advanced)
```bash
adb install path/to/voice-recorder.apk
```

### Step 4: Grant Permissions
When you first open the app, it will ask for:
- 🎤 **Microphone** (required for recording)
- 💾 **Storage** (required to save files)
- ⏰ **Alarms** (required for scheduling)
- 📢 **Notifications** (to show recording status)

**IMPORTANT:** Grant ALL permissions for the app to work properly!

### Step 5: Test the App
1. Open the app
2. Set a recording time (1-2 minutes from now)
3. Set duration (1 minute for testing)
4. Tap "Schedule Recording"
5. Wait and check if it records!

## Expected File Locations:
- **APK file**: ~8-25 MB
- **Recordings saved to**: `/storage/emulated/0/VoiceRecordings/`
- **File format**: WAV audio files
- **File names**: `recording_YYYYMMDD_HHMMSS.wav`

## Troubleshooting:
- **Can't install**: Enable Unknown Sources
- **No permissions**: Go to Settings > Apps > Voice Recorder > Permissions
- **No recordings**: Check storage permissions and available space
- **App crashes**: Check Android version (needs 5.0+)