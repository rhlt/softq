# Logging functionality

import json
import authentication.user
import storage.encryption
import validation.datetime

def log(activity, details, suspicious = False):
    """Log a message"""

    if not isinstance(activity, str) or len(activity) == 0:
        return # Nothing to log
    
    if not isinstance(details, str) or len(details) == 0:
        details = "(no details available)"

    username = authentication.user.name()
    date = validation.datetime.date()
    time = validation.datetime.time()

    # Restrict message length to prevent trouble when validating and encrypting the log file contents
    activity = activity[:100]
    while len(activity.encode()) > 100:
        activity = activity[:-1] # Remove double-byte characters safely
    details = details[:100]
    while len(details.encode()) > 100:
        details = details[:-1] # Remove double-byte characters safely

    # Replace all ASCII control characters (including newlines and tabs) with a space to make the message valid
    controlChars = dict.fromkeys(range(32), " ")
    activity = activity.translate(controlChars)
    details = details.translate(controlChars)

    data = { "date": date, "time": time, "activity": activity, "details": details, "username": "" if username is None else username, "suspicious": "Y" if suspicious else "N" }

    # Convert to string and create a field to validate it
    logstring = json.dumps(data)
    # print("## LOG", logstring)

    line = storage.encryption.encrypt(logstring) + "\n"
    with open("./output/logs", "a") as file:
        file.write(line)
    if suspicious:
        with open("./output/logs-suspicious", "a") as file:
            file.write(line)
    