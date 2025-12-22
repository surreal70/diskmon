#!/usr/bin/env python3
"""
Disk Monitor - Data processing layer for formatting raw system data.

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
- 2025-12-22 v1.0.0: Initial data formatting implementation
  * Created human-readable byte formatting with appropriate units
  * Implemented I/O rate calculations with interval validation
  * Added disk usage formatting for display output
  * Included comprehensive error handling and validation

Data processing layer for formatting raw system data into human-readable metrics.
"""

from .models import IOStats, IORates


class MetricsFormatter:
    """Converts raw system data into human-readable formats."""

    def format_bytes(self, bytes_value: int) -> str:
        """Converts bytes to MB/GB/TB with appropriate precision."""
        if bytes_value < 1024:
            return f"{bytes_value} B"
        elif bytes_value < 1024**2:
            return f"{bytes_value / 1024:.1f} KB"
        elif bytes_value < 1024**3:
            return f"{bytes_value / (1024 ** 2):.1f} MB"
        elif bytes_value < 1024**4:
            return f"{bytes_value / (1024 ** 3):.1f} GB"
        else:
            return f"{bytes_value / (1024 ** 4):.1f} TB"

    def calculate_io_rates(
        self, current: IOStats, previous: IOStats, interval: float
    ) -> IORates:
        """Calculates per-second rates from two IOStats measurements."""
        if interval <= 0:
            raise ValueError("Interval must be positive")

        if current.device != previous.device:
            raise ValueError("IOStats must be for the same device")

        # Calculate rate differences
        read_ops_diff = current.read_ops - previous.read_ops
        write_ops_diff = current.write_ops - previous.write_ops
        read_bytes_diff = current.read_bytes - previous.read_bytes
        write_bytes_diff = current.write_bytes - previous.write_bytes

        # Calculate per-second rates
        read_ops_per_sec = read_ops_diff / interval
        write_ops_per_sec = write_ops_diff / interval
        read_kb_per_sec = (read_bytes_diff / interval) / 1024  # Convert to KB/s
        write_kb_per_sec = (write_bytes_diff / interval) / 1024  # Convert to KB/s

        return IORates(
            device=current.device,
            read_ops_per_sec=read_ops_per_sec,
            write_ops_per_sec=write_ops_per_sec,
            read_kb_per_sec=read_kb_per_sec,
            write_kb_per_sec=write_kb_per_sec,
        )

    def format_disk_usage(self, disk_usage) -> str:
        """Formats disk usage information for display."""
        from .models import DiskUsage

        if not isinstance(disk_usage, DiskUsage):
            raise TypeError("Expected DiskUsage object")

        used_str = self.format_bytes(disk_usage.used_bytes)
        available_str = self.format_bytes(disk_usage.available_bytes)
        total_str = self.format_bytes(disk_usage.total_bytes)

        # Format: "Used: X, Available: Y, Total: Z"
        return f"Used: {used_str}, Available: {available_str}, Total: {total_str}"

    def format_io_metrics(self, rates: IORates) -> str:
        """Formats I/O rates for display."""
        # Implementation will be added in later tasks
        pass
