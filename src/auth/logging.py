# Logging functionality

import datetime
import auth.user
import json
import storage.encryption

def log(message, suspicious = False):
    """Log a message"""

    if not isinstance(message, str) or len(message) == 0:
        return # Nothing to log

    username = auth.user.name()
    timestamp = str(datetime.datetime.now())

    if len(message) > 10000:
        # Restrict message length to prevent trouble when validating the log file contents
        message = message[:10000]
    
    data = { "timestamp": timestamp, "message": message, "username": "" if username is None else username, "suspicious": "YES" if suspicious else "" }
    print("LOG", data) ###########
    line = storage.encryption.encrypt(json.dumps(data)) + "\n"
    open("./output/.logs", "a").write(line)
    