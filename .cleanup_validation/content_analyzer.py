#!/usr/bin/env python3
"""
Content Analyzer - Analyzes markdown files for unique content and categorization.

Usage:
    python content_analyzer.py [directory]
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


# File categorization based on design document
CORE_FILES = {
    'README.md',
    'AGENTS.md',
    'PRIVACY.md',
    'DEPLOYMENT.md',
    'HOW_IT_WORKS.md',
    'PERFORMANCE.md'
}

REDUNDANT_FILES = {
    'README_ENHANCED.md',
    'FALLBACK_SYSTEM.md',
    'REALTIME_ANALYTICS.md',
    'PERSONALIZATION.md'
}

OBSOLETE_FILES = {
    'REVAMP_SUMMARY.md',
    'BUGFIX_SUMMARY.md',
    'COMPLETE_STATUS.md',
    'UX_FIXES.md',
    'GEMINI.md',
    'CLAUDE.md'
}


def extract_sections(content: str) -> List[str]:
    """Extract section headers from markdown content."""
    sections = []
    for line in content.split('\n'):
        if line.startswith('#'):
            sections.append(line.strip())
    return sections


def analyze_file(file_path: Path) -> Dict:
    """Analyze a single markdown file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        return {
            'path': str(file_path),
            'size': len(content),
            'lines': len(content.split('\n')),
            'sections': extract_sections(content),
            'word_count': len(content.split())
        }
    except Exception as e:
        return {
            'path': str(file_path),
            'error': str(e)
        }


def categorize_file(filename: str) -> str:
    """Categorize file as CORE, REDUNDANT, or OBSOLETE."""
    if filename in CORE_FILES:
        return 'CORE'
    elif filename in REDUNDANT_FILES:
        return 'REDUNDANT'
    elif filename in OBSOLETE_FILES:
        return 'OBSOLETE'
    else:
        return 'UNKNOWN'


def main():
    """Main entry point."""
    root_dir = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    
    print(f"Analyzing markdown files in: {root_dir.absolute()}\n")
    
    md_files = list(root_dir.glob('*.md'))
    
    if not md_files:
        print("No markdown files found.")
        return 0
    
    # Categorize files
    categorized = defaultdict(list)
    
    for md_file in sorted(md_files):
        category = categorize_file(md_file.name)
        analysis = analyze_file(md_file)
        categorized[category].append((md_file.name, analysis))
    
    # Print results
    for category in ['CORE', 'REDUNDANT', 'OBSOLETE', 'UNKNOWN']:
        if category in categorized:
            print(f"\n{'='*60}")
            print(f"{category} FILES ({len(categorized[category])})")
            print('='*60)
            
            for filename, analysis in categorized[category]:
                if 'error' in analysis:
                    print(f"\n❌ {filename}: ERROR - {analysis['error']}")
                else:
                    print(f"\n📄 {filename}")
                    print(f"   Size: {analysis['size']:,} bytes")
                    print(f"   Lines: {analysis['lines']:,}")
                    print(f"   Words: {analysis['word_count']:,}")
                    print(f"   Sections: {len(analysis['sections'])}")
                    if analysis['sections']:
                        print(f"   Top sections:")
                        for section in analysis['sections'][:5]:
                            print(f"     - {section}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Core files: {len(categorized['CORE'])}")
    print(f"Redundant files: {len(categorized['REDUNDANT'])}")
    print(f"Obsolete files: {len(categorized['OBSOLETE'])}")
    print(f"Unknown files: {len(categorized.get('UNKNOWN', []))}")
    print(f"\nTotal files: {len(md_files)}")
    print(f"Files to remove: {len(categorized['REDUNDANT']) + len(categorized['OBSOLETE'])}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
