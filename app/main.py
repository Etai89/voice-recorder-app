#!/usr/bin/env python3
"""
Voice Recorder App - Main Application
A background voice recording app that records audio at scheduled times
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

if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        from jnius import autoclass, cast
        from android import activity
        from android.runnable import run_on_ui_thread
        
        # Android classes
        PythonService = autoclass('org.kivy.android.PythonService')
        Context = autoclass('android.content.Context')
        Intent = autoclass('android.content.Intent')
        PendingIntent = autoclass('android.app.PendingIntent')
        AlarmManager = autoclass('android.app.AlarmManager')
        System = autoclass('java.lang.System')
        
        # Request permissions
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WAKE_LOCK
        ])
    except ImportError as e:
        Logger.warning(f"VoiceRecorder: Android imports failed: {e}")


class VoiceRecorderApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('recording_settings.json')
        self.is_recording = False
        
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='Voice Recorder Scheduler',
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
            text='No recording scheduled',
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.status_label)
        
        # Control buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        
        self.schedule_btn = Button(text='Schedule Recording')
        self.schedule_btn.bind(on_press=self.schedule_recording)
        button_layout.add_widget(self.schedule_btn)
        
        self.cancel_btn = Button(text='Cancel Recording')
        self.cancel_btn.bind(on_press=self.cancel_recording)
        button_layout.add_widget(self.cancel_btn)
        
        self.stop_btn = Button(text='Stop Current Recording')
        self.stop_btn.bind(on_press=self.stop_recording)
        button_layout.add_widget(self.stop_btn)
        
        main_layout.add_widget(button_layout)
        
        # Recordings list
        recordings_label = Label(
            text='Recent Recordings:',
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(recordings_label)
        
        self.recordings_list = Label(
            text='No recordings yet',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        main_layout.add_widget(self.recordings_list)
        
        # Load saved settings
        self.load_settings()
        
        # Update status periodically
        Clock.schedule_interval(self.update_status, 1.0)
        
        return main_layout
    
    def schedule_recording(self, instance):
        """Schedule a recording for the specified time"""
        try:
            hour = int(self.hour_spinner.text)
            minute = int(self.minute_spinner.text)
            duration = int(self.duration_input.text)
            
            if duration <= 0:
                self.status_label.text = 'Error: Duration must be positive'
                return
            
            # Calculate next occurrence of the specified time
            now = datetime.datetime.now()
            scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If the time has passed today, schedule for tomorrow
            if scheduled_time <= now:
                scheduled_time += datetime.timedelta(days=1)
            
            # Save settings
            self.store.put('recording', 
                          hour=hour, 
                          minute=minute, 
                          duration=duration,
                          scheduled_timestamp=scheduled_time.timestamp(),
                          is_scheduled=True)
            
            if platform == 'android':
                self.schedule_android_alarm(scheduled_time, duration)
            
            self.status_label.text = f'Recording scheduled for {scheduled_time.strftime("%Y-%m-%d %H:%M")}'
            self.schedule_btn.text = 'Reschedule Recording'
            
        except ValueError:
            self.status_label.text = 'Error: Please enter valid numbers'
    
    def cancel_recording(self, instance):
        """Cancel the scheduled recording"""
        self.store.put('recording', is_scheduled=False)
        
        if platform == 'android':
            self.cancel_android_alarm()
        
        self.status_label.text = 'Recording cancelled'
        self.schedule_btn.text = 'Schedule Recording'
    
    def stop_recording(self, instance):
        """Stop any current recording"""
        if platform == 'android':
            self.stop_android_service()
        
        self.status_label.text = 'Recording stopped'
        self.is_recording = False
    
    def schedule_android_alarm(self, scheduled_time, duration):
        """Schedule Android alarm for recording"""
        if platform != 'android':
            return
            
        try:
            # Get Android context and alarm manager
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            alarm_manager = context.getSystemService(Context.ALARM_SERVICE)
            
            # Create intent for the recording service
            intent = Intent(context, PythonService)
            intent.putExtra('action', 'start_recording')
            intent.putExtra('duration', duration)
            
            # Create pending intent
            pending_intent = PendingIntent.getService(
                context, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT
            )
            
            # Schedule alarm
            alarm_time = int(scheduled_time.timestamp() * 1000)  # Convert to milliseconds
            alarm_manager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                alarm_time,
                pending_intent
            )
            
            Logger.info(f"VoiceRecorder: Alarm scheduled for {scheduled_time}")
            
        except Exception as e:
            Logger.error(f"VoiceRecorder: Error scheduling alarm: {e}")
            self.status_label.text = f'Error scheduling: {e}'
    
    def cancel_android_alarm(self):
        """Cancel the Android alarm"""
        if platform != 'android':
            return
            
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            alarm_manager = context.getSystemService(Context.ALARM_SERVICE)
            
            intent = Intent(context, PythonService)
            pending_intent = PendingIntent.getService(
                context, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT
            )
            
            alarm_manager.cancel(pending_intent)
            Logger.info("VoiceRecorder: Alarm cancelled")
            
        except Exception as e:
            Logger.error(f"VoiceRecorder: Error cancelling alarm: {e}")
    
    def stop_android_service(self):
        """Stop the Android recording service"""
        if platform != 'android':
            return
            
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            
            intent = Intent(context, PythonService)
            intent.putExtra('action', 'stop_recording')
            context.startService(intent)
            
            Logger.info("VoiceRecorder: Stop signal sent to service")
            
        except Exception as e:
            Logger.error(f"VoiceRecorder: Error stopping service: {e}")
    
    def load_settings(self):
        """Load saved settings"""
        if self.store.exists('recording'):
            settings = self.store.get('recording')
            if 'hour' in settings:
                self.hour_spinner.text = f"{settings['hour']:02d}"
            if 'minute' in settings:
                self.minute_spinner.text = f"{settings['minute']:02d}"
            if 'duration' in settings:
                self.duration_input.text = str(settings['duration'])
    
    def update_status(self, dt):
        """Update status periodically"""
        if self.store.exists('recording'):
            settings = self.store.get('recording')
            if settings.get('is_scheduled', False):
                scheduled_timestamp = settings.get('scheduled_timestamp', 0)
                scheduled_time = datetime.datetime.fromtimestamp(scheduled_timestamp)
                now = datetime.datetime.now()
                
                if now < scheduled_time:
                    time_left = scheduled_time - now
                    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    self.status_label.text = f'Recording in {hours:02d}:{minutes:02d}:{seconds:02d}'
                else:
                    self.status_label.text = 'Recording should be active'
        
        # Update recordings list
        self.update_recordings_list()
    
    def update_recordings_list(self):
        """Update the list of recent recordings"""
        recordings_dir = self.get_recordings_directory()
        if os.path.exists(recordings_dir):
            recordings = []
            for file in os.listdir(recordings_dir):
                if file.endswith('.wav'):
                    file_path = os.path.join(recordings_dir, file)
                    mtime = os.path.getmtime(file_path)
                    recordings.append((file, datetime.datetime.fromtimestamp(mtime)))
            
            recordings.sort(key=lambda x: x[1], reverse=True)
            
            if recordings:
                text = '\n'.join([f'{name} - {time.strftime("%Y-%m-%d %H:%M")}' 
                                for name, time in recordings[:5]])
                self.recordings_list.text = text
            else:
                self.recordings_list.text = 'No recordings yet'
        else:
            self.recordings_list.text = 'No recordings directory found'
    
    def get_recordings_directory(self):
        """Get the directory for storing recordings"""
        if platform == 'android':
            from android.storage import primary_external_storage_path
            recordings_dir = os.path.join(primary_external_storage_path(), 'VoiceRecordings')
        else:
            # For desktop testing
            recordings_dir = os.path.join(os.path.expanduser('~'), 'VoiceRecordings')
        
        if not os.path.exists(recordings_dir):
            os.makedirs(recordings_dir)
        
        return recordings_dir


if __name__ == '__main__':
    VoiceRecorderApp().run()