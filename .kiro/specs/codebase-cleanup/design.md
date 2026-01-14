# Design Document

## Overview

This design outlines the approach for refactoring and cleaning up the Migru codebase by removing redundant documentation, consolidating information, and establishing a clear documentation hierarchy. The cleanup will maintain all critical information while significantly reducing file clutter and improving maintainability.

## Architecture

### Documentation Hierarchy

The cleaned codebase will follow this documentation structure:

```
migru/
├── README.md                 # Main project documentation (installation, usage, features)
├── AGENTS.md                 # Development guidelines and conventions
├── PRIVACY.md                # Privacy policy and data handling
├── DEPLOYMENT.md             # Deployment and production setup
├── HOW_IT_WORKS.md          # Architecture and technical deep dive
├── PERFORMANCE.md            # Performance optimization guide
├── .env.example              # Configuration template
└── app/                      # Source code with inline documentation
```

### File Classification

**Files to Keep (Core Documentation):**
- README.md - Main entry point
- AGENTS.md - Development guidelines
- PRIVACY.md - Privacy policy
- DEPLOYMENT.md - Deployment guide
- HOW_IT_WORKS.md - Architecture overview
- PERFORMANCE.md - Performance tuning

**Files to Remove (Redundant/Obsolete):**
- REVAMP_SUMMARY.md - Status report, information outdated
- BUGFIX_SUMMARY.md - Status report, fixes already applied
- COMPLETE_STATUS.md - Status report, no longer relevant
- UX_FIXES.md - Implementation details, belongs in code/AGENTS.md
- FALLBACK_SYSTEM.md - Implementation details, belongs in code/AGENTS.md
- GEMINI.md - AI-specific context, not needed for general development
- CLAUDE.md - AI-specific context, not needed for general development
- README_ENHANCED.md - Duplicate of README.md with local LLM features
- REALTIME_ANALYTICS.md - Feature documentation, can be consolidated
- PERSONALIZATION.md - Feature documentation, can be consolidated

## Components and Interfaces

### Documentation Consolidation Service

**Purpose:** Merge information from redundant files into core documentation

**Interface:**
```python
class DocumentationConsolidator:
    def analyze_files(self, file_paths: List[str]) -> Dict[str, FileAnalysis]
    def extract_unique_content(self, source_file: str, target_file: str) -> str
    def merge_content(self, source: str, target: str, section: str) -> None
    def validate_links(self, file_path: str) -> List[str]
```

### File Cleanup Service

**Purpose:** Remove redundant files and update references

**Interface:**
```python
class FileCleanupService:
    def identify_redundant_files(self) -> List[str]
    def check_file_references(self, file_path: str) -> List[str]
    def safe_delete(self, file_path: str) -> bool
    def update_references(self, old_path: str, new_path: str) -> None
```

## Data Models

### File Analysis Model

```python
@dataclass
class FileAnalysis:
    path: str
    category: FileCategory  # CORE, REDUNDANT, OBSOLETE
    size: int
    last_modified: datetime
    unique_content: List[str]
    references: List[str]
    consolidation_target: Optional[str]
```

### Consolidation Plan Model

