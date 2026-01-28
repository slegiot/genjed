"""Validation Utilities.

Input validation functions for the Genjed workflow.
"""

import re
from typing import Dict, List, Optional, Tuple


def validate_product(data: Dict) -> Tuple[bool, List[str]]:
    """Validate product data.
    
    Args:
        data: Product data dictionary
        
    Returns:
        Tuple of (is_valid, list of errors)
    """
    errors = []
    
    if not data.get('name'):
        errors.append("Product name is required")
    elif len(data['name']) < 2:
        errors.append("Product name must be at least 2 characters")
    elif len(data['name']) > 200:
        errors.append("Product name must be less than 200 characters")
    
    if not data.get('description'):
        errors.append("Product description is required")
    
    price = data.get('price')
    if price is not None:
        try:
            price = float(price)
            if price < 0:
                errors.append("Price must be non-negative")
        except (ValueError, TypeError):
            errors.append("Price must be a valid number")
    
    category = data.get('category')
    valid_categories = [
        'electronics', 'fashion', 'home_garden', 'beauty',
        'food_beverage', 'sports', 'toys', 'automotive', 'other'
    ]
    if category and category not in valid_categories:
        errors.append(f"Category must be one of: {', '.join(valid_categories)}")
    
    image_urls = data.get('image_urls', [])
    if image_urls:
        for url in image_urls:
            if not _is_valid_url(url):
                errors.append(f"Invalid image URL: {url}")
    
    return len(errors) == 0, errors


def validate_template(data: Dict) -> Tuple[bool, List[str]]:
    """Validate template data.
    
    Args:
        data: Template data dictionary
        
    Returns:
        Tuple of (is_valid, list of errors)
    """
    errors = []
    
    if not data.get('name'):
        errors.append("Template name is required")
    
    template_type = data.get('type')
    valid_types = [
        'product_ad', 'brand_story', 'testimonial',
        'tutorial', 'unboxing', 'comparison', 'lifestyle'
    ]
    if template_type and template_type not in valid_types:
        errors.append(f"Template type must be one of: {', '.join(valid_types)}")
    
    visual_config = data.get('visual_config', {})
    if visual_config:
        aspect_ratios = visual_config.get('aspect_ratios', [])
        valid_ratios = ['9:16', '16:9', '1:1', '4:5']
        for ratio in aspect_ratios:
            if ratio not in valid_ratios:
                errors.append(f"Invalid aspect ratio: {ratio}")
        
        durations = visual_config.get('duration_seconds', [])
        for duration in durations:
            if not isinstance(duration, int) or duration < 1 or duration > 180:
                errors.append(f"Duration must be between 1 and 180 seconds")
    
    return len(errors) == 0, errors


def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
    return bool(re.match(pattern, url))
