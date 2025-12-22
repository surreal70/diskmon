# Disk Monitor

A Python console application for real-time monitoring of disk usage and I/O performance on Linux systems.

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

**Copyright (C) 2025 Andreas Huemmer <andreas.huemmer@adminsend.de>**

## Changelog

### Version 1.0.0 (2025-12-22)

#### Added
- **Command Line Interface**: Added support for command line arguments
  - `--net` flag to include network mounted drives (NFS, CIFS, SMB, SSHFS, etc.)
  - `--time SECONDS` option to set custom refresh interval (default: 2.0s, minimum: 0.1s)
- **Network Filesystem Support**: Enhanced collector to properly handle network drives
  - Automatic detection of network filesystem types (NFS, CIFS, SMB, SSHFS, GlusterFS)
  - Configurable inclusion/exclusion of network drives
- **GPL v3 Licensing**: Added comprehensive GPL v3 license headers to all source files
- **Python Development Framework**: Applied standardized Python development practices
  - Virtual environment support with automated setup
  - PEP 8 compliance with Black formatting and Flake8 linting
  - Modern Python packaging with pyproject.toml
  - Comprehensive development tooling (tox, pre-commit, mypy)
- **Author-Copyright Headers**: Enhanced all source files with detailed metadata
  - Author attribution and copyright notices
  - Version tracking and changelog information
  - GPL v3 license headers with proper formatting
- **Enhanced Documentation**: Updated README with comprehensive setup and usage instructions

#### Changed
- **Flexible Refresh Interval**: Replaced fixed 2-second refresh with configurable timing
- **Improved Startup Messages**: Added informative messages about configuration and network drive inclusion
- **Enhanced Error Handling**: Better validation for command line arguments and system access
- **Code Quality**: 100% PEP 8 compliance with automated formatting and linting

#### Technical Details
- **Architecture**: Clean modular design with separation of concerns
  - `monitor.py`: Main controller with monitoring loop and signal handling
  - `collector.py`: System data collection from Linux `/proc/diskstats` and psutil
  - `models.py`: Type-safe data structures using dataclasses
  - `formatter.py`: Data formatting and rate calculations
  - `display.py`: Console output with tabular formatting
- **Testing**: Comprehensive property-based testing using Hypothesis framework
- **Compatibility**: Python 3.8+ with Linux system requirements (currently using Python 3.12.7)
- **Dependencies**: psutil for cross-platform disk operations, comprehensive dev dependencies
- **Development Environment**: Virtual environment with full development toolchain

#### Initial Features
- **Real-time Monitoring**: Live disk usage and I/O performance tracking
- **Comprehensive Metrics**: 
  - Disk usage (used, available, total space, usage percentage)
  - I/O performance (read/write operations per second, throughput in KB/s)
- **Clean Console Interface**: Formatted table output with proper column alignment
- **Graceful Shutdown**: Handles Ctrl+C and system signals properly
- **Robust Error Handling**: Continues running even when encountering system access errors
- **Smart Filtering**: Automatically excludes special filesystems (tmpfs, devtmpfs, squashfs, overlay)

## Features

- **Real-time disk usage monitoring** - Shows used, available, and total space for all mounted disks
- **I/O performance tracking** - Displays read/write operations per second and throughput in KB/s
- **Auto-refresh display** - Updates every 2 seconds with live data
- **Clean console interface** - Formatted table output with proper column alignment
- **Graceful shutdown** - Handles Ctrl+C and system signals properly
- **Error handling** - Continues running even when encountering system access errors

## Requirements

- Python 3.6+
- Linux operating system
- psutil library (automatically installed with requirements)

## Installation

### Prerequisites

- Python 3.8 or higher (currently tested with Python 3.12.7)
- Linux operating system
- Virtual environment support (recommended)

### Quick Setup

1. Clone or download this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # or
   venv\Scripts\activate     # On Windows
   ```
3. Install the application:
   ```bash
   pip install -e .
   ```

### Development Setup

For development work, install with development dependencies:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev,test]"
pip install -r requirements-dev.txt

# Optional: Install pre-commit hooks
pre-commit install
```

### Using Make (Recommended)

The project includes a comprehensive Makefile for common development tasks:

```bash
# Setup development environment
make dev-setup

# Activate virtual environment
source venv/bin/activate

# Run the application
make run

# Run tests
make test

# Check code quality
make check

# Format code
make format
```

