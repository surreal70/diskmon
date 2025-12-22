#!/usr/bin/env python3
"""
Disk Monitor - Display layer for managing console output and screen updates.

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
- 2025-12-22 v1.0.0: Console display implementation
  * Created tabular output formatting with proper column alignment
  * Implemented device name matching for I/O rate display
  * Added error message handling and screen management
  * Included cross-platform screen clearing functionality

Display layer for managing console output and screen updates.
"""

import os
import sys
from typing import List, Optional
from .models import DiskUsage, IORates
from .formatter import MetricsFormatter


class ConsoleDisplay:
    """Manages console output and screen updates."""

    def __init__(self):
        """Initialize the console display with a formatter."""
        self.formatter = MetricsFormatter()

    def clear_screen(self):
        """Clears the console display."""
        # Use ANSI escape sequences for cross-platform compatibility
        os.system("clear" if os.name == "posix" else "cls")
        # Alternative: print ANSI escape sequence directly
        print("\033[2J\033[H", end="")

    def display_header(self):
        """Shows column headers for the metrics table."""
        header = (
            f"{'Device':<15} "
            f"{'Mount Point':<20} "
            f"{'Used':<10} "
            f"{'Available':<10} "
            f"{'Total':<10} "
            f"{'Usage %':<8} "
            f"{'Read Ops/s':<12} "
            f"{'Write Ops/s':<13} "
            f"{'Read KB/s':<12} "
            f"{'Write KB/s':<12}"
        )
        print(header)
        print("-" * len(header))

    def display_disk_row(
        self, disk_usage: DiskUsage, io_rates: Optional[IORates] = None
    ):
        """Displays metrics for a single disk."""
        # Format basic disk usage information
        device = (
            disk_usage.device[:14] if len(disk_usage.device) > 14 else disk_usage.device
        )
        mountpoint = (
            disk_usage.mountpoint[:19]
            if len(disk_usage.mountpoint) > 19
            else disk_usage.mountpoint
        )
        used = self.formatter.format_bytes(disk_usage.used_bytes)
        available = self.formatter.format_bytes(disk_usage.available_bytes)
        total = self.formatter.format_bytes(disk_usage.total_bytes)
        usage_percent = f"{disk_usage.usage_percent:.1f}%"

        # Format I/O rates if available
        if io_rates:
            read_ops = f"{io_rates.read_ops_per_sec:.1f}"
            write_ops = f"{io_rates.write_ops_per_sec:.1f}"
            read_kb = f"{io_rates.read_kb_per_sec:.1f}"
            write_kb = f"{io_rates.write_kb_per_sec:.1f}"
        else:
            read_ops = "N/A"
            write_ops = "N/A"
            read_kb = "N/A"
            write_kb = "N/A"

        # Display the formatted row
        row = (
            f"{device:<15} "
            f"{mountpoint:<20} "
            f"{used:<10} "
            f"{available:<10} "
            f"{total:<10} "
            f"{usage_percent:<8} "
            f"{read_ops:<12} "
            f"{write_ops:<13} "
            f"{read_kb:<12} "
            f"{write_kb:<12}"
        )
        print(row)

    def display_error(self, message: str):
        """Shows error messages."""
        print(f"ERROR: {message}", file=sys.stderr)

    def display_disk_metrics(
        self, disk_usages: List[DiskUsage], io_rates_dict: Optional[dict] = None
    ):
        """Displays complete disk metrics table."""
        self.clear_screen()
        self.display_header()

        for disk_usage in disk_usages:
            # Try to find matching I/O rates for this disk
            io_rates = None
            if io_rates_dict:
                # Extract device name from full device path for matching
                device_name = os.path.basename(disk_usage.device)
                # Try different variations of device name matching
                for device_key in io_rates_dict:
                    if (
                        device_key == device_name
                        or device_name.startswith(device_key)
                        or device_key.startswith(device_name.rstrip("0123456789"))
                    ):
                        io_rates = io_rates_dict[device_key]
                        break

            self.display_disk_row(disk_usage, io_rates)
