"""
Property-based tests for rate calculations and data collection.

**Feature: disk-monitor, Properties 4-8: Rate calculation accuracy and consistency**
"""

import pytest
from hypothesis import given, strategies as st, assume
from disk_monitor.models import IOStats
from disk_monitor.formatter import MetricsFormatter
import time


class TestRateCalculationProperties:
    """Property-based tests for I/O rate calculations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = MetricsFormatter()
    
    @given(
        device_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        initial_read_ops=st.integers(min_value=0, max_value=10**9),
        additional_read_ops=st.integers(min_value=0, max_value=10**6),
        interval=st.floats(min_value=0.1, max_value=10.0)
    )
    def test_read_operations_rate_calculation_accuracy(self, device_name, initial_read_ops, additional_read_ops, interval):
        """
        **Feature: disk-monitor, Property 4: Read operations rate calculation accuracy**
        **Validates: Requirements 2.1**
        
        For any pair of I/O statistics with valid timestamps, the calculated read operations 
        per second should equal the difference in read operations divided by the time interval.
        """
        # Create two IOStats with different read operations
        timestamp1 = time.time()
        timestamp2 = timestamp1 + interval
        
        previous_stats = IOStats(
            device=device_name,
            read_ops=initial_read_ops,
            write_ops=0,
            read_bytes=0,
            write_bytes=0,
            timestamp=timestamp1
        )
        
        current_stats = IOStats(
            device=device_name,
            read_ops=initial_read_ops + additional_read_ops,
            write_ops=0,
            read_bytes=0,
            write_bytes=0,
            timestamp=timestamp2
        )
        
        # Calculate rates
        rates = self.formatter.calculate_io_rates(current_stats, previous_stats, interval)
        
        # Property: Read operations per second should equal difference divided by interval
        expected_read_ops_per_sec = additional_read_ops / interval
        assert abs(rates.read_ops_per_sec - expected_read_ops_per_sec) < 1e-10, \
            f"Expected {expected_read_ops_per_sec}, got {rates.read_ops_per_sec}"
    
    @given(
        device_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        initial_write_ops=st.integers(min_value=0, max_value=10**9),
        additional_write_ops=st.integers(min_value=0, max_value=10**6),
        interval=st.floats(min_value=0.1, max_value=10.0)
    )
    def test_write_operations_rate_calculation_accuracy(self, device_name, initial_write_ops, additional_write_ops, interval):
        """
        **Feature: disk-monitor, Property 5: Write operations rate calculation accuracy**
        **Validates: Requirements 2.2**
        
        For any pair of I/O statistics with valid timestamps, the calculated write operations 
        per second should equal the difference in write operations divided by the time interval.
        """
        # Create two IOStats with different write operations
        timestamp1 = time.time()
        timestamp2 = timestamp1 + interval
        
        previous_stats = IOStats(
            device=device_name,
            read_ops=0,
            write_ops=initial_write_ops,
            read_bytes=0,
            write_bytes=0,
            timestamp=timestamp1
        )
        
        current_stats = IOStats(
            device=device_name,
            read_ops=0,
            write_ops=initial_write_ops + additional_write_ops,
            read_bytes=0,
            write_bytes=0,
            timestamp=timestamp2
        )
        
        # Calculate rates
        rates = self.formatter.calculate_io_rates(current_stats, previous_stats, interval)
        
        # Property: Write operations per second should equal difference divided by interval
        expected_write_ops_per_sec = additional_write_ops / interval
        assert abs(rates.write_ops_per_sec - expected_write_ops_per_sec) < 1e-10, \
            f"Expected {expected_write_ops_per_sec}, got {rates.write_ops_per_sec}"
    
    @given(
        device_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        initial_read_bytes=st.integers(min_value=0, max_value=10**12),
        additional_read_bytes=st.integers(min_value=0, max_value=10**9),
        interval=st.floats(min_value=0.1, max_value=10.0)
    )
    def test_read_throughput_calculation_accuracy(self, device_name, initial_read_bytes, additional_read_bytes, interval):
        """
        **Feature: disk-monitor, Property 6: Read throughput calculation accuracy**
        **Validates: Requirements 2.3**
        
        For any pair of I/O statistics with valid timestamps, the calculated read throughput 
        in KB/s should equal the difference in read bytes divided by the time interval and converted to kilobytes.
        """
        # Create two IOStats with different read bytes
        timestamp1 = time.time()
        timestamp2 = timestamp1 + interval
        
        previous_stats = IOStats(
            device=device_name,
            read_ops=0,
            write_ops=0,
            read_bytes=initial_read_bytes,
            write_bytes=0,
            timestamp=timestamp1
        )
        
        current_stats = IOStats(
            device=device_name,
            read_ops=0,
            write_ops=0,
            read_bytes=initial_read_bytes + additional_read_bytes,
            write_bytes=0,
            timestamp=timestamp2
        )
        
        # Calculate rates
        rates = self.formatter.calculate_io_rates(current_stats, previous_stats, interval)
        
        # Property: Read throughput should equal (bytes difference / interval) / 1024
        expected_read_kb_per_sec = (additional_read_bytes / interval) / 1024
        assert abs(rates.read_kb_per_sec - expected_read_kb_per_sec) < 1e-10, \
            f"Expected {expected_read_kb_per_sec}, got {rates.read_kb_per_sec}"
    
    @given(
        device_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        initial_write_bytes=st.integers(min_value=0, max_value=10**12),
        additional_write_bytes=st.integers(min_value=0, max_value=10**9),
        interval=st.floats(min_value=0.1, max_value=10.0)
    )
    def test_write_throughput_calculation_accuracy(self, device_name, initial_write_bytes, additional_write_bytes, interval):
        """
        **Feature: disk-monitor, Property 7: Write throughput calculation accuracy**
        **Validates: Requirements 2.4**
        
        For any pair of I/O statistics with valid timestamps, the calculated write throughput 
        in KB/s should equal the difference in write bytes divided by the time interval and converted to kilobytes.
        """
        # Create two IOStats with different write bytes
        timestamp1 = time.time()
        timestamp2 = timestamp1 + interval
        
        previous_stats = IOStats(
            device=device_name,
            read_ops=0,
            write_ops=0,
            read_bytes=0,
            write_bytes=initial_write_bytes,
            timestamp=timestamp1
        )
        
        current_stats = IOStats(
            device=device_name,
            read_ops=0,
            write_ops=0,
            read_bytes=0,
            write_bytes=initial_write_bytes + additional_write_bytes,
            timestamp=timestamp2
        )
        
        # Calculate rates
        rates = self.formatter.calculate_io_rates(current_stats, previous_stats, interval)
        
        # Property: Write throughput should equal (bytes difference / interval) / 1024
        expected_write_kb_per_sec = (additional_write_bytes / interval) / 1024
        assert abs(rates.write_kb_per_sec - expected_write_kb_per_sec) < 1e-10, \
            f"Expected {expected_write_kb_per_sec}, got {rates.write_kb_per_sec}"
    
    @given(
        device_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        initial_read_ops=st.integers(min_value=0, max_value=10**9),
        additional_read_ops=st.integers(min_value=0, max_value=10**6),
        initial_write_ops=st.integers(min_value=0, max_value=10**9),
        additional_write_ops=st.integers(min_value=0, max_value=10**6),
        initial_read_bytes=st.integers(min_value=0, max_value=10**12),
        additional_read_bytes=st.integers(min_value=0, max_value=10**9),
        initial_write_bytes=st.integers(min_value=0, max_value=10**12),
        additional_write_bytes=st.integers(min_value=0, max_value=10**9)
    )
    def test_rate_calculation_interval_consistency(self, device_name, initial_read_ops, additional_read_ops,
                                                 initial_write_ops, additional_write_ops, initial_read_bytes,
                                                 additional_read_bytes, initial_write_bytes, additional_write_bytes):
        """
        **Feature: disk-monitor, Property 8: Rate calculation interval consistency**
        **Validates: Requirements 2.5**
        
        For any I/O rate calculation, when given statistics separated by a 2-second interval, 
        the calculated rates should use exactly that interval in the computation.
        """
        # Use exactly 2.0 seconds as specified in requirements
        interval = 2.0
        
        timestamp1 = time.time()
        timestamp2 = timestamp1 + interval
        
        previous_stats = IOStats(
            device=device_name,
            read_ops=initial_read_ops,
            write_ops=initial_write_ops,
            read_bytes=initial_read_bytes,
            write_bytes=initial_write_bytes,
            timestamp=timestamp1
        )
        
        current_stats = IOStats(
            device=device_name,
            read_ops=initial_read_ops + additional_read_ops,
            write_ops=initial_write_ops + additional_write_ops,
            read_bytes=initial_read_bytes + additional_read_bytes,
            write_bytes=initial_write_bytes + additional_write_bytes,
            timestamp=timestamp2
        )
        
        # Calculate rates
        rates = self.formatter.calculate_io_rates(current_stats, previous_stats, interval)
        
        # Property: All rates should be calculated using the 2-second interval
        expected_read_ops_per_sec = additional_read_ops / 2.0
        expected_write_ops_per_sec = additional_write_ops / 2.0
        expected_read_kb_per_sec = (additional_read_bytes / 2.0) / 1024
        expected_write_kb_per_sec = (additional_write_bytes / 2.0) / 1024
        
        assert abs(rates.read_ops_per_sec - expected_read_ops_per_sec) < 1e-10
        assert abs(rates.write_ops_per_sec - expected_write_ops_per_sec) < 1e-10
        assert abs(rates.read_kb_per_sec - expected_read_kb_per_sec) < 1e-10
        assert abs(rates.write_kb_per_sec - expected_write_kb_per_sec) < 1e-10