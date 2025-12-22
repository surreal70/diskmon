#!/usr/bin/env python3
"""
Disk Monitor - Data collection layer for disk usage and I/O statistics.

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
- 2025-12-22 v1.0.0: Enhanced data collection with network filesystem support
  * Added network filesystem type detection and filtering
  * Implemented configurable network drive inclusion
  * Enhanced /proc/diskstats parsing for I/O statistics
  * Added robust error handling for system access

Data collection layer for disk usage and I/O statistics.
"""

import shutil
import time
from typing import List, Dict
import psutil
from .models import DiskUsage, IOStats


class DiskInfoCollector:
    """Collects disk usage and I/O statistics from the Linux system."""

    # Network filesystem types to filter by default
    NETWORK_FS_TYPES = {
        "nfs",
        "nfs4",
        "cifs",
        "smb",
        "smbfs",
        "fuse.sshfs",
        "fuse.glusterfs",
    }

    # Special filesystem types to always filter
    SPECIAL_FS_TYPES = {"tmpfs", "devtmpfs", "squashfs", "overlay"}

    def __init__(self, include_network=False):
        """
        Initialize the disk info collector.

        Args:
            include_network (bool): Whether to include network mounted drives
        """
        self.include_network = include_network

    def get_disk_usage(self) -> List[DiskUsage]:
        """Returns usage statistics for all mounted disks."""
        disk_usage_list = []

        # Get all mounted disk partitions
        partitions = psutil.disk_partitions()

        for partition in partitions:
            try:
                # Always skip special filesystems
                if partition.fstype in self.SPECIAL_FS_TYPES:
                    continue

                # Skip network filesystems unless explicitly included
                if (
                    not self.include_network
                    and partition.fstype in self.NETWORK_FS_TYPES
                ):
                    continue

                # Get disk usage statistics
                usage = shutil.disk_usage(partition.mountpoint)
                total_bytes = usage.total
                free_bytes = usage.free
                used_bytes = total_bytes - free_bytes

                # Calculate usage percentage
                usage_percent = (
                    (used_bytes / total_bytes * 100) if total_bytes > 0 else 0.0
                )

                disk_usage = DiskUsage(
                    device=partition.device,
                    mountpoint=partition.mountpoint,
                    total_bytes=total_bytes,
                    used_bytes=used_bytes,
                    available_bytes=free_bytes,
                    usage_percent=usage_percent,
                )

                disk_usage_list.append(disk_usage)

            except (OSError, PermissionError):
                # Skip partitions we can't access
                continue

        return disk_usage_list

    def get_disk_io_stats(self) -> Dict[str, IOStats]:
        """Returns I/O statistics per disk device."""
        io_stats = {}
        current_time = time.time()

        try:
            # Read /proc/diskstats for I/O statistics
            with open("/proc/diskstats", "r") as f:
                for line in f:
                    fields = line.strip().split()
                    if len(fields) >= 14:
                        # Extract device name and statistics
                        device_name = fields[2]

                        # Skip loop devices and ram devices
                        if device_name.startswith(("loop", "ram")):
                            continue

                        # Parse I/O statistics (fields from /proc/diskstats)
                        read_ops = int(fields[3])  # reads completed
                        write_ops = int(fields[7])  # writes completed
                        read_sectors = int(fields[5])  # sectors read
                        write_sectors = int(fields[9])  # sectors written

                        # Convert sectors to bytes (assuming 512 bytes per sector)
                        read_bytes = read_sectors * 512
                        write_bytes = write_sectors * 512

                        io_stat = IOStats(
                            device=device_name,
                            read_ops=read_ops,
                            write_ops=write_ops,
                            read_bytes=read_bytes,
                            write_bytes=write_bytes,
                            timestamp=current_time,
                        )

                        io_stats[device_name] = io_stat

        except (OSError, IOError, PermissionError):
            # Return empty dict if we can't read /proc/diskstats
            pass

        return io_stats

    def get_mounted_disks(self) -> List[str]:
        """Returns list of currently mounted disk devices."""
        mounted_disks = []

        # Get all mounted disk partitions
        partitions = psutil.disk_partitions()

        for partition in partitions:
            # Always skip special filesystems
            if partition.fstype in self.SPECIAL_FS_TYPES:
                continue

            # Skip network filesystems unless explicitly included
            if not self.include_network and partition.fstype in self.NETWORK_FS_TYPES:
                continue

            mounted_disks.append(partition.device)

        return mounted_disks
