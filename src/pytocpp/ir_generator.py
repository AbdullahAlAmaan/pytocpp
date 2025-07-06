"""
Intermediate Representation (IR) generator module (Milestone 3).

Responsible for converting AST into SSA-style 3-address IR for optimization.
"""

from typing import Dict, Any, List, Optional


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
        if not ast_node:
            return {"functions": [], "global_vars": [], "instructions": [], "basic_blocks": [], "cfg": {}}
        
        # Initialize IR structure
        ir = {
            "functions": [],
            "global_vars": [],
            "instructions": [],
            "basic_blocks": [],
            "cfg": {}
        }
        
        # Process module body
        if ast_node.get("node_type") == "Module":
            body = ast_node.get("body", [])
            
            # Separate global variables and functions
            global_vars = []
            functions = []
            
            for node in body:
                if node.get("node_type") == "FunctionDef":
                    functions.append(node)
                else:
                    global_vars.append(node)
            
            # Process global variables
            ir["global_vars"] = self._process_global_vars(global_vars, type_info)
            
            # Process functions
            for func_node in functions:
                func_ir = self._process_function(func_node, type_info)
                ir["functions"].append(func_ir)
        
        return ir
    
    def _process_global_vars(self, global_nodes: List[Dict[str, Any]], type_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Process global variable declarations."""
        global_vars = []
        
        for node in global_nodes:
            if node.get("node_type") == "Assign":
                targets = node.get("targets", [])
                value = node.get("value")
                
                for target in targets:
                    if target.get("node_type") == "Name":
                        var_name = target.get("id")
                        var_type = type_info.get(var_name, "auto")
                        
                        # Convert value to IR
                        value_ir = self._expression_to_ir(value, type_info)
                        
                        global_vars.append({
                            "name": var_name,
                            "type": var_type,
                            "value": value_ir,
                            "instruction": {
                                "opcode": "store",
                                "operands": [value_ir.get("result", "null"), var_name],
                                "result": None
                            }
                        })
        
        return global_vars
    
    def _process_function(self, func_node: Dict[str, Any], type_info: Dict[str, str]) -> Dict[str, Any]:
        """Process function definition."""
        func_name = func_node.get("name")
        args = func_node.get("args", {})
        body = func_node.get("body", [])
        returns = func_node.get("returns")
        
        # Get function type information
        return_type = "void"
        if returns:
            return_type = self._annotation_to_type(returns)
        elif f"{func_name}.return" in type_info:
            return_type = type_info[f"{func_name}.return"]
        
        # Create function IR
        func_ir = IRFunction(func_name, return_type)
        
        # Process parameters
        params = args.get("args", [])
        for param in params:
            param_name = param.get("arg")
            param_type = "auto"
            
            if param.get("annotation"):
                param_type = self._annotation_to_type(param.get("annotation"))
            elif f"{func_name}.{param_name}" in type_info:
                param_type = type_info[f"{func_name}.{param_name}"]
            
            func_ir.add_parameter(param_name, param_type)
        
        # Process function body
        self._process_statements(body, func_ir, type_info)
        
        return func_ir.to_dict()
    
    def _process_statements(self, statements: List[Dict[str, Any]], func_ir: IRFunction, type_info: Dict[str, str]) -> None:
        """Process a list of statements."""
        current_block = BasicBlock(self._new_block())
        func_ir.add_basic_block(current_block)
        
        for stmt in statements:
            if stmt.get("node_type") == "Assign":
                self._process_assignment(stmt, current_block, type_info)
            elif stmt.get("node_type") == "Return":
                self._process_return(stmt, current_block, type_info)
            elif stmt.get("node_type") == "If":
                self._process_if(stmt, func_ir, type_info)
            elif stmt.get("node_type") == "For":
                self._process_for(stmt, func_ir, type_info)
            elif stmt.get("node_type") == "While":
                self._process_while(stmt, func_ir, type_info)
            elif stmt.get("node_type") == "Expr":
                # Expression statement (function call, etc.)
                expr_ir = self._expression_to_ir(stmt.get("value"), type_info)
                if expr_ir.get("result"):
                    # Discard result
                    current_block.add_instruction(IRInstruction("nop", [], None))
    
    def _process_assignment(self, assign_node: Dict[str, Any], block: BasicBlock, type_info: Dict[str, str]) -> None:
        """Process assignment statement."""
        targets = assign_node.get("targets", [])
        value = assign_node.get("value")
        
        # Convert value to IR
        value_ir = self._expression_to_ir(value, type_info)
        
        # Assign to all targets
        for target in targets:
            if target.get("node_type") == "Name":
                var_name = target.get("id")
                var_type = type_info.get(var_name, "auto")
                
                # Create store instruction
                store_inst = IRInstruction("store", [value_ir.get("result", "null"), var_name], None)
                block.add_instruction(store_inst)
    
    def _process_return(self, return_node: Dict[str, Any], block: BasicBlock, type_info: Dict[str, str]) -> None:
        """Process return statement."""
        value = return_node.get("value")
        
        if value:
            # Convert return value to IR
            value_ir = self._expression_to_ir(value, type_info)
            return_inst = IRInstruction("return", [value_ir.get("result", "null")], None)
        else:
            return_inst = IRInstruction("return", [], None)
        
        block.add_instruction(return_inst)
    
    def _process_if(self, if_node: Dict[str, Any], func_ir: IRFunction, type_info: Dict[str, str]) -> None:
        """Process if statement."""
        test = if_node.get("test")
        body = if_node.get("body", [])
        orelse = if_node.get("orelse", [])
        
        # Convert test to IR
        test_ir = self._expression_to_ir(test, type_info)
        
        # Create basic blocks
        then_block = BasicBlock(self._new_block())
        else_block = BasicBlock(self._new_block())
        merge_block = BasicBlock(self._new_block())
        
        # Add conditional branch
        branch_inst = IRInstruction("branch", [test_ir.get("result", "null")], None)
        # Find current block and add branch
        current_block = func_ir.basic_blocks[-1]
        current_block.add_instruction(branch_inst)
        current_block.successors = [then_block.name, else_block.name]
        
        # Process then block
        func_ir.add_basic_block(then_block)
        self._process_statements(body, func_ir, type_info)
        
        # Process else block
        func_ir.add_basic_block(else_block)
        if orelse:
            self._process_statements(orelse, func_ir, type_info)
        
        # Add merge block
        func_ir.add_basic_block(merge_block)
        then_block.successors = [merge_block.name]
        else_block.successors = [merge_block.name]
        merge_block.predecessors = [then_block.name, else_block.name]
    
    def _process_for(self, for_node: Dict[str, Any], func_ir: IRFunction, type_info: Dict[str, str]) -> None:
        """Process for loop."""
        target = for_node.get("target")
        iter_expr = for_node.get("iter")
        body = for_node.get("body", [])
        
        # Create loop blocks
        init_block = BasicBlock(self._new_block())
        loop_block = BasicBlock(self._new_block())
        body_block = BasicBlock(self._new_block())
        exit_block = BasicBlock(self._new_block())
        
        # Initialize iterator
        iter_ir = self._expression_to_ir(iter_expr, type_info)
        init_inst = IRInstruction("init_iter", [iter_ir.get("result", "null")], self._new_temp())
        init_block.add_instruction(init_inst)
        
        # Loop condition
        has_next_inst = IRInstruction("has_next", [init_inst.result], self._new_temp())
        loop_block.add_instruction(has_next_inst)
        
        # Get next value
        next_inst = IRInstruction("get_next", [init_inst.result], self._new_temp())
        body_block.add_instruction(next_inst)
        
        # Assign to target
        if target.get("node_type") == "Name":
            target_name = target.get("id")
            assign_inst = IRInstruction("store", [next_inst.result, target_name], None)
            body_block.add_instruction(assign_inst)
        
        # Process loop body
        self._process_statements(body, func_ir, type_info)
        
        # Add blocks to function
        func_ir.add_basic_block(init_block)
        func_ir.add_basic_block(loop_block)
        func_ir.add_basic_block(body_block)
        func_ir.add_basic_block(exit_block)
        
        # Set up control flow
        init_block.successors = [loop_block.name]
        loop_block.successors = [body_block.name, exit_block.name]
        body_block.successors = [loop_block.name]
    
    def _process_while(self, while_node: Dict[str, Any], func_ir: IRFunction, type_info: Dict[str, str]) -> None:
        """Process while loop."""
        test = while_node.get("test")
        body = while_node.get("body", [])
        
        # Create loop blocks
        test_block = BasicBlock(self._new_block())
        body_block = BasicBlock(self._new_block())
        exit_block = BasicBlock(self._new_block())
        
        # Convert test to IR
        test_ir = self._expression_to_ir(test, type_info)
        test_inst = IRInstruction("branch", [test_ir.get("result", "null")], None)
        test_block.add_instruction(test_inst)
        
        # Process loop body
        self._process_statements(body, func_ir, type_info)
        
        # Add blocks to function
        func_ir.add_basic_block(test_block)
        func_ir.add_basic_block(body_block)
        func_ir.add_basic_block(exit_block)
        
        # Set up control flow
        test_block.successors = [body_block.name, exit_block.name]
        body_block.successors = [test_block.name]
    
    def _expression_to_ir(self, expr_node: Dict[str, Any], type_info: Dict[str, str]) -> Dict[str, Any]:
        """Convert expression to IR."""
        if not expr_node:
            return {"result": "null", "type": "auto"}
        
        node_type = expr_node.get("node_type")
        
        if node_type == "Constant":
            return self._constant_to_ir(expr_node)
        elif node_type == "Name":
            return self._name_to_ir(expr_node, type_info)
        elif node_type == "BinOp":
            return self._binop_to_ir(expr_node, type_info)
        elif node_type == "Call":
            return self._call_to_ir(expr_node, type_info)
        elif node_type == "List":
            return self._list_to_ir(expr_node, type_info)
        elif node_type == "Dict":
            return self._dict_to_ir(expr_node, type_info)
        else:
            # Unknown expression type
            temp = self._new_temp()
            return {"result": temp, "type": "auto"}
    
    def _constant_to_ir(self, const_node: Dict[str, Any]) -> Dict[str, Any]:
        """Convert constant to IR."""
        value = const_node.get("value")
        
        if type(value) is bool:
            return {"result": str(value), "type": "bool"}
        elif isinstance(value, int):
            return {"result": str(value), "type": "int"}
        elif isinstance(value, float):
            return {"result": str(value), "type": "float"}
        elif isinstance(value, str):
            return {"result": f'"{value}"', "type": "str"}
        elif value is None:
            return {"result": "null", "type": "void"}
        else:
            temp = self._new_temp()
            return {"result": temp, "type": "auto"}
    
    def _name_to_ir(self, name_node: Dict[str, Any], type_info: Dict[str, str]) -> Dict[str, Any]:
        """Convert variable name to IR."""
        var_name = name_node.get("id")
        var_type = type_info.get(var_name, "auto")
        
        return {"result": var_name, "type": var_type}
    
    def _binop_to_ir(self, binop_node: Dict[str, Any], type_info: Dict[str, str]) -> Dict[str, Any]:
        """Convert binary operation to IR."""
        left = binop_node.get("left")
        right = binop_node.get("right")
        op = binop_node.get("op", {})
        
        # Convert operands to IR
        left_ir = self._expression_to_ir(left, type_info)
        right_ir = self._expression_to_ir(right, type_info)
        
        # Map Python operators to IR opcodes
        op_map = {
            "Add": "add",
            "Sub": "sub", 
            "Mult": "mul",
            "Div": "div",
            "Mod": "mod",
            "Pow": "pow",
            "LShift": "shl",
            "RShift": "shr",
            "BitOr": "or",
            "BitXor": "xor",
            "BitAnd": "and",
            "FloorDiv": "floordiv"
        }
        
        opcode = op_map.get(op.get("node_type", ""), "unknown")
        result = self._new_temp()
        
        return {
            "result": result,
            "type": "auto",
            "instruction": IRInstruction(opcode, [left_ir.get("result"), right_ir.get("result")], result)
        }
    
    def _call_to_ir(self, call_node: Dict[str, Any], type_info: Dict[str, str]) -> Dict[str, Any]:
        """Convert function call to IR."""
        func = call_node.get("func")
        args = call_node.get("args", [])
        
        # Convert function name
        if func.get("node_type") == "Name":
            func_name = func.get("id")
        else:
            func_name = "unknown"
        
        # Convert arguments to IR
        arg_results = []
        for arg in args:
            arg_ir = self._expression_to_ir(arg, type_info)
            arg_results.append(arg_ir.get("result"))
        
        # Create call instruction
        result = self._new_temp()
        call_inst = IRInstruction("call", [func_name] + arg_results, result)
        
        return {
            "result": result,
            "type": "auto",
            "instruction": call_inst
        }
    
    def _list_to_ir(self, list_node: Dict[str, Any], type_info: Dict[str, str]) -> Dict[str, Any]:
        """Convert list literal to IR."""
        elements = list_node.get("elts", [])
        
        # Convert elements to IR
        element_results = []
        for element in elements:
            elem_ir = self._expression_to_ir(element, type_info)
            element_results.append(elem_ir.get("result"))
        
        # Create list instruction
        result = self._new_temp()
        list_inst = IRInstruction("create_list", element_results, result)
        
        return {
            "result": result,
            "type": "List[auto]",
            "instruction": list_inst
        }
    
    def _dict_to_ir(self, dict_node: Dict[str, Any], type_info: Dict[str, str]) -> Dict[str, Any]:
        """Convert dictionary literal to IR."""
        keys = dict_node.get("keys", [])
        values = dict_node.get("values", [])
        
        # Convert keys and values to IR
        key_results = []
        value_results = []
        
        for key in keys:
            key_ir = self._expression_to_ir(key, type_info)
            key_results.append(key_ir.get("result"))
        
        for value in values:
            value_ir = self._expression_to_ir(value, type_info)
            value_results.append(value_ir.get("result"))
        
        # Create dict instruction
        result = self._new_temp()
        dict_inst = IRInstruction("create_dict", key_results + value_results, result)
        
        return {
            "result": result,
            "type": "Dict[auto, auto]",
            "instruction": dict_inst
        }
    
    def _annotation_to_type(self, annotation: Dict[str, Any]) -> str:
        """Convert type annotation to type string."""
        if not annotation:
            return "auto"
        
        node_type = annotation.get("node_type")
        
        if node_type == "Name":
            return annotation.get("id", "auto")
        elif node_type == "Constant":
            return annotation.get("value", "auto")
        elif node_type == "Subscript":
            # Handle generic types like List[int]
            value = annotation.get("value", {})
            slice_val = annotation.get("slice", {})
            
            if value.get("node_type") == "Name":
                base_type = value.get("id", "auto")
                if slice_val:
                    slice_type = self._annotation_to_type(slice_val)
                    return f"{base_type}[{slice_type}]"
                return base_type
        
        return "auto"
    
    def _apply_optimizations(self, ir_code: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply optimizations to IR code.
        
        Args:
            ir_code: IR code to optimize
            
        Returns:
            List of applied optimizations
        """
        optimizations = []
        
        # Apply constant folding
        const_folding = self._constant_folding(ir_code)
        if const_folding:
            optimizations.append({
                "type": "constant_folding",
                "description": "Folded constant expressions",
                "details": const_folding
            })
        
        # Apply dead code elimination
        dead_code = self._dead_code_elimination(ir_code)
        if dead_code:
            optimizations.append({
                "type": "dead_code_elimination",
                "description": "Removed unreachable code",
                "details": dead_code
            })
        
        # Apply common subexpression elimination
        cse = self._common_subexpression_elimination(ir_code)
        if cse:
            optimizations.append({
                "type": "common_subexpression_elimination",
                "description": "Eliminated redundant expressions",
                "details": cse
            })
        
        return optimizations
    
    def _constant_folding(self, ir_code: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply constant folding optimization."""
        folded = []
        
        # Process functions
        for func in ir_code.get("functions", []):
            for block in func.get("basic_blocks", []):
                instructions = block.get("instructions", [])
                i = 0
                while i < len(instructions):
                    inst = instructions[i]
                    
                    # Check for binary operations with constant operands
                    if inst.get("opcode") in ["add", "sub", "mul", "div", "mod"]:
                        op1, op2 = inst.get("operands", [])
                        result = inst.get("result")
                        
                        # Try to evaluate constant expressions
                        try:
                            if op1.isdigit() and op2.isdigit():
                                val1, val2 = int(op1), int(op2)
                                if inst["opcode"] == "add":
                                    folded_val = val1 + val2
                                elif inst["opcode"] == "sub":
                                    folded_val = val1 - val2
                                elif inst["opcode"] == "mul":
                                    folded_val = val1 * val2
                                elif inst["opcode"] == "div" and val2 != 0:
                                    folded_val = val1 // val2
                                elif inst["opcode"] == "mod" and val2 != 0:
                                    folded_val = val1 % val2
                                else:
                                    i += 1
                                    continue
                                
                                # Replace with constant
                                instructions[i] = {
                                    "opcode": "const",
                                    "operands": [str(folded_val)],
                                    "result": result
                                }
                                
                                folded.append({
                                    "original": inst,
                                    "folded": str(folded_val),
                                    "location": f"{func.get('name')}.{block.get('name')}"
                                })
                        except (ValueError, ZeroDivisionError):
                            pass
                    
                    i += 1
        
        return folded
    
    def _dead_code_elimination(self, ir_code: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply dead code elimination optimization."""
        eliminated = []
        
        # Process functions
        for func in ir_code.get("functions", []):
            for block in func.get("basic_blocks", []):
                instructions = block.get("instructions", [])
                i = 0
                while i < len(instructions):
                    inst = instructions[i]
                    
                    # Check for unreachable code after return
                    if inst.get("opcode") == "return":
                        # Remove all instructions after return in this block
                        removed_count = len(instructions) - i - 1
                        if removed_count > 0:
                            instructions[i+1:] = []
                            eliminated.append({
                                "type": "unreachable_after_return",
                                "count": removed_count,
                                "location": f"{func.get('name')}.{block.get('name')}"
                            })
                        break
                    
                    # Check for unused temporary variables
                    if inst.get("result") and inst.get("result").startswith("t"):
                        result = inst.get("result")
                        used = False
                        
                        # Check if this temp is used in subsequent instructions
                        for j in range(i + 1, len(instructions)):
                            if result in instructions[j].get("operands", []):
                                used = True
                                break
                        
                        if not used:
                            eliminated.append({
                                "type": "unused_temp",
                                "temp": result,
                                "location": f"{func.get('name')}.{block.get('name')}"
                            })
                            # Remove the instruction
                            instructions.pop(i)
                            continue
                    
                    i += 1
        
        return eliminated
    
    def _common_subexpression_elimination(self, ir_code: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply common subexpression elimination optimization."""
        eliminated = []
        
        # Process functions
        for func in ir_code.get("functions", []):
            for block in func.get("basic_blocks", []):
                instructions = block.get("instructions", [])
                i = 0
                while i < len(instructions):
                    inst = instructions[i]
                    
                    # Check for common subexpressions
                    if inst.get("opcode") in ["add", "sub", "mul", "div", "mod"]:
                        opcode = inst.get("opcode")
                        operands = inst.get("operands", [])
                        
                        # Look for identical expressions earlier in the block
                        for j in range(i):
                            prev_inst = instructions[j]
                            if (prev_inst.get("opcode") == opcode and 
                                prev_inst.get("operands") == operands):
                                
                                # Replace with reference to previous result
                                result = inst.get("result")
                                prev_result = prev_inst.get("result")
                                
                                instructions[i] = {
                                    "opcode": "copy",
                                    "operands": [prev_result],
                                    "result": result
                                }
                                
                                eliminated.append({
                                    "type": "common_subexpression",
                                    "original": inst,
                                    "reused": prev_result,
                                    "location": f"{func.get('name')}.{block.get('name')}"
                                })
                                break
                    
                    i += 1
        
        return eliminated
    
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