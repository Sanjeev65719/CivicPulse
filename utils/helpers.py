"""
CivicPulse Utility Helpers

Provides common utility functions used across the application:
file size formatting, file validation, haversine distance calculation,
and SLA threshold lookups per complaint category.
"""

import math
from typing import Any


# SLA thresholds in hours per complaint category
SLA_THRESHOLDS: dict[str, int] = {
    "pothole": 168,        # 7 days
    "streetlight": 72,     # 3 days
    "garbage": 24,         # 1 day
    "water_leakage": 48,   # 2 days
    "drainage": 96,        # 4 days
}


def format_bytes(size: int) -> str:
    """Convert a byte count into a human-readable string (e.g. '2.34 MB').

    Args:
        size: Number of bytes.

    Returns:
        Human-readable file size string.
    """
    if size == 0:
        return "0 B"
    units = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size, 1024)))
    i = min(i, len(units) - 1)
    value = size / (1024 ** i)
    return f"{value:.2f} {units[i]}"


def validate_file_size(file: Any, max_size_mb: int = 50) -> bool:
    """Check whether an uploaded file is within the allowed size limit.

    Args:
        file: A Streamlit UploadedFile (or any object with a `.size` attribute
              or that supports ``seek``/``tell``).
        max_size_mb: Maximum allowed size in megabytes.

    Returns:
        True if the file is within the limit, False otherwise.
    """
    max_bytes = max_size_mb * 1024 * 1024
    if hasattr(file, "size"):
        return file.size <= max_bytes
    # Fallback: seek to end to measure
    try:
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        return size <= max_bytes
    except (AttributeError, OSError):
        return False


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute the great-circle distance between two points on Earth.

    Uses the Haversine formula.

    Args:
        lat1: Latitude of point 1 (degrees).
        lon1: Longitude of point 1 (degrees).
        lat2: Latitude of point 2 (degrees).
        lon2: Longitude of point 2 (degrees).

    Returns:
        Distance in kilometres.
    """
    R = 6371.0  # Earth radius in km

    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = (math.sin(dlat / 2) ** 2
         + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_sla_threshold(category: str) -> int:
    """Return the SLA resolution threshold (in hours) for a complaint category.

    Args:
        category: Complaint category string (case-insensitive). Recognised
                  values: pothole, streetlight, garbage, water_leakage, drainage.

    Returns:
        Expected resolution time in hours.  Defaults to 72 hours if the
        category is not recognised.
    """
    return SLA_THRESHOLDS.get(category.lower().strip(), 72)
