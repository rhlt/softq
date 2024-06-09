# Classes for input types and validation, which can be used to receive input and validate data

import data.rules

class Text:
    """Handle a validated text (string) value"""

    def __init__(self, name, rules = None, allow_empty = False):
        """Initialize values and set defaults"""
        self.name = str(name)
        self.errors = []
        # Never allow values longer than 100 characters or that contain control characters (ASCII < 32), including newline and NULL bytes
        self.rules = [data.rules.notTooLong(self.name), data.rules.noControlCharacters(self.name)]
        if not allow_empty:
            # Add the rule that input must not be empty
            self.rules.append(data.rules.notEmpty(self.name))
        if isinstance(rules, list):
            self.rules += map(lambda rule: rule(self.name), rules)
            
    def validate(self, value, allow_none = False, show_error = True):
        """Validate the response and print/log any rules that are violated"""
        valid = True
        if value is None:
            return allow_none
        if not isinstance(value, str):
            return False
        for rule in self.rules:
            if not rule[1](value):
                if show_error:
                    print(" :: " + rule[0])
                self.errors.append(rule[0])
                valid = False
        return valid

    def run(self):
        """Ask the user and validate the response (the response is guaranteed to be valid, or None)"""
        try:
            value = input("> " + self.name + (" <" if isinstance(self, EmptyValue) else ": "))
        except:
            # Most likly because user pressed Ctrl+C
            print() # newline
            return None
        if not self.validate(value, True):
            # Run again if validation fails
            return self.run()
        return value


class Number(Text):
    """Handle a validated number (positive integer) value"""

    def __init__(self, name, rules = None, allow_empty = False):
        """Initialize number input based on text input"""
        super().__init__(name, rules, allow_empty)
        # Add rule that input must only contain digits
        self.rules.append(data.rules.digitsOnly(self.name))

    def run(self):
        """Run the input and convert result to int (unless it is None or "", which is possible if allow empty is true)"""
        value = super().run()
        if value is None:
            return None
        if isinstance(value, str) and len(value) == 0:
            return ""
        return int(value)
    
    def validate(self, value, allow_none = False, show_error = True):
        """Custom validation for number (positive integer) to ensure it is int and not str"""
        return super().validate(None if str is None else str(value), allow_none, show_error)
    
    
class FromList(Text):
    """Handle a text (string) value that must be one of a specified list of values"""

    def __init__(self, name, allowed_values = []):
        """Initialize input with custom rule to check if value is in the list of allowed values"""
        if not isinstance(allowed_values, list) or len(allowed_values) == 0:
            # If allowed_values is empty or invalid, make sure to allow value to be empty
            allowed_values = [""]
        super().__init__(name, [], "" in allowed_values)
        # Create custom rule for the list of allowed values
        self.rules.append(data.rules.valueInList(allowed_values)(self.name))


class ReadOnly(Text):
    """Handle a read-only value (does not allow user input but but allows for validation)"""

    def __init__(self, name, rules = None):
        """Initialize as always allowing empty (because it is read-only)"""
        super().__init__(name, rules, True)

    def run(self):
        """Value is not editable so no input should be asked"""
        return None
    

class EmptyValue(Text):
    """Handle an input that should not receive a response ('Press enter to continue')"""

    def __init__(self, name):
        """Initialize a Text input that must be empty"""
        super().__init__(name, [data.rules.mustBeEmpty], True)