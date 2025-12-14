"""
Data collection layer for disk usage and I/O statistics.
"""

import os
import shutil
import time
from typing import List, Dict
import psutil
from .models import DiskUsage, IOStats


class DiskInfoCollector:
    """Collects disk usage and I/O statistics from the Linux system."""
    
    def get_disk_usage(self) -> List[DiskUsage]:
        """Returns usage statistics for all mounted disks."""
        disk_usage_list = []
        
        # Get all mounted disk partitions
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                # Skip special filesystems that don't represent actual disks
                if partition.fstype in ('tmpfs', 'devtmpfs', 'squashfs', 'overlay'):
                    continue
                    
                # Get disk usage statistics
                usage = shutil.disk_usage(partition.mountpoint)
                total_bytes = usage.total
                free_bytes = usage.free
                used_bytes = total_bytes - free_bytes
                
                # Calculate usage percentage
                usage_percent = (used_bytes / total_bytes * 100) if total_bytes > 0 else 0.0
                
                disk_usage = DiskUsage(
                    device=partition.device,
                    mountpoint=partition.mountpoint,
                    total_bytes=total_bytes,
                    used_bytes=used_bytes,
                    available_bytes=free_bytes,
                    usage_percent=usage_percent
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
            with open('/proc/diskstats', 'r') as f:
                for line in f:
                    fields = line.strip().split()
                    if len(fields) >= 14:
                        # Extract device name and statistics
                        device_name = fields[2]
                        
                        # Skip loop devices and ram devices
                        if device_name.startswith(('loop', 'ram')):
                            continue
                            
                        # Parse I/O statistics (fields from /proc/diskstats)
                        read_ops = int(fields[3])      # reads completed
                        write_ops = int(fields[7])     # writes completed  
                        read_sectors = int(fields[5])  # sectors read
                        write_sectors = int(fields[9]) # sectors written
                        
                        # Convert sectors to bytes (assuming 512 bytes per sector)
                        read_bytes = read_sectors * 512
                        write_bytes = write_sectors * 512
                        
                        io_stat = IOStats(
                            device=device_name,
                            read_ops=read_ops,
                            write_ops=write_ops,
                            read_bytes=read_bytes,
                            write_bytes=write_bytes,
                            timestamp=current_time
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
            # Skip special filesystems that don't represent actual disks
            if partition.fstype not in ('tmpfs', 'devtmpfs', 'squashfs', 'overlay'):
                mounted_disks.append(partition.device)
                
        return mounted_disks