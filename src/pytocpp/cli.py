"""
Command-line interface for Py2CppAI.
"""

import click
from pathlib import Path
from typing import Optional
import keyword

from .transpiler import PyToCppTranspiler
from .parser import PythonParser
from .type_checker import TypeChecker
from .ir_generator import IRGenerator


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o", 
    type=click.Path(path_type=Path), 
    help="Output C++ file path (default: input_file.cpp)"
)
@click.option(
    "--ai", 
    is_flag=True, 
    help="Enable AI-powered type inference and optimizations"
)
@click.option(
    "--ollama-model",
    default="wizardlm2:latest",
    help="Ollama model to use for AI type inference (default: wizardlm2:latest)"
)
@click.option(
    "--optimize", "-O", 
    type=click.Choice(["0", "1", "2", "3"]), 
    default="2",
    help="C++ optimization level (default: 2)"
)
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Enable verbose output"
)
@click.option(
    "--benchmark", 
    is_flag=True, 
    help="Run performance benchmark comparison"
)
@click.option(
    "--type-check-only", 
    is_flag=True, 
    help="Only run type checking, don't transpile"
)
@click.option(
    "--ir-only", 
    is_flag=True, 
    help="Generate IR and show it, don't transpile"
)
def main(
    input_file: Path,
    output: Optional[Path],
    ai: bool,
    ollama_model: str,
    optimize: str,
    verbose: bool,
    benchmark: bool,
    type_check_only: bool,
    ir_only: bool,
) -> None:
    """
    Transpile Python code to optimized C++17.
    
    INPUT_FILE: Python source file to transpile
    """
    if output is None:
        output = input_file.with_suffix(".cpp")
    
    if verbose:
        click.echo(f"Processing {input_file}")
        if not type_check_only:
            click.echo(f"Output will be: {output}")
    
            # Always show key settings
        click.echo(f"AI mode: {'enabled' if ai else 'disabled'}")
        if ai:
            click.echo(f"Ollama model: {ollama_model}")
        if not type_check_only:
            click.echo(f"Optimization level: -O{optimize}")
    
    try:
        # Step 1: Parse the Python code
        if verbose:
            click.echo("\n🔍 Step 1: Parsing Python code...")
        
        parser = PythonParser()
        parse_result = parser.parse_file(input_file)
        
        if not parse_result["parse_success"]:
            click.echo("❌ Parse failed!")
            for error in parse_result["errors"]:
                click.echo(f"  Error: {error}")
            raise click.Abort()
        
        if verbose:
            click.echo("✅ Parse successful")
        
        # Step 2: Type checking
        if verbose:
            click.echo("\n🔍 Step 2: Type analysis...")
        
        type_checker = TypeChecker(ai_enabled=ai, ollama_model=ollama_model)
        type_result = type_checker.analyze(parse_result)
        
        if not type_result["success"]:
            click.echo("❌ Type analysis failed!")
            for error in type_result.get("errors", []):
                click.echo(f"  Error: {error}")
            raise click.Abort()
        
        # Final filter for built-ins/keywords before display
        builtins_and_keywords = set(dir(__builtins__)) | set(keyword.kwlist)
        def is_user_symbol(name):
            return name.split(".")[0] not in builtins_and_keywords
        
        if verbose:
            click.echo("✅ Type analysis successful")
            
            # Show type information
            type_info = type_result["type_info"]
            if type_info:
                click.echo("\n📊 Type Information:")
                for var_name, var_type in type_info.items():
                    if not is_user_symbol(var_name):
                        continue
                    confidence = type_result["confidence_scores"].get(var_name, 0.0)
                    click.echo(f"  {var_name}: {var_type} (confidence: {confidence:.2f})")
            else:
                click.echo("  No type information found")
            
            # Show AI suggestions if any
            ai_suggestions = type_result.get("ai_suggestions", [])
            if ai_suggestions:
                click.echo("\n🤖 AI Type Suggestions:")
                for suggestion in ai_suggestions:
                    var_name = suggestion["variable"]
                    if not is_user_symbol(var_name):
                        continue
                    var_type = suggestion["type"]
                    confidence = suggestion["confidence"]
                    click.echo(f"  {var_name}: {var_type} (confidence: {confidence:.2f})")
        
        if type_check_only:
            click.echo("\n✅ Type checking completed successfully!")
            return
        
        # Step 3: IR Generation
        if verbose:
            click.echo("\n🔍 Step 3: IR Generation...")
        
        ir_generator = IRGenerator()
        ir_result = ir_generator.generate(parse_result, type_result)
        
        if not ir_result["success"]:
            click.echo("❌ IR generation failed!")
            for error in ir_result.get("errors", []):
                click.echo(f"  Error: {error}")
            raise click.Abort()
        
        if verbose:
            click.echo("✅ IR generation successful")
            
            # Show IR statistics
            metadata = ir_result["metadata"]
            click.echo(f"\n📊 IR Statistics:")
            click.echo(f"  Functions: {metadata['functions']}")
            click.echo(f"  Basic blocks: {metadata['basic_blocks']}")
            click.echo(f"  Temporary variables: {metadata['temp_vars_used']}")
            
            # Show optimizations
            optimizations = ir_result["optimizations"]
            if optimizations:
                click.echo(f"\n⚡ Applied Optimizations:")
                for opt in optimizations:
                    click.echo(f"  {opt['description']}")
                    if opt.get('details'):
                        for detail in opt['details'][:3]:  # Show first 3 details
                            click.echo(f"    - {detail}")
                        if len(opt['details']) > 3:
                            click.echo(f"    ... and {len(opt['details']) - 3} more")
        
        if ir_only:
            click.echo("\n✅ IR generation completed successfully!")
            return
        
        # TODO: Implement actual transpilation (Milestone 4)
        click.echo("\n🚧 Transpilation not yet implemented - coming in Milestone 4!")
        click.echo(f"Would transpile: {input_file} -> {output}")
        
        if benchmark:
            click.echo("🚧 Benchmarking not yet implemented - coming in Milestone 7!")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main() 