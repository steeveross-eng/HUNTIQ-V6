"""
BIONIC Safe Get Helper
======================
Provides type-safe data access utilities to prevent TypeError exceptions
when accessing MongoDB documents with potentially corrupted data types.

Version: 1.0.0
Date: 2026-02-19

Problem Solved:
- context.get('field', []) does NOT protect against wrong types
- If field EXISTS with value 42 (int), .get() returns 42, not []
- This causes TypeError when len() is called

Solution:
- safe_get() validates the type before returning
- Returns default if type is incorrect
- Logs the type correction for debugging
"""

import logging
from typing import Any, Type, List, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

T = TypeVar('T')


def safe_get(
    data: Dict[str, Any],
    key: str,
    expected_type: Type[T],
    default: T,
    log_correction: bool = True
) -> T:
    """
    Safely get a value from a dictionary with type validation.
    
    Args:
        data: Dictionary to get value from
        key: Key to access
        expected_type: Expected type of the value (list, dict, str, int, etc.)
        default: Default value to return if key missing or type incorrect
        log_correction: Whether to log type corrections
    
    Returns:
        The value if it exists and has correct type, otherwise default
    
    Example:
        # Instead of: pages = context.get('pages_visited', [])
        # Use: pages = safe_get(context, 'pages_visited', list, [])
    """
    if data is None:
        return default
    
    value = data.get(key)
    
    # Key doesn't exist
    if value is None:
        return default
    
    # Type is correct
    if isinstance(value, expected_type):
        return value
    
    # Type is incorrect - log and return default
    if log_correction:
        logger.warning(
            f"BIONIC TypeError Prevention: Field '{key}' has type {type(value).__name__}, "
            f"expected {expected_type.__name__}. Resetting to default."
        )
    
    return default


def safe_list(data: Dict[str, Any], key: str, default: Optional[List] = None) -> List:
    """
    Safely get a list from a dictionary.
    
    Args:
        data: Dictionary to get value from
        key: Key to access
        default: Default list to return (defaults to empty list)
    
    Returns:
        The list value if it exists and is a list, otherwise empty list
    
    Example:
        pages = safe_list(context, 'pages_visited')
        tools = safe_list(context, 'tools_used')
    """
    if default is None:
        default = []
    return safe_get(data, key, list, default)


def safe_dict(data: Dict[str, Any], key: str, default: Optional[Dict] = None) -> Dict:
    """
    Safely get a dict from a dictionary.
    
    Args:
        data: Dictionary to get value from
        key: Key to access
        default: Default dict to return (defaults to empty dict)
    
    Returns:
        The dict value if it exists and is a dict, otherwise empty dict
    """
    if default is None:
        default = {}
    return safe_get(data, key, dict, default)


def validate_list_field(value: Any, field_name: str = "unknown") -> List:
    """
    Validate and convert a field to a list.
    Used in dataclass __post_init__ methods.
    
    Args:
        value: Value to validate
        field_name: Name of the field (for logging)
    
    Returns:
        Original list if valid, empty list otherwise
    
    Example:
        @dataclass
        class UserContext:
            pages_visited: List[str] = field(default_factory=list)
            
            def __post_init__(self):
                self.pages_visited = validate_list_field(self.pages_visited, 'pages_visited')
    """
    if isinstance(value, list):
        return value
    
    logger.warning(
        f"BIONIC TypeError Prevention: Field '{field_name}' has type {type(value).__name__}, "
        f"expected list. Resetting to empty list."
    )
    return []


def validate_dict_field(value: Any, field_name: str = "unknown") -> Dict:
    """
    Validate and convert a field to a dict.
    Used in dataclass __post_init__ methods.
    
    Args:
        value: Value to validate
        field_name: Name of the field (for logging)
    
    Returns:
        Original dict if valid, empty dict otherwise
    """
    if isinstance(value, dict):
        return value
    
    logger.warning(
        f"BIONIC TypeError Prevention: Field '{field_name}' has type {type(value).__name__}, "
        f"expected dict. Resetting to empty dict."
    )
    return {}
