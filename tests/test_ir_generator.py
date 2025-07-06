"""
Tests for the IR generator module (Milestone 3).
"""

import pytest
from unittest.mock import patch, MagicMock

from pytocpp.ir_generator import IRGenerator, IRInstruction, BasicBlock, IRFunction


class TestIRGenerator:
    """Test cases for the IRGenerator class."""
    
    def test_init(self):
        """Test IRGenerator initialization."""
        generator = IRGenerator()
        assert generator.temp_counter == 0
        assert generator.block_counter == 0
        assert generator.function_counter == 0
    
    def test_generate_with_invalid_ast(self):
        """Test generate with invalid AST data."""
        generator = IRGenerator()
        
        # Test with failed parse
        invalid_data = {
            "parse_success": False,
            "errors": ["Parse error"]
        }
        
        result = generator.generate(invalid_data, {})
        
        assert result["success"] is False
        assert result["errors"] == ["Parse error"]
        assert result["ir"] == {}
        assert result["optimizations"] == []
    
    def test_ast_to_ir_empty(self):
        """Test AST to IR conversion with empty AST."""
        generator = IRGenerator()
        
        result = generator._ast_to_ir({}, {})
        
        assert result["functions"] == []
        assert result["global_vars"] == []
        assert result["instructions"] == []
        assert result["basic_blocks"] == []
        assert result["cfg"] == {}
    
    def test_ast_to_ir_simple_module(self):
        """Test AST to IR conversion with simple module."""
        generator = IRGenerator()
        
        ast_data = {
            "node_type": "Module",
            "body": [
                {
                    "node_type": "Assign",
                    "targets": [{"node_type": "Name", "id": "x"}],
                    "value": {"node_type": "Constant", "value": 42}
                }
            ]
        }
        
        type_info = {"x": "int"}
        
        result = generator._ast_to_ir(ast_data, type_info)
        
        assert len(result["global_vars"]) == 1
        assert result["global_vars"][0]["name"] == "x"
        assert result["global_vars"][0]["type"] == "int"
    
    def test_ast_to_ir_function(self):
        """Test AST to IR conversion with function definition."""
        generator = IRGenerator()
        
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
                    "body": [
                        {
                            "node_type": "Return",
                            "value": {
                                "node_type": "BinOp",
                                "left": {"node_type": "Name", "id": "a"},
                                "right": {"node_type": "Name", "id": "b"},
                                "op": {"node_type": "Add"}
                            }
                        }
                    ],
                    "returns": {"node_type": "Name", "id": "int"}
                }
            ]
        }
        
        type_info = {
            "add.a": "int",
            "add.b": "int",
            "add.return": "int"
        }
        
        result = generator._ast_to_ir(ast_data, type_info)
        
        assert len(result["functions"]) == 1
        func = result["functions"][0]
        assert func["name"] == "add"
        assert func["return_type"] == "int"
        assert len(func["parameters"]) == 2
    
    def test_constant_to_ir(self):
        """Test constant to IR conversion."""
        generator = IRGenerator()
        
        # Test different constant types
        int_const = {"node_type": "Constant", "value": 42}
        float_const = {"node_type": "Constant", "value": 3.14}
        str_const = {"node_type": "Constant", "value": "hello"}
        bool_const = {"node_type": "Constant", "value": True}
        none_const = {"node_type": "Constant", "value": None}
        
        assert generator._constant_to_ir(int_const)["result"] == "42"
        assert generator._constant_to_ir(int_const)["type"] == "int"
        assert generator._constant_to_ir(float_const)["result"] == "3.14"
        assert generator._constant_to_ir(float_const)["type"] == "float"
        assert generator._constant_to_ir(str_const)["result"] == '"hello"'
        assert generator._constant_to_ir(str_const)["type"] == "str"
        assert generator._constant_to_ir(bool_const)["result"] == "True"
        assert generator._constant_to_ir(bool_const)["type"] == "bool"
        assert generator._constant_to_ir(none_const)["result"] == "null"
        assert generator._constant_to_ir(none_const)["type"] == "void"
    
    def test_name_to_ir(self):
        """Test variable name to IR conversion."""
        generator = IRGenerator()
        
        name_node = {"node_type": "Name", "id": "x"}
        type_info = {"x": "int"}
        
        result = generator._name_to_ir(name_node, type_info)
        
        assert result["result"] == "x"
        assert result["type"] == "int"
    
    def test_binop_to_ir(self):
        """Test binary operation to IR conversion."""
        generator = IRGenerator()
        
        binop_node = {
            "node_type": "BinOp",
            "left": {"node_type": "Constant", "value": 1},
            "right": {"node_type": "Constant", "value": 2},
            "op": {"node_type": "Add"}
        }
        
        result = generator._binop_to_ir(binop_node, {})
        
        assert result["result"].startswith("t")
        assert result["type"] == "auto"
        assert result["instruction"].opcode == "add"
        assert result["instruction"].operands == ["1", "2"]
    
    def test_call_to_ir(self):
        """Test function call to IR conversion."""
        generator = IRGenerator()
        
        call_node = {
            "node_type": "Call",
            "func": {"node_type": "Name", "id": "len"},
            "args": [{"node_type": "Constant", "value": "hello"}]
        }
        
        result = generator._call_to_ir(call_node, {})
        
        assert result["result"].startswith("t")
        assert result["type"] == "auto"
        assert result["instruction"].opcode == "call"
        assert result["instruction"].operands[0] == "len"
    
    def test_list_to_ir(self):
        """Test list literal to IR conversion."""
        generator = IRGenerator()
        
        list_node = {
            "node_type": "List",
            "elts": [
                {"node_type": "Constant", "value": 1},
                {"node_type": "Constant", "value": 2}
            ]
        }
        
        result = generator._list_to_ir(list_node, {})
        
        assert result["result"].startswith("t")
        assert result["type"] == "List[auto]"
        assert result["instruction"].opcode == "create_list"
        assert len(result["instruction"].operands) == 2
    
    def test_dict_to_ir(self):
        """Test dictionary literal to IR conversion."""
        generator = IRGenerator()
        
        dict_node = {
            "node_type": "Dict",
            "keys": [{"node_type": "Constant", "value": "key"}],
            "values": [{"node_type": "Constant", "value": "value"}]
        }
        
        result = generator._dict_to_ir(dict_node, {})
        
        assert result["result"].startswith("t")
        assert result["type"] == "Dict[auto, auto]"
        assert result["instruction"].opcode == "create_dict"
        assert len(result["instruction"].operands) == 2
    
    def test_annotation_to_type(self):
        """Test type annotation conversion."""
        generator = IRGenerator()
        
        # Simple type
        simple_ann = {"node_type": "Name", "id": "int"}
        assert generator._annotation_to_type(simple_ann) == "int"
        
        # Generic type
        generic_ann = {
            "node_type": "Subscript",
            "value": {"node_type": "Name", "id": "List"},
            "slice": {"node_type": "Name", "id": "int"}
        }
        assert generator._annotation_to_type(generic_ann) == "List[int]"
        
        # None annotation
        assert generator._annotation_to_type(None) == "auto"
    
    def test_constant_folding(self):
        """Test constant folding optimization."""
        generator = IRGenerator()
        
        ir_code = {
            "functions": [
                {
                    "name": "test",
                    "basic_blocks": [
                        {
                            "name": "block_1",
                            "instructions": [
                                {"opcode": "add", "operands": ["5", "3"], "result": "t1"},
                                {"opcode": "mul", "operands": ["2", "4"], "result": "t2"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = generator._constant_folding(ir_code)
        
        assert len(result) == 2
        assert result[0]["folded"] == "8"  # 5 + 3
        assert result[1]["folded"] == "8"  # 2 * 4
    
    def test_dead_code_elimination(self):
        """Test dead code elimination optimization."""
        generator = IRGenerator()
        
        ir_code = {
            "functions": [
                {
                    "name": "test",
                    "basic_blocks": [
                        {
                            "name": "block_1",
                            "instructions": [
                                {"opcode": "return", "operands": ["42"], "result": None},
                                {"opcode": "add", "operands": ["1", "2"], "result": "t1"},  # Dead code
                                {"opcode": "store", "operands": ["t1", "x"], "result": None}  # Dead code
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = generator._dead_code_elimination(ir_code)
        
        assert len(result) == 1
        assert result[0]["type"] == "unreachable_after_return"
        assert result[0]["count"] == 2
    
    def test_common_subexpression_elimination(self):
        """Test common subexpression elimination optimization."""
        generator = IRGenerator()
        
        ir_code = {
            "functions": [
                {
                    "name": "test",
                    "basic_blocks": [
                        {
                            "name": "block_1",
                            "instructions": [
                                {"opcode": "add", "operands": ["a", "b"], "result": "t1"},
                                {"opcode": "add", "operands": ["a", "b"], "result": "t2"},  # Common subexpression
                                {"opcode": "mul", "operands": ["x", "y"], "result": "t3"},
                                {"opcode": "mul", "operands": ["x", "y"], "result": "t4"}  # Common subexpression
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = generator._common_subexpression_elimination(ir_code)
        
        assert len(result) == 2
        assert result[0]["reused"] == "t1"
        assert result[1]["reused"] == "t3"
    
    def test_new_temp(self):
        """Test temporary variable generation."""
        generator = IRGenerator()
        
        temp1 = generator._new_temp()
        temp2 = generator._new_temp()
        
        assert temp1 == "t1"
        assert temp2 == "t2"
        assert generator.temp_counter == 2
    
    def test_new_block(self):
        """Test basic block generation."""
        generator = IRGenerator()
        
        block1 = generator._new_block()
        block2 = generator._new_block()
        
        assert block1 == "block_1"
        assert block2 == "block_2"
        assert generator.block_counter == 2
    
    def test_new_function(self):
        """Test function generation."""
        generator = IRGenerator()
        
        func1 = generator._new_function()
        func2 = generator._new_function()
        
        assert func1 == "func_1"
        assert func2 == "func_2"
        assert generator.function_counter == 2
    
    def test_generate_complete_workflow(self):
        """Test complete IR generation workflow."""
        generator = IRGenerator()
        
        # Mock parse result
        parse_result = {
            "parse_success": True,
            "ast": {
                "node_type": "Module",
                "body": [
                    {
                        "node_type": "Assign",
                        "targets": [{"node_type": "Name", "id": "x"}],
                        "value": {"node_type": "Constant", "value": 42}
                    }
                ]
            }
        }
        
        type_result = {
            "success": True,
            "type_info": {"x": "int"}
        }
        
        result = generator.generate(parse_result, type_result)
        
        assert result["success"] is True
        assert "ir" in result
        assert "optimizations" in result
        assert "metadata" in result


class TestIRInstruction:
    """Test cases for IRInstruction class."""
    
    def test_init(self):
        """Test IRInstruction initialization."""
        inst = IRInstruction("add", ["a", "b"], "result")
        
        assert inst.opcode == "add"
        assert inst.operands == ["a", "b"]
        assert inst.result == "result"
    
    def test_to_dict(self):
        """Test IRInstruction to_dict conversion."""
        inst = IRInstruction("add", ["a", "b"], "result")
        
        result = inst.to_dict()
        
        assert result["opcode"] == "add"
        assert result["operands"] == ["a", "b"]
        assert result["result"] == "result"


class TestBasicBlock:
    """Test cases for BasicBlock class."""
    
    def test_init(self):
        """Test BasicBlock initialization."""
        block = BasicBlock("test_block")
        
        assert block.name == "test_block"
        assert block.instructions == []
        assert block.predecessors == []
        assert block.successors == []
    
    def test_add_instruction(self):
        """Test adding instruction to basic block."""
        block = BasicBlock("test_block")
        inst = IRInstruction("add", ["a", "b"], "result")
        
        block.add_instruction(inst)
        
        assert len(block.instructions) == 1
        assert block.instructions[0] == inst
    
    def test_to_dict(self):
        """Test BasicBlock to_dict conversion."""
        block = BasicBlock("test_block")
        inst = IRInstruction("add", ["a", "b"], "result")
        block.add_instruction(inst)
        
        result = block.to_dict()
        
        assert result["name"] == "test_block"
        assert len(result["instructions"]) == 1
        assert result["instructions"][0]["opcode"] == "add"


class TestIRFunction:
    """Test cases for IRFunction class."""
    
    def test_init(self):
        """Test IRFunction initialization."""
        func = IRFunction("test_func", "int")
        
        assert func.name == "test_func"
        assert func.return_type == "int"
        assert func.parameters == []
        assert func.basic_blocks == []
        assert func.local_vars == {}
    
    def test_add_parameter(self):
        """Test adding parameter to function."""
        func = IRFunction("test_func", "int")
        
        func.add_parameter("x", "int")
        func.add_parameter("y", "float")
        
        assert len(func.parameters) == 2
        assert func.parameters[0]["name"] == "x"
        assert func.parameters[0]["type"] == "int"
        assert func.parameters[1]["name"] == "y"
        assert func.parameters[1]["type"] == "float"
    
    def test_add_basic_block(self):
        """Test adding basic block to function."""
        func = IRFunction("test_func", "int")
        block = BasicBlock("test_block")
        
        func.add_basic_block(block)
        
        assert len(func.basic_blocks) == 1
        assert func.basic_blocks[0] == block
    
    def test_to_dict(self):
        """Test IRFunction to_dict conversion."""
        func = IRFunction("test_func", "int")
        func.add_parameter("x", "int")
        block = BasicBlock("test_block")
        func.add_basic_block(block)
        
        result = func.to_dict()
        
        assert result["name"] == "test_func"
        assert result["return_type"] == "int"
        assert len(result["parameters"]) == 1
        assert len(result["basic_blocks"]) == 1


if __name__ == "__main__":
    pytest.main([__file__]) 