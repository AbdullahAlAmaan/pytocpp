"""
Tests for the Python parser module (Milestone 1).
"""

import pytest
from pathlib import Path
from src.pytocpp.parser import PythonParser


class TestPythonParser:
    """Test cases for PythonParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PythonParser()
    
    def test_parse_simple_assignment(self):
        """Test parsing a simple assignment statement."""
        source = "x = 42"
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["ast"] is not None
        assert result["errors"] == []
        assert result["validation"]["valid"] is True
    
    def test_parse_function_definition(self):
        """Test parsing a function definition."""
        source = """
def add(a, b):
    return a + b
"""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["ast"] is not None
        assert result["errors"] == []
        assert result["validation"]["valid"] is True
    
    def test_parse_syntax_error(self):
        """Test parsing code with syntax errors."""
        source = "x = 42 +"  # Incomplete expression
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is False
        assert result["ast"] is None
        assert len(result["errors"]) > 0
    
    def test_parse_complex_expression(self):
        """Test parsing a complex mathematical expression."""
        source = "result = (a + b) * c / d"
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["ast"] is not None
        assert result["validation"]["valid"] is True
    
    def test_parse_list_operations(self):
        """Test parsing list operations."""
        source = """
numbers = [1, 2, 3, 4, 5]
sum_result = sum(numbers)
"""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["ast"] is not None
        assert result["validation"]["valid"] is True
    
    def test_parse_conditional_statement(self):
        """Test parsing if-else statements."""
        source = """
if x > 0:
    result = "positive"
elif x < 0:
    result = "negative"
else:
    result = "zero"
"""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["ast"] is not None
        assert result["validation"]["valid"] is True
    
    def test_parse_loop_statement(self):
        """Test parsing for and while loops."""
        source = """
for i in range(10):
    print(i)

while condition:
    do_something()
"""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["ast"] is not None
        assert result["validation"]["valid"] is True
    
    def test_ast_to_dict_conversion(self):
        """Test AST to dictionary conversion."""
        source = "x = 42"
        result = self.parser.parse_source(source)
        
        # Check that AST is properly converted to dict
        ast_dict = result["ast"]
        assert isinstance(ast_dict, dict)
        
        # Check for expected AST structure
        if ast_dict and "body" in ast_dict:
            assert isinstance(ast_dict["body"], list)
    
    def test_supported_features_validation(self):
        """Test validation of supported Python features."""
        source = "x = 42"
        result = self.parser.parse_source(source)
        
        validation = result["validation"]
        assert validation["valid"] is True
        assert isinstance(validation["unsupported_features"], list)
        assert isinstance(validation["warnings"], list)
        assert isinstance(validation["used_features"], list)
    
    def test_unsupported_class_feature(self):
        """Test detection of unsupported class feature."""
        source = """
class MyClass:
    def __init__(self):
        self.value = 42
"""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["validation"]["valid"] is False
        assert len(result["validation"]["unsupported_features"]) > 0
        
        # Check that classes are detected as unsupported
        unsupported = result["validation"]["unsupported_features"]
        class_features = [f for f in unsupported if f["feature"] == "classes"]
        assert len(class_features) > 0
    
    def test_unsupported_async_feature(self):
        """Test detection of unsupported async feature."""
        source = """
async def async_function():
    await some_async_operation()
"""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["validation"]["valid"] is False
        assert len(result["validation"]["unsupported_features"]) > 0
        
        # Check that async features are detected as unsupported
        unsupported = result["validation"]["unsupported_features"]
        async_features = [f for f in unsupported if f["feature"] == "async_await"]
        assert len(async_features) > 0
    
    def test_unsupported_decorator_feature(self):
        """Test detection of unsupported decorator feature."""
        source = """
@decorator
def decorated_function():
    pass
"""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["validation"]["valid"] is False
        assert len(result["validation"]["unsupported_features"]) > 0
    
    def test_feature_summary(self):
        """Test feature summary generation."""
        source = """
def add(a, b):
    return a + b

x = [1, 2, 3]
if x:
    print("not empty")
"""
        result = self.parser.parse_source(source)
        
        summary = self.parser.get_feature_summary(result["ast"])
        
        assert "total_features_used" in summary
        assert "supported_features_used" in summary
        assert "unsupported_features_used" in summary
        assert "feature_breakdown" in summary
        
        # Should have some supported features
        assert len(summary["supported_features_used"]) > 0
        assert summary["total_features_used"] > 0
    
    def test_mixed_supported_unsupported_features(self):
        """Test code with both supported and unsupported features."""
        source = """
