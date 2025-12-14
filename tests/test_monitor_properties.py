"""
Property-based tests for the DiskMonitor main controller.

**Feature: disk-monitor, Property 11: Error handling robustness**
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import patch, Mock, MagicMock
from disk_monitor.monitor import DiskMonitor
from disk_monitor.models import DiskUsage, IOStats


class TestDiskMonitorProperties:
    """Property-based tests for DiskMonitor error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = DiskMonitor()
    
    @given(
        error_type=st.sampled_from([OSError, IOError, PermissionError, FileNotFoundError]),
        error_message=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc',)))
    )
    def test_error_handling_robustness(self, error_type, error_message):
        """
        **Feature: disk-monitor, Property 11: Error handling robustness**
        **Validates: Requirements 4.3**
        
        For any system condition where I/O statistics are unavailable or corrupted, 
        the application should handle the error gracefully without terminating unexpectedly.
        """
        # Mock the collector to raise various system errors
        with patch.object(self.monitor.collector, 'get_disk_usage') as mock_disk_usage, \
             patch.object(self.monitor.collector, 'get_disk_io_stats') as mock_io_stats, \
             patch.object(self.monitor.display, 'display_error') as mock_display_error, \
             patch.object(self.monitor.display, 'display_disk_metrics') as mock_display_metrics:
            
            # Configure mocks to raise the specified error
            mock_disk_usage.side_effect = error_type(error_message)
            mock_io_stats.side_effect = error_type(error_message)
            
            # Property: update_display should not raise exceptions when system errors occur
            try:
                self.monitor.update_display()
            except Exception as e:
                pytest.fail(f"update_display should handle {error_type.__name__} gracefully, but raised: {e}")
            
            # Property: Error should be displayed to user when system access fails
            mock_display_error.assert_called()
            
            # Property: Should not attempt to display metrics when data collection fails
            # (This depends on implementation - may or may not be called with empty data)
    
    @given(
        disk_usage_error=st.booleans(),
        io_stats_error=st.booleans(),
        error_message=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc',)))
    )
    def test_partial_error_handling(self, disk_usage_error, io_stats_error, error_message):
        """
        Property test for handling partial system failures.
        
        For any combination of disk usage and I/O statistics failures, 
        the application should continue operating with available data.
        """
        # Create some valid test data
        valid_disk_usage = [
            DiskUsage(
                device="/dev/sda1",
                mountpoint="/",
                total_bytes=1000000000,
                used_bytes=500000000,
                available_bytes=500000000,
                usage_percent=50.0
            )
        ]
        
        valid_io_stats = {
            "sda": IOStats(
                device="sda",
                read_ops=1000,
                write_ops=500,
                read_bytes=1024000,
                write_bytes=512000,
                timestamp=1234567890.0
            )
        }
        
        with patch.object(self.monitor.collector, 'get_disk_usage') as mock_disk_usage, \
             patch.object(self.monitor.collector, 'get_disk_io_stats') as mock_io_stats, \
             patch.object(self.monitor.display, 'display_error') as mock_display_error, \
             patch.object(self.monitor.display, 'display_disk_metrics') as mock_display_metrics:
            
            # Configure mocks based on error conditions
            if disk_usage_error:
                mock_disk_usage.side_effect = OSError(error_message)
            else:
                mock_disk_usage.return_value = valid_disk_usage
            
            if io_stats_error:
                mock_io_stats.side_effect = IOError(error_message)
            else:
                mock_io_stats.return_value = valid_io_stats
            
            # Property: Should not crash regardless of which subsystem fails
            try:
                self.monitor.update_display()
            except Exception as e:
                pytest.fail(f"update_display should handle partial failures gracefully, but raised: {e}")
            
            # Property: Should display error messages for failed subsystems
            if disk_usage_error or io_stats_error:
                mock_display_error.assert_called()
    
    @given(
        corrupted_data_type=st.sampled_from(['empty_list', 'invalid_values', 'missing_fields']),
        num_iterations=st.integers(min_value=1, max_value=5)
    )
    def test_corrupted_data_handling(self, corrupted_data_type, num_iterations):
        """
        Property test for handling corrupted or invalid system data.
        
        For any type of corrupted system data, the application should 
        handle it gracefully without crashing.
        """
        with patch.object(self.monitor.collector, 'get_disk_usage') as mock_disk_usage, \
             patch.object(self.monitor.collector, 'get_disk_io_stats') as mock_io_stats, \
             patch.object(self.monitor.display, 'display_error') as mock_display_error, \
             patch.object(self.monitor.display, 'display_disk_metrics') as mock_display_metrics:
            
            # Configure mocks to return corrupted data
            if corrupted_data_type == 'empty_list':
                mock_disk_usage.return_value = []
                mock_io_stats.return_value = {}
            elif corrupted_data_type == 'invalid_values':
                # Create disk usage with invalid values
                invalid_disk_usage = [
                    DiskUsage(
                        device="",  # Empty device name
                        mountpoint="",  # Empty mount point
                        total_bytes=-1,  # Negative total
                        used_bytes=-1,  # Negative used
                        available_bytes=-1,  # Negative available
                        usage_percent=-1.0  # Negative percentage
                    )
                ]
                mock_disk_usage.return_value = invalid_disk_usage
                mock_io_stats.return_value = {"": IOStats("", -1, -1, -1, -1, -1.0)}
            elif corrupted_data_type == 'missing_fields':
                # This would be handled by the dataclass validation, 
                # but we can test with None values
                mock_disk_usage.return_value = None
                mock_io_stats.return_value = None
            
            # Property: Should handle corrupted data gracefully for multiple iterations
            for _ in range(num_iterations):
                try:
                    self.monitor.update_display()
                except Exception as e:
                    pytest.fail(f"update_display should handle corrupted data gracefully, but raised: {e}")
    
    @given(
        permission_denied=st.booleans(),
        file_not_found=st.booleans(),
        io_error=st.booleans()
    )
    def test_system_access_error_recovery(self, permission_denied, file_not_found, io_error):
        """
        Property test for recovery from various system access errors.
        
        For any combination of system access errors, the application should 
        continue attempting to collect data on subsequent updates.
        """
        # Skip the case where no errors occur (not testing error recovery)
        if not (permission_denied or file_not_found or io_error):
            return
        
        with patch.object(self.monitor.collector, 'get_disk_usage') as mock_disk_usage, \
             patch.object(self.monitor.collector, 'get_disk_io_stats') as mock_io_stats, \
             patch.object(self.monitor.display, 'display_error') as mock_display_error, \
             patch.object(self.monitor.display, 'display_disk_metrics') as mock_display_metrics:
            
            # Configure first call to fail with specified errors
            errors = []
            if permission_denied:
                errors.append(PermissionError("Permission denied"))
            if file_not_found:
                errors.append(FileNotFoundError("File not found"))
            if io_error:
                errors.append(IOError("I/O error"))
            
            # Use the first error for the first call
            first_error = errors[0]
            
            # Configure mocks to succeed on first call, then fail on specific method
            valid_disk_usage = [
                DiskUsage(
                    device="/dev/sda1",
                    mountpoint="/",
                    total_bytes=1000000000,
                    used_bytes=500000000,
                    available_bytes=500000000,
                    usage_percent=50.0
                )
            ]
            valid_io_stats = {}
            
            # Make only one method fail, so we can test recovery
            mock_disk_usage.side_effect = [first_error, valid_disk_usage]  # Fail first, succeed second
            mock_io_stats.return_value = valid_io_stats  # Always succeed
            
            # Property: First call should handle error gracefully
            try:
                self.monitor.update_display()
            except Exception as e:
                pytest.fail(f"First update_display call should handle {type(first_error).__name__} gracefully, but raised: {e}")
            
            # Property: Should display error for first call
            mock_display_error.assert_called()
            
            # Reset mock call counts
            mock_display_error.reset_mock()
            
            # Property: Second call should succeed (recovery)
            try:
                self.monitor.update_display()
            except Exception as e:
                pytest.fail(f"Second update_display call should succeed after recovery, but raised: {e}")
            
            # Property: Should attempt to collect disk usage data again (methods called twice total)
            assert mock_disk_usage.call_count == 2, "Should attempt disk usage collection twice"
            
            # Property: Should not display error on successful recovery
            mock_display_error.assert_not_called()