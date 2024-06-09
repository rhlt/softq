import data.forms

# TODO: interface (controllers), storage (database + file), logging, ...


# login = data.forms.Login()
# result = login.run()
# print(result)


user = data.forms.User()
result = user.run()
print(result)


# member = data.forms.Member()
# result = member.run()
# print(result)



# number = data.Number("Enter a number: ").run()
# print("Received number +1:", number + 1)

# city = data.FromList("Enter a city: ", ["Amsterdam", "Rotterdam", "Den Haag", "Utrecht", "Eindhoven", "Groningen", "Leiden", "Delft", "Dordrecht", "Gouda"]).run()
# print("Received city:", city)