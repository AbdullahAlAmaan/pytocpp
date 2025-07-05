"""
Main transpiler class that orchestrates the Python to C++ conversion pipeline.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .parser import PythonParser
from .type_checker import TypeChecker
from .ir_generator import IRGenerator
from .code_generator import CppCodeGenerator
from .compiler import CppCompiler


class PyToCppTranspiler:
    """
    Main transpiler that converts Python code to optimized C++17.
    
    Pipeline:
    1. Parse Python AST
    2. Type checking and inference
    3. Generate Intermediate Representation
    4. Generate C++ code
    5. Compile and optimize
    """
    
    def __init__(
        self,
        ai_enabled: bool = False,
        optimization_level: int = 2,
        verbose: bool = False
    ):
        self.ai_enabled = ai_enabled
        self.optimization_level = optimization_level
        self.verbose = verbose
        
        # Initialize pipeline components
        self.parser = PythonParser()
        self.type_checker = TypeChecker(ai_enabled=ai_enabled)
        self.ir_generator = IRGenerator()
        self.code_generator = CppCodeGenerator()
        self.compiler = CppCompiler(optimization_level=optimization_level)
    
    def transpile(self, input_file: Path, output_file: Path) -> Dict[str, Any]:
        """
        Transpile a Python file to C++.
        
        Args:
            input_file: Path to Python source file
            output_file: Path for output C++ file
            
        Returns:
            Dictionary with transpilation results and metrics
        """
        if self.verbose:
            print(f"Starting transpilation: {input_file} -> {output_file}")
        
        # Step 1: Parse Python AST
        if self.verbose:
            print("Step 1: Parsing Python AST...")
        ast_tree = self.parser.parse_file(input_file)
        
        # Step 2: Type checking and inference
        if self.verbose:
            print("Step 2: Type checking and inference...")
        type_info = self.type_checker.analyze(ast_tree)
        
        # Step 3: Generate Intermediate Representation
        if self.verbose:
            print("Step 3: Generating IR...")
        ir_code = self.ir_generator.generate(ast_tree, type_info)
        
        # Step 4: Generate C++ code
        if self.verbose:
            print("Step 4: Generating C++ code...")
        cpp_code = self.code_generator.generate(ir_code)
        
        # Step 5: Write C++ file
        output_file.write_text(cpp_code)
        
        # Step 6: Compile (optional)
        compile_result = None
        if self.verbose:
            print("Step 6: Compiling C++ code...")
            compile_result = self.compiler.compile(output_file)
        
        return {
            "input_file": str(input_file),
            "output_file": str(output_file),
            "ast_tree": ast_tree,
            "type_info": type_info,
            "ir_code": ir_code,
            "cpp_code": cpp_code,
            "compile_result": compile_result,
            "success": True
        }
    
    def benchmark(self, input_file: Path) -> Dict[str, Any]:
        """
        Run performance benchmark comparing Python vs C++ versions.
        
        Args:
            input_file: Path to Python source file
            
        Returns:
            Dictionary with benchmark results
        """
        # TODO: Implement benchmarking in Milestone 7
        raise NotImplementedError("Benchmarking will be implemented in Milestone 7") 