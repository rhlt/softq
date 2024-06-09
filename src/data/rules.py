# Validation rules used for checking input

from functools import reduce 
import re
import data.datetime

# General/common rules
notTooLong = lambda name: (f"{name} should not be longer than 100 characters", lambda s: isinstance(s, str) and len(s) <= 100) # Always applied
noControlCharacters = lambda name: (f"{name} should not contain ASCII control characters", lambda s: reduce(lambda valid, char: ord(char) >= 32 and valid, s, True)) # Always applied
notEmpty = lambda name: (f"{name} should not be empty", lambda s: len(s) > 0) # Applied unless "allow_empty" is explicitly set to True 
digitsOnly = lambda name: (f"{name} should only contain the digits 0-9", lambda s: re.search(r"^\d*$", s))
valueInList = lambda values: lambda name: (f"{name} should be one of the following: " + ", ".join(values), lambda s: s.upper() in map(lambda v: str(v).upper(), values))

# Username/Password rules
atLeastThisLong = lambda length: lambda name: (f"{name} should have at least {length} characters", lambda s: isinstance(s, str) and len(s) >= length)
noLongerThan = lambda length: lambda name: (f"{name} should have no more than {length} characters", lambda s: isinstance(s, str) and len(s) <= length)
startWithLetterOrUnderscore = lambda name: (f"{name} should start with a letter or underscore", lambda s: re.search(r"^[a-zA-Z_]", s))
validUsernameCharacters = lambda name: (f"{name} should contain only letters, numbers, underscores, apostrophes or periods", lambda s: re.search(r"^[a-zA-Z\d'.]*$", s))
containsLowercase = lambda name: (f"{name} should contain at least one lowercase letter", lambda s: re.search(r"[a-z]", s))
containsUppercase = lambda name: (f"{name} should contain at least one uppercase letter", lambda s: re.search(r"[A-Z]", s))
containsDigit = lambda name: (f"{name} should contain at least one digit", lambda s: re.search(r"\d", s))
containsSpecial = lambda name: (f"{name} should contain at least one special character", lambda s: re.search(r"[^A-Za-z\d]", s))

# User/Member profile rules
memberID = lambda name: (f"{name} should be a valid ID", lambda s: re.search(r"^\d{10}$", s) and data.datetime.valid_short_year(s[:2]) and str(reduce(lambda check, digit: (check + int(digit)) % 10, s[:9], 0)) == s[9:])
date = lambda name: (f"{name} should be a valid date (YYYY-MM-DD)", data.datetime.valid_date)
homeNumber = lambda name: (f"{name} should be a valid home number (number + possible suffix)", lambda s: re.search(r"^\d+\w*$", s))
postcode = lambda name: (f"{name} should be a valid postcode (such as 1234AB)", lambda s: re.search(r"^\d{4}[a-zA-Z]{2}$", s)) 
email = lambda name: (f"{name} should be a valid e-mail address", lambda s: re.search(r"^([a-zA-Z\d][a-zA-Z\d+\-.]*[a-zA-Z\d]|[a-zA-Z\d])@([a-zA-Z\d][a-zA-Z\d\-.]*[a-zA-Z\d]|[a-zA-Z\d])\.[a-zA-Z\d]+$", s))
phone = lambda name: (f"{name} should be a valid eight-digit mobile phone number (excluding 06 or +31 6)", lambda s: re.search(r"^\d{8}$", s))