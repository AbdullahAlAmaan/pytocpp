"""
Demo file for testing type checker functionality.

This file contains various Python patterns to test type inference:
- Basic variable assignments
- Type annotations
- Function definitions
- Container types
- Complex expressions
"""

# Basic variable assignments
count = 0
name = "Alice"
pi = 3.14159
is_active = True
data = None

# Type annotations
age: int = 25
score: float = 95.5
message: str = "Hello, World!"
items: list = [1, 2, 3, 4, 5]

# Function definitions
def add_numbers(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b

def calculate_average(numbers: list) -> float:
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

def process_data(data: dict) -> str:
    """Process a dictionary and return a string representation."""
    result = ""
    for key, value in data.items():
        result += f"{key}: {value}\n"
    return result

# Container types
numbers_list = [1, 2, 3, 4, 5]
names_tuple = ("Alice", "Bob", "Charlie")
config_dict = {"host": "localhost", "port": 8080}
unique_set = {1, 2, 3, 4, 5}

# Complex expressions
total = add_numbers(10, 20)
average = calculate_average(numbers_list)
processed = process_data(config_dict)

# List comprehensions
squares = [x**2 for x in range(10)]
filtered = [x for x in numbers_list if x > 3]

# Dictionary comprehensions
squared_dict = {x: x**2 for x in range(5)}

# Function calls with type inference
length = len(name)
converted = str(count)
rounded = round(pi, 2)

# Variables without explicit types (for AI inference)
user_count = 0
file_path = "/path/to/file.txt"
is_visible = True
empty_list = []
mixed_data = {"key": "value", "number": 42}

# Nested structures
nested_list = [[1, 2], [3, 4], [5, 6]]
nested_dict = {
    "users": [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30}
    ],
    "settings": {
        "theme": "dark",
        "language": "en"
    }
}

# Function with complex return type
def get_user_data(user_id: int) -> dict:
    """Get user data by ID."""
    return {
        "id": user_id,
        "name": "User",
        "email": "user@example.com",
        "active": True
    }

# Variables that will need AI inference
result_data = get_user_data(123)
first_user = result_data["name"]
user_active = result_data["active"] 