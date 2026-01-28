"""Helper Utilities.

Common helper functions for the Genjed workflow.
"""

import uuid
import re
import os
from datetime import datetime
from typing import Optional


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique ID string
    """
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def format_timestamp(
    timestamp: Optional[float] = None,
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """Format a timestamp as a string.
    
    Args:
        timestamp: Unix timestamp (defaults to current time)
        format_string: strftime format string
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        dt = datetime.utcnow()
    else:
        dt = datetime.utcfromtimestamp(timestamp)
    return dt.strftime(format_string)


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """Sanitize a filename for safe filesystem use.
    
    Args:
        filename: Original filename
        max_length: Maximum allowed length
        
    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = os.path.basename(filename)
    
    # Replace invalid characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    filename = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Truncate if too long
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        name = name[:max_length - len(ext)]
        filename = name + ext
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"
    
    return filename


def calculate_video_size_estimate(
    duration_seconds: int,
    resolution: str = "1080p",
    codec: str = "h264"
) -> int:
    """Estimate video file size in bytes.
    
    Args:
        duration_seconds: Video duration
        resolution: Video resolution (1080p, 2k, 4k)
        codec: Video codec
        
    Returns:
        Estimated size in bytes
    """
    # Base bitrates in Mbps
    bitrates = {
        "1080p": 8,
        "2k": 16,
        "4k": 35
    }
    
    # Codec efficiency multipliers
    codec_multipliers = {
        "h264": 1.0,
        "h265": 0.6,
        "vp9": 0.65
    }
    
    bitrate = bitrates.get(resolution, 8)
    multiplier = codec_multipliers.get(codec, 1.0)
    
    # Calculate size: bitrate (Mbps) * duration (s) * multiplier / 8 (bits to bytes) * 1024^2 (MB to bytes)
    size_bytes = int(bitrate * duration_seconds * multiplier * 1024 * 1024 / 8)
    
    return size_bytes


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
