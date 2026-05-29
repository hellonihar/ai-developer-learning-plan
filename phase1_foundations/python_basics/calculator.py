import sys

def calculate(a, b, operator):
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        if b == 0:
            return "Error: Division by zero"
        return a / b
    else:
        return "Error: Unsupported operator"

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python calculator.py <a> <op> <b>")
        sys.exit(1)
    a = float(sys.argv[1])
    op = sys.argv[2]
    b = float(sys.argv[3])
    result = calculate(a, b, op)
    print(f"{a} {op} {b} = {result}")
