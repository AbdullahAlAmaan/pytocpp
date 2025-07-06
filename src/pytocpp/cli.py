"""
Command-line interface for Py2CppAI.
"""

import click
from pathlib import Path
from typing import Optional

from .transpiler import PyToCppTranspiler


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
def main(
    input_file: Path,
    output: Optional[Path],
    ai: bool,
    optimize: str,
    verbose: bool,
    benchmark: bool,
) -> None:
    """
    Transpile Python code to optimized C++17.
    
    INPUT_FILE: Python source file to transpile
    """
    if output is None:
        output = input_file.with_suffix(".cpp")
    
    if verbose:
        click.echo(f"Transpiling {input_file} -> {output}")
    
    # Always show key settings
    click.echo(f"AI mode: {'enabled' if ai else 'disabled'}")
    click.echo(f"Optimization level: -O{optimize}")
    
    try:
        transpiler = PyToCppTranspiler(
            ai_enabled=ai,
            optimization_level=int(optimize),
            verbose=verbose
        )
        
        # TODO: Implement actual transpilation
        click.echo("🚧 Transpilation not yet implemented - coming in Milestone 4!")
        click.echo(f"Would transpile: {input_file} -> {output}")
        
        if benchmark:
            click.echo("🚧 Benchmarking not yet implemented - coming in Milestone 7!")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main() 