def supported_function():
    x = 42
    return x

class UnsupportedClass:
    pass
"""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["validation"]["valid"] is False
        
        # Should have both supported and unsupported features
        used_features = result["validation"]["used_features"]
        assert "function_defs" in used_features  # Supported
        assert "classes" in used_features  # Unsupported
        
        # Should have unsupported features in the list
        assert len(result["validation"]["unsupported_features"]) > 0
    
    def test_empty_source(self):
        """Test parsing empty source code."""
        source = ""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["validation"]["valid"] is True
        assert len(result["validation"]["used_features"]) == 0
    
    def test_comments_only(self):
        """Test parsing source with only comments."""
        source = "# This is a comment\n# Another comment"
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["validation"]["valid"] is True
    
    def test_nested_unsupported_features(self):
        """Test nested unsupported features (class inside function, async inside class)."""
        source = """
def outer():
    class Inner:
        async def foo(self):
            await bar()
"""
        result = self.parser.parse_source(source)
        assert result["parse_success"] is True
        assert result["validation"]["valid"] is False
        features = [f["feature"] for f in result["validation"]["unsupported_features"]]
        assert "classes" in features
        assert "async_await" in features

    def test_lambda_and_comprehensions(self):
        """Test detection of lambdas and comprehensions."""
        source = """
l = lambda x: x + 1
squares = [x*x for x in range(10)]
d = {x: x*x for x in range(5)}
s = {x for x in range(3)}
g = (x for x in range(2))
"""
        result = self.parser.parse_source(source)
        assert result["parse_success"] is True
        # Lambdas and comprehensions should be detected (and unsupported for v1)
        features = result["validation"]["used_features"]
        assert "lambdas" in features or "generators" in features or "comprehensions" in features

    def test_try_except_finally(self):
        """Test detection of try/except/finally blocks."""
        source = """
try:
    x = 1/0
except ZeroDivisionError:
    x = 0
finally:
    print(x)
"""
        result = self.parser.parse_source(source)
        assert result["parse_success"] is True
        features = result["validation"]["used_features"]
        assert "try_except" in features

    def test_with_statement(self):
        """Test detection of with statements."""
        source = """
with open('file.txt') as f:
    data = f.read()
"""
        result = self.parser.parse_source(source)
        assert result["parse_success"] is True
        features = result["validation"]["used_features"]
        assert "with_statements" in features

    def test_walrus_operator(self):
        """Test detection of walrus operator (:=)."""
        source = """
if (n := 10) > 5:
    print(n)
"""
        result = self.parser.parse_source(source)
        assert result["parse_success"] is True
        features = result["validation"]["used_features"]
        assert "walrus" in features

    def test_type_comments_and_annotations(self):
        """Test detection of type comments and annotations."""
        source = """
x = 1  # type: int
def foo(a: int) -> str:
    return str(a)
"""
        result = self.parser.parse_source(source)
        assert result["parse_success"] is True
        features = result["validation"]["used_features"]
        assert "type_comments" in features or "annotations" in features

    def test_imports(self):
        """Test detection of import statements (import, from, star)."""
        source = """
import os
from sys import path
from math import *
"""
        result = self.parser.parse_source(source)
        assert result["parse_success"] is True
        features = result["validation"]["used_features"]
        assert "imports" in features

    def test_pass_break_continue_ellipsis(self):
        """Test detection of pass, break, continue, ellipsis, docstrings."""
        source = """
def foo():
    "Docstring"
    pass
    ...
    for i in range(3):
        if i == 1:
            break
        else:
            continue
"""
        result = self.parser.parse_source(source)
        assert result["parse_success"] is True
        features = result["validation"]["used_features"]
        assert "pass" in features
        assert "break" in features
        assert "continue" in features
        assert "ellipsis" in features
        assert "docstrings" in features

    def test_large_deeply_nested_code(self):
        """Test parser performance and recursion on large/deeply nested code."""
        # Create a deeply nested if-else chain
        source = "x = 0\n"
        for i in range(100):
            source += f"if x == {i}:\n    x += 1\n"
        result = self.parser.parse_source(source)
        assert result["parse_success"] is True
        assert result["validation"]["valid"] is True 