# Helper functions to generate and validate date/time values (since try/except doesn't work with lambdas)

from datetime import datetime


def date():
    """Return today's date as string"""
    return str(datetime.now().date())


def time():
    """Return the current time as string"""
    return str(datetime.now().time()).split('.')[0] # No fractions of seconds


def shortYear():
    """Return the current two-digit year (24 for 2024)"""
    return date()[2:4]


def validDate(date):
    """Check if a date is valid in the format YYYY-mm-dd"""
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validShortYear(yy):
    """Check if the two-digit year is valid and not in the future"""
    try:
        date = datetime.strptime(f"20{yy}-01-01", "%Y-%m-%d")
        return date <= datetime.today()
    except ValueError:
        return False