"""
File finding utilities for pattern-based file discovery.

Supports glob patterns in file paths, including directory wildcards,
with security validation to prevent path traversal attacks.
"""

from pathlib import Path
from typing import List, Optional, Union, Literal
import os
import re


def _normalize_pattern(pattern: str) -> str:
    """
    Normalize glob pattern by converting recursive wildcards to single-level.
    
    Converts '**' to '*' to enforce single-level directory search only.
    
    Args:
        pattern: Glob pattern string
    
    Returns:
        Normalized pattern with ** converted to *
    """
    # Replace ** with * (recursive to single-level)
    return pattern.replace('**', '*')


def _resolve_base_directory(
    base_directory: Optional[str],
    config_file_path: Optional[Path] = None
) -> Path:
    """
    Resolve base directory path.
    
    If base_directory is None, defaults to config file's directory.
    If base_directory is relative, resolves relative to config file location.
    If base_directory is absolute, uses it as-is.
    
    Args:
        base_directory: Base directory path (relative or absolute, or None)
        config_file_path: Path to config file (for resolving relative paths)
    
    Returns:
        Resolved absolute Path to base directory
    """
    if base_directory is None:
        # Default to config file's directory
        if config_file_path is not None:
            return config_file_path.parent.resolve()
        else:
            # Fallback to current working directory
            return Path.cwd().resolve()
    
    base_path = Path(base_directory)
    
    if base_path.is_absolute():
        # Absolute path - use as-is
        return base_path.resolve()
    else:
        # Relative path - resolve relative to config file location
        if config_file_path is not None:
            return (config_file_path.parent / base_path).resolve()
        else:
            # Fallback to current working directory
            return (Path.cwd() / base_path).resolve()


def validate_path_within_base(
    resolved_path: Path,
    base_directory: Path
) -> bool:
    """
    Validate that resolved path is within the base directory.
    
    Prevents path traversal attacks by ensuring all resolved paths
    stay within the allowed base directory boundary.
    
    Args:
        resolved_path: Resolved absolute path to validate
        base_directory: Base directory that path must be within
    
    Returns:
        True if path is within base directory, False otherwise
    """
    try:
        # Resolve both to absolute paths
        resolved_base = base_directory.resolve()
        resolved_target = resolved_path.resolve()
        
        # Check if target is within base
        # Use commonpath to detect if paths share a common ancestor
        try:
            common = Path(os.path.commonpath([resolved_base, resolved_target]))
            # Path is valid if common path equals the base directory
            return common == resolved_base
        except ValueError:
            # No common path (different drives on Windows, or invalid paths)
            return False
    except (OSError, ValueError, TypeError):
        # Invalid paths or resolution errors
        return False


