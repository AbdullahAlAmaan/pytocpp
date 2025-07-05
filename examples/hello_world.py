"""
Simple Hello World example for Py2CppAI.

This demonstrates basic Python code that will be transpiled to C++.
"""

def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

def main():
    """Main function demonstrating basic operations."""
    # Simple variable assignment
    message = greet("World")
    
    # Print the result
    print(message)
    
    # Basic arithmetic
    x = 10
    y = 20
    result = x + y
    print(f"Sum: {result}")
    
    # Conditional statement
    if result > 25:
        print("Result is greater than 25")
    else:
        print("Result is 25 or less")
    
    # Simple loop
    for i in range(3):
        print(f"Count: {i}")

if __name__ == "__main__":
    main() 