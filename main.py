import calculator
import helpers.helper as helper

print("starting app")

x = input("Enter your name: ")
print("Hello " + x)

result = calculator.add(5, 3)
print("Result:", result)

data = helper.getData()
print("Data:", data)
