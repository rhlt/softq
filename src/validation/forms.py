import validation.fields
import validation.rules

class Form:
    """Create a form (list of inputs) for the user to fill out"""

    def __init__(self):
        self.name = "Form"
        self.fields = {}
        self.displayFields = None


    def run(self, defaults = None, skipFields = None):
        """Ask the user to fill out the form; the result is guaranteed to be a validated model, or None; assuming defaults and skipped fields are valid)"""
        valid = True
        self.errors = {}
        result = {}
        for field in self.fields:
            # Run all inputs except those in skipFields
            default = defaults[field] if defaults is not None and field in defaults else None
            if skipFields is not None and field in skipFields:
                # This field should be skipped
                result[field] = default
                continue
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
        if model is None:
            return
        for field in self.fields:
            row = self.fields[field].display("" if field not in model else model[field])
            if row is not None:
                print(row)
        print() # newline

    
    def getColumns(self):
        """Get list of columns and widths for table view"""
        # Default to showing all values with a max width of 15
        return self.columns if hasattr(self, "columns") else dict(zip([field for field in self.fields], [15 for _ in self.fields]))


    def generateHeader(self, firstCol = None):
        """Generate header for table display"""

        columns = self.getColumns()
        values = []
        separator = []
        if firstCol is not None:
            values = [firstCol]
            separator = [len(firstCol) * "-"]
        for field in columns:
            value = self.fields[field].name
            maxWidth = columns[field]
            if len(value) > maxWidth and maxWidth > 5:
                value = value[:maxWidth - 3] + "..."
            elif len(value) > maxWidth:
                value = value[:maxWidth] # No room for "..."
            else:
                value = value.ljust(maxWidth)
            values.append(value)
            separator.append("-" * len(value))
        return " | ".join(values) + "\n" + "-+-".join(separator)

    
    def row(self, model):
        """Get selected form fields in a table row"""

        columns = self.getColumns()
        values = []
        for field in columns:
            values.append(self.fields[field].displayValue("" if field not in model else model[field], columns[field]))
        return " | ".join(values)


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
            "firstName": validation.fields.Text("First name"),
            "lastName": validation.fields.Text("Last name"),
            "role": validation.fields.FromList("Role", ["Administrator", "Consultant"]),
            "registrationDate": validation.fields.ReadOnly("Registration date", [validation.rules.date])
        }
        self.columns = {
            "password": 30, ## TEST
            "firstName": 12,
            "lastName": 16,
            "role": 16,
            "registrationDate": 12,
        }


class Consultant(User):
    """Create a consultant user form with fixed role"""

    def __init__(self):
        super().__init__()
        self.name = "Consultant"
        self.fields["role"] = validation.fields.Hidden("Role", [validation.rules.valueInList("Consultant")])


class Administrator(User):
    """Create a administrator user form with fixed role"""

    def __init__(self):
        super().__init__()
        self.name = "Administrator"
        self.fields["role"] = validation.fields.Hidden("Role", [validation.rules.valueInList("Administrator")])


class Member(Form):
    """Create a form for member data"""

    def __init__(self):
        self.name = "Member"
        self.fields = {
            "id": validation.fields.Text("ID", [validation.rules.tenDigits, validation.rules.twoDigitYear, validation.rules.checksum]),
            "firstName": validation.fields.Text("First name"),
            "lastName": validation.fields.Text("Last name"),
            "age": validation.fields.Number("Age", [validation.rules.age, validation.rules.realisticAge]),
            "gender": validation.fields.FromList("Gender", ["M", "F", "X"]),
            "weight": validation.fields.Number("Weight", [validation.rules.weight]),
            "street": validation.fields.Text("Street"),
            "no": validation.fields.Text("Number", [validation.rules.homeNumber]),
            "zip": validation.fields.Text("ZIP (Postcode)", [validation.rules.postcode]),
            "city": validation.fields.FromList("City", ["Amsterdam", "Rotterdam", "Den Haag", "Utrecht", "Eindhoven", "Groningen", "Leiden", "Delft", "Dordrecht", "Gouda"]),
            "email": validation.fields.Text("E-mail address", [validation.rules.email]),
            "phone": validation.fields.Text("Mobile phone (+31 6)", [validation.rules.phone]),
            "registrationDate": validation.fields.ReadOnly("Registration date", [validation.rules.date])
        }
        self.columns = {
            "firstName": 12,
            "lastName": 16,
            "gender": 6,
            "street": 20,
            "zip": 6,
            "city": 10,
            "registrationDate": 12,
        }


class Log(Form):
    """Log form with timestamp, username, message and whether it's suspicious"""

    def __init__(self):
        self.name = "Log"
        self.fields = {
            "date": validation.fields.Text("Date"),
            "time": validation.fields.Text("Time"),
            "username": validation.fields.Text("Username", None, True),
            "activity": validation.fields.Text("Activity"),
            "details": validation.fields.Text("Details"),
            "suspicious": validation.fields.FromList("Suspicious", ["Y", "N"], ["YES", "no"]),
        }
        self.columns = {
            "date": 12,
            "time": 10,
            "username": 15,
            "activity": 30,
            "suspicious": 10,
        }