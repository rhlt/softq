# Logging functionality

import datetime
import authorization.user

def log(message, suspicious = False):
    """Log a message"""

    username = authorization.user.name()
    if username and not authorization.user.logged_in():
        username += " (unauthorized)"
    print("LOG", datetime.datetime.now(), message, username, suspicious)