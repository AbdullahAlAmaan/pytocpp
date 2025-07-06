"""
Tests for the type checker module (Milestone 2).
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from pytocpp.type_checker import TypeChecker


class TestTypeChecker:
    """Test cases for the TypeChecker class."""
    
    def test_init(self):
        """Test TypeChecker initialization."""
        # Test without AI
        checker = TypeChecker(ai_enabled=False)
        assert checker.ai_enabled is False
        assert checker.type_cache == {}
        
        # Test with AI
        checker = TypeChecker(ai_enabled=True)
        assert checker.ai_enabled is True
        assert checker.type_cache == {}
    
    def test_analyze_with_invalid_ast(self):
        """Test analyze with invalid AST data."""
        checker = TypeChecker()
        
        # Test with failed parse
        invalid_data = {
            "parse_success": False,
            "errors": ["Syntax error"]
        }
        
        result = checker.analyze(invalid_data)
        
        assert result["success"] is False
        assert result["errors"] == ["Syntax error"]
        assert result["type_info"] == {}
        assert result["ai_suggestions"] == []
    
    def test_extract_types_from_ast_basic(self):
        """Test basic type extraction from AST."""
        checker = TypeChecker()
        
        # Simple AST with variable assignments
        ast_data = {
            "node_type": "Module",
            "body": [
                {
                    "node_type": "Assign",
                    "targets": [{"node_type": "Name", "id": "x"}],
                    "value": {"node_type": "Constant", "value": 42}
                },
                {
                    "node_type": "Assign",
                    "targets": [{"node_type": "Name", "id": "name"}],
                    "value": {"node_type": "Constant", "value": "hello"}
                }
            ]
        }
        
        type_info = checker._extract_types_from_ast(ast_data)
        
        assert type_info["x"] == "int"
        assert type_info["name"] == "str"
    
    def test_extract_types_from_ast_annotated(self):
        """Test type extraction from annotated assignments."""
        checker = TypeChecker()
        
        ast_data = {
            "node_type": "Module",
            "body": [
                {
                    "node_type": "AnnAssign",
                    "target": {"node_type": "Name", "id": "count"},
                    "annotation": {"node_type": "Name", "id": "int"},
                    "value": {"node_type": "Constant", "value": 0}
                }
            ]
        }
        
        type_info = checker._extract_types_from_ast(ast_data)
        
        assert type_info["count"] == "int"
    
    def test_extract_types_from_ast_function(self):
        """Test type extraction from function definitions."""
        checker = TypeChecker()
        
        ast_data = {
            "node_type": "Module",
            "body": [
                {
                    "node_type": "FunctionDef",
                    "name": "add",
                    "args": {
                        "args": [
                            {
                                "node_type": "arg",
                                "arg": "a",
                                "annotation": {"node_type": "Name", "id": "int"}
                            },
                            {
                                "node_type": "arg",
                                "arg": "b",
                                "annotation": {"node_type": "Name", "id": "int"}
                            }
                        ]
                    },
                    "returns": {"node_type": "Name", "id": "int"}
                }
            ]
        }
        
        type_info = checker._extract_types_from_ast(ast_data)
        
        assert type_info["add.a"] == "int"
        assert type_info["add.b"] == "int"
        assert type_info["add.return"] == "int"
    
    def test_extract_types_from_ast_containers(self):
        """Test type extraction from container literals."""
        checker = TypeChecker()
        
        ast_data = {
            "node_type": "Module",
            "body": [
                {
                    "node_type": "Assign",
                    "targets": [{"node_type": "Name", "id": "numbers"}],
                    "value": {
                        "node_type": "List",
                        "elts": [
                            {"node_type": "Constant", "value": 1},
                            {"node_type": "Constant", "value": 2}
                        ]
                    }
                },
                {
                    "node_type": "Assign",
                    "targets": [{"node_type": "Name", "id": "data"}],
                    "value": {
                        "node_type": "Dict",
                        "keys": [{"node_type": "Constant", "value": "key"}],
                        "values": [{"node_type": "Constant", "value": "value"}]
                    }
                }
            ]
        }
        
        type_info = checker._extract_types_from_ast(ast_data)
        
        assert type_info["numbers"] == "List[int]"
        assert type_info["data"] == "Dict[str, str]"
    
    def test_extract_types_from_ast_function_calls(self):
        """Test type extraction from function calls."""
        checker = TypeChecker()
        
        ast_data = {
            "node_type": "Module",
            "body": [
                {
                    "node_type": "Assign",
                    "targets": [{"node_type": "Name", "id": "length"}],
                    "value": {
                        "node_type": "Call",
                        "func": {"node_type": "Name", "id": "len"},
                        "args": [{"node_type": "Constant", "value": "hello"}]
                    }
                }
            ]
        }
        
        type_info = checker._extract_types_from_ast(ast_data)
        
        assert type_info["length"] == "int"
    
    def test_infer_value_type_literals(self):
        """Test type inference for literal values."""
        checker = TypeChecker()
        
        # Test different literal types
        int_node = {"node_type": "Constant", "value": 42}
        float_node = {"node_type": "Constant", "value": 3.14}
        str_node = {"node_type": "Constant", "value": "hello"}
        bool_node = {"node_type": "Constant", "value": True}
        none_node = {"node_type": "Constant", "value": None}
        
        assert checker._infer_value_type(int_node) == "int"
        assert checker._infer_value_type(float_node) == "float"
        assert checker._infer_value_type(str_node) == "str"
        assert checker._infer_value_type(bool_node) == "bool"
        assert checker._infer_value_type(none_node) == "None"
    
    def test_infer_value_type_operations(self):
        """Test type inference for binary operations."""
        checker = TypeChecker()
        
        # Integer addition
        int_add = {
            "node_type": "BinOp",
            "left": {"node_type": "Constant", "value": 1},
            "right": {"node_type": "Constant", "value": 2}
        }
        
        # Float addition
        float_add = {
            "node_type": "BinOp",
            "left": {"node_type": "Constant", "value": 1.0},
            "right": {"node_type": "Constant", "value": 2}
        }
        
        assert checker._infer_value_type(int_add) == "int"
        assert checker._infer_value_type(float_add) == "float"
    
    def test_annotation_to_type_string(self):
        """Test conversion of annotations to type strings."""
        checker = TypeChecker()
        
        # Simple type
        simple_ann = {"node_type": "Name", "id": "int"}
        assert checker._annotation_to_type_string(simple_ann) == "int"
        
        # Generic type
        generic_ann = {
            "node_type": "Subscript",
            "value": {"node_type": "Name", "id": "List"},
            "slice": {"node_type": "Name", "id": "int"}
        }
        assert checker._annotation_to_type_string(generic_ann) == "List[int]"
    
    @patch('pytocpp.type_checker.mypy.api.run')
    def test_run_mypy_analysis_success(self, mock_mypy):
        """Test successful mypy analysis."""
        checker = TypeChecker()
        
        # Mock mypy response
        mock_mypy.return_value = ("Success: no issues found", "", 0)
        
        result = checker._run_mypy_analysis("x = 42")
        
        assert result["success"] is True
        assert result["stdout"] == "Success: no issues found"
        assert result["exit_code"] == 0
    
    @patch('pytocpp.type_checker.mypy.api.run')
    def test_run_mypy_analysis_failure(self, mock_mypy):
        """Test mypy analysis failure."""
        checker = TypeChecker()
        
        # Mock mypy error
        mock_mypy.side_effect = Exception("mypy not found")
        
        result = checker._run_mypy_analysis("x = 42")
        
        assert result["success"] is False
        assert "mypy not found" in result["error"]
    
    def test_parse_mypy_output(self):
        """Test parsing mypy output."""
        checker = TypeChecker()
        
        # Mock mypy output
        mypy_output = """
        note: type: x: int
        note: Revealed type is 'str'
        """
        
        type_info = checker._parse_mypy_output(mypy_output)
        
        assert type_info["x"] == "int"
        assert type_info["revealed_var"] == "str"
    
    def test_merge_type_info(self):
        """Test merging type information from AST and mypy."""
        checker = TypeChecker()
        
        ast_types = {"x": "int", "y": "str"}
        mypy_results = {
            "success": True,
            "stdout": "note: type: x: float\nnote: type: z: bool"
        }
        
        merged = checker._merge_type_info(ast_types, mypy_results)
        
        # mypy should override AST types
        assert merged["x"] == "float"
        assert merged["y"] == "str"
        assert merged["z"] == "bool"
    
    def test_find_untyped_variables(self):
        """Test finding variables without type information."""
        checker = TypeChecker()
        
        ast_data = {
            "node_type": "Module",
            "body": [
                {
                    "node_type": "Assign",
                    "targets": [{"node_type": "Name", "id": "x"}],
                    "value": {"node_type": "Constant", "value": 42}
                },
                {
                    "node_type": "Assign",
                    "targets": [{"node_type": "Name", "id": "y"}],
                    "value": {"node_type": "Constant", "value": "hello"}
                }
            ]
        }
        
        current_types = {"x": "int"}  # y is missing
        
        untyped = checker._find_untyped_variables(ast_data, current_types)
        
        assert "y" in untyped
        assert "x" not in untyped
    
    def test_get_ai_suggestion_for_variable(self):
        """Test AI suggestion generation."""
        checker = TypeChecker(ai_enabled=True)
        
        context = "Python code for type inference:\ncount = 0\n"
        suggestion = checker._get_ai_suggestion_for_variable("count", context)
        
        assert suggestion is not None
        assert suggestion["variable"] == "count"
        assert suggestion["type"] == "int"
        assert "confidence" in suggestion
    
    def test_apply_ai_suggestions(self):
        """Test applying AI suggestions to type information."""
        checker = TypeChecker()
        
        type_info = {"x": "int"}
        suggestions = [
            {
                "variable": "y",
                "type": "str",
                "confidence": 0.8
            },
            {
                "variable": "z",
                "type": "list",
                "confidence": 0.3  # Too low confidence
            }
        ]
        
        updated = checker._apply_ai_suggestions(type_info, suggestions)
        
        assert updated["x"] == "int"
        assert updated["y"] == "str"
        assert "z" not in updated  # Low confidence suggestion not applied
    
    def test_calculate_confidence_scores(self):
        """Test confidence score calculation."""
        checker = TypeChecker()
        
        type_info = {
            "x": "int",
            "func.param": "str",
            "func.return": "bool",
            "complex": "List[Dict[str, Any]]"
        }
        
        scores = checker._calculate_confidence_scores(type_info)
        
        assert scores["x"] > 0.7  # Basic type, high confidence
        assert scores["func.param"] > 0.7  # Function parameter
        assert scores["func.return"] < 0.7  # Function return, lower confidence
        assert scores["complex"] < 0.9  # Complex type, slightly lower confidence
    
    def test_analyze_complete_workflow(self):
        """Test complete type analysis workflow."""
        checker = TypeChecker(ai_enabled=True)
        
        # Mock parse result
        parse_result = {
            "parse_success": True,
            "ast": {
                "node_type": "Module",
                "body": [
                    {
                        "node_type": "Assign",
                        "targets": [{"node_type": "Name", "id": "count"}],
                        "value": {"node_type": "Constant", "value": 0}
                    }
                ]
            },
            "source_code": "count = 0"
        }
        
        with patch.object(checker, '_run_mypy_analysis') as mock_mypy:
            mock_mypy.return_value = {
                "success": True,
                "stdout": "",
                "stderr": "",
                "exit_code": 0
            }
            
            result = checker.analyze(parse_result)
            
            assert result["success"] is True
            assert "type_info" in result
            assert "confidence_scores" in result
            assert "ai_suggestions" in result
    
    def test_analyze_with_mypy_errors(self):
        """Test analysis when mypy finds errors."""
        checker = TypeChecker()
        
        parse_result = {
            "parse_success": True,
            "ast": {"node_type": "Module", "body": []},
            "source_code": "x = 42"
        }
        
        with patch.object(checker, '_run_mypy_analysis') as mock_mypy:
            mock_mypy.return_value = {
                "success": True,
                "stdout": "error: Name 'undefined_var' is not defined",
                "stderr": "",
                "exit_code": 1
            }
            
            result = checker.analyze(parse_result)
            
            # Should still succeed, but with mypy errors in output
            assert result["success"] is True
            assert "mypy_results" in result
            assert result["mypy_results"]["exit_code"] == 1


if __name__ == "__main__":
    pytest.main([__file__]) 