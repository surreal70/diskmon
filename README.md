# Disk Monitor

A Python console application for real-time monitoring of disk usage and I/O performance on Linux systems.

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

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the disk monitor from the project root directory:

```bash
python -m disk_monitor
```

The application will start monitoring and display a real-time table of disk metrics. Press `Ctrl+C` to exit.

### Command Line Options

The application currently runs with default settings:
- Refresh interval: 2 seconds
- Displays all mounted disks (excluding special filesystems like tmpfs, devtmpfs)

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