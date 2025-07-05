"""
C++ code generator module (Milestone 4).

Responsible for converting IR into readable C++17 code using Jinja2 templates.
"""

from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, Template


class CppCodeGenerator:
    """
    Generates C++17 code from IR using Jinja2 templates.
    
    This is the fourth step in the transpilation pipeline.
    """
    
    def __init__(self):
        self.template_env = Environment(
            loader=FileSystemLoader(self._get_template_dir()),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.template_env.globals.update({
            'cpp_type_map': self._get_cpp_type_map(),
            'cpp_operator_map': self._get_cpp_operator_map()
        })
    
    def generate(self, ir_data: Dict[str, Any]) -> str:
        """
        Generate C++ code from IR data.
        
        Args:
            ir_data: IR data from IR generator
            
        Returns:
            Generated C++ source code
        """
        if not ir_data.get("success", False):
            return self._generate_error_code(ir_data.get("errors", []))
        
        # Get main template
        template = self.template_env.get_template("main.cpp.j2")
        
        # Prepare template context
        context = self._prepare_template_context(ir_data)
        
        # Generate C++ code
        cpp_code = template.render(**context)
        
        return cpp_code
    
    def _get_template_dir(self) -> Path:
        """Get the directory containing Jinja2 templates."""
        # TODO: Create templates directory and add template files
        return Path(__file__).parent / "templates"
    
    def _get_cpp_type_map(self) -> Dict[str, str]:
        """Get mapping from Python types to C++ types."""
        return {
            # Basic types
            "int": "int",
            "float": "double",  # Use double for better precision
            "str": "std::string",
            "bool": "bool",
            
            # Container types
            "list": "std::vector",
            "tuple": "std::tuple",
            "dict": "std::map",
            "set": "std::set",
            
            # Special types
            "None": "void",
            "auto": "auto",
            
            # Numeric types
            "complex": "std::complex<double>",
        }
    
    def _get_cpp_operator_map(self) -> Dict[str, str]:
        """Get mapping from IR operators to C++ operators."""
        return {
            # Arithmetic
            "add": "+",
            "sub": "-",
            "mul": "*",
            "div": "/",
            "mod": "%",
            "pow": "std::pow",
            
            # Comparison
            "eq": "==",
            "ne": "!=",
            "lt": "<",
            "le": "<=",
            "gt": ">",
            "ge": ">=",
            
            # Logical
            "and": "&&",
            "or": "||",
            "not": "!",
            
            # Bitwise
            "bitand": "&",
            "bitor": "|",
            "bitxor": "^",
            "lshift": "<<",
            "rshift": ">>",
        }
    
    def _prepare_template_context(self, ir_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare context data for Jinja2 template rendering.
        
        Args:
            ir_data: IR data from generator
            
        Returns:
            Template context dictionary
        """
        ir = ir_data.get("ir", {})
        
        return {
            "includes": self._generate_includes(ir),
            "functions": self._process_functions(ir.get("functions", [])),
            "global_vars": self._process_global_vars(ir.get("global_vars", [])),
            "main_function": self._generate_main_function(ir),
            "optimizations": ir_data.get("optimizations", []),
            "metadata": ir_data.get("metadata", {})
        }
    
    def _generate_includes(self, ir: Dict[str, Any]) -> List[str]:
        """Generate C++ include statements based on IR content."""
        includes = [
            "#include <iostream>",
            "#include <vector>",
            "#include <string>",
            "#include <map>",
            "#include <cmath>",
            "#include <algorithm>",
        ]
        
        # Add includes based on IR content
        if ir.get("functions"):
            includes.append("#include <functional>")
        
        if any("std::complex" in str(var) for var in ir.get("global_vars", [])):
            includes.append("#include <complex>")
        
        return includes
    
    def _process_functions(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process IR functions for template rendering."""
        processed = []
        
        for func in functions:
            processed_func = {
                "name": func.get("name", "unknown"),
                "return_type": self._map_cpp_type(func.get("return_type", "void")),
                "parameters": self._process_parameters(func.get("parameters", [])),
                "body": self._generate_function_body(func),
                "local_vars": func.get("local_vars", {})
            }
            processed.append(processed_func)
        
        return processed
    
    def _process_parameters(self, parameters: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Process function parameters for C++."""
        processed = []
        
        for param in parameters:
            processed_param = {
                "name": param.get("name", "param"),
                "type": self._map_cpp_type(param.get("type", "auto"))
            }
            processed.append(processed_param)
        
        return processed
    
    def _process_global_vars(self, global_vars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process global variables for C++."""
        processed = []
        
        for var in global_vars:
            processed_var = {
                "name": var.get("name", "var"),
                "type": self._map_cpp_type(var.get("type", "auto")),
                "value": var.get("value", ""),
                "is_const": var.get("is_const", False)
            }
            processed.append(processed_var)
        
        return processed
    
    def _generate_function_body(self, func: Dict[str, Any]) -> str:
        """Generate C++ function body from IR basic blocks."""
        # TODO: Implement function body generation in Milestone 4
        # This will convert IR basic blocks to C++ statements
        
        return "// TODO: Function body generation in Milestone 4"
    
    def _generate_main_function(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """Generate main function for C++ program."""
        return {
            "has_main": True,
            "body": "// TODO: Main function generation in Milestone 4",
            "return_type": "int"
        }
    
    def _map_cpp_type(self, python_type: str) -> str:
        """Map Python type to C++ type."""
        type_map = self._get_cpp_type_map()
        return type_map.get(python_type, "auto")
    
    def _generate_error_code(self, errors: List[str]) -> str:
        """Generate C++ code that reports transpilation errors."""
        error_code = """#include <iostream>
#include <string>

int main() {
    std::cout << "Py2CppAI Transpilation Errors:" << std::endl;
"""
        
        for error in errors:
            error_code += f'    std::cout << "Error: {error}" << std::endl;\n'
        
        error_code += """    return 1;
}
"""
        return error_code 