#!/usr/bin/env python3
"""
Background Recording Service
Handles scheduled audio recording in the background
"""

import os
import time
import datetime
import wave
import threading
from kivy.logger import Logger
from kivy.utils import platform

if platform == 'android':
    try:
        import pyaudio
        from jnius import autoclass, cast
        from android.storage import primary_external_storage_path
        
        # Android classes for notifications and services
        PythonService = autoclass('org.kivy.android.PythonService')
        Context = autoclass('android.content.Context')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        Intent = autoclass('android.content.Intent')
        PendingIntent = autoclass('android.app.PendingIntent')
        PowerManager = autoclass('android.os.PowerManager')
        R = autoclass('android.R')
    except ImportError as e:
        Logger.warning(f"RecordingService: Android imports failed: {e}")
        pyaudio = None
else:
    # For desktop testing
    try:
        import pyaudio
    except ImportError:
        Logger.warning("RecordingService: PyAudio not available for desktop testing")
        pyaudio = None


class RecordingService:
    def __init__(self):
        self.is_recording = False
        self.recording_thread = None
        self.audio_stream = None
        self.wave_file = None
        self.notification_id = 1
        self.wake_lock = None
        
        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16 if pyaudio else None
        self.channels = 1
        self.rate = 44100
        
        if platform == 'android':
            self.setup_android_service()
    
    def setup_android_service(self):
        """Setup Android-specific service components"""
        try:
            # Get service and context
            service = PythonService.mService
            if service:
                # Create notification channel
                self.create_notification_channel(service)
                
                # Acquire wake lock
                power_manager = service.getSystemService(Context.POWER_SERVICE)
                self.wake_lock = power_manager.newWakeLock(
                    PowerManager.PARTIAL_WAKE_LOCK,
                    "VoiceRecorder:RecordingWakeLock"
                )
                
                Logger.info("RecordingService: Android service setup complete")
            else:
                Logger.error("RecordingService: Could not get PythonService")
                
        except Exception as e:
            Logger.error(f"RecordingService: Error setting up Android service: {e}")
    
    def create_notification_channel(self, context):
        """Create notification channel for Android O+"""
        try:
            channel_id = "voice_recorder_channel"
            channel_name = "Voice Recorder"
            importance = NotificationManager.IMPORTANCE_LOW
            
            channel = NotificationChannel(channel_id, channel_name, importance)
            channel.setDescription("Voice recorder background service notifications")
            
            notification_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
            notification_manager.createNotificationChannel(channel)
            
            Logger.info("RecordingService: Notification channel created")
            
        except Exception as e:
            Logger.error(f"RecordingService: Error creating notification channel: {e}")
    
    def show_notification(self, title, message):
        """Show notification during recording"""
        if platform != 'android':
            return
            
        try:
            service = PythonService.mService
            if not service:
                return
            
            channel_id = "voice_recorder_channel"
            
            # Create notification builder
            builder = NotificationCompat.Builder(service, channel_id)
            builder.setContentTitle(title)
            builder.setContentText(message)
            builder.setSmallIcon(R.drawable.ic_media_play)  # Use built-in icon
            builder.setOngoing(True)  # Make it persistent
            builder.setPriority(NotificationCompat.PRIORITY_LOW)
            
            # Create intent to return to main app
            intent = Intent(service, autoclass('org.kivy.android.PythonActivity'))
            pending_intent = PendingIntent.getActivity(
                service, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT
            )
            builder.setContentIntent(pending_intent)
            
            # Show notification
            notification_manager = service.getSystemService(Context.NOTIFICATION_SERVICE)
            notification = builder.build()
            notification_manager.notify(self.notification_id, notification)
            
            Logger.info(f"RecordingService: Notification shown: {title}")
            
        except Exception as e:
            Logger.error(f"RecordingService: Error showing notification: {e}")
    
    def hide_notification(self):
        """Hide the recording notification"""
        if platform != 'android':
            return
            
        try:
            service = PythonService.mService
            if service:
                notification_manager = service.getSystemService(Context.NOTIFICATION_SERVICE)
                notification_manager.cancel(self.notification_id)
                
                Logger.info("RecordingService: Notification hidden")
                
        except Exception as e:
            Logger.error(f"RecordingService: Error hiding notification: {e}")
    
    def start_recording(self, duration_minutes):
        """Start recording for the specified duration"""
        if self.is_recording:
            Logger.warning("RecordingService: Recording already in progress")
            return
        
        try:
            # Acquire wake lock
            if self.wake_lock:
                self.wake_lock.acquire()
            
            # Create filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
            
            # Get recordings directory
            recordings_dir = self.get_recordings_directory()
            filepath = os.path.join(recordings_dir, filename)
            
            # Show notification
            self.show_notification(
                "Voice Recorder", 
                f"Recording for {duration_minutes} minutes..."
            )
            
            # Start recording in a separate thread
            self.is_recording = True
            self.recording_thread = threading.Thread(
                target=self._record_audio,
                args=(filepath, duration_minutes * 60)  # Convert to seconds
            )
            self.recording_thread.start()
            
            Logger.info(f"RecordingService: Started recording to {filepath}")
            
        except Exception as e:
            Logger.error(f"RecordingService: Error starting recording: {e}")
            self.stop_recording()
    
    def stop_recording(self):
        """Stop the current recording"""
        if not self.is_recording:
            return
        
        try:
            self.is_recording = False
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5.0)
            
            # Clean up audio resources
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            
            if self.wave_file:
                self.wave_file.close()
                self.wave_file = None
            
            # Hide notification
            self.hide_notification()
            
            # Release wake lock
            if self.wake_lock and self.wake_lock.isHeld():
                self.wake_lock.release()
            
            Logger.info("RecordingService: Recording stopped")
            
        except Exception as e:
            Logger.error(f"RecordingService: Error stopping recording: {e}")
    
    def _record_audio(self, filepath, duration_seconds):
        """Internal method to handle audio recording"""
        if not pyaudio:
            Logger.error("RecordingService: PyAudio not available")
            return
        
        try:
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Open audio stream
            self.audio_stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            # Open wave file for writing
            self.wave_file = wave.open(filepath, 'wb')
            self.wave_file.setnchannels(self.channels)
            self.wave_file.setsampwidth(audio.get_sample_size(self.format))
            self.wave_file.setframerate(self.rate)
            
            Logger.info(f"RecordingService: Recording audio to {filepath}")
            
            # Record audio
            frames = []
            start_time = time.time()
            
            while self.is_recording and (time.time() - start_time) < duration_seconds:
                try:
                    data = self.audio_stream.read(self.chunk, exception_on_overflow=False)
                    frames.append(data)
                    self.wave_file.writeframes(data)
                except Exception as e:
                    Logger.warning(f"RecordingService: Error reading audio data: {e}")
                    break
            
            # Finalize recording
            self.wave_file.close()
            self.wave_file = None
            
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
            
            audio.terminate()
            
            # Update notification
            if self.is_recording:  # Recording completed normally
                self.show_notification(
                    "Voice Recorder", 
                    f"Recording saved: {os.path.basename(filepath)}"
                )
                # Hide notification after a delay
                threading.Timer(5.0, self.hide_notification).start()
            
            Logger.info(f"RecordingService: Recording completed: {filepath}")
            
        except Exception as e:
            Logger.error(f"RecordingService: Error during recording: {e}")
        finally:
            self.is_recording = False
    
    def get_recordings_directory(self):
        """Get the directory for storing recordings"""
        if platform == 'android':
            recordings_dir = os.path.join(primary_external_storage_path(), 'VoiceRecordings')
        else:
            # For desktop testing
            recordings_dir = os.path.join(os.path.expanduser('~'), 'VoiceRecordings')
        
        if not os.path.exists(recordings_dir):
            os.makedirs(recordings_dir)
        
        return recordings_dir


# Global service instance
recording_service = None


def start_service(action, duration=5):
    """Entry point for the background service"""
    global recording_service
    
    Logger.info(f"RecordingService: Service started with action: {action}")
    
    if action == 'start_recording':
        if recording_service is None:
            recording_service = RecordingService()
        
        duration_minutes = int(duration)
        recording_service.start_recording(duration_minutes)
        
        # Keep service alive for the recording duration plus buffer
        time.sleep((duration_minutes * 60) + 30)
        
    elif action == 'stop_recording':
        if recording_service:
            recording_service.stop_recording()


# Service entry point for Android
if __name__ == '__main__':
    # This will be called when the service starts
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        start_service(action, duration)
    else:
        Logger.info("RecordingService: Service started without parameters")