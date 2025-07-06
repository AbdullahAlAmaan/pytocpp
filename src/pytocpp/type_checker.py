"""
Type checker module (Milestone 2).

Responsible for type inference and validation using mypy and AI assistance.
"""

from typing import Dict, Any, Optional, List
import mypy.api
import keyword
import requests


class TypeChecker:
    """
    Type checker that uses mypy for static analysis and AI for inference.
    
    This is the second step in the transpilation pipeline.
    """
    
    def __init__(self, ai_enabled: bool = False, ollama_model: str = "wizardlm2:latest"):
        self.ai_enabled = ai_enabled
        self.ollama_model = ollama_model
        self.type_cache: Dict[str, str] = {}
        self.builtins_and_keywords = set(dir(__builtins__)) | set(keyword.kwlist)
        
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
        
        # Filter out built-ins and keywords from type_info
        type_info = self._filter_builtins_and_keywords(type_info)
        
        # Use mypy for static type checking
        mypy_results = self._run_mypy_analysis(ast_data["source_code"])
        
        # Merge mypy results with AST analysis
        type_info = self._merge_type_info(type_info, mypy_results)
        
        # Use AI for missing types if enabled
        ai_suggestions = []
        if self.ai_enabled:
            ai_suggestions = self._get_ai_type_suggestions(ast_data["ast"], type_info)
            ai_suggestions = self._filter_ai_suggestions(ai_suggestions)
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
        Extract type information from AST nodes, skipping built-ins and keywords.
        """
        type_info = {}
        
        if not ast_node:
            return type_info
        
        self._walk_ast_for_types(ast_node, type_info)
        
        # Remove built-ins and keywords from type_info
        type_info = {k: v for k, v in type_info.items() if k.split(".")[0] not in self.builtins_and_keywords}
        
        return type_info
    
    def _walk_ast_for_types(self, node: Any, type_info: Dict[str, str]) -> None:
        """
        Recursively walk AST to extract type information.
        
        Args:
            node: AST node or value
            type_info: Dictionary to store extracted types
        """
        if isinstance(node, dict):
            node_type = node.get("node_type")
            
            if node_type == "Assign":
                # Handle variable assignments
                self._extract_assignment_types(node, type_info)
            elif node_type == "AnnAssign":
                # Handle annotated assignments (x: int = 5)
                self._extract_annotated_assignment_types(node, type_info)
            elif node_type == "FunctionDef":
                # Handle function definitions
                self._extract_function_types(node, type_info)
            elif node_type == "arg":
                # Handle function parameters
                self._extract_parameter_types(node, type_info)
            elif node_type == "Constant":
                # Handle literal constants
                self._extract_literal_types(node, type_info)
            elif node_type == "List":
                # Handle list literals
                self._extract_list_types(node, type_info)
            elif node_type == "Tuple":
                # Handle tuple literals
                self._extract_tuple_types(node, type_info)
            elif node_type == "Dict":
                # Handle dictionary literals
                self._extract_dict_types(node, type_info)
            elif node_type == "Call":
                # Handle function calls (for return type inference)
                self._extract_call_types(node, type_info)
            
            # Recursively process all values
            for value in node.values():
                self._walk_ast_for_types(value, type_info)
                
        elif isinstance(node, list):
            # Recursively process all items
            for item in node:
                self._walk_ast_for_types(item, type_info)
    
    def _extract_assignment_types(self, node: Dict[str, Any], type_info: Dict[str, str]) -> None:
        """Extract types from variable assignments."""
        targets = node.get("targets", [])
        value = node.get("value")
        
        if not targets or not value:
            return
        
        # Determine the type of the value
        value_type = self._infer_value_type(value)
        
        # Assign the type to all targets
        for target in targets:
            if target.get("node_type") == "Name":
                var_name = target.get("id")
                if var_name:
                    type_info[var_name] = value_type
    
    def _extract_annotated_assignment_types(self, node: Dict[str, Any], type_info: Dict[str, str]) -> None:
        """Extract types from annotated assignments."""
        target = node.get("target")
        annotation = node.get("annotation")
        
        if target and target.get("node_type") == "Name" and annotation:
            var_name = target.get("id")
            if var_name:
                # Convert annotation to type string
                type_str = self._annotation_to_type_string(annotation)
                type_info[var_name] = type_str
    
    def _extract_function_types(self, node: Dict[str, Any], type_info: Dict[str, str]) -> None:
        """Extract types from function definitions."""
        func_name = node.get("name")
        args = node.get("args", {})
        returns = node.get("returns")
        
        if func_name:
            # Extract parameter types
            params = args.get("args", [])
            param_types = []
            for param in params:
                param_name = param.get("arg")
                param_annotation = param.get("annotation")
                if param_annotation:
                    param_type = self._annotation_to_type_string(param_annotation)
                    param_types.append(param_type)
                    if param_name:
                        type_info[f"{func_name}.{param_name}"] = param_type
                else:
                    param_types.append("Any")
            
            # Extract return type
            if returns:
                return_type = self._annotation_to_type_string(returns)
                type_info[f"{func_name}.return"] = return_type
            else:
                type_info[f"{func_name}.return"] = "Any"
    
    def _extract_parameter_types(self, node: Dict[str, Any], type_info: Dict[str, str]) -> None:
        """Extract types from function parameters."""
        param_name = node.get("arg")
        annotation = node.get("annotation")
        
        if param_name and annotation:
            param_type = self._annotation_to_type_string(annotation)
            type_info[param_name] = param_type
    
    def _extract_literal_types(self, node: Dict[str, Any], type_info: Dict[str, str]) -> str:
        """Extract types from literal constants."""
        value = node.get("value")
        
        if value is None:
            return "None"
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        
        return "Any"
    
    def _extract_list_types(self, node: Dict[str, Any], type_info: Dict[str, str]) -> str:
        """Extract types from list literals."""
        elements = node.get("elts", [])
        
        if not elements:
            return "List[Any]"
        
        # Try to infer the type of the first element
        first_element = elements[0]
        element_type = self._infer_value_type(first_element)
        
        return f"List[{element_type}]"
    
    def _extract_tuple_types(self, node: Dict[str, Any], type_info: Dict[str, str]) -> str:
        """Extract types from tuple literals."""
        elements = node.get("elts", [])
        
        if not elements:
            return "Tuple[()]"
        
        # Extract types of all elements
        element_types = []
        for element in elements:
            element_type = self._infer_value_type(element)
            element_types.append(element_type)
        
        return f"Tuple[{', '.join(element_types)}]"
    
    def _extract_dict_types(self, node: Dict[str, Any], type_info: Dict[str, str]) -> str:
        """Extract types from dictionary literals."""
        keys = node.get("keys", [])
        values = node.get("values", [])
        
        if not keys or not values:
            return "Dict[Any, Any]"
        
        # Try to infer key and value types from first pair
        key_type = self._infer_value_type(keys[0])
        value_type = self._infer_value_type(values[0])
        
        return f"Dict[{key_type}, {value_type}]"
    
    def _extract_call_types(self, node: Dict[str, Any], type_info: Dict[str, str]) -> str:
        """Extract types from function calls."""
        func = node.get("func")
        
        if func and func.get("node_type") == "Name":
            func_name = func.get("id")
            
            # Map common function names to their return types
            common_returns = {
                "len": "int",
                "str": "str",
                "int": "int",
                "float": "float",
                "bool": "bool",
                "list": "List[Any]",
                "dict": "Dict[Any, Any]",
                "tuple": "Tuple[Any, ...]",
                "sum": "int",
                "max": "Any",
                "min": "Any",
                "abs": "int",
                "round": "int",
                "print": "None",
            }
            
            return common_returns.get(func_name, "Any")
        
        return "Any"
    
    def _infer_value_type(self, value_node: Dict[str, Any]) -> str:
        """Infer the type of a value node."""
        if not isinstance(value_node, dict):
            return "Any"
        
        node_type = value_node.get("node_type")
        
        if node_type == "Constant":
            return self._extract_literal_types(value_node, {})
        elif node_type == "List":
            return self._extract_list_types(value_node, {})
        elif node_type == "Tuple":
            return self._extract_tuple_types(value_node, {})
        elif node_type == "Dict":
            return self._extract_dict_types(value_node, {})
        elif node_type == "Call":
            return self._extract_call_types(value_node, {})
        elif node_type == "Name":
            # Variable reference - we'll need to look it up
            return "Any"
        elif node_type == "BinOp":
            # Binary operation - infer from operands
            left_type = self._infer_value_type(value_node.get("left", {}))
            right_type = self._infer_value_type(value_node.get("right", {}))
            
            # Simple type inference for arithmetic
            if left_type == "int" and right_type == "int":
                return "int"
            elif left_type in ["int", "float"] and right_type in ["int", "float"]:
                return "float"
            else:
                return "Any"
        
        return "Any"
    
    def _annotation_to_type_string(self, annotation: Dict[str, Any]) -> str:
        """Convert an annotation node to a type string."""
        if not isinstance(annotation, dict):
            return "Any"
        
        node_type = annotation.get("node_type")
        
        if node_type == "Name":
            return annotation.get("id", "Any")
        elif node_type == "Constant":
            return annotation.get("value", "Any")
        elif node_type == "Subscript":
            # Handle generic types like List[int]
            value = annotation.get("value", {})
            slice_val = annotation.get("slice", {})
            
            if value.get("node_type") == "Name":
                base_type = value.get("id", "Any")
                if slice_val:
                    slice_type = self._annotation_to_type_string(slice_val)
                    return f"{base_type}[{slice_type}]"
                return base_type
        
        return "Any"
    
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
        
        if not mypy_results.get("success", False):
            return merged
        
        # Parse mypy output for type information
        mypy_types = self._parse_mypy_output(mypy_results.get("stdout", ""))
        
        # Merge mypy types with AST types (mypy takes precedence)
        for var_name, mypy_type in mypy_types.items():
            merged[var_name] = mypy_type
        
        return merged
    
    def _parse_mypy_output(self, mypy_output: str) -> Dict[str, str]:
        """
        Parse mypy output to extract type information.
        
        Args:
            mypy_output: Raw mypy output
            
        Returns:
            Dictionary of variable names to types from mypy
        """
        type_info = {}
        
        if not mypy_output:
            return type_info
        
        lines = mypy_output.strip().split('\n')
        
        for line in lines:
            # Look for type annotation messages
            if "note:" in line and "type:" in line:
                # Extract type information from mypy notes
                type_match = self._extract_type_from_mypy_note(line)
                if type_match:
                    var_name, var_type = type_match
                    type_info[var_name] = var_type
            
            # Look for "revealed type" messages
            elif "Revealed type is" in line:
                type_match = self._extract_type_from_revealed(line)
                if type_match:
                    var_name, var_type = type_match
                    type_info[var_name] = var_type
        
        return type_info
    
    def _extract_type_from_mypy_note(self, line: str) -> Optional[tuple[str, str]]:
        """Extract type information from mypy note messages."""
        import re
        
        # Pattern for "note: type: ..."
        pattern = r'note:\s*type:\s*([^:]+):\s*([^\s]+)'
        match = re.search(pattern, line)
        
        if match:
            var_name = match.group(1).strip()
            var_type = match.group(2).strip()
            return var_name, var_type
        
        return None
    
    def _extract_type_from_revealed(self, line: str) -> Optional[tuple[str, str]]:
        """Extract type information from 'Revealed type' messages."""
        import re
        
        # Pattern for "Revealed type is 'type'"
        pattern = r"Revealed type is '([^']+)'"
        match = re.search(pattern, line)
        
        if match:
            var_type = match.group(1)
            # Try to extract variable name from context
            # This is a simplified approach - in practice, we'd need more context
            return "revealed_var", var_type
        
        return None
    
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
        
        # Identify variables without type information
        untyped_vars = self._find_untyped_variables(ast_node, current_types)
        
        if not untyped_vars:
            return suggestions
        
        # Generate context for AI
        context = self._generate_ai_context(ast_node, current_types, untyped_vars)
        
        # Get AI suggestions for each untyped variable
        for var_name in untyped_vars:
            suggestion = self._get_ai_suggestion_for_variable(var_name, context)
            if suggestion:
                suggestions.append(suggestion)
        
        return suggestions
    
    def _find_untyped_variables(self, ast_node: Dict[str, Any], current_types: Dict[str, str]) -> List[str]:
        """Find variables that don't have type information."""
        untyped_vars = []
        
        # Walk AST to find all variable names
        all_vars = set()
        self._collect_variable_names(ast_node, all_vars)
        
        # Filter out variables that already have types
        for var_name in all_vars:
            if var_name not in current_types:
                untyped_vars.append(var_name)
        
        return untyped_vars
    
    def _collect_variable_names(self, node: Any, var_names: set) -> None:
        """Collect all variable names from AST, skipping built-ins and keywords."""
        if isinstance(node, dict):
            node_type = node.get("node_type")
            
            if node_type == "Name":
                var_name = node.get("id")
                if var_name and not var_name.startswith("__") and var_name not in self.builtins_and_keywords:
                    var_names.add(var_name)
            elif node_type == "FunctionDef":
                func_name = node.get("name")
                if func_name and func_name not in self.builtins_and_keywords:
                    var_names.add(func_name)
            
            # Recursively process all values
            for value in node.values():
                self._collect_variable_names(value, var_names)
                
        elif isinstance(node, list):
            for item in node:
                self._collect_variable_names(item, var_names)
    
    def _generate_ai_context(self, ast_node: Dict[str, Any], current_types: Dict[str, str], untyped_vars: List[str]) -> str:
        """Generate context for AI type inference."""
        # Convert AST back to source code for context
        source_code = self._ast_to_source_code(ast_node)
        
        context = f"""Python code for type inference:

{source_code}

Known types:
"""
        
        for var_name, var_type in current_types.items():
            context += f"- {var_name}: {var_type}\n"
        
        context += f"\nVariables needing type inference: {', '.join(untyped_vars)}\n"
        
        return context
    
    def _ast_to_source_code(self, ast_node: Dict[str, Any]) -> str:
        """Convert AST back to source code (simplified version)."""
        # This is a simplified implementation
        # In a real implementation, you'd use ast.unparse() or similar
        
        if not ast_node:
            return ""
        
        # For now, return a placeholder
        # In practice, you'd walk the AST and reconstruct the code
        return "# Source code reconstruction not implemented in this version"
    
    def _get_ai_suggestion_for_variable(self, var_name: str, context: str) -> Optional[Dict[str, Any]]:
        """Get AI suggestion for a specific variable."""
        try:
            # Generate prompt for Code-Llama
            prompt = self._generate_type_inference_prompt(var_name, context)
            
            # Call AI model (placeholder for now)
            ai_response = self._call_ai_model(prompt)
            
            # Parse AI response
            parsed_type, confidence = self._parse_ai_type_response(ai_response)
            
            if parsed_type:
                return {
                    "variable": var_name,
                    "type": parsed_type,
                    "confidence": confidence,
                    "source": "ai_inference"
                }
            
        except Exception as e:
            # Log error but continue
            print(f"AI type inference failed for {var_name}: {e}")
        
        return None
    
    def _generate_type_inference_prompt(self, var_name: str, context: str) -> str:
        """Generate prompt for AI type inference."""
        prompt = f"""{context}

Based on the code above, what is the most likely Python type for the variable '{var_name}'?

Consider:
1. How the variable is used in the code
2. The types of other variables it interacts with
3. Common Python patterns and conventions

Respond with only the type name (e.g., 'int', 'str', 'List[int]', 'Dict[str, Any]', etc.)
"""
        return prompt
    
    def _call_ai_model(self, prompt: str) -> str:
        """Call Ollama model for type inference."""
        try:
            # Call Ollama API
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent type inference
                        "top_p": 0.9,
                        "max_tokens": 50  # We only need short type names
                    }
                },
                timeout=30  # 30 second timeout
            )
            response.raise_for_status()
            
            # Extract the response text
            result = response.json()
            ai_response = result.get("response", "").strip()
            
            # Clean up the response - remove any extra text
            ai_response = ai_response.split('\n')[0].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            print(f"Warning: Ollama API call failed: {e}")
            # Fallback to simple pattern matching
            return self._fallback_type_inference(prompt)
        except Exception as e:
            print(f"Warning: AI type inference error: {e}")
            return self._fallback_type_inference(prompt)
    
    def _fallback_type_inference(self, prompt: str) -> str:
        """Fallback type inference when AI model is unavailable."""
        prompt_lower = prompt.lower()
        
        if "count" in prompt_lower or "length" in prompt_lower or "index" in prompt_lower:
            return "int"
        elif "name" in prompt_lower or "text" in prompt_lower or "message" in prompt_lower:
            return "str"
        elif "items" in prompt_lower or "list" in prompt_lower or "array" in prompt_lower:
            return "List[Any]"
        elif "data" in prompt_lower or "dict" in prompt_lower or "mapping" in prompt_lower:
            return "Dict[str, Any]"
        elif "flag" in prompt_lower or "is_" in prompt_lower or "has_" in prompt_lower:
            return "bool"
        elif "price" in prompt_lower or "rate" in prompt_lower or "ratio" in prompt_lower:
            return "float"
        else:
            return "Any"
    
    def _parse_ai_type_response(self, response: str) -> tuple[Optional[str], float]:
        """Parse AI response to extract type and confidence."""
        if not response:
            return None, 0.0
        
        # Clean up response
        response = response.strip().lower()
        
        # Common Python types
        valid_types = {
            "int", "float", "str", "bool", "list", "dict", "tuple", "set",
            "any", "none", "object", "bytes", "complex"
        }
        
        # Check if response contains a valid type
        for valid_type in valid_types:
            if valid_type in response:
                # Simple confidence scoring
                if valid_type in ["int", "str", "float", "bool"]:
                    confidence = 0.8  # High confidence for basic types
                elif valid_type in ["list", "dict", "tuple"]:
                    confidence = 0.6  # Medium confidence for containers
                else:
                    confidence = 0.4  # Lower confidence for others
                
                return valid_type, confidence
        
        return None, 0.0
    
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
            # Base confidence depends on the type source
            if var_name.endswith(".return"):
                # Function return types - lower confidence unless explicitly annotated
                confidence = 0.6
            elif "." in var_name:
                # Function parameters - higher confidence if annotated
                confidence = 0.8
            else:
                # Regular variables
                confidence = 0.7
            
            # Adjust confidence based on type complexity
            if var_type == "Any":
                confidence *= 0.5  # Lower confidence for Any
            elif "[" in var_type:
                confidence *= 0.9  # Slightly lower for generics
            elif var_type in ["int", "str", "float", "bool"]:
                confidence *= 1.1  # Higher confidence for basic types
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
            confidence_scores[var_name] = confidence
        
        return confidence_scores
    
    def _filter_builtins_and_keywords(self, type_info: Dict[str, str]) -> Dict[str, str]:
        """Remove built-in names and keywords from type info."""
        return {k: v for k, v in type_info.items() if k.split(".")[0] not in self.builtins_and_keywords}
    
    def _filter_ai_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove built-in names and keywords from AI suggestions."""
        filtered = []
        for suggestion in suggestions:
            var_name = suggestion.get("variable", "")
            if var_name.split(".")[0] not in self.builtins_and_keywords:
                filtered.append(suggestion)
        return filtered 