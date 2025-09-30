"""
Codebase Context Generator
Generates intelligent context files from codebases for LLM consumption
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .main import (
    generate_context_file,
    scan_codebase,
    estimate_tokens,
    CODE_EXTENSIONS,
    SKIP_DIRS,
    SKIP_FILES
)

__all__ = [
    'generate_context_file',
    'scan_codebase',
    'estimate_tokens',
    'CODE_EXTENSIONS',
    'SKIP_DIRS',
    'SKIP_FILES'
]