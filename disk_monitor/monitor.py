#!/usr/bin/env python3
"""
Disk Monitor - Main controller for the disk monitor application.

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
- 2025-12-22 v1.0.0: Enhanced monitoring controller
  * Added configurable refresh interval support
  * Added network drive inclusion option
  * Implemented graceful shutdown with signal handling
  * Enhanced error handling and user feedback

Main controller for the disk monitor application.
"""

import signal
import sys
import time
from typing import Dict
from .collector import DiskInfoCollector
from .formatter import MetricsFormatter
from .display import ConsoleDisplay
from .models import IOStats


class DiskMonitor:
    """Main controller that coordinates monitoring loop and application lifecycle."""

    def __init__(self, include_network=False, refresh_interval=2.0):
        """
        Initialize the disk monitor.

        Args:
            include_network (bool): Whether to include network mounted drives
            refresh_interval (float): Refresh interval in seconds
        """
        self.collector = DiskInfoCollector(include_network=include_network)
        self.formatter = MetricsFormatter()
        self.display = ConsoleDisplay()
        self.running = True
        self.refresh_interval = refresh_interval
        self.previous_io_stats: Dict[str, IOStats] = {}

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def run(self):
        """Main monitoring loop with configurable refresh interval."""
        network_msg = (
            " (including network drives)" if self.collector.include_network else ""
        )
        print(f"Starting disk monitor{network_msg}... Press Ctrl+C to exit.")
        print(f"Refresh interval: {self.refresh_interval} seconds")

        try:
            while self.running:
                self.update_display()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            self.handle_shutdown(signal.SIGINT, None)
        except Exception as e:
            self.display.display_error(f"Unexpected error in monitoring loop: {e}")
            self.handle_shutdown(None, None)

    def handle_shutdown(self, signum, frame):
        """Graceful shutdown handling with signal handlers."""
        self.running = False
        print("\nShutting down disk monitor...")
        # Clear screen and restore normal console state
        try:
            self.display.clear_screen()
        except Exception:
            pass  # Ignore errors during shutdown
        sys.exit(0)

    def update_display(self):
        """Orchestrates data collection and display update with error handling."""
        try:
            # Collect disk usage information
            disk_usages = self.collector.get_disk_usage()

            # Collect I/O statistics
            current_io_stats = self.collector.get_disk_io_stats()

            # Calculate I/O rates if we have previous data
            io_rates_dict = {}
            if self.previous_io_stats:
                for device, current_stats in current_io_stats.items():
                    if device in self.previous_io_stats:
                        try:
                            previous_stats = self.previous_io_stats[device]
                            interval = (
                                current_stats.timestamp - previous_stats.timestamp
                            )
                            if interval > 0:
                                rates = self.formatter.calculate_io_rates(
                                    current_stats, previous_stats, interval
                                )
                                io_rates_dict[device] = rates
                        except (ValueError, ZeroDivisionError):
                            # Skip rate calculation for this device if there's an error
                            continue

            # Store current stats for next iteration
            self.previous_io_stats = current_io_stats

            # Display the metrics
            self.display.display_disk_metrics(disk_usages, io_rates_dict)

        except (OSError, IOError, PermissionError) as e:
            # Handle system access errors gracefully
            self.display.display_error(f"System access error: {e}")
            # Continue running - don't crash on system errors
        except Exception as e:
            # Handle any other unexpected errors
            self.display.display_error(f"Unexpected error during update: {e}")
            # Continue running - don't crash on unexpected errors
