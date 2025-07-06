"""
Python AST parser module (Milestone 1).

Responsible for parsing Python source code into an AST and converting it to JSON.
"""

import ast
import json
from pathlib import Path
from typing import Dict, Any, Union, List, Set


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
            "lambdas": False,
            "comprehensions": False,
            "try_except": False,
            "with_statements": False,
            "walrus": False,
            "type_comments": False,
            "annotations": True,  # Allow type annotations
            "pass": True,
            "break": True,
            "continue": True,
            "ellipsis": True,
            "docstrings": True,
        }
        
        # Mapping of AST node types to feature names
        self.node_to_feature_map = {
            # Basic constructs
            "Assign": "assignments",
            "AugAssign": "assignments",
            "AnnAssign": "assignments",
            "Expr": "expressions",
            "FunctionDef": "function_defs",
            "AsyncFunctionDef": "async_await",
            "If": "if_statements",
            "For": "for_loops",
            "AsyncFor": "async_await",
            "While": "while_loops",
            "Return": "return_statements",
            
            # Data structures
            "List": "lists",
            "Tuple": "tuples",
            "Dict": "dictionaries",
            "Set": "dictionaries",  # Treat sets as dictionaries for now
            
            # Function calls
            "Call": "function_calls",
            
            # Classes and OOP
            "ClassDef": "classes",
            "AsyncClassDef": "classes",
            
            # Generators and async
            "Yield": "generators",
            "YieldFrom": "generators",
            "Await": "async_await",
            
            # Imports
            "Import": "imports",
            "ImportFrom": "imports",
            
            # Lambdas
            "Lambda": "lambdas",
            
            # Comprehensions
            "ListComp": "comprehensions",
            "DictComp": "comprehensions",
            "SetComp": "comprehensions",
            "GeneratorExp": "comprehensions",
            
            # Try/Except/Finally
            "Try": "try_except",
            
            # With
            "With": "with_statements",
            "AsyncWith": "with_statements",
            
            # Walrus operator
            "NamedExpr": "walrus",
            
            # Pass, break, continue, ellipsis
            "Pass": "pass",
            "Break": "break",
            "Continue": "continue",
            "Constant": "ellipsis",  # Will check for value is Ellipsis
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
            
            # Validate features
            validation = self.validate_supported_features(ast_json)
            
            return {
                "filename": filename,
                "source_code": source_code,
                "ast": ast_json,
                "supported_features": self.supported_features,
                "parse_success": True,
                "validation": validation,
                "errors": []
            }
            
        except SyntaxError as e:
            return {
                "filename": filename,
                "source_code": source_code,
                "ast": None,
                "supported_features": self.supported_features,
                "parse_success": False,
                "validation": {"valid": False, "unsupported_features": [], "warnings": []},
                "errors": [f"Syntax error: {e}"]
            }
        except Exception as e:
            return {
                "filename": filename,
                "source_code": source_code,
                "ast": None,
                "supported_features": self.supported_features,
                "parse_success": False,
                "validation": {"valid": False, "unsupported_features": [], "warnings": []},
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
        if not ast_dict:
            return {
                "valid": True,
                "unsupported_features": [],
                "warnings": [],
                "used_features": set()
            }
        
        used_features = set()
        unsupported_features = []
        warnings = []
        
        # Walk through the AST and collect used features
        self._collect_features(ast_dict, used_features, unsupported_features, warnings)
        
        # Check if any unsupported features are used
        is_valid = len(unsupported_features) == 0
        
        return {
            "valid": is_valid,
            "unsupported_features": unsupported_features,
            "warnings": warnings,
            "used_features": list(used_features)
        }
    
    def _collect_features(self, node: Any, used_features: Set[str], 
                         unsupported_features: List[str], warnings: List[str]) -> None:
        """
        Recursively collect features used in the AST.
        
        Args:
            node: AST node or value
            used_features: Set to collect all used features
            unsupported_features: List to collect unsupported features
            warnings: List to collect warnings
        """
        if isinstance(node, dict):
            node_type = node.get("node_type")
            if node_type:
                feature_name = self.node_to_feature_map.get(node_type)
                if feature_name:
                    # Special handling for ellipsis
                    if node_type == "Constant" and node.get("value") == Ellipsis:
                        used_features.add("ellipsis")
                        if not self.supported_features.get("ellipsis", False):
                            unsupported_features.append({
                                "feature": "ellipsis",
                                "node_type": node_type,
                                "line": node.get("lineno"),
                                "description": "Unsupported feature: ellipsis"
                            })
                    else:
                        used_features.add(feature_name)
                        if not self.supported_features.get(feature_name, False):
                            unsupported_features.append({
                                "feature": feature_name,
                                "node_type": node_type,
                                "line": node.get("lineno"),
                                "description": f"Unsupported feature: {feature_name}"
                            })
                # Special handling for decorators in function definitions
                if node_type == "FunctionDef" and node.get("decorator_list"):
                    used_features.add("decorators")
                    if not self.supported_features.get("decorators", False):
                        unsupported_features.append({
                            "feature": "decorators",
                            "node_type": "FunctionDef",
                            "line": node.get("lineno"),
                            "description": "Unsupported feature: decorators"
                        })
                # Special handling for docstrings
                if node_type == "FunctionDef" and node.get("body") and isinstance(node["body"], list):
                    first_stmt = node["body"][0] if node["body"] else None
                    if first_stmt and first_stmt.get("node_type") == "Expr":
                        value = first_stmt.get("value")
                        # For Python 3.8+, value is a Constant node with a string value
                        if isinstance(value, dict) and value.get("node_type") == "Constant" and isinstance(value.get("value"), str):
                            used_features.add("docstrings")
                        # For older Python, value may be a string directly
                        elif isinstance(value, str):
                            used_features.add("docstrings")
                # Special handling for type comments
                if node.get("type_comment") is not None:
                    used_features.add("type_comments")
                    if not self.supported_features.get("type_comments", False):
                        unsupported_features.append({
                            "feature": "type_comments",
                            "node_type": node_type,
                            "line": node.get("lineno"),
                            "description": "Unsupported feature: type_comments"
                        })
                # Special handling for annotations
                if node_type == "arg" and node.get("annotation") is not None:
                    used_features.add("annotations")
            
            # Recursively process all values in the dict
            for value in node.values():
                self._collect_features(value, used_features, unsupported_features, warnings)
                
        elif isinstance(node, list):
            # Recursively process all items in the list
            for item in node:
                self._collect_features(item, used_features, unsupported_features, warnings)
    
    def get_feature_summary(self, ast_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of features used in the AST.
        
        Args:
            ast_dict: AST in dictionary format
            
        Returns:
            Summary of features used
        """
        validation = self.validate_supported_features(ast_dict)
        
        summary = {
            "total_features_used": len(validation["used_features"]),
            "supported_features_used": [],
            "unsupported_features_used": [],
            "feature_breakdown": {}
        }
        
        for feature in validation["used_features"]:
            if self.supported_features.get(feature, False):
                summary["supported_features_used"].append(feature)
            else:
                summary["unsupported_features_used"].append(feature)
            
            summary["feature_breakdown"][feature] = {
                "supported": self.supported_features.get(feature, False),
                "description": self._get_feature_description(feature)
            }
        
        return summary
    
    def _get_feature_description(self, feature: str) -> str:
        """Get a human-readable description of a feature."""
        descriptions = {
            "assignments": "Variable assignments and expressions",
            "expressions": "Mathematical and logical expressions",
            "function_defs": "Function definitions",
            "if_statements": "Conditional statements (if/elif/else)",
            "for_loops": "For loops and iterations",
            "while_loops": "While loops",
            "return_statements": "Return statements",
            "lists": "List data structures",
            "tuples": "Tuple data structures",
            "dictionaries": "Dictionary and set data structures",
            "function_calls": "Function and method calls",
            "method_calls": "Method calls on objects",
            "classes": "Class definitions and OOP",
            "async_await": "Async/await functionality",
            "generators": "Generator functions and yield",
            "decorators": "Function and class decorators",
            "imports": "Import statements",
            "lambdas": "Lambda expressions",
            "comprehensions": "List, dictionary, and set comprehensions",
            "try_except": "Try/except/finally statements",
            "with_statements": "With statements",
            "walrus": "Walrus operator",
            "type_comments": "Type comments",
            "annotations": "Type annotations",
            "pass": "Pass statement",
            "break": "Break statement",
            "continue": "Continue statement",
            "ellipsis": "Ellipsis",
            "docstrings": "Docstrings",
        }
        return descriptions.get(feature, f"Unknown feature: {feature}") 