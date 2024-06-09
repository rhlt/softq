import data.forms
import data.input
import data.rules

# TODO: interface (controllers), storage (database + file), logging, ...


# login = data.forms.Login()
# result = login.run()
# print(result)


# user = data.forms.User()
# result = user.run()
# print(result)


# member = data.forms.Member()
# result = member.run()
# print(result)

data.input.Text("ID", [data.rules.tenDigits, data.rules.twoDigitYear, data.rules.checksum]).run()
data.input.Text("Date", [data.rules.date]).run()

# number = data.input.Number("Enter a number: ").run()
# print("Received number +1:", number + 1)

# city = data.input.FromList("Enter a city: ", ["Amsterdam", "Rotterdam", "Den Haag", "Utrecht", "Eindhoven", "Groningen", "Leiden", "Delft", "Dordrecht", "Gouda"]).run()
# print("Received city:", city)