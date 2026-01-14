#!/usr/bin/env python3
"""
Link Checker - Validates all internal links in markdown files.

Usage:
    python link_checker.py [directory]
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def extract_markdown_links(content: str) -> List[Tuple[str, str]]:
    """Extract all markdown links from content."""
    # Match [text](link) format
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    return re.findall(link_pattern, content)


def is_internal_link(link: str) -> bool:
    """Check if link is internal (not http/https)."""
    return not link.startswith(('http://', 'https://', 'mailto:', '#'))


def check_file_links(file_path: Path, root_dir: Path) -> Dict[str, List[str]]:
    """Check all links in a markdown file."""
    results = {
        'valid': [],
        'broken': [],
        'external': []
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        links = extract_markdown_links(content)
        
        for text, link in links:
            if not is_internal_link(link):
                results['external'].append(f"{text} -> {link}")
                continue
            
            # Remove anchor if present
            link_path = link.split('#')[0]
            if not link_path:  # Just an anchor
                continue
                
            # Resolve relative path
            target = (file_path.parent / link_path).resolve()
            
            if target.exists():
                results['valid'].append(f"{text} -> {link}")
            else:
                results['broken'].append(f"{text} -> {link}")
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
    
    return results


def main():
    """Main entry point."""
    root_dir = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    
    print(f"Checking links in: {root_dir.absolute()}\n")
    
    md_files = list(root_dir.glob('*.md'))
    
    if not md_files:
        print("No markdown files found.")
        return 0
    
    all_broken = []
    
    for md_file in sorted(md_files):
        results = check_file_links(md_file, root_dir)
        
        if results['broken']:
            print(f"\n❌ {md_file.name}:")
            for link in results['broken']:
                print(f"  BROKEN: {link}")
            all_broken.extend(results['broken'])
        else:
            print(f"✓ {md_file.name}: All links valid")
    
    print(f"\n{'='*60}")
    if all_broken:
        print(f"Found {len(all_broken)} broken link(s)")
        return 1
    else:
        print("All links are valid!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
