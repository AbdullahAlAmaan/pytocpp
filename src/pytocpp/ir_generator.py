"""
Intermediate Representation (IR) generator module (Milestone 3).

Responsible for converting AST into SSA-style 3-address IR for optimization.
"""

from typing import Dict, Any, List, Optional


class IRGenerator:
    """
    Generates SSA-style 3-address Intermediate Representation from AST.
    
    This is the third step in the transpilation pipeline.
    """
    
    def __init__(self):
        self.temp_counter = 0
        self.block_counter = 0
        self.function_counter = 0
        
    def generate(self, ast_data: Dict[str, Any], type_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate IR from AST and type information.
        
        Args:
            ast_data: AST data from parser
            type_info: Type information from type checker
            
        Returns:
            IR representation in dictionary format
        """
        if not ast_data.get("parse_success", False):
            return {
                "success": False,
                "errors": ast_data.get("errors", []),
                "ir": {},
                "optimizations": []
            }
        
        # Reset counters
        self.temp_counter = 0
        self.block_counter = 0
        self.function_counter = 0
        
        # Generate IR from AST
        ir_code = self._ast_to_ir(ast_data["ast"], type_info.get("type_info", {}))
        
        # Apply optimizations
        optimizations = self._apply_optimizations(ir_code)
        
        return {
            "success": True,
            "ir": ir_code,
            "optimizations": optimizations,
            "metadata": {
                "temp_vars_used": self.temp_counter,
                "basic_blocks": self.block_counter,
                "functions": self.function_counter
            }
        }
    
    def _ast_to_ir(self, ast_node: Dict[str, Any], type_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Convert AST node to IR representation.
        
        Args:
            ast_node: AST node in dictionary format
            type_info: Type information dictionary
            
        Returns:
            IR representation
        """
        # TODO: Implement AST to IR conversion in Milestone 3
        # This will create:
        # - Basic blocks with 3-address instructions
        # - SSA form with phi nodes
        # - Control flow graph
        # - Function definitions and calls
        
        return {
            "functions": [],
            "global_vars": [],
            "instructions": [],
            "basic_blocks": [],
            "cfg": {}
        }
    
    def _apply_optimizations(self, ir_code: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply optimizations to IR code.
        
        Args:
            ir_code: IR code to optimize
            
        Returns:
            List of applied optimizations
        """
        optimizations = []
        
        # TODO: Implement IR optimizations in Milestone 3
        # This will include:
        # - Constant folding
        # - Dead code elimination
        # - Common subexpression elimination
        # - Loop optimizations (for Milestone 6)
        
        return optimizations
    
    def _new_temp(self, type_name: str = "auto") -> str:
        """
        Generate a new temporary variable name.
        
        Args:
            type_name: Type of the temporary variable
            
        Returns:
            Temporary variable name
        """
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def _new_block(self) -> str:
        """
        Generate a new basic block name.
        
        Args:
            Basic block name
        """
        self.block_counter += 1
        return f"block_{self.block_counter}"
    
    def _new_function(self) -> str:
        """
        Generate a new function name.
        
        Args:
            Function name
        """
        self.function_counter += 1
        return f"func_{self.function_counter}"


class IRInstruction:
    """Represents a single IR instruction."""
    
    def __init__(self, opcode: str, operands: List[str], result: Optional[str] = None):
        self.opcode = opcode
        self.operands = operands
        self.result = result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "opcode": self.opcode,
            "operands": self.operands,
            "result": self.result
        }


class BasicBlock:
    """Represents a basic block in the IR."""
    
    def __init__(self, name: str):
        self.name = name
        self.instructions: List[IRInstruction] = []
        self.predecessors: List[str] = []
        self.successors: List[str] = []
    
    def add_instruction(self, instruction: IRInstruction) -> None:
        """Add an instruction to this basic block."""
        self.instructions.append(instruction)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "instructions": [inst.to_dict() for inst in self.instructions],
            "predecessors": self.predecessors,
            "successors": self.successors
        }


class IRFunction:
    """Represents a function in the IR."""
    
    def __init__(self, name: str, return_type: str = "void"):
        self.name = name
        self.return_type = return_type
        self.parameters: List[Dict[str, str]] = []
        self.basic_blocks: List[BasicBlock] = []
        self.local_vars: Dict[str, str] = {}
    
    def add_parameter(self, name: str, type_name: str) -> None:
        """Add a parameter to this function."""
        self.parameters.append({"name": name, "type": type_name})
    
    def add_basic_block(self, block: BasicBlock) -> None:
        """Add a basic block to this function."""
        self.basic_blocks.append(block)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "return_type": self.return_type,
            "parameters": self.parameters,
            "basic_blocks": [block.to_dict() for block in self.basic_blocks],
            "local_vars": self.local_vars
        } 