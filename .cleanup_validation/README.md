# Cleanup Validation Scripts

This directory contains validation scripts for the codebase cleanup operation.

## Available Scripts

### 1. Link Checker (`link_checker.py`)

Validates all internal links in markdown files to ensure no broken references.

**Usage:**
```bash
python .cleanup_validation/link_checker.py .
```

**Output:**
- Lists all markdown files with their link status
- Reports broken links with file and link details
- Returns exit code 1 if broken links found, 0 otherwise

### 2. Content Analyzer (`content_analyzer.py`)

Analyzes and categorizes markdown files as CORE, REDUNDANT, or OBSOLETE.

**Usage:**
```bash
python .cleanup_validation/content_analyzer.py .
```

**Output:**
- Categorizes files based on design document
- Shows file statistics (size, lines, word count, sections)
- Provides summary of files to keep vs. remove

### 3. Reference Scanner (`reference_scanner.py`)

Finds all references to a specific file in other markdown documents.

**Usage:**
```bash
python .cleanup_validation/reference_scanner.py FILENAME.md .
```

**Example:**
```bash
python .cleanup_validation/reference_scanner.py FALLBACK_SYSTEM.md .
```

**Output:**
- Lists all files that reference the target file
- Shows line numbers and content of references
- Indicates if file is safe to delete

## Validation Workflow

Before cleanup:
1. Run `content_analyzer.py` to verify file categorization
2. Run `link_checker.py` to establish baseline link status
3. For each file to be deleted, run `reference_scanner.py`

After cleanup:
1. Run `link_checker.py` to verify no new broken links
2. Run `content_analyzer.py` to verify only core files remain

## Requirements

- Python 3.8+
- No external dependencies (uses only standard library)
