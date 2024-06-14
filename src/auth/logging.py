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

    # Replace all ASCII control characters (including newlines and tabs) with a space to make the message valid
    controlChars = dict.fromkeys(range(32), " ")
    message = message.translate(controlChars)

    data = { "timestamp": timestamp, "message": message, "username": "" if username is None else username, "suspicious": "YES" if suspicious else "" }

    # Convert to string and create a field to validate it
    logstring = json.dumps(data)

    print("LOG", logstring, data) ###########
    line = storage.encryption.encrypt(logstring) + "\n"
    open("./output/.logs", "a").write(line)
    