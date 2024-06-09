import data.input
import data.rules

class Form:
    """Create a form (list of inputs) for the user to fill out"""

    def __init__(self):
        self.fields = {}

    def run(self):
        """Ask the user to fill out the form; the result is guaranteed to be a validated, completely filled model (with the possible exception of ReadOnly fields, which may have None value), or None)"""
        valid = True
        result = {}
        for field in self.fields:
            # Run all inputs
            value = self.fields[field].run()
            if value == None and not isinstance(self.fields[field], data.input.ReadOnly):
                valid = False
                break
            result[field] = value
        return result if valid else None
    
    def validate(self, model):
        """Validate a model (dict) to be valid for this form (also checks for any None values)"""
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
            if not self.fields[field].validate(model[field], False, False):
                # Model value not valid
                return False
        return True


class Login(Form):
    """Create a login form with username and password"""

    def __init__(self):
        """Define username and password fields"""
        
        self.fields = {
            # No complicated validation here (because hard-coded super admin does not match, and also this will be checked against the values in the database anyway)
            "username": data.input.Text("Username"),
            "password": data.input.Text("Password"),
        }


class ChangePassword(Form):
    """Change password form"""
    
    def __init__(self):
        """Define current and new password fields fields"""
    
        self.fields = {
            "currentPassword": data.input.Text("Current password"),
            "newPassword": data.input.Text("New password", [
                data.rules.atLeastThisLong(12),
                data.rules.noLongerThan(30),
                data.rules.containsLowercase,
                data.rules.containsUppercase,
                data.rules.containsDigit,
                data.rules.containsSpecial,
            ]),
        }
    



class User(Form):
    """Create a user form with username, password and profile information"""

    def __init__(self):
        """Define user profile fields"""
        
        self.fields = {
            "username": data.input.Text("Username", [
                data.rules.atLeastThisLong(8),
                data.rules.noLongerThan(10),
                data.rules.startWithLetterOrUnderscore,
                data.rules.validUsernameCharacters,
            ]),
            "password": data.input.Text("Password", [
                data.rules.atLeastThisLong(12),
                data.rules.noLongerThan(30),
                data.rules.containsLowercase,
                data.rules.containsUppercase,
                data.rules.containsDigit,
                data.rules.containsSpecial,
            ]),
            "admin": data.input.ReadOnly("Is admin?", [data.rules.valueInList([0, 1])])
        }


class Member(Form):
    """Create a form for member data"""

    def __init__(self):
        """Define member data fields"""
        
        self.fields = {
            "id": data.input.ReadOnly("ID", [data.rules.tenDigits, data.rules.twoDigitYear, data.rules.checksum]),
            "firstName": data.input.Text("First name"),
            "lastName": data.input.Text("Last name"),
            "age": data.input.Number("Age"),
            "gender": data.input.FromList("Gender", ["M", "F", "X"]),
            "weight": data.input.Number("Weight"),
            "street": data.input.Text("Street"),
            "no": data.input.Text("Number", [data.rules.homeNumber]),
            "zip": data.input.Text("ZIP (Postcode)", [data.rules.postcode]),
            "city": data.input.FromList("City", ["Amsterdam", "Rotterdam", "Den Haag", "Utrecht", "Eindhoven", "Groningen", "Leiden", "Delft", "Dordrecht", "Gouda"]),
            "email": data.input.Text("E-mail address", [data.rules.email]),
            "phone": data.input.Text("Mobile phone (+31 6)", [data.rules.phone]),
            "registrationDate": data.input.ReadOnly("Registration date", [data.rules.date])
        }