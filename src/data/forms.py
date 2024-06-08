import data.input as input

class Form:
    """Create a form (list of inputs) for the user to fill out"""

    def __init__(self):
        self.fields = {}

    def run(self):
        """Ask the user to fill out the form (the result is guaranteed to be a validated model, or None)"""
        valid = True
        result = {}
        for field in self.fields:
            # Run all inputs
            value = self.fields[field].run()
            if value == None:
                valid = False
                break
            result[field] = value
        return result if valid else None
    
    def validate(self, model):
        """Validate a model (dict) to be valid for this form"""
        if not isinstance(model, dict):
            # Not a dictionary
            return False
        for field in self.fields:
            if field not in model:
                # Model is missing field
                return False
        for field in model:
            if field not in self.fields:
                # Model contains unknown field
                return False
            if not self.fields[field].validate(model[field], False):
                # Model value not valid
                return False
        return True


class Login(Form):
    """Create a login form asking for username and password"""

    def __init__(self):
        """Define username and password fields"""
        
        super().__init__()
        self.fields = {
            "username": input.Text("Enter your username: "),
            "password": input.Text("Enter your password: "),
        }