def find_files_by_pattern(
    pattern: str,
    base_directory: Optional[str] = None,
    config_file_path: Optional[Path] = None,
    match_strategy: Literal["first", "latest", "all"] = "first"
) -> Union[Path, List[Path]]:
    """
    Find files matching a glob pattern.
    
    Supports patterns in entire path, including directory names:
    - "data_*.csv" (filename only)
    - "Test*/data_*.csv" (directory + filename)
    - "Test*/raw_*/dataname_*.csv" (multiple directories + filename)
    
    Args:
        pattern: Glob pattern (may include directory wildcards)
                If absolute path, base_directory is ignored
        base_directory: Base directory to search from (default: config file directory)
                       Ignored if pattern is absolute
        config_file_path: Path to config file (for resolving base_directory)
        match_strategy: 
            - "first": First match alphabetically (default)
            - "latest": Most recently modified file
            - "all": All matching files
    
    Returns:
        Path object (for "first" or "latest") or List[Path] (for "all")
    
    Raises:
        FileNotFoundError: If no matching files found
        ValueError: If resolved pattern path is outside base_directory
    """
    # Normalize pattern (convert ** to *)
    normalized_pattern = _normalize_pattern(pattern)
    
    # Determine if pattern is absolute
    pattern_path = Path(normalized_pattern)
    is_absolute_pattern = pattern_path.is_absolute() or (os.name != 'nt' and normalized_pattern.startswith('/'))
    
    # Resolve base directory for validation and searching
    if is_absolute_pattern:
        # For absolute patterns, extract the longest non-wildcard prefix as base
        # Pattern like "/absolute/path/to/sub*/file_*.csv"
        # Base for validation: "/absolute/path/to"
        pattern_parts = normalized_pattern.split('/')
        base_parts = []
        search_parts = []
        found_wildcard = False
        
        for part in pattern_parts:
            if not found_wildcard and ('*' in part or '?' in part):
                found_wildcard = True
                search_parts.append(part)
            elif found_wildcard:
                search_parts.append(part)
            elif part:  # Skip empty parts
                base_parts.append(part)
        
        if base_parts:
            # Construct base directory from non-wildcard parts
            if normalized_pattern.startswith('/'):
                base_dir = Path('/' + '/'.join(base_parts)).resolve()
            else:
                base_dir = Path('/'.join(base_parts)).resolve()
            search_pattern = '/'.join(search_parts) if search_parts else '*'
        else:
            # Entire pattern is wildcards, use root
            base_dir = Path('/').resolve() if normalized_pattern.startswith('/') else Path.cwd().resolve()
            search_pattern = normalized_pattern.lstrip('/')
        
        search_base = base_dir
    else:
        # For relative patterns, use provided base_directory
        base_dir = _resolve_base_directory(base_directory, config_file_path)
        search_base = base_dir
        search_pattern = normalized_pattern
    
    # Validate that base directory exists
    if not search_base.exists():
        raise FileNotFoundError(
            f"Base directory does not exist: {search_base}"
        )
    
    if not search_base.is_dir():
        raise ValueError(
            f"Base directory is not a directory: {search_base}"
        )
    
    # Find matching files using glob
    # Handle patterns with directory wildcards
    matches = list(search_base.glob(search_pattern))
    
    # Filter to only files (not directories)
    file_matches = [p for p in matches if p.is_file()]
    
    if not file_matches:
        raise FileNotFoundError(
            f"No files found matching pattern '{pattern}' "
            f"in directory '{search_base}'"
        )
    
    # Validate all matches are within base directory
    for match in file_matches:
        if not validate_path_within_base(match, base_dir):
            raise ValueError(
                f"Pattern '{pattern}' resolved to path outside base directory. "
                f"Match: {match.resolve()}, Base: {base_dir}"
            )
    
    # Apply match strategy
    if match_strategy == "all":
        # Sort alphabetically for consistency
        return sorted(file_matches, key=lambda p: str(p))
    elif match_strategy == "latest":
        # Sort by modification time, most recent first
        return max(file_matches, key=lambda p: p.stat().st_mtime)
    else:  # "first" (default)
        # Sort alphabetically and return first
        return sorted(file_matches, key=lambda p: str(p))[0]


def resolve_file_path(
    source: str,
    base_directory: Optional[str] = None,
    config_file_path: Optional[Path] = None,
    match_strategy: Literal["first", "latest", "all"] = "first"
) -> Path:
    """
    Resolve a file path, supporting both exact paths and glob patterns.
    
    Tries exact path first, then pattern matching if exact path doesn't exist.
    All resolved paths are validated to be within the base directory.
    
    Args:
        source: File path or glob pattern
        base_directory: Base directory for resolving relative paths/patterns
                       (default: config file directory)
        config_file_path: Path to config file (for resolving base_directory)
        match_strategy: Strategy for multiple pattern matches
                       (only used if source is a pattern)
    
    Returns:
        Resolved file path
    
    Raises:
        FileNotFoundError: If no matching file found
        ValueError: If resolved path is outside base_directory
    """
    # Resolve base directory
    base_dir = _resolve_base_directory(base_directory, config_file_path)
    
    # Check if source is an absolute path
    source_path = Path(source)
    is_absolute = source_path.is_absolute() or source.startswith('/')
    
    if is_absolute:
        # Absolute path - validate it's within base directory
        resolved = source_path.resolve()
        
        if not validate_path_within_base(resolved, base_dir):
            raise ValueError(
                f"Absolute path '{source}' is outside base directory '{base_dir}'. "
                f"Resolved path: {resolved}"
            )
        
        if resolved.exists() and resolved.is_file():
            return resolved
        else:
            # Try as pattern
            return find_files_by_pattern(
                source,
                base_directory=base_directory,
                config_file_path=config_file_path,
                match_strategy=match_strategy
            )
    else:
        # Relative path - try exact match first
        exact_path = (base_dir / source_path).resolve()
        
        # Validate exact path is within base
        if not validate_path_within_base(exact_path, base_dir):
            raise ValueError(
                f"Path '{source}' resolves outside base directory '{base_dir}'. "
                f"Resolved path: {exact_path}"
            )
        
        if exact_path.exists() and exact_path.is_file():
            return exact_path
        else:
            # Try as pattern
            return find_files_by_pattern(
                source,
                base_directory=base_directory,
                config_file_path=config_file_path,
                match_strategy=match_strategy
            )

