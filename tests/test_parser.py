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
    
    def test_parse_list_operations(self):
        """Test parsing list operations."""
        source = """
numbers = [1, 2, 3, 4, 5]
sum_result = sum(numbers)
"""
        result = self.parser.parse_source(source)
        
        assert result["parse_success"] is True
        assert result["ast"] is not None
    
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
        
        validation = self.parser.validate_supported_features(result["ast"])
        assert validation["valid"] is True
        assert isinstance(validation["unsupported_features"], list)
        assert isinstance(validation["warnings"], list) 