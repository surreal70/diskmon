"""
Property-based tests for the MetricsFormatter class.

**Feature: disk-monitor, Property 2: Human-readable formatting consistency**
"""

import pytest
from hypothesis import given, strategies as st
from disk_monitor.formatter import MetricsFormatter
from disk_monitor.models import DiskUsage


class TestMetricsFormatterProperties:
    """Property-based tests for MetricsFormatter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = MetricsFormatter()
    
    @given(st.integers(min_value=0, max_value=10**18))
    def test_human_readable_formatting_consistency(self, bytes_value):
        """
        **Feature: disk-monitor, Property 2: Human-readable formatting consistency**
        **Validates: Requirements 1.3**
        
        For any byte value, the formatting function should return a string 
        with appropriate units (MB, GB, TB) and consistent precision.
        """
        result = self.formatter.format_bytes(bytes_value)
        
        # Property: Result should always be a string
        assert isinstance(result, str)
        
        # Property: Result should contain a numeric value followed by a unit
        parts = result.split()
        assert len(parts) == 2, f"Expected format 'number unit', got '{result}'"
        
        numeric_part, unit_part = parts
        
        # Property: Numeric part should be parseable as float
        try:
            numeric_value = float(numeric_part)
            assert numeric_value >= 0, f"Numeric value should be non-negative, got {numeric_value}"
        except ValueError:
            pytest.fail(f"Numeric part '{numeric_part}' should be parseable as float")
        
        # Property: Unit should be one of the expected units
        expected_units = {'B', 'KB', 'MB', 'GB', 'TB'}
        assert unit_part in expected_units, f"Unit '{unit_part}' should be one of {expected_units}"
        
        # Property: For values >= 1024, should use larger units when appropriate
        if bytes_value >= 1024**4:  # >= 1 TB
            assert unit_part == 'TB'
        elif bytes_value >= 1024**3:  # >= 1 GB
            assert unit_part in {'GB', 'TB'}
        elif bytes_value >= 1024**2:  # >= 1 MB
            assert unit_part in {'MB', 'GB', 'TB'}
        elif bytes_value >= 1024:  # >= 1 KB
            assert unit_part in {'KB', 'MB', 'GB', 'TB'}
        else:  # < 1 KB
            assert unit_part == 'B'
        
        # Property: Precision should be consistent (1 decimal place for non-byte units)
        if unit_part != 'B' and '.' in numeric_part:
            decimal_places = len(numeric_part.split('.')[1])
            assert decimal_places == 1, f"Expected 1 decimal place for {unit_part}, got {decimal_places}"
    
    @given(
        device=st.text(min_size=1, max_size=20),
        mountpoint=st.text(min_size=1, max_size=50),
        total_bytes=st.integers(min_value=1, max_value=10**18),
        used_bytes=st.integers(min_value=0, max_value=10**18)
    )
    def test_disk_usage_display_completeness(self, device, mountpoint, total_bytes, used_bytes):
        """
        **Feature: disk-monitor, Property 1: Disk usage display completeness**
        **Validates: Requirements 1.2**
        
        For any disk usage data, the display output should contain used space, 
        available space, and total capacity information.
        """
        # Ensure used_bytes doesn't exceed total_bytes
        if used_bytes > total_bytes:
            used_bytes = total_bytes
        
        available_bytes = total_bytes - used_bytes
        usage_percent = (used_bytes / total_bytes) * 100 if total_bytes > 0 else 0
        
        disk_usage = DiskUsage(
            device=device,
            mountpoint=mountpoint,
            total_bytes=total_bytes,
            used_bytes=used_bytes,
            available_bytes=available_bytes,
            usage_percent=usage_percent
        )
        
        result = self.formatter.format_disk_usage(disk_usage)
        
        # Property: Result should be a string
        assert isinstance(result, str)
        
        # Property: Result should contain "Used:", "Available:", and "Total:" labels
        assert "Used:" in result, f"Result should contain 'Used:', got '{result}'"
        assert "Available:" in result, f"Result should contain 'Available:', got '{result}'"
        assert "Total:" in result, f"Result should contain 'Total:', got '{result}'"
        
        # Property: Each value should be formatted with appropriate units
        # Extract the formatted values
        parts = result.split(", ")
        assert len(parts) == 3, f"Expected 3 parts separated by ', ', got {len(parts)}: {result}"
        
        used_part = parts[0].replace("Used: ", "")
        available_part = parts[1].replace("Available: ", "")
        total_part = parts[2].replace("Total: ", "")
        
        # Property: Each part should be a valid formatted byte string
        for part_name, part_value in [("Used", used_part), ("Available", available_part), ("Total", total_part)]:
            value_parts = part_value.split()
            assert len(value_parts) == 2, f"{part_name} part should have format 'number unit', got '{part_value}'"
            
            numeric_part, unit_part = value_parts
            try:
                float(numeric_part)
            except ValueError:
                pytest.fail(f"{part_name} numeric part '{numeric_part}' should be parseable as float")
            
            expected_units = {'B', 'KB', 'MB', 'GB', 'TB'}
            assert unit_part in expected_units, f"{part_name} unit '{unit_part}' should be one of {expected_units}"
    
    @given(
        device=st.text(min_size=1, max_size=20),
        mountpoint=st.text(min_size=1, max_size=50),
        total_bytes=st.integers(min_value=1, max_value=10**18),
        usage_percent=st.floats(min_value=95.0, max_value=100.0)
    )
    def test_high_usage_display_stability(self, device, mountpoint, total_bytes, usage_percent):
        """
        **Feature: disk-monitor, Property 3: High usage display stability**
        **Validates: Requirements 1.4**
        
        For any disk usage percentage including values near 100%, the display should 
        show the information without triggering additional alerts or errors.
        """
        used_bytes = int((usage_percent / 100.0) * total_bytes)
        # Ensure used_bytes doesn't exceed total_bytes due to floating point precision
        if used_bytes > total_bytes:
            used_bytes = total_bytes
        
        available_bytes = total_bytes - used_bytes
        
        disk_usage = DiskUsage(
            device=device,
            mountpoint=mountpoint,
            total_bytes=total_bytes,
            used_bytes=used_bytes,
            available_bytes=available_bytes,
            usage_percent=usage_percent
        )
        
        # Property: Should not raise any exceptions for high usage scenarios
        try:
            result = self.formatter.format_disk_usage(disk_usage)
        except Exception as e:
            pytest.fail(f"format_disk_usage should not raise exceptions for high usage, got: {e}")
        
        # Property: Result should still be a valid string
        assert isinstance(result, str)
        assert len(result) > 0, "Result should not be empty for high usage scenarios"
        
        # Property: Should still contain all required information
        assert "Used:" in result, f"High usage result should contain 'Used:', got '{result}'"
        assert "Available:" in result, f"High usage result should contain 'Available:', got '{result}'"
        assert "Total:" in result, f"High usage result should contain 'Total:', got '{result}'"
        
        # Property: Should handle edge case where available space is 0
        if available_bytes == 0:
            assert "Available: 0 B" in result, f"Should show '0 B' for zero available space, got '{result}'"