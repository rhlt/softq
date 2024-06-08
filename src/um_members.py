import interface.forms

login = interface.forms.Login()
result = login.run()

print(result)

print(login.validate(result))
print(login.validate({ "username": 1, "password": 2 }))
print(login.validate({ "username": "1" }))
print(login.validate({ "username": "1", "password": "2", "extra": "3" }))
print(login.validate({ "username": "1", "password": "2" }))

# username = input.Text("Enter your username: ").run()

# print("Received input:", username)


# number = input.Number("Enter a number: ").run()
# print("Received number +1:", number + 1)

# city = input.FromList("Enter a city: ", ["Amsterdam", "Rotterdam", "Den Haag", "Utrecht", "Eindhoven", "Groningen", "Leiden", "Delft", "Dordrecht", "Gouda"]).run()
# print("Received city:", city)