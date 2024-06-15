import validation.fields
import validation.rules

class Form:
    """Create a form (list of inputs) for the user to fill out"""

    def __init__(self):
        self.name = "Form"
        self.fields = {}


    def run(self, defaults = None):
        """Ask the user to fill out the form; the result is guaranteed to be a validated model, or None; assuming defaults are valid)"""
        valid = True
        self.errors = {}
        result = {}
        for field in self.fields:
            # Run all inputs
            default = defaults[field] if defaults is not None and field in defaults else None
            value = self.fields[field].run(default)
            if value == None and not isinstance(self.fields[field], validation.fields.ReadOnly):
                self.errors[field] = self.fields[field].errors
                valid = False
                break
            result[field] = value
        print() # newline
        return result if valid else None
    

    def validate(self, model):
        """Validate a model (dict) to be valid for this form (also checks for any None values)"""
        self.model = None
        self.errors = {}
        if not isinstance(model, dict):
            # Not a dictionary
            return False
        for field in self.fields:
            if field not in model:
                self.errors[field] = ["Field is missing"]
                # Model is missing field
                return False
        for field in model:
            if field not in self.fields:
                # Model contains unknown field
                self.errors[field] = ["Unknown field"]
                return False
            if not self.fields[field].validate(model[field], False, False):
                # Model value not valid
                self.errors[field] = self.fields[field].errors
                return False
        self.model = model
        return True
    

    def display(self, model):
        """Display all form fields and their values from a model (which must be validated and written to self.model)"""
        for field in self.fields:
            self.fields[field].display("(no data)" if field not in model else model[field])
        print() # newline


class Login(Form):
    """Login form with username and password"""

    def __init__(self):
        self.name = "Login"
        self.fields = {
            "username": validation.fields.Text("Username"),
            "password": validation.fields.Text("Password"),
        }


class ChangePassword(Form):
    """Change password form"""
    
    def __init__(self):
        self.name = "Change password"
        self.fields = {
            "currentPassword": validation.fields.Text("Current password"),
            "newPassword": validation.fields.Text("New password", [
                validation.rules.atLeastThisLong(12),
                validation.rules.noLongerThan(30),
                validation.rules.containsLowercase,
                validation.rules.containsUppercase,
                validation.rules.containsDigit,
                validation.rules.containsSpecial,
            ]),
        }


class User(Form):
    """Create a user form with username, password and profile information"""

    def __init__(self):
        self.name = "User"
        self.fields = {
            "username": validation.fields.Text("Username", [
                validation.rules.atLeastThisLong(8),
                validation.rules.noLongerThan(10),
                validation.rules.startWithLetterOrUnderscore,
                validation.rules.validUsernameCharacters,
            ]),
            "password": validation.fields.Hidden("Password"),
            "admin": validation.fields.ReadOnly("Admin", [validation.rules.valueInList(["Y", "N"])])
        }


class Member(Form):
    """Create a form for member data"""

    def __init__(self):
        self.name = "Member"
        self.fields = {
            "id": validation.fields.ReadOnly("ID", [validation.rules.tenDigits, validation.rules.twoDigitYear, validation.rules.checksum]),
            "firstName": validation.fields.Text("First name"),
            "lastName": validation.fields.Text("Last name"),
            "age": validation.fields.Number("Age"),
            "gender": validation.fields.FromList("Gender", ["M", "F", "X"]),
            "weight": validation.fields.Number("Weight"),
            "street": validation.fields.Text("Street"),
            "no": validation.fields.Text("Number", [validation.rules.homeNumber]),
            "zip": validation.fields.Text("ZIP (Postcode)", [validation.rules.postcode]),
            "city": validation.fields.FromList("City", ["Amsterdam", "Rotterdam", "Den Haag", "Utrecht", "Eindhoven", "Groningen", "Leiden", "Delft", "Dordrecht", "Gouda"]),
            "email": validation.fields.Text("E-mail address", [validation.rules.email]),
            "phone": validation.fields.Text("Mobile phone (+31 6)", [validation.rules.phone]),
            "registrationDate": validation.fields.ReadOnly("Registration date", [validation.rules.date])
        }


class Log(Form):
    """Log form with timestamp, username, message and whether it's suspicious"""

    def __init__(self):
        self.name = "Log"
        self.fields = {
            "date": validation.fields.Text("Date"),
            "time": validation.fields.Text("Time"),
            "username": validation.fields.Text("Username", None, True),
            "activity": validation.fields.Text("Message"),
            "details": validation.fields.Text("Details"),
            "suspicious": validation.fields.FromList("Suspicious", ["Y", "N"]),
        }