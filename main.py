#!/usr/bin/env python3
"""
Simple Voice Recorder App - Minimal version for Android
"""

import os
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
from kivy.logger import Logger

# Try to import Android-specific modules
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        from plyer import storagepath
        android_available = True
        
        # Request basic permissions
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ])
    except ImportError:
        android_available = False
        Logger.warning("Android modules not available")
else:
    android_available = False


class SimpleVoiceRecorderApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('recording_settings.json')
        self.is_recording = False
        
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='Simple Voice Recorder',
            size_hint_y=None,
            height=50,
            font_size=24
        )
        main_layout.add_widget(title)
        
        # Time input section
        time_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        time_layout.add_widget(Label(text='Recording Time:', size_hint_x=0.4))
        
        # Hour spinner
        self.hour_spinner = Spinner(
            text='12',
            values=[f'{i:02d}' for i in range(24)],
            size_hint_x=0.2
        )
        time_layout.add_widget(self.hour_spinner)
        
        time_layout.add_widget(Label(text=':', size_hint_x=0.1))
        
        # Minute spinner
        self.minute_spinner = Spinner(
            text='00',
            values=[f'{i:02d}' for i in range(60)],
            size_hint_x=0.2
        )
        time_layout.add_widget(self.minute_spinner)
        
        main_layout.add_widget(time_layout)
        
        # Duration input
        duration_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        duration_layout.add_widget(Label(text='Duration (minutes):', size_hint_x=0.6))
        self.duration_input = TextInput(
            text='5',
            multiline=False,
            input_filter='int',
            size_hint_x=0.4
        )
        duration_layout.add_widget(self.duration_input)
        main_layout.add_widget(duration_layout)
        
        # Status label
        self.status_label = Label(
            text='Simple Voice Recorder Ready',
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.status_label)
        
        # Control buttons
        button_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=200, spacing=10)
        
        self.record_btn = Button(text='Start Recording Test', height=60, size_hint_y=None)
        self.record_btn.bind(on_press=self.test_recording)
        button_layout.add_widget(self.record_btn)
        
        self.schedule_btn = Button(text='Schedule Recording (Placeholder)', height=60, size_hint_y=None)
        self.schedule_btn.bind(on_press=self.schedule_recording)
        button_layout.add_widget(self.schedule_btn)
        
        self.info_btn = Button(text='Show App Info', height=60, size_hint_y=None)
        self.info_btn.bind(on_press=self.show_info)
        button_layout.add_widget(self.info_btn)
        
        main_layout.add_widget(button_layout)
        
        # Info display
        self.info_label = Label(
            text='This is a simplified version of the Voice Recorder app.\nBasic functionality for testing APK build.',
            text_size=(None, None),
            halign='center',
            valign='top'
        )
        main_layout.add_widget(self.info_label)
        
        return main_layout
    
    def test_recording(self, instance):
        """Test basic recording functionality"""
        if not self.is_recording:
            self.is_recording = True
            self.record_btn.text = 'Stop Recording'
            self.status_label.text = 'Recording... (Test Mode)'
            
            # Simulate recording for 3 seconds
            Clock.schedule_once(self.stop_test_recording, 3.0)
            
            # Create a test file
            self.create_test_recording()
        else:
            self.stop_test_recording()
    
    def stop_test_recording(self, dt=None):
        """Stop test recording"""
        self.is_recording = False
        self.record_btn.text = 'Start Recording Test'
        self.status_label.text = 'Test recording completed!'
    
    def create_test_recording(self):
        """Create a test recording file"""
        try:
            recordings_dir = self.get_recordings_directory()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            test_file = os.path.join(recordings_dir, f"test_recording_{timestamp}.txt")
            
            with open(test_file, 'w') as f:
                f.write(f"Test recording created at {datetime.datetime.now()}\n")
                f.write("This is a placeholder for audio recording functionality.\n")
                f.write("Platform: " + platform + "\n")
                f.write("Android available: " + str(android_available) + "\n")
            
            self.status_label.text = f'Test file created: {os.path.basename(test_file)}'
            
        except Exception as e:
            self.status_label.text = f'Error creating test file: {e}'
    
    def schedule_recording(self, instance):
        """Placeholder for scheduling functionality"""
        hour = self.hour_spinner.text
        minute = self.minute_spinner.text
        duration = self.duration_input.text
        
        self.status_label.text = f'Would schedule recording at {hour}:{minute} for {duration} minutes'
        
        # Save settings
        self.store.put('recording', 
                      hour=int(hour), 
                      minute=int(minute), 
                      duration=int(duration),
                      scheduled=True)
    
    def show_info(self, instance):
        """Show app information"""
        info_text = f"""Simple Voice Recorder v1.0
Platform: {platform}
Android modules: {'Available' if android_available else 'Not Available'}
Storage directory: {self.get_recordings_directory()}

This is a test build of the Voice Recorder app.
Use the buttons above to test basic functionality.
"""
        self.info_label.text = info_text
    
    def get_recordings_directory(self):
        """Get the directory for storing recordings"""
        if platform == 'android' and android_available:
            try:
                # Try to use Android external storage
                from plyer import storagepath
                external_storage = storagepath.get_external_storage_dir()
                recordings_dir = os.path.join(external_storage, 'VoiceRecordings')
            except:
                # Fallback to app directory
                recordings_dir = os.path.join(App.get_running_app().user_data_dir, 'VoiceRecordings')
        else:
            # Desktop or fallback
            recordings_dir = os.path.join(os.path.expanduser('~'), 'VoiceRecordings')
        
        # Create directory if it doesn't exist
        try:
            os.makedirs(recordings_dir, exist_ok=True)
        except:
            # If we can't create in external storage, use app data dir
            recordings_dir = os.path.join(App.get_running_app().user_data_dir, 'VoiceRecordings')
            os.makedirs(recordings_dir, exist_ok=True)
        
        return recordings_dir


if __name__ == '__main__':
    SimpleVoiceRecorderApp().run()