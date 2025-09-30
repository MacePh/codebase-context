#!/usr/bin/env python3
"""
Intelligent Codebase Context Generator for LLMs
Main module - contains all the core functionality
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Common code file extensions
CODE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
    '.html', '.css', '.scss', '.sass', '.vue', '.svelte',
    '.json', '.yaml', '.yml', '.toml', '.xml',
    '.sql', '.sh', '.bash', '.ps1', '.bat',
    '.md', '.txt', '.rst'
}

# Directories to always skip
SKIP_DIRS = {
    'node_modules', 'venv', 'env', '.env', '__pycache__', '.git', '.svn',
    'dist', 'build', 'target', 'bin', 'obj', '.idea', '.vscode',
    'coverage', '.pytest_cache', '.mypy_cache', 'vendor', 'bower_components', 
    '*_venv'
}

# Files to always skip
SKIP_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitignore', '.dockerignore',
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Pipfile.lock'
}

def estimate_tokens(text):
    """Rough estimate: 1 token ≈ 4 characters"""
    return len(text) // 4

def get_file_info(filepath):
    """Get file size and line count"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.count('\n') + 1
            tokens = estimate_tokens(content)
            return {
                'size': len(content),
                'lines': lines,
                'tokens': tokens,
                'content': content
            }
    except Exception as e:
        return None

def should_include_file(filepath, custom_extensions=None):
    """Determine if file should be included"""
    path = Path(filepath)
    
    # Skip if in skip list
    if path.name in SKIP_FILES:
        return False
    
    # Check extension
    extensions = custom_extensions if custom_extensions else CODE_EXTENSIONS
    return path.suffix.lower() in extensions or path.suffix == ''

def scan_codebase(root_path, max_tokens=100000, custom_extensions=None):
    """Scan codebase and collect files with metadata"""
    root = Path(root_path)
    files_data = []
    total_tokens = 0
    
    for filepath in root.rglob('*'):
        # Skip directories
        if filepath.is_dir():
            continue
        
        # Skip if in excluded directory
        if any(skip_dir in filepath.parts for skip_dir in SKIP_DIRS):
            continue
        
        # Skip if not a code file
        if not should_include_file(filepath, custom_extensions):
            continue
        
        # Get file info
        info = get_file_info(filepath)
        if not info:
            continue
        
        relative_path = filepath.relative_to(root)
        files_data.append({
            'path': relative_path,
            'full_path': filepath,
            **info
        })
        total_tokens += info['tokens']
    
    # Sort by importance (prioritize smaller, core files)
    files_data.sort(key=lambda x: (x['tokens'], str(x['path'])))
    
    return files_data, total_tokens

def generate_tree_structure(root_path, files_data):
    """Generate visual tree structure of included files"""
    tree_lines = [f"📁 {Path(root_path).name}/"]
    
    # Group by directory
    dirs = {}
    for file_info in files_data:
        parts = file_info['path'].parts
        if len(parts) > 1:
            dir_name = parts[0]
            if dir_name not in dirs:
                dirs[dir_name] = []
            dirs[dir_name].append(file_info)
        else:
            tree_lines.append(f"├── {file_info['path'].name}")
    
    for dir_name, files in dirs.items():
        tree_lines.append(f"├── 📁 {dir_name}/")
        for f in files:
            tree_lines.append(f"│   ├── {f['path'].name}")
    
    return '\n'.join(tree_lines)

def generate_summary(files_data, total_tokens):
    """Generate codebase summary"""
    summary = []
    summary.append("=" * 80)
    summary.append("CODEBASE SUMMARY")
    summary.append("=" * 80)
    summary.append(f"Total Files: {len(files_data)}")
    summary.append(f"Total Lines: {sum(f['lines'] for f in files_data):,}")
    summary.append(f"Total Tokens (estimated): {total_tokens:,}")
    summary.append(f"Total Size: {sum(f['size'] for f in files_data) / 1024:.2f} KB")
    summary.append("")
    
    # File type breakdown
    extensions = {}
    for f in files_data:
        ext = f['path'].suffix or 'no extension'
        extensions[ext] = extensions.get(ext, 0) + 1
    
    summary.append("File Types:")
    for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
        summary.append(f"  {ext}: {count} files")
    
    summary.append("")
    summary.append("Largest Files:")
    largest = sorted(files_data, key=lambda x: x['tokens'], reverse=True)[:5]
    for f in largest:
        summary.append(f"  {f['path']} - {f['lines']} lines, ~{f['tokens']:,} tokens")
    
    summary.append("=" * 80)
    summary.append("")
    
    return '\n'.join(summary)