```python
@dataclass
class ConsolidationPlan:
    files_to_remove: List[str]
    files_to_update: Dict[str, List[ContentUpdate]]
    reference_updates: Dict[str, str]
    validation_checks: List[ValidationCheck]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Information Preservation

*For any* documentation file marked for deletion, all unique and critical information should be preserved in an appropriate core documentation file before deletion.

**Validates: Requirements 1.4**

### Property 2: Reference Integrity

*For any* file that is deleted, all references to that file in remaining documentation should be updated or removed to prevent broken links.

**Validates: Requirements 2.5**

### Property 3: Single Source of Truth

*For any* topic or piece of information, it should exist in exactly one core documentation file after consolidation.

**Validates: Requirements 1.3**

### Property 4: Essential File Retention

*For all* core documentation files (README.md, AGENTS.md, PRIVACY.md, DEPLOYMENT.md, HOW_IT_WORKS.md, PERFORMANCE.md), they should remain in the repository after cleanup.

**Validates: Requirements 1.1**

### Property 5: Documentation Hierarchy

*For any* documentation file in the cleaned repository, it should have a clear purpose and position in the documentation hierarchy without overlap with other files.

**Validates: Requirements 4.1**

## Error Handling

### Missing Content Detection

**Strategy:** Before deleting any file, scan for unique content that doesn't exist in target consolidation files.

**Implementation:**
- Parse markdown files into sections
- Compare content across files using similarity metrics
- Flag unique sections for manual review
- Require explicit confirmation before deletion

### Broken Reference Prevention

**Strategy:** Validate all internal links before and after cleanup.

**Implementation:**
- Extract all markdown links from files
- Check if referenced files exist
- Update or remove broken links
- Generate report of all link changes

### Rollback Capability

**Strategy:** Create backup of all files before deletion.

**Implementation:**
- Copy all files to `.cleanup_backup/` directory
- Store metadata about changes made
- Provide rollback script if needed
- Keep backup for 30 days

## Testing Strategy

### Manual Testing Approach

Since this is a one-time cleanup operation, we'll use manual testing with validation scripts:

**Validation Scripts:**
1. **Link Checker** - Verify all internal links are valid
2. **Content Analyzer** - Ensure no unique content is lost
3. **Reference Scanner** - Find all references to deleted files
4. **Completeness Checker** - Verify all requirements are covered

**Manual Review Process:**
1. Review list of files to be deleted
2. Verify consolidation plan for each file
3. Check that all unique content is preserved
4. Validate updated documentation structure
5. Test navigation and link integrity

### Validation Checklist

Before finalizing cleanup:
- [ ] All core files (README, AGENTS, PRIVACY, DEPLOYMENT, HOW_IT_WORKS, PERFORMANCE) exist
- [ ] No broken internal links in remaining files
- [ ] All unique content from deleted files is preserved
- [ ] Documentation hierarchy is clear and logical
- [ ] No duplicate information across files
- [ ] All references to deleted files are updated
- [ ] Backup of original files is created

## Implementation Plan

### Phase 1: Analysis

1. Scan all markdown files in repository root
2. Categorize files as CORE, REDUNDANT, or OBSOLETE
3. Extract unique content from each file
4. Identify all internal references and links
5. Create consolidation plan

### Phase 2: Content Consolidation

1. For each redundant file:
   - Extract unique, valuable content
   - Identify appropriate target file (README, AGENTS, etc.)
   - Merge content into target file
   - Update formatting and structure
2. Validate that no information is lost

### Phase 3: File Removal

1. Create backup directory with all original files
2. Delete redundant and obsolete files
3. Update all references to deleted files
4. Validate link integrity

### Phase 4: Validation

1. Run link checker on all remaining files
2. Verify documentation hierarchy
3. Check for duplicate content
4. Review consolidated documentation
5. Test navigation and usability

## Consolidation Strategy

### Files to Remove and Their Content Disposition

**REVAMP_SUMMARY.md** → Delete (outdated status report)
- Architecture changes already documented in HOW_IT_WORKS.md
- Feature descriptions already in README.md

**BUGFIX_SUMMARY.md** → Delete (completed fixes)
- Bug fixes are already applied to codebase
- No ongoing reference value

**COMPLETE_STATUS.md** → Delete (outdated status)
- Project status is current, not historical
- Metrics already in README.md

**UX_FIXES.md** → Delete (implementation details)
- Technical details belong in code comments
- User-facing improvements in README.md

**FALLBACK_SYSTEM.md** → Consolidate into AGENTS.md
- Fallback strategy is development guideline
- Move to "Error Handling" section in AGENTS.md

**GEMINI.md** → Delete (AI-specific context)
- Not needed for general development
- Information duplicates AGENTS.md

**CLAUDE.md** → Delete (AI-specific context)
- Not needed for general development
- Information duplicates AGENTS.md

**README_ENHANCED.md** → Merge into README.md
- Local LLM features should be in main README
- Add section for local deployment options

**REALTIME_ANALYTICS.md** → Consolidate into HOW_IT_WORKS.md
- Technical architecture belongs in architecture doc
- Add section on analytics pipeline

**PERSONALIZATION.md** → Consolidate into HOW_IT_WORKS.md
- Feature architecture belongs in architecture doc
- Add section on personalization system

### Updated Core Files Structure

**README.md** - Enhanced with:
- Local LLM deployment options (from README_ENHANCED.md)
- Clearer feature overview
- Simplified getting started section

**AGENTS.md** - Enhanced with:
- Fallback system guidelines (from FALLBACK_SYSTEM.md)
- Error handling best practices
- Testing conventions

**HOW_IT_WORKS.md** - Enhanced with:
- Real-time analytics architecture (from REALTIME_ANALYTICS.md)
- Personalization system design (from PERSONALIZATION.md)
- Complete technical architecture

## Success Criteria

The cleanup is successful when:

1. **File Count Reduced:** Repository root has 6-7 core documentation files (down from 15+)
2. **No Information Loss:** All unique, valuable content is preserved in core files
3. **No Broken Links:** All internal documentation links are valid
4. **Clear Hierarchy:** Each file has a distinct purpose with no overlap
5. **Improved Navigation:** Developers can quickly find information
6. **Maintainability:** Single source of truth for each topic area
