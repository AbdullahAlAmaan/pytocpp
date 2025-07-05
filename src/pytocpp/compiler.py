"""
C++ compiler module (Milestone 4).

Responsible for compiling generated C++ code using GCC/Clang.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


class CppCompiler:
    """
    Compiles C++ code using GCC or Clang with optimization flags.
    
    This is the final step in the transpilation pipeline.
    """
    
    def __init__(self, optimization_level: int = 2):
        self.optimization_level = optimization_level
        self.compiler = self._detect_compiler()
        self.sanitizer_flags = self._get_sanitizer_flags()
    
    def compile(self, cpp_file: Path) -> Dict[str, Any]:
        """
        Compile C++ source file to executable.
        
        Args:
            cpp_file: Path to C++ source file
            
        Returns:
            Compilation results and executable path
        """
        if not cpp_file.exists():
            return {
                "success": False,
                "error": f"C++ source file not found: {cpp_file}",
                "executable": None,
                "warnings": [],
                "optimizations": []
            }
        
        # Generate output executable name
        output_file = cpp_file.with_suffix("")
        if self.compiler == "gcc":
            output_file = output_file.with_suffix("")
        else:
            output_file = output_file.with_suffix("")
        
        # Build compilation command
        cmd = self._build_compilation_command(cpp_file, output_file)
        
        try:
            # Run compilation
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "executable": output_file,
                    "warnings": self._parse_warnings(result.stderr),
                    "optimizations": self._get_applied_optimizations(),
                    "compiler": self.compiler,
                    "optimization_level": self.optimization_level
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "executable": None,
                    "warnings": self._parse_warnings(result.stderr),
                    "compiler": self.compiler
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Compilation timed out after 60 seconds",
                "executable": None,
                "compiler": self.compiler
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Compilation failed: {str(e)}",
                "executable": None,
                "compiler": self.compiler
            }
    
    def run_executable(self, executable: Path, args: List[str] = None) -> Dict[str, Any]:
        """
        Run compiled executable and capture output.
        
        Args:
            executable: Path to compiled executable
            args: Command line arguments
            
        Returns:
            Execution results
        """
        if not executable.exists():
            return {
                "success": False,
                "error": f"Executable not found: {executable}",
                "stdout": "",
                "stderr": "",
                "return_code": -1
            }
        
        if args is None:
            args = []
        
        try:
            result = subprocess.run(
                [str(executable)] + args,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "executable": str(executable)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timed out after 30 seconds",
                "stdout": "",
                "stderr": "",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "stdout": "",
                "stderr": "",
                "return_code": -1
            }
    
    def _detect_compiler(self) -> str:
        """Detect available C++ compiler (GCC or Clang)."""
        # Try GCC first
        try:
            result = subprocess.run(
                ["g++", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return "gcc"
        except FileNotFoundError:
            pass
        
        # Try Clang
        try:
            result = subprocess.run(
                ["clang++", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return "clang"
        except FileNotFoundError:
            pass
        
        # Default to GCC
        return "gcc"
    
    def _get_sanitizer_flags(self) -> List[str]:
        """Get sanitizer flags for better debugging."""
        return [
            "-fsanitize=address",  # Address sanitizer
            "-fsanitize=undefined",  # Undefined behavior sanitizer
            "-fno-omit-frame-pointer",  # Better stack traces
        ]
    
    def _build_compilation_command(self, input_file: Path, output_file: Path) -> List[str]:
        """Build the compilation command with all flags."""
        cmd = []
        
        # Compiler
        if self.compiler == "gcc":
            cmd.append("g++")
        else:
            cmd.append("clang++")
        
        # C++ standard
        cmd.extend(["-std=c++17"])
        
        # Optimization level
        cmd.extend([f"-O{self.optimization_level}"])
        
        # Warning flags
        cmd.extend([
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Werror=return-type"
        ])
        
        # Debug info
        cmd.extend(["-g"])
        
        # Sanitizer flags (only in debug builds)
        if self.optimization_level == 0:
            cmd.extend(self.sanitizer_flags)
        
        # Input and output files
        cmd.extend([str(input_file), "-o", str(output_file)])
        
        return cmd
    
    def _parse_warnings(self, stderr: str) -> List[str]:
        """Parse compiler warnings from stderr."""
        warnings = []
        
        for line in stderr.split('\n'):
            line = line.strip()
            if line and ('warning:' in line.lower() or 'note:' in line.lower()):
                warnings.append(line)
        
        return warnings
    
    def _get_applied_optimizations(self) -> List[str]:
        """Get list of optimizations applied by the compiler."""
        optimizations = []
        
        if self.optimization_level >= 1:
            optimizations.extend([
                "constant folding",
                "dead code elimination",
                "basic block optimization"
            ])
        
        if self.optimization_level >= 2:
            optimizations.extend([
                "loop optimization",
                "function inlining",
                "instruction scheduling"
            ])
        
        if self.optimization_level >= 3:
            optimizations.extend([
                "aggressive optimization",
                "link-time optimization (if available)"
            ])
        
        return optimizations
    
    def get_compiler_info(self) -> Dict[str, Any]:
        """Get information about the detected compiler."""
        try:
            if self.compiler == "gcc":
                result = subprocess.run(
                    ["g++", "--version"],
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ["clang++", "--version"],
                    capture_output=True,
                    text=True
                )
            
            version_line = result.stdout.split('\n')[0] if result.stdout else "Unknown"
            
            return {
                "compiler": self.compiler,
                "version": version_line,
                "available": True
            }
            
        except Exception:
            return {
                "compiler": self.compiler,
                "version": "Unknown",
                "available": False
            } 