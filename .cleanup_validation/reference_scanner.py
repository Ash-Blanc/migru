#!/usr/bin/env python3
"""
Reference Scanner - Finds all references to specific files in markdown documents.

Usage:
    python reference_scanner.py <filename_to_search> [directory]
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


def find_references(content: str, target_filename: str) -> List[Tuple[int, str]]:
    """Find all references to a target filename in content."""
    references = []
    
    # Split into lines for line number tracking
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Check for various reference patterns
        if target_filename in line:
            references.append((line_num, line.strip()))
    
    return references


def scan_file(file_path: Path, target_filename: str) -> List[Tuple[int, str]]:
    """Scan a file for references to target filename."""
    try:
        content = file_path.read_text(encoding='utf-8')
        return find_references(content, target_filename)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python reference_scanner.py <filename_to_search> [directory]")
        return 1
    
    target_filename = sys.argv[1]
    root_dir = Path(sys.argv[2] if len(sys.argv) > 2 else '.')
    
    print(f"Scanning for references to: {target_filename}")
    print(f"In directory: {root_dir.absolute()}\n")
    
    md_files = list(root_dir.glob('*.md'))
    
    if not md_files:
        print("No markdown files found.")
        return 0
    
    total_references = 0
    
    for md_file in sorted(md_files):
        # Skip the target file itself
        if md_file.name == target_filename:
            continue
        
        references = scan_file(md_file, target_filename)
        
        if references:
            print(f"\n📄 {md_file.name} ({len(references)} reference(s)):")
            for line_num, line in references:
                print(f"   Line {line_num}: {line[:80]}{'...' if len(line) > 80 else ''}")
            total_references += len(references)
    
    print(f"\n{'='*60}")
    if total_references > 0:
        print(f"Found {total_references} reference(s) to {target_filename}")
        print("\n⚠️  These references will need to be updated or removed.")
    else:
        print(f"No references found to {target_filename}")
        print("✓ Safe to delete without updating other files.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
