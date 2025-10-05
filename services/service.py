#!/usr/bin/env python3
"""
Service starter for Android background recording
This file is executed when the Android service starts
"""

import os
import sys

# Add the app directory to the Python path
sys.path.append('/android_asset/app')
sys.path.append('/android_asset/services')

# Import the recording service
from recording_service import start_service

if __name__ == '__main__':
    # Get parameters from Android intent
    action = os.environ.get('PYTHON_SERVICE_ARGUMENT', 'start_recording')
    duration = int(os.environ.get('RECORDING_DURATION', '5'))
    
    # Start the service
    start_service(action, duration)