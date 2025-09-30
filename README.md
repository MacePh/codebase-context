# Codebase Context Generator

Generate intelligent codebase context files optimized for Large Language Models like Qwen-Coder-30B, Claude, GPT-4, etc.

## Features

✅ Smart file selection with token budgeting
 ✅ Automatic exclusion of build artifacts and dependencies
 ✅ Priority file support
 ✅ Visual project structure tree
 ✅ Comprehensive statistics and summaries
 ✅ Customizable file type filtering

## Installation

```bash
pip install -e .
```

This installs the `codebase-context` command globally on your system.

## Usage

### Basic Usage

```bash
# Scan current directory
codebase-context

# Scan specific directory
codebase-context /path/to/your/project

# Custom output file
codebase-context -o my-project-context.txt
```

### Advanced Usage

```bash
# Set token limit (for different LLM context windows)
codebase-context --max-tokens 50000

# Filter specific file types only
codebase-context -e .py .js .html

# Prioritize specific files (included first)
codebase-context -p main.py utils.py config.py

# Exclude tree structure (saves tokens)
codebase-context --no-tree

# Complete example
codebase-context ./my-app \
  -o app-context.txt \
  --max-tokens 80000 \
  -e .py .json \
  -p app.py models.py
```

## Token Recommendations by Model

| Model                | Context Window | Recommended --max-tokens |
| -------------------- | -------------- | ------------------------ |
| Qwen-Coder-30B (16k) | 16,384         | 12,000                   |
| Qwen-Coder-30B (32k) | 32,768         | 22,000                   |
| Qwen-Coder-30B (64k) | 65,536         | 44,000                   |
| Claude Sonnet        | 200,000        | 150,000                  |
| GPT-4 Turbo          | 128,000        | 90,000                   |

*Leave 30% headroom for prompts and responses*

## Output Format

The generated context file includes:

1. **Header** - Metadata about generation
2. **Summary** - File counts, token estimates, size statistics
3. **Project Structure** - Visual tree of included files
4. **File Contents** - Complete contents of all files with headers

## Automatically Excluded

The tool automatically skips:

**Directories**: `node_modules`, `venv`, `__pycache__`, `.git`, `dist`, `build`, etc.
 **Files**: `package-lock.json`, `.DS_Store`, `Thumbs.db`, etc.

## Using with LM Studio

1. Generate context:

   ```bash
   codebase-context --max-tokens 22000
   ```

2. In LM Studio, attach `codebase-context.txt`

3. Ask questions about your code!

## Programmatic Usage

You can also use it as a Python library:

```python
from codebase_context import generate_context_file

generate_context_file(
    root_path='./my-project',
    output_file='context.txt',
    max_tokens=50000,
    custom_extensions={'.py', '.js'},
    priority_files=['main.py', 'utils.py']
)
```

## Requirements

- Python 3.7+
- No external dependencies!

## License

MIT License

## Author

MacePh