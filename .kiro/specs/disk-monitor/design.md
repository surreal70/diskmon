# Disk Monitor Design Document

## Overview

The Disk Monitor is a Python3 console application that provides real-time monitoring of disk usage and I/O performance metrics on Linux systems. The application uses system APIs and the `/proc` filesystem to gather disk statistics, presenting them in a continuously updating console interface with human-readable formatting.

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **Data Collection Layer**: Interfaces with Linux system APIs to gather disk and I/O statistics
- **Data Processing Layer**: Formats raw system data into human-readable metrics
- **Display Layer**: Manages console output and screen updates
- **Main Controller**: Orchestrates the monitoring loop and coordinates between layers

The architecture supports real-time updates through a polling mechanism that refreshes data every 2 seconds.

## Components and Interfaces

### DiskInfoCollector
**Purpose**: Collects disk usage and I/O statistics from the Linux system
**Key Methods**:
- `get_disk_usage()` -> List[DiskUsage]: Returns usage statistics for all mounted disks
- `get_disk_io_stats()` -> Dict[str, IOStats]: Returns I/O statistics per disk device
- `get_mounted_disks()` -> List[str]: Returns list of currently mounted disk devices

### MetricsFormatter  
**Purpose**: Converts raw system data into human-readable formats
**Key Methods**:
- `format_bytes(bytes: int) -> str`: Converts bytes to MB/GB/TB with appropriate precision
- `calculate_io_rates(current: IOStats, previous: IOStats, interval: float) -> IORates`: Calculates per-second rates
- `format_io_metrics(rates: IORates) -> str`: Formats I/O rates for display

### ConsoleDisplay
**Purpose**: Manages console output and screen updates
**Key Methods**:
- `clear_screen()`: Clears the console display
- `display_header()`: Shows column headers for the metrics table
- `display_disk_row(disk_info: DiskInfo)`: Displays metrics for a single disk
- `display_error(message: str)`: Shows error messages

### DiskMonitor (Main Controller)
**Purpose**: Coordinates the monitoring loop and manages application lifecycle
**Key Methods**:
- `run()`: Main monitoring loop
- `handle_shutdown()`: Graceful shutdown handling
- `update_display()`: Orchestrates data collection and display update

## Data Models

### DiskUsage
```python
@dataclass
class DiskUsage:
    device: str          # Device path (e.g., /dev/sda1)
    mountpoint: str      # Mount path (e.g., /)
    total_bytes: int     # Total disk capacity
    used_bytes: int      # Used space
    available_bytes: int # Available space
    usage_percent: float # Percentage used
```

### IOStats
```python
@dataclass  
class IOStats:
    device: str          # Device name (e.g., sda)
    read_ops: int        # Total read operations
    write_ops: int       # Total write operations  
    read_bytes: int      # Total bytes read
    write_bytes: int     # Total bytes written
    timestamp: float     # When stats were collected
```

### IORates
```python
@dataclass
class IORates:
    device: str              # Device name
    read_ops_per_sec: float  # Read operations per second
    write_ops_per_sec: float # Write operations per second
    read_kb_per_sec: float   # Read throughput in KB/s
    write_kb_per_sec: float  # Write throughput in KB/s
```
## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Disk usage display completeness
*For any* disk usage data, the display output should contain used space, available space, and total capacity information
**Validates: Requirements 1.2**

### Property 2: Human-readable formatting consistency  
*For any* byte value, the formatting function should return a string with appropriate units (MB, GB, TB) and consistent precision
**Validates: Requirements 1.3**

### Property 3: High usage display stability
*For any* disk usage percentage including values near 100%, the display should show the information without triggering additional alerts or errors
**Validates: Requirements 1.4**

### Property 4: Read operations rate calculation accuracy
*For any* pair of I/O statistics with valid timestamps, the calculated read operations per second should equal the difference in read operations divided by the time interval
**Validates: Requirements 2.1**

### Property 5: Write operations rate calculation accuracy  
*For any* pair of I/O statistics with valid timestamps, the calculated write operations per second should equal the difference in write operations divided by the time interval
**Validates: Requirements 2.2**

### Property 6: Read throughput calculation accuracy
*For any* pair of I/O statistics with valid timestamps, the calculated read throughput in KB/s should equal the difference in read bytes divided by the time interval and converted to kilobytes
**Validates: Requirements 2.3**

### Property 7: Write throughput calculation accuracy
*For any* pair of I/O statistics with valid timestamps, the calculated write throughput in KB/s should equal the difference in write bytes divided by the time interval and converted to kilobytes  
**Validates: Requirements 2.4**

### Property 8: Rate calculation interval consistency
*For any* I/O rate calculation, when given statistics separated by a 2-second interval, the calculated rates should use exactly that interval in the computation
**Validates: Requirements 2.5**

### Property 9: Tabular format structure
*For any* set of disk metrics, the display output should contain proper table formatting with consistent column alignment and headers
**Validates: Requirements 3.1**

### Property 10: Disk layout consistency
*For any* sequence of display updates with the same set of disks, each disk should appear in the same relative position across all updates
**Validates: Requirements 3.4**

### Property 11: Error handling robustness
*For any* system condition where I/O statistics are unavailable or corrupted, the application should handle the error gracefully without terminating unexpectedly
**Validates: Requirements 4.3**

## Error Handling

The application implements comprehensive error handling across all system interactions:

### System Access Errors
- **File system access failures**: Graceful degradation when `/proc/diskstats` or mount information is unavailable
- **Permission errors**: Clear error messages when insufficient privileges prevent data access
- **Device enumeration failures**: Continued operation when some devices cannot be queried

### Data Processing Errors  
- **Invalid system data**: Validation and sanitization of all system-provided statistics
- **Calculation errors**: Safe handling of division by zero and negative values in rate calculations
- **Format conversion errors**: Fallback formatting when byte conversion fails

### Display Errors
- **Console access issues**: Graceful handling when terminal capabilities are limited
- **Screen size constraints**: Adaptive display when terminal is too small for full output
- **Character encoding problems**: Safe handling of device names with special characters

## Testing Strategy

The testing approach combines unit testing and property-based testing to ensure comprehensive coverage:

### Unit Testing Framework
- **Framework**: pytest for Python unit testing
- **Coverage**: Specific examples, edge cases, and integration points between components
- **Mock Strategy**: Mock system calls and file system access for predictable testing

### Property-Based Testing Framework  
- **Framework**: Hypothesis for Python property-based testing
- **Configuration**: Minimum 100 iterations per property test to ensure thorough validation
- **Test Tagging**: Each property test tagged with format: `**Feature: disk-monitor, Property {number}: {property_text}**`

### Testing Approach
- **Unit tests** verify specific examples that demonstrate correct behavior and test integration points between components
- **Property tests** verify universal properties that should hold across all inputs, focusing on mathematical correctness of calculations and formatting consistency
- **Combined coverage** ensures both concrete bugs are caught by unit tests and general correctness is verified by property tests

### Test Categories
- **Data collection tests**: Verify system data parsing and device enumeration
- **Calculation tests**: Validate I/O rate calculations and byte formatting
- **Display tests**: Ensure proper console output formatting and error handling
- **Integration tests**: Test end-to-end workflows and error recovery scenarios