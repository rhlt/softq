from functools import reduce 
import re

class Text:
    """Show input to receive a validated text (string) value"""


    def __init__(self, question = "", rules = None):
        """Initialize values and set defaults"""
        self.question = str(question) # force string 
        self.rules = {
            # Input will only be accepted if all rules return True
            # By default, do not allow whitespace or control characters (ASCII < 32)
            "Input should not contain ASCII control characters": lambda str: reduce(lambda valid, char: ord(char) >= 32 and valid, str, True)
        }
        if isinstance(rules, dict):
            for rule in rules:
                if rule in self.rules:
                    continue
                self.rules[rule] = rules[rule]
            
    def validate(self, value):
        """Validate inputted value and print any rules that are violated"""
        valid = True
        if value is None:
            return True
        if not isinstance(value, str):
            return False
        for rule in self.rules:
            if not self.rules[rule](value):
                print(":: " + rule)
                valid = False
        return valid

    def run(self):
        """Run the input: ask the user and validate the response (the response is guaranteed to be valid, or None)"""
        try:
            value = input("> " + self.question)
        except:
            # Most likly because user pressed Ctrl+C
            print() # newline
            return None
        if not self.validate(value):
            # Try again if validation fails
            return self.run()
        return value


class Number(Text):
    """Show input to receive a validated number (positive integer) value"""

    def __init__(self, question = "", rules = None, retry = True, allow_empty = False):
        """Initialize number input based on text input"""
        if not isinstance(rules, dict):
            rules = {}
        if not allow_empty:
            # Add the rule that input must not be empty
            rules["Input should not be empty"] = lambda str: len(str) > 0
        # Add rule that input must only contain digits
        rules["Input should only contain the digits 0-9"] = lambda str: re.match(r"^\d*$", str)
        super().__init__(question, rules, retry)

    def run(self):
        """Run the input and convert result to int (unless it is None or "", which is possible if retry is false or allow empty is true)"""
        value = super().run()
        if value is None:
            return None
        if isinstance(value, str) and len(value) == 0:
            return ""
        return int(value)
    
    
class FromList(Text):
    """Show input to receive a text (string) value that must be one of a specified set of values"""

    def __init__(self, question = "", allowed_values = [], allow_empty = False, retry = True):
        if not isinstance(allowed_values, list) or len(allowed_values) == 0:
            # If allowed_values is invalid, make sure to allow value to be empty
            allowed_values = []
            allowed_values_as_string = "(empty value)"
            allow_empty = True
        else:
            allowed_values_as_string = ", ".join(allowed_values)
            if allow_empty:
                allowed_values_as_string += ", (empty value)"
        
        rules = { "Input should be one of the following: " + allowed_values_as_string: lambda str: (str == "" and allow_empty) or str in allowed_values }
        super().__init__(question, rules, retry)