def generate_context_file(root_path, output_file, max_tokens=100000, 
                         include_tree=True, custom_extensions=None,
                         priority_files=None):
    """Generate the complete context file"""
    
    print(f"🔍 Scanning codebase at: {root_path}")
    files_data, total_tokens = scan_codebase(root_path, max_tokens, custom_extensions)
    
    print(f"📊 Found {len(files_data)} files (~{total_tokens:,} tokens)")
    
    # Apply token limit if needed
    selected_files = []
    running_tokens = 0
    
    # Prioritize specific files if provided
    if priority_files:
        priority_set = set(priority_files)
        priority_data = [f for f in files_data if str(f['path']) in priority_set]
        other_data = [f for f in files_data if str(f['path']) not in priority_set]
        files_data = priority_data + other_data
    
    for file_info in files_data:
        if running_tokens + file_info['tokens'] > max_tokens:
            print(f"⚠️  Reached token limit. Including {len(selected_files)}/{len(files_data)} files")
            break
        selected_files.append(file_info)
        running_tokens += file_info['tokens']
    
    # Generate output
    with open(output_file, 'w', encoding='utf-8') as out:
        # Header
        out.write(f"# CODEBASE CONTEXT FOR LLM\n")
        out.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"# Root: {root_path}\n")
        out.write(f"# Token Budget: {max_tokens:,}\n")
        out.write(f"# Actual Tokens: ~{running_tokens:,}\n\n")
        
        # Summary
        out.write(generate_summary(selected_files, running_tokens))
        
        # Tree structure
        if include_tree:
            out.write("\nPROJECT STRUCTURE:\n")
            out.write(generate_tree_structure(root_path, selected_files))
            out.write("\n\n")
        
        # File contents
        out.write("=" * 80 + "\n")
        out.write("FILE CONTENTS\n")
        out.write("=" * 80 + "\n\n")
        
        for file_info in selected_files:
            out.write(f"\n{'='*80}\n")
            out.write(f"FILE: {file_info['path']}\n")
            out.write(f"Lines: {file_info['lines']} | Tokens: ~{file_info['tokens']}\n")
            out.write(f"{'='*80}\n\n")
            out.write(file_info['content'])
            out.write("\n\n")
    
    print(f"✅ Context file generated: {output_file}")
    print(f"📝 Included {len(selected_files)} files with ~{running_tokens:,} tokens")
    
    if len(selected_files) < len(files_data):
        print(f"\n⚠️  {len(files_data) - len(selected_files)} files were excluded due to token limit")
        print("💡 Consider increasing --max-tokens or using --priority to include specific files")

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description='Generate intelligent codebase context for LLMs like Qwen-Coder-30B',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codebase-context                                    # Scan current directory
  codebase-context /path/to/project                   # Scan specific directory
  codebase-context -o output.txt --max-tokens 50000   # Custom settings
  codebase-context -e .py .js -p main.py utils.py     # Filter files and prioritize
        """
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to codebase (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='codebase-context.txt',
        help='Output file name (default: codebase-context.txt)'
    )
    parser.add_argument(
        '-m', '--max-tokens',
        type=int,
        default=100000,
        help='Maximum tokens to include (default: 100000)'
    )
    parser.add_argument(
        '--no-tree',
        action='store_true',
        help='Exclude directory tree structure'
    )
    parser.add_argument(
        '-e', '--extensions',
        nargs='+',
        help='Custom file extensions to include (e.g., .py .js .txt)'
    )
    parser.add_argument(
        '-p', '--priority',
        nargs='+',
        help='Priority files to include first (relative paths)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='codebase-context 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Convert extensions to set
    custom_ext = set(args.extensions) if args.extensions else None
    
    # Validate path
    if not os.path.exists(args.path):
        print(f"❌ Error: Path '{args.path}' does not exist")
        sys.exit(1)
    
    # Generate context
    try:
        generate_context_file(
            root_path=args.path,
            output_file=args.output,
            max_tokens=args.max_tokens,
            include_tree=not args.no_tree,
            custom_extensions=custom_ext,
            priority_files=args.priority
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
