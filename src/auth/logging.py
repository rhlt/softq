# Logging functionality

import datetime
import auth.user

def log(message, suspicious = False):
    """Log a message"""

    username = auth.user.name()
    timestamp = str(datetime.datetime.now())
    
    line = (timestamp, message, username, suspicious)
    print("LOG:", line)