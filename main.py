import src.code1 as code1
import helper.helpers2 as helpers2

print("starting app")

x = input("Enter your name: ")
print(f"Hello {x}")

result = code1.add(5, 3)
print("Result:", result)

data = helpers2.getData()
print("Data:", data)
