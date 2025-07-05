"""
Type checker module (Milestone 2).

Responsible for type inference and validation using mypy and AI assistance.
"""

from typing import Dict, Any, Optional, List
import mypy.api


class TypeChecker:
    """
    Type checker that uses mypy for static analysis and AI for inference.
    
    This is the second step in the transpilation pipeline.
    """
    
    def __init__(self, ai_enabled: bool = False):
        self.ai_enabled = ai_enabled
        self.type_cache: Dict[str, str] = {}
        
    def analyze(self, ast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze AST for type information.
        
        Args:
            ast_data: AST data from parser
            
        Returns:
            Dictionary with type information for all variables and functions
        """
        if not ast_data.get("parse_success", False):
            return {
                "success": False,
                "errors": ast_data.get("errors", []),
                "type_info": {},
                "ai_suggestions": []
            }
        
        # Extract type information from AST
        type_info = self._extract_types_from_ast(ast_data["ast"])
        
        # Use mypy for static type checking
        mypy_results = self._run_mypy_analysis(ast_data["source_code"])
        
        # Merge mypy results with AST analysis
        type_info = self._merge_type_info(type_info, mypy_results)
        
        # Use AI for missing types if enabled
        ai_suggestions = []
        if self.ai_enabled:
            ai_suggestions = self._get_ai_type_suggestions(ast_data["ast"], type_info)
            type_info = self._apply_ai_suggestions(type_info, ai_suggestions)
        
        return {
            "success": True,
            "type_info": type_info,
            "mypy_results": mypy_results,
            "ai_suggestions": ai_suggestions,
            "confidence_scores": self._calculate_confidence_scores(type_info)
        }
    
    def _extract_types_from_ast(self, ast_node: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract type information from AST nodes.
        
        Args:
            ast_node: AST node in dictionary format
            
        Returns:
            Dictionary mapping variable names to their types
        """
        type_info = {}
        
        # TODO: Implement AST type extraction in Milestone 2
        # This will walk the AST and extract:
        # - Variable assignments and their types
        # - Function parameters and return types
        # - Literal types (int, float, str, bool)
        # - Container types (list, tuple, dict)
        
        return type_info
    
    def _run_mypy_analysis(self, source_code: str) -> Dict[str, Any]:
        """
        Run mypy type checker on the source code.
        
        Args:
            source_code: Python source code
            
        Returns:
            mypy analysis results
        """
        try:
            # Create temporary file for mypy
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(source_code)
                temp_file = f.name
            
            # Run mypy
            result = mypy.api.run([temp_file, '--show-error-codes', '--no-error-summary'])
            
            # Clean up
            import os
            os.unlink(temp_file)
            
            return {
                "success": True,
                "stdout": result[0],
                "stderr": result[1],
                "exit_code": result[2]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "exit_code": -1
            }
    
    def _merge_type_info(self, ast_types: Dict[str, str], mypy_results: Dict[str, Any]) -> Dict[str, str]:
        """
        Merge type information from AST analysis and mypy.
        
        Args:
            ast_types: Types extracted from AST
            mypy_results: Results from mypy analysis
            
        Returns:
            Merged type information
        """
        merged = ast_types.copy()
        
        # TODO: Parse mypy output and merge with AST types
        # This will extract type annotations and inferred types from mypy output
        
        return merged
    
    def _get_ai_type_suggestions(self, ast_node: Dict[str, Any], current_types: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Get AI suggestions for missing types.
        
        Args:
            ast_node: AST node in dictionary format
            current_types: Currently known types
            
        Returns:
            List of AI type suggestions with confidence scores
        """
        suggestions = []
        
        # TODO: Implement AI type inference in Milestone 2
        # This will:
        # 1. Identify variables without type information
        # 2. Generate prompts for Code-Llama
        # 3. Parse AI responses for type suggestions
        # 4. Calculate confidence scores
        
        return suggestions
    
    def _apply_ai_suggestions(self, type_info: Dict[str, str], suggestions: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Apply AI type suggestions to type information.
        
        Args:
            type_info: Current type information
            suggestions: AI type suggestions
            
        Returns:
            Updated type information with AI suggestions applied
        """
        updated = type_info.copy()
        
        for suggestion in suggestions:
            var_name = suggestion.get("variable")
            suggested_type = suggestion.get("type")
            confidence = suggestion.get("confidence", 0.0)
            
            # Only apply high-confidence suggestions
            if confidence > 0.7 and var_name and suggested_type:
                updated[var_name] = suggested_type
        
        return updated
    
    def _calculate_confidence_scores(self, type_info: Dict[str, str]) -> Dict[str, float]:
        """
        Calculate confidence scores for type information.
        
        Args:
            type_info: Type information dictionary
            
        Returns:
            Dictionary mapping variable names to confidence scores
        """
        confidence_scores = {}
        
        for var_name, var_type in type_info.items():
            # TODO: Implement confidence scoring in Milestone 2
            # Factors to consider:
            # - Source of type information (AST vs mypy vs AI)
            # - Type complexity
            # - Context clues
            confidence_scores[var_name] = 0.8  # Placeholder
        
        return confidence_scores 