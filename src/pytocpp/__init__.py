"""
Py2CppAI - AI-powered Python to C++ transpiler for 20-60x speed-ups

A one-command transpiler that turns a safe subset of Python into modern, 
readable C++17 with AI-suggested types and performance hints.
"""

__version__ = "0.1.0"
__author__ = "Py2CppAI Contributors"
__email__ = "team@pytocpp.ai"

from .cli import main

__all__ = ["main"] 