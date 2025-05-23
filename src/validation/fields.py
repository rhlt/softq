# Classes for input types and validation, which can be used to receive input and validate data

import validation.rules

class Text:
    """Handle a validated text (string) value"""

    def __init__(self, name, rules = None, allowEmpty = False):
        """Initialize values and set defaults"""
        self.name = str(name)
        self.errors = []
        self.displayValues = {}
        # Never allow values longer than 1000 characters or that contain control characters (ASCII < 32), including newline and NULL bytes
        self.rules = [validation.rules.notTooLong(self.name), validation.rules.noControlCharacters(self.name)]
        if not allowEmpty:
            # Add the rule that input must not be empty
            self.rules.append(validation.rules.notEmpty(self.name))
        if isinstance(rules, list):
            self.rules += map(lambda rule: rule(self.name), rules)
            

    def validate(self, value, allowNone = False, showError = True):
        """Validate the response and print/log any rules that are violated"""
        valid = True
        if value is None:
            return allowNone
        if not isinstance(value, str):
            return False
        for rule in self.rules:
            if not rule[1](value):
                if showError:
                    print(" :: " + rule[0])
                self.errors.append(rule[0])
                valid = False
        return valid


    def run(self, default = None):
        """Ask the user and validate the response (the response is guaranteed to be valid, or None)"""
        try:
            value = input("> " + self.name + (f" ({default})" if default else "") + (" <" if isinstance(self, EmptyValue) else ": "))
        except:
            # Most likly because user pressed Ctrl+C
            print() # newline
            return None
        if default is not None and value == "":
            # Return default value if empty
            return default
        if not self.validate(value, True):
            # Run again if validation fails
            return self.run(default)
        return value
    

    def display(self, value, maxLabelWidth = 22, maxValueWidth = None):
        """Display the label and value"""
        label = self.name + ":"
        if maxLabelWidth is not None:
            if len(label) > maxLabelWidth and maxLabelWidth > 5:
                label = label[:maxLabelWidth - 3] + "..."
            elif len(label) > maxLabelWidth:
                label = label[:maxLabelWidth] # No room for "..."
            else:
                label = label.ljust(maxLabelWidth)
        return "  " + label + " " + self.displayValue(value, maxValueWidth)


    def displayValue(self, value, maxWidth = None):
        """Display the value"""
        value = str(value)
        if value.upper() in self.displayValues:
            value = self.displayValues[value.upper()]
        if maxWidth is not None:
            if len(value) > maxWidth and maxWidth > 5:
                value = value[:maxWidth - 3] + "..."
            elif len(value) > maxWidth:
                value = value[:maxWidth] # No room for "..."
            else:
                value = value.ljust(maxWidth)
        return value


class Number(Text):
    """Handle a validated number (positive integer) value"""

    def __init__(self, name, rules = None, allowEmpty = False):
        """Initialize number input based on text input"""
        super().__init__(name, rules, allowEmpty)
        # Add rule that input must only contain digits
        self.rules.append(validation.rules.digitsOnly(self.name))


    def run(self, default = None):
        """Run the input and convert result to int (unless it is None or "", which is possible if allow empty is true)"""
        value = super().run(default)
        if value is None:
            return None
        if isinstance(value, str) and len(value) == 0:
            return ""
        return int(value)
    

    def validate(self, value, allowNone = False, showError = True):
        """Custom validation for number (positive integer) to ensure it is int and not str"""
        return super().validate(None if str is None else str(value), allowNone, showError)
    
    
class FromList(Text):
    """Handle a text (string) value that must be one of a specified list of values"""

    def __init__(self, name, allowedValues = [], displayValues = None):
        """Initialize input with custom rule to check if value is in the list of allowed values"""
        if not isinstance(allowedValues, list) or len(allowedValues) == 0:
            # If allowedValues is empty or invalid, make sure to allow value to be empty
            allowedValues = [""]
            displayValues = None
        super().__init__(name, [], "" in allowedValues)
        # Create custom rule for the list of allowed values
        self.rules.append(validation.rules.valueInList(allowedValues)(self.name))
        if displayValues is None:
            # Set displayValues equal to allowedValues (this will display upper and lowercase as intended even if the actual data differs)
            displayValues = allowedValues
        if len(allowedValues) == len(displayValues):
            self.displayValues = dict(zip([value.upper() for value in allowedValues], displayValues))


class ReadOnly(Text):
    """Handle a read-only value (does not allow user input but but allows for validation)"""

    def __init__(self, name, rules = None):
        """Initialize as always allowing empty (because it is read-only)"""
        super().__init__(name, rules, True)


    def run(self, default = None):
        """Value is not editable so no input should be asked"""
        return default
    

class Hidden(ReadOnly):
    "Handle a hidden field value (part of the model but cannot be seen or changed by the user)"

    def __init__(self, name, rules = None):
        """Initialize as always allowing empty (because it is not editable)"""
        super().__init__(name, rules)


    def run(self, default = None):
        """Value is not editable so no input should be asked"""
        return default
    
    
    def display(self, _):
        """Do not display a hidden value"""
        return
    

class EmptyValue(Text):
    """Handle an input that should not receive a response ('Press enter to continue')"""

    def __init__(self, name):
        """Initialize a Text input that must be empty"""
        super().__init__(name, [validation.rules.mustBeEmpty], True)