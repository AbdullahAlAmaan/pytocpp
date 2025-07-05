"""
Python AST parser module (Milestone 1).

Responsible for parsing Python source code into an AST and converting it to JSON.
"""

import ast
import json
from pathlib import Path
from typing import Dict, Any, Union


class PythonParser:
    """
    Parser that converts Python source code to AST and JSON representation.
    
    This is the first step in the transpilation pipeline.
    """
    
    def __init__(self):
        self.supported_features = {
            # Basic constructs
            "assignments": True,
            "expressions": True,
            "function_defs": True,
            "if_statements": True,
            "for_loops": True,
            "while_loops": True,
            "return_statements": True,
            
            # Data structures
            "lists": True,
            "tuples": True,
            "dictionaries": True,
            
            # Functions and calls
            "function_calls": True,
            "method_calls": True,
            
            # Not supported in v1
            "classes": False,
            "async_await": False,
            "generators": False,
            "decorators": False,
            "imports": False,  # Limited support
        }
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a Python file into AST and convert to JSON.
        
        Args:
            file_path: Path to Python source file
            
        Returns:
            Dictionary containing AST and metadata
        """
        source_code = file_path.read_text()
        return self.parse_source(source_code, str(file_path))
    
    def parse_source(self, source_code: str, filename: str = "<string>") -> Dict[str, Any]:
        """
        Parse Python source code into AST and convert to JSON.
        
        Args:
            source_code: Python source code as string
            filename: Source filename for error reporting
            
        Returns:
            Dictionary containing AST and metadata
        """
        try:
            # Parse into AST
            tree = ast.parse(source_code, filename=filename)
            
            # Convert to JSON-serializable format
            ast_json = self._ast_to_dict(tree)
            
            return {
                "filename": filename,
                "source_code": source_code,
                "ast": ast_json,
                "supported_features": self.supported_features,
                "parse_success": True,
                "errors": []
            }
            
        except SyntaxError as e:
            return {
                "filename": filename,
                "source_code": source_code,
                "ast": None,
                "supported_features": self.supported_features,
                "parse_success": False,
                "errors": [f"Syntax error: {e}"]
            }
        except Exception as e:
            return {
                "filename": filename,
                "source_code": source_code,
                "ast": None,
                "supported_features": self.supported_features,
                "parse_success": False,
                "errors": [f"Parse error: {e}"]
            }
    
    def _ast_to_dict(self, node: Union[ast.AST, list, str, int, float, bool, None]) -> Any:
        """
        Convert AST node to JSON-serializable dictionary.
        
        Args:
            node: AST node or primitive value
            
        Returns:
            JSON-serializable representation
        """
        if node is None:
            return None
        elif isinstance(node, (str, int, float, bool)):
            return node
        elif isinstance(node, list):
            return [self._ast_to_dict(item) for item in node]
        elif isinstance(node, ast.AST):
            result = {
                "node_type": node.__class__.__name__,
                "lineno": getattr(node, "lineno", None),
                "col_offset": getattr(node, "col_offset", None),
            }
            
            # Add node-specific fields
            for field, value in ast.iter_fields(node):
                result[field] = self._ast_to_dict(value)
            
            return result
        else:
            return str(node)
    
    def validate_supported_features(self, ast_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the AST only uses supported Python features.
        
        Args:
            ast_dict: AST in dictionary format
            
        Returns:
            Validation results with any unsupported features
        """
        # TODO: Implement feature validation in Milestone 1
        return {
            "valid": True,
            "unsupported_features": [],
            "warnings": []
        } 