"""
Tests for the CLI module.
"""

import pytest
from pathlib import Path
from click.testing import CliRunner
from src.pytocpp.cli import main


class TestCLI:
    """Test cases for CLI functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "Transpile Python code to optimized C++17" in result.output
    
    def test_cli_missing_input_file(self):
        """Test CLI with missing input file."""
        result = self.runner.invoke(main, [])
        assert result.exit_code != 0  # Should fail without input file
    
    def test_cli_nonexistent_input_file(self):
        """Test CLI with non-existent input file."""
        result = self.runner.invoke(main, ['nonexistent.py'])
        assert result.exit_code != 0
    
    def test_cli_basic_usage(self, tmp_path):
        """Test basic CLI usage with a simple Python file."""
        # Create a simple Python file
        python_file = tmp_path / "test.py"
        python_file.write_text("x = 42\nprint(x)")
        
        result = self.runner.invoke(main, [str(python_file)])
        assert result.exit_code == 0
        assert "🚧 Transpilation not yet implemented" in result.output
    
    def test_cli_with_output_option(self, tmp_path):
        """Test CLI with custom output file."""
        # Create a simple Python file
        python_file = tmp_path / "test.py"
        python_file.write_text("x = 42")
        
        output_file = tmp_path / "output.cpp"
        result = self.runner.invoke(main, [str(python_file), '--output', str(output_file)])
        assert result.exit_code == 0
    
    def test_cli_with_ai_option(self, tmp_path):
        """Test CLI with AI option enabled."""
        python_file = tmp_path / "test.py"
        python_file.write_text("x = 42")
        
        result = self.runner.invoke(main, [str(python_file), '--ai'])
        assert result.exit_code == 0
        assert "AI mode: enabled" in result.output
    
    def test_cli_with_optimization_level(self, tmp_path):
        """Test CLI with different optimization levels."""
        python_file = tmp_path / "test.py"
        python_file.write_text("x = 42")
        
        for level in ["0", "1", "2", "3"]:
            result = self.runner.invoke(main, [str(python_file), '--optimize', level])
            assert result.exit_code == 0
            assert f"Optimization level: -O{level}" in result.output
    
    def test_cli_with_verbose_option(self, tmp_path):
        """Test CLI with verbose output."""
        python_file = tmp_path / "test.py"
        python_file.write_text("x = 42")
        
        result = self.runner.invoke(main, [str(python_file), '--verbose'])
        assert result.exit_code == 0
        assert "Transpiling" in result.output
    
    def test_cli_with_benchmark_option(self, tmp_path):
        """Test CLI with benchmark option."""
        python_file = tmp_path / "test.py"
        python_file.write_text("x = 42")
        
        result = self.runner.invoke(main, [str(python_file), '--benchmark'])
        assert result.exit_code == 0
        assert "🚧 Benchmarking not yet implemented" in result.output
    
    def test_cli_invalid_optimization_level(self, tmp_path):
        """Test CLI with invalid optimization level."""
        python_file = tmp_path / "test.py"
        python_file.write_text("x = 42")
        
        result = self.runner.invoke(main, [str(python_file), '--optimize', '5'])
        assert result.exit_code != 0  # Should fail with invalid level 