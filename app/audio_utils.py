#!/usr/bin/env python3
"""
Audio recording utilities
Cross-platform audio recording functionality
"""

import os
import time
import datetime
import threading
from kivy.utils import platform

# Try to import audio libraries
audio_lib = None
if platform == 'android':
    try:
        # Try PyAudio first
        import pyaudio
        audio_lib = 'pyaudio'
    except ImportError:
        try:
            # Fallback to plyer for Android
            from plyer import audio
            audio_lib = 'plyer'
        except ImportError:
            audio_lib = None
else:
    # Desktop - try multiple audio libraries
    try:
        import pyaudio
        audio_lib = 'pyaudio'
    except ImportError:
        try:
            import sounddevice as sd
            import soundfile as sf
            audio_lib = 'sounddevice'
        except ImportError:
            audio_lib = None


class AudioRecorder:
    """Cross-platform audio recorder"""
    
    def __init__(self):
        self.is_recording = False
        self.recording_thread = None
        self.audio_data = []
        
        # Audio settings
        self.sample_rate = 44100
        self.channels = 1
        self.chunk_size = 1024
        
        # Initialize based on available library
        if audio_lib == 'pyaudio':
            self.format = pyaudio.paInt16
            self.audio = pyaudio.PyAudio()
        elif audio_lib == 'sounddevice':
            self.format = 'int16'
        
    def start_recording(self, filepath, duration_seconds=None):
        """Start recording to the specified file"""
        if self.is_recording:
            return False
        
        self.is_recording = True
        self.audio_data = []
        
        self.recording_thread = threading.Thread(
            target=self._record_worker,
            args=(filepath, duration_seconds)
        )
        self.recording_thread.start()
        return True
    
    def stop_recording(self):
        """Stop the current recording"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=5.0)
    
    def _record_worker(self, filepath, duration_seconds):
        """Worker thread for recording audio"""
        if audio_lib == 'pyaudio':
            self._record_with_pyaudio(filepath, duration_seconds)
        elif audio_lib == 'sounddevice':
            self._record_with_sounddevice(filepath, duration_seconds)
        elif audio_lib == 'plyer':
            self._record_with_plyer(filepath, duration_seconds)
        else:
            # Fallback - create a dummy file for testing
            self._create_dummy_recording(filepath)
    
    def _record_with_pyaudio(self, filepath, duration_seconds):
        """Record using PyAudio"""
        try:
            import wave
            
            # Open audio stream
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Open wave file
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                
                start_time = time.time()
                
                while self.is_recording:
                    if duration_seconds and (time.time() - start_time) >= duration_seconds:
                        break
                    
                    try:
                        data = stream.read(self.chunk_size, exception_on_overflow=False)
                        wf.writeframes(data)
                    except Exception as e:
                        print(f"Error reading audio: {e}")
                        break
            
            # Clean up
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"PyAudio recording error: {e}")
        finally:
            self.is_recording = False
    
    def _record_with_sounddevice(self, filepath, duration_seconds):
        """Record using sounddevice"""
        try:
            import soundfile as sf
            
            # Calculate number of frames
            if duration_seconds:
                frames = int(duration_seconds * self.sample_rate)
            else:
                frames = self.sample_rate * 300  # 5 minutes max
            
            # Record audio
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.format
            )
            
            # Wait for recording to complete or stop signal
            start_time = time.time()
            while self.is_recording:
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break
                time.sleep(0.1)
            
            # Stop recording
            sd.stop()
            
            # Save to file
            sf.write(filepath, recording[:int((time.time() - start_time) * self.sample_rate)], self.sample_rate)
            
        except Exception as e:
            print(f"SoundDevice recording error: {e}")
        finally:
            self.is_recording = False
    
    def _record_with_plyer(self, filepath, duration_seconds):
        """Record using Plyer (mobile fallback)"""
        try:
            from plyer import audio
            
            # Start recording
            audio.start()
            
            start_time = time.time()
            while self.is_recording:
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break
                time.sleep(0.1)
            
            # Stop and save
            audio.stop()
            audio.file_path = filepath
            
        except Exception as e:
            print(f"Plyer recording error: {e}")
            self._create_dummy_recording(filepath)
        finally:
            self.is_recording = False
    
    def _create_dummy_recording(self, filepath):
        """Create a dummy audio file for testing when no audio library is available"""
        try:
            import wave
            import struct
            import math
            
            # Create a simple tone as a test
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                
                # Generate a 440Hz tone for 1 second
                duration = 1.0
                frames = int(duration * self.sample_rate)
                
                for i in range(frames):
                    sample = int(32767 * math.sin(2 * math.pi * 440 * i / self.sample_rate))
                    wf.writeframes(struct.pack('<h', sample))
            
            print(f"Created dummy recording: {filepath}")
            
        except Exception as e:
            print(f"Error creating dummy recording: {e}")
        finally:
            self.is_recording = False
    
    def cleanup(self):
        """Clean up audio resources"""
        if audio_lib == 'pyaudio' and hasattr(self, 'audio'):
            self.audio.terminate()


def get_recordings_directory():
    """Get the directory for storing recordings"""
    if platform == 'android':
        try:
            from android.storage import primary_external_storage_path
            recordings_dir = os.path.join(primary_external_storage_path(), 'VoiceRecordings')
        except ImportError:
            # Fallback for Android
            recordings_dir = '/sdcard/VoiceRecordings'
    else:
        # Desktop
        recordings_dir = os.path.join(os.path.expanduser('~'), 'VoiceRecordings')
    
    # Create directory if it doesn't exist
    os.makedirs(recordings_dir, exist_ok=True)
    
    return recordings_dir


def create_recording_filename():
    """Create a unique filename for a new recording"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"recording_{timestamp}.wav"


# Test function
if __name__ == '__main__':
    print(f"Audio library available: {audio_lib}")
    
    if audio_lib:
        recorder = AudioRecorder()
        filepath = os.path.join(get_recordings_directory(), create_recording_filename())
        
        print(f"Starting test recording to: {filepath}")
        recorder.start_recording(filepath, 3)  # 3 second test
        
        time.sleep(4)  # Wait for recording to finish
        
        recorder.cleanup()
        
        if os.path.exists(filepath):
            print(f"Recording created successfully: {os.path.getsize(filepath)} bytes")
        else:
            print("Recording failed")
    else:
        print("No audio library available for testing")