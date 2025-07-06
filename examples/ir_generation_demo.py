"""
Demo file for testing IR generation functionality.

This file contains various Python constructs to test IR generation:
- Global variables
- Function definitions
- Control flow (if/else, loops)
- Expressions and operations
- Return statements
"""

# Global variables
x = 42
y = 3.14
message = "Hello, IR!"

def add_numbers(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b

def calculate_factorial(n: int) -> int:
    """Calculate factorial using iteration."""
    if n <= 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result = result * i
    
    return result

def find_max(numbers: list) -> int:
    """Find the maximum value in a list."""
    if not numbers:
        return 0
    
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    
    return max_val

def process_data(data: dict) -> str:
    """Process a dictionary and return a string representation."""
    result = ""
    for key, value in data.items():
        result = result + str(key) + ": " + str(value) + "\n"
    return result

# Test expressions
sum_result = add_numbers(10, 20)
factorial_5 = calculate_factorial(5)
max_number = find_max([1, 5, 3, 9, 2])

# Test with dictionary
sample_data = {"name": "Alice", "age": 25, "city": "New York"}
processed = process_data(sample_data)

# Simple arithmetic
total = x + y
product = x * 2
remainder = x % 10 