def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero not allowed")
    return a / b


if __name__ == "__main__":
    print("Simple CLI Calculator")
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    op = input("Choose operation (+, -, *, /): ")

    if op == "+":
        print("Result:", add(a, b))
    elif op == "-":
        print("Result:", subtract(a, b))
    elif op == "*":
        print("Result:", multiply(a, b))
    elif op == "/":
        print("Result:", divide(a, b))
    else:
        print("Invalid operation")
