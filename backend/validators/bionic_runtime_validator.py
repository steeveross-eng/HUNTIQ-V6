"""
BIONIC Runtime Validator
========================
Data Validation Layer for BIONIC Engine.
Validates data structures before they are used in scoring and analysis.

Version: 1.0.0
Date: 2026-02-19

Purpose:
- Validate user context data from MongoDB
- Prevent TypeError by ensuring correct types
- Log validation issues for debugging
- Provide clean, validated data to modules
"""

import logging
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BionicValidationError(Exception):
    """Exception raised for BIONIC data validation errors."""
    pass


# Fields that must be lists
LIST_FIELDS = [
    'pages_visited',
    'tools_used',
    'gibiers_secondaires',
    'pourvoiries_consulted',
    'setups_consulted',
    'permis_consulted'
]

# Fields that must be dicts
DICT_FIELDS = [
    'season_dates',
    'quotas'
]


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    field_name: str
    expected_type: str
    actual_type: str
    was_corrected: bool
    corrected_value: Any = None


def validate_pages_visited(value: Any) -> Tuple[List[str], bool]:
    """
    Validate pages_visited field.
    
    Args:
        value: Value to validate
    
    Returns:
        Tuple of (validated_value, was_corrected)
    """
    if isinstance(value, list):
        # Ensure all items are strings
        validated = [str(item) for item in value if item is not None]
        return validated, False
    
    logger.warning(
        f"BIONIC Validation: pages_visited has type {type(value).__name__}, "
        f"expected list. Value was: {repr(value)[:50]}"
    )
    return [], True


def validate_tools_used(value: Any) -> Tuple[List[str], bool]:
    """
    Validate tools_used field.
    
    Args:
        value: Value to validate
    
    Returns:
        Tuple of (validated_value, was_corrected)
    """
    if isinstance(value, list):
        # Ensure all items are strings
        validated = [str(item) for item in value if item is not None]
        return validated, False
    
    logger.warning(
        f"BIONIC Validation: tools_used has type {type(value).__name__}, "
        f"expected list. Value was: {repr(value)[:50]}"
    )
    return [], True


def validate_list_field(value: Any, field_name: str) -> Tuple[List, bool]:
    """
    Generic list field validator.
    
    Args:
        value: Value to validate
        field_name: Name of the field
    
    Returns:
        Tuple of (validated_value, was_corrected)
    """
    if isinstance(value, list):
        return value, False
    
    logger.warning(
        f"BIONIC Validation: {field_name} has type {type(value).__name__}, "
        f"expected list. Resetting to empty list."
    )
    return [], True


def validate_dict_field(value: Any, field_name: str) -> Tuple[Dict, bool]:
    """
    Generic dict field validator.
    
    Args:
        value: Value to validate
        field_name: Name of the field
    
    Returns:
        Tuple of (validated_value, was_corrected)
    """
    if isinstance(value, dict):
        return value, False
    
    logger.warning(
        f"BIONIC Validation: {field_name} has type {type(value).__name__}, "
        f"expected dict. Resetting to empty dict."
    )
    return {}, True


def validate_user_context(context: Dict[str, Any]) -> Tuple[Dict[str, Any], List[ValidationResult]]:
    """
    Validate a complete user context document.
    
    Args:
        context: User context dictionary from MongoDB
    
    Returns:
        Tuple of (validated_context, validation_results)
    
    Example:
        context, results = validate_user_context(doc)
        if any(r.was_corrected for r in results):
            logger.warning("Some fields were corrected")
    """
    if context is None:
        return {}, [ValidationResult(
            is_valid=False,
            field_name="context",
            expected_type="dict",
            actual_type="NoneType",
            was_corrected=True,
            corrected_value={}
        )]
    
    validated = dict(context)
    results = []
    
    # Validate list fields
    for field in LIST_FIELDS:
        if field in validated:
            value, was_corrected = validate_list_field(validated[field], field)
            validated[field] = value
            results.append(ValidationResult(
                is_valid=not was_corrected,
                field_name=field,
                expected_type="list",
                actual_type=type(context.get(field)).__name__,
                was_corrected=was_corrected,
                corrected_value=value if was_corrected else None
            ))
    
    # Validate dict fields
    for field in DICT_FIELDS:
        if field in validated:
            value, was_corrected = validate_dict_field(validated[field], field)
            validated[field] = value
            results.append(ValidationResult(
                is_valid=not was_corrected,
                field_name=field,
                expected_type="dict",
                actual_type=type(context.get(field)).__name__,
                was_corrected=was_corrected,
                corrected_value=value if was_corrected else None
            ))
    
    return validated, results


def validate_checklist_items(items: Any) -> Tuple[List[Dict], bool]:
    """
    Validate checklist items field.
    
    Args:
        items: Items value to validate
    
    Returns:
        Tuple of (validated_items, was_corrected)
    """
    if isinstance(items, list):
        # Ensure all items are dicts
        validated = [item for item in items if isinstance(item, dict)]
        return validated, len(validated) != len(items)
    
    logger.warning(
        f"BIONIC Validation: checklist items has type {type(items).__name__}, "
        f"expected list of dicts. Resetting to empty list."
    )
    return [], True


# Log initialization
logger.info("BIONIC Runtime Validator initialized - V1.0.0")
