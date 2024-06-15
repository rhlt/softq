# Validation rules used for checking data

from functools import reduce 
import re
import validation.datetime

# General/common rules
notTooLong = lambda name: (f"{name} should not be longer than 100 characters", lambda s: isinstance(s, str) and len(s) <= 10000) # Always applied
noControlCharacters = lambda name: (f"{name} should not contain ASCII control characters", lambda s: reduce(lambda valid, char: ord(char) >= 32 and valid, s, True)) # Always applied
notEmpty = lambda name: (f"{name} should not be empty", lambda s: isinstance(s, str) and len(s) > 0) # Applied unless "allowEmpty" is explicitly set to True 
mustBeEmpty = lambda name: (f"{name} must be empty", lambda s: isinstance(s, str) and len(s) == 0) # For "Press enter to continue" displays
digitsOnly = lambda name: (f"{name} should only contain the digits 0-9", lambda s: re.search(r"^\d*$", s))
valueInList = lambda values: lambda name: (f"{name} should be one of the following: " + ", ".join(filter(lambda v: len(v) > 0, values)), lambda s: s.upper() in map(lambda v: str(v).upper(), values))
duplicateValue = lambda value: lambda name: (f"Duplicate {name}: '{value}' already exists", lambda _: False) # This rule is dynamically added if the value was already found and therefore always returns False for "invalid"

# Username/Password rules
atLeastThisLong = lambda length: lambda name: (f"{name} should have at least {length} characters", lambda s: isinstance(s, str) and len(s) >= length)
noLongerThan = lambda length: lambda name: (f"{name} should have no more than {length} characters", lambda s: isinstance(s, str) and len(s) <= length)
startWithLetterOrUnderscore = lambda name: (f"{name} should start with a letter or underscore", lambda s: re.search(r"^[a-zA-Z_]", s))
validUsernameCharacters = lambda name: (f"{name} should contain only letters, numbers, underscores, apostrophes or periods", lambda s: re.search(r"^[a-zA-Z\d'.]*$", s))
containsLowercase = lambda name: (f"{name} should contain at least one lowercase letter", lambda s: re.search(r"[a-z]", s))
containsUppercase = lambda name: (f"{name} should contain at least one uppercase letter", lambda s: re.search(r"[A-Z]", s))
containsDigit = lambda name: (f"{name} should contain at least one digit", lambda s: re.search(r"\d", s))
containsSpecial = lambda name: (f"{name} should contain at least one special character", lambda s: re.search(r"[^A-Za-z\d]", s))

# Member ID rules
tenDigits = lambda name: (f"{name} should be ten digits", lambda s: re.search(r"^\d{10}$", s))
twoDigitYear = lambda name: (f"{name} should start with a two-digit year that is not in the future", lambda s: validation.datetime.validShortYear(s[:2]))
checksum = lambda name: (f"{name} should have a valid checksum", lambda s: str(reduce(lambda check, digit: (check + ord(digit) - 8) % 10, s[:9], 0)) == s[9:])

# Profile fields rules
date = lambda name: (f"{name} should be a valid date (YYYY-MM-DD)", validation.datetime.validDate)
age = lambda name: (f"{name} should be over 18", lambda s: re.search(r"^\d*$", s) and int(s) >= 18)
realisticAge = lambda name: (f"{name} should be a realistic number", lambda s: re.search(r"^\d*$", s) and int(s) <= 122) # Oldest person ever was 122
weight = lambda name: (f"{name} should be a realistic number", lambda s: re.search(r"^\d*$", s) and int(s) >= 30 and int(s) <= 600) # What would be realistic here?
homeNumber = lambda name: (f"{name} should be a valid home number (number + possible suffix)", lambda s: re.search(r"^\d+[\s\-]?[a-zA-Z\d]*$", s))
postcode = lambda name: (f"{name} should be a valid postcode (such as 1234AB)", lambda s: re.search(r"^\d{4}[a-zA-Z]{2}$", s)) 
email = lambda name: (f"{name} should be a valid e-mail address", lambda s: re.search(r"^([a-zA-Z\d][a-zA-Z\d+\-.]*[a-zA-Z\d]|[a-zA-Z\d])@([a-zA-Z\d][a-zA-Z\d\-.]*[a-zA-Z\d]|[a-zA-Z\d])\.[a-zA-Z\d]+$", s))
phone = lambda name: (f"{name} should be a valid eight-digit mobile phone number (excluding 06 or +31 6)", lambda s: re.search(r"^\d{8}$", s))