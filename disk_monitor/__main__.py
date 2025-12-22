#!/usr/bin/env python3
"""
Disk Monitor - Real-time disk usage and I/O performance monitor for Linux systems.

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
- 2025-12-22 v1.0.0: Initial release with command line argument support
  * Added --net flag for network drive inclusion
  * Added --time option for configurable refresh interval
  * Implemented argument parsing and validation

Main entry point for the disk monitor application.
"""

import argparse
from .monitor import DiskMonitor


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Real-time disk usage and I/O performance monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m disk_monitor                    # Default monitoring
  python -m disk_monitor --net              # Include network drives
  python -m disk_monitor --time 5           # Refresh every 5 seconds
  python -m disk_monitor --net --time 1     # Network drives, 1s refresh
        """,
    )

    parser.add_argument(
        "--net",
        action="store_true",
        help="Include network mounted drives (NFS, CIFS, etc.) in monitoring",
    )

    parser.add_argument(
        "--time",
        type=float,
        default=2.0,
        metavar="SECONDS",
        help="Set refresh interval in seconds (default: 2.0, minimum: 0.1)",
    )

    return parser.parse_args()


def main():
    """Main entry point function."""
    args = parse_arguments()

    # Validate refresh interval
    if args.time < 0.1:
        print("Error: Refresh interval must be at least 0.1 seconds")
        return 1

    monitor = DiskMonitor(include_network=args.net, refresh_interval=args.time)
    monitor.run()
    return 0


if __name__ == "__main__":
    exit(main())
