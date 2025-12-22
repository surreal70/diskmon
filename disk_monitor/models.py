#!/usr/bin/env python3
"""
Disk Monitor - Data models for the disk monitor application.

Engineered by Andreas Huemmer [andreas.huemmer@adminsend.de]
Copyright (C) 2025 Andreas Huemmer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Version: 1.0.0
Last Modified: 2025-12-22

Changelog:
- 2025-12-22 v1.0.0: Initial data model definitions
  * Created DiskUsage dataclass for disk usage statistics
  * Created IOStats dataclass for I/O statistics tracking
  * Created IORates dataclass for calculated I/O rates

Data models for the disk monitor application.
"""

from dataclasses import dataclass


@dataclass
class DiskUsage:
    """Represents disk usage statistics for a mounted disk."""

    device: str  # Device path (e.g., /dev/sda1)
    mountpoint: str  # Mount path (e.g., /)
    total_bytes: int  # Total disk capacity
    used_bytes: int  # Used space
    available_bytes: int  # Available space
    usage_percent: float  # Percentage used


@dataclass
class IOStats:
    """Represents I/O statistics for a disk device."""

    device: str  # Device name (e.g., sda)
    read_ops: int  # Total read operations
    write_ops: int  # Total write operations
    read_bytes: int  # Total bytes read
    write_bytes: int  # Total bytes written
    timestamp: float  # When stats were collected


@dataclass
class IORates:
    """Represents calculated I/O rates for a disk device."""

    device: str  # Device name
    read_ops_per_sec: float  # Read operations per second
    write_ops_per_sec: float  # Write operations per second
    read_kb_per_sec: float  # Read throughput in KB/s
    write_kb_per_sec: float  # Write throughput in KB/s
