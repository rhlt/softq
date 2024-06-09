# Helper functions to validate date/time values

from datetime import datetime

def valid_short_year(yy):
    # Check if the two-digit year is valid and not in the future
    try:
        date = datetime.strptime(f"20{yy}-01-01", "%Y-%m-%d")
        return date <= datetime.today()
    except ValueError:
        return False

def valid_date(date):
    # Check if a date is valid in the format YYYY-mm-dd
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False