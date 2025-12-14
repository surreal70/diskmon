"""
Data models for the disk monitor application.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DiskUsage:
    """Represents disk usage statistics for a mounted disk."""
    device: str          # Device path (e.g., /dev/sda1)
    mountpoint: str      # Mount path (e.g., /)
    total_bytes: int     # Total disk capacity
    used_bytes: int      # Used space
    available_bytes: int # Available space
    usage_percent: float # Percentage used


@dataclass  
class IOStats:
    """Represents I/O statistics for a disk device."""
    device: str          # Device name (e.g., sda)
    read_ops: int        # Total read operations
    write_ops: int       # Total write operations  
    read_bytes: int      # Total bytes read
    write_bytes: int     # Total bytes written
    timestamp: float     # When stats were collected


@dataclass
class IORates:
    """Represents calculated I/O rates for a disk device."""
    device: str              # Device name
    read_ops_per_sec: float  # Read operations per second
    write_ops_per_sec: float # Write operations per second
    read_kb_per_sec: float   # Read throughput in KB/s
    write_kb_per_sec: float  # Write throughput in KB/s