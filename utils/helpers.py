"""
Helper functions for string conversion and file operations.

Provides utilities for:
- Case conversion (snake_case, PascalCase, camelCase, kebab-case)
- Directory and file operations
"""

import re
from pathlib import Path
from typing import Optional


def to_snake_case(text: str) -> str:
    """
    Convert text to snake_case.

    Examples:
        ProductItem -> product_item
        product-item -> product_item
        ProductITEM -> product_item
        serviceProvider -> service_provider
    """
    # Replace hyphens and spaces with underscores
    text = text.replace('-', '_').replace(' ', '_')

    # Insert underscores before uppercase letters
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    text = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)

    # Remove duplicate underscores and lowercase
    text = re.sub('_+', '_', text)
    return text.lower().strip('_')


def to_pascal_case(text: str) -> str:
    """
    Convert text to PascalCase.

    Examples:
        product_item -> ProductItem
        product-item -> ProductItem
        product item -> ProductItem
    """
    # Replace separators with spaces
    text = text.replace('_', ' ').replace('-', ' ')

    # Capitalize each word and join
    return ''.join(word.capitalize() for word in text.split())


def to_camel_case(text: str) -> str:
    """
    Convert text to camelCase.

    Examples:
        product_item -> productItem
        ProductItem -> productItem
    """
    pascal = to_pascal_case(text)
    return pascal[0].lower() + pascal[1:] if pascal else ''


def to_kebab_case(text: str) -> str:
    """
    Convert text to kebab-case.

    Examples:
        ProductItem -> product-item
        product_item -> product-item
    """
    return to_snake_case(text).replace('_', '-')


def to_upper_case(text: str) -> str:
    """
    Convert text to UPPER_CASE.

    Examples:
        ProductItem -> PRODUCT_ITEM
        product-item -> PRODUCT_ITEM
    """
    return to_snake_case(text).upper()


def pluralize(text: str) -> str:
    """
    Simple pluralization for English words.
    
    Examples:
        category -> categories
        product -> products
        status -> statuses
    """
    if text.endswith('y') and len(text) > 1 and text[-2] not in 'aeiou':
        return text[:-1] + 'ies'
    elif text.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return text + 'es'
    else:
        return text + 's'


def ensure_directory(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str, overwrite: bool = False) -> bool:
    """
    Write content to file.

    Args:
        path: File path to write to
        content: Content to write
        overwrite: If True, overwrite existing file

    Returns:
        True if file was written, False if it exists and overwrite is False
    """
    if path.exists() and not overwrite:
        return False

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    path.write_text(content, encoding='utf-8')
    return True


def get_table_name(class_name: str) -> str:
    """
    Convert class name to database table name (plural snake_case).
    
    Examples:
        ServiceProvider -> service_providers
        Category -> categories
    """
    snake = to_snake_case(class_name)
    return pluralize(snake)