## Usage

Run the disk monitor from the project root directory:

```bash
python -m disk_monitor
```

The application will start monitoring and display a real-time table of disk metrics. Press `Ctrl+C` to exit.

### Command Line Options

- `--net`: Include network mounted drives (NFS, CIFS, etc.) in monitoring
- `--time SECONDS`: Set refresh interval in seconds (default: 2.0, minimum: 0.1)

#### Examples

```bash
# Default monitoring (2s refresh, no network drives)
python -m disk_monitor

# Include network mounted drives
python -m disk_monitor --net

# Refresh every 5 seconds
python -m disk_monitor --time 5

# Include network drives and refresh every 1 second
python -m disk_monitor --net --time 1

# Fast refresh for detailed monitoring
python -m disk_monitor --time 0.5
```

### Default Behavior

The application runs with these default settings:
- Refresh interval: 2 seconds
- Network drives: Excluded (only local disks shown)
- Displays all mounted local disks (excluding special filesystems like tmpfs, devtmpfs)
- Network filesystems (NFS, CIFS, SMB, SSHFS, etc.) are filtered out unless `--net` is specified

## Sample Output

```
Starting disk monitor... Press Ctrl+C to exit.
Device          Mount Point          Used       Available  Total      Usage %  Read Ops/s   Write Ops/s   Read KB/s    Write KB/s  
-----------------------------------------------------------------------------------------------------------------------------------
/dev/nvme1n1p2  /                    114.3 GB   353.5 GB   467.9 GB   24.4%    0.0          6.5           0.0          121.8       
/dev/nvme1n1p1  /boot/efi            6.1 MB     504.9 MB   511.0 MB   1.2%     0.0          6.5           0.0          121.8       
/dev/nvme0n1p1  /data                56.1 GB    859.8 GB   915.8 GB   6.1%     0.0          0.0           0.0          0.0         
/dev/nvme1n1p2  /var/snap/firefox/c  114.3 GB   353.5 GB   467.9 GB   24.4%    0.0          6.5           0.0          121.8       
```

### Column Descriptions

- **Device**: The disk device path (e.g., /dev/nvme1n1p2)
- **Mount Point**: Where the disk is mounted in the filesystem
- **Used**: Amount of disk space currently used
- **Available**: Amount of free disk space available
- **Total**: Total disk capacity
- **Usage %**: Percentage of disk space used
- **Read Ops/s**: Number of read operations per second
- **Write Ops/s**: Number of write operations per second  
- **Read KB/s**: Data read throughput in kilobytes per second
- **Write KB/s**: Data write throughput in kilobytes per second

*Note: I/O statistics show "N/A" for the first refresh cycle as rates are calculated between measurements.*

## Architecture

The application follows a clean modular architecture:

- **`monitor.py`** - Main controller and monitoring loop
- **`collector.py`** - Data collection from system APIs (/proc/diskstats, psutil)
- **`models.py`** - Data structures for disk usage and I/O statistics
- **`formatter.py`** - Data formatting and rate calculations
- **`display.py`** - Console output and screen management

## Development

### Running Tests

The project includes property-based tests using pytest and Hypothesis:

```bash
pytest
```

### Project Structure

```
disk_monitor/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point
├── monitor.py           # Main controller
├── collector.py         # System data collection
├── models.py            # Data models
├── formatter.py         # Data formatting
└── display.py           # Console display
tests/
├── test_collector_properties.py
├── test_display_properties.py
├── test_formatter_properties.py
└── test_monitor_properties.py
```

## Technical Details

- Uses `/proc/diskstats` for I/O statistics on Linux systems
- Leverages `psutil` library for cross-platform disk usage information
- Implements proper signal handling for graceful shutdown
- Calculates I/O rates by comparing measurements over time intervals
- Filters out special filesystems (tmpfs, devtmpfs, squashfs, overlay)

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Troubleshooting

**Permission Errors**: The application may show "N/A" for I/O statistics if it cannot read `/proc/diskstats`. This is normal for non-privileged users on some systems.

**Missing Disks**: Only mounted filesystems are displayed. Unmounted disks or special filesystems are filtered out by design.

**High CPU Usage**: The 2-second refresh interval is optimized for real-time monitoring while maintaining reasonable system resource usage.