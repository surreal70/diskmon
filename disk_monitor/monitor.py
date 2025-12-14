"""
Main controller for the disk monitor application.
"""

import signal
import sys
import time
from typing import Dict, Optional
from .collector import DiskInfoCollector
from .formatter import MetricsFormatter
from .display import ConsoleDisplay
from .models import IOStats, IORates


class DiskMonitor:
    """Main controller that coordinates the monitoring loop and manages application lifecycle."""
    
    def __init__(self):
        self.collector = DiskInfoCollector()
        self.formatter = MetricsFormatter()
        self.display = ConsoleDisplay()
        self.running = True
        self.previous_io_stats: Dict[str, IOStats] = {}
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def run(self):
        """Main monitoring loop with 2-second refresh interval."""
        print("Starting disk monitor... Press Ctrl+C to exit.")
        
        try:
            while self.running:
                self.update_display()
                time.sleep(2.0)  # 2-second refresh interval as per requirements
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
                            interval = current_stats.timestamp - previous_stats.timestamp
                            if interval > 0:
                                rates = self.formatter.calculate_io_rates(
                                    current_stats, previous_stats, interval
                                )
                                io_rates_dict[device] = rates
                        except (ValueError, ZeroDivisionError) as e:
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