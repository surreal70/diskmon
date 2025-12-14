"""
Property-based tests for the ConsoleDisplay class.

**Feature: disk-monitor, Properties 9-10: Tabular format structure and layout consistency**
"""

import pytest
from hypothesis import given, strategies as st
from io import StringIO
import sys
from unittest.mock import patch
from disk_monitor.display import ConsoleDisplay
from disk_monitor.models import DiskUsage, IORates


class TestConsoleDisplayProperties:
    """Property-based tests for ConsoleDisplay."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = ConsoleDisplay()
    
    @given(
        disk_usages=st.lists(
            st.builds(
                DiskUsage,
                device=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), whitelist_characters='/-_')),
                mountpoint=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), whitelist_characters='/-_')),
                total_bytes=st.integers(min_value=1, max_value=10**15),
                used_bytes=st.integers(min_value=0, max_value=10**15),
                available_bytes=st.integers(min_value=0, max_value=10**15),
                usage_percent=st.floats(min_value=0.0, max_value=100.0)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_tabular_format_structure(self, disk_usages):
        """
        **Feature: disk-monitor, Property 9: Tabular format structure**
        **Validates: Requirements 3.1**
        
        For any set of disk metrics, the display output should contain proper table 
        formatting with consistent column alignment and headers.
        """
        # Capture stdout to analyze the output
        captured_output = StringIO()
        
        with patch('sys.stdout', captured_output), patch('os.system'):
            self.display.display_disk_metrics(disk_usages)
        
        output_lines = captured_output.getvalue().split('\n')
        # Filter out empty lines and clean ANSI escape sequences
        cleaned_lines = []
        for line in output_lines:
            if line.strip():
                # Remove ANSI escape sequences
                import re
                clean_line = re.sub(r'\x1b\[[0-9;]*[mJHK]', '', line)
                if clean_line.strip():
                    cleaned_lines.append(clean_line)
        output_lines = cleaned_lines
        
        # Property: Should have at least header and separator lines
        assert len(output_lines) >= 2, f"Expected at least header and separator, got {len(output_lines)} lines"
        
        # Property: First line should be the header with expected columns
        header_line = output_lines[0]
        expected_columns = ['Device', 'Mount Point', 'Used', 'Available', 'Total', 'Usage %', 'Read Ops/s', 'Write Ops/s', 'Read KB/s', 'Write KB/s']
        
        for column in expected_columns:
            assert column in header_line, f"Header should contain '{column}', got: '{header_line}'"
        
        # Property: Second line should be a separator (dashes)
        separator_line = output_lines[1]
        assert all(c == '-' for c in separator_line), f"Separator should be all dashes, got: '{separator_line}'"
        
        # Property: Should have one data row per disk usage
        data_lines = output_lines[2:]  # Skip header and separator
        assert len(data_lines) == len(disk_usages), f"Expected {len(disk_usages)} data rows, got {len(data_lines)}"
        
        # Property: Each data row should have consistent structure
        for i, line in enumerate(data_lines):
            # Should contain device information
            assert len(line.strip()) > 0, f"Data row {i} should not be empty"
            
            # Should have multiple columns (spaces separate them)
            parts = line.split()
            assert len(parts) >= 6, f"Data row {i} should have at least 6 parts (device, mount, used, available, total, usage%), got {len(parts)}: '{line}'"
    
    @given(
        disk_usages=st.lists(
            st.builds(
                DiskUsage,
                device=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), whitelist_characters='/-_')),
                mountpoint=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), whitelist_characters='/-_')),
                total_bytes=st.integers(min_value=1, max_value=10**15),
                used_bytes=st.integers(min_value=0, max_value=10**15),
                available_bytes=st.integers(min_value=0, max_value=10**15),
                usage_percent=st.floats(min_value=0.0, max_value=100.0)
            ),
            min_size=2,
            max_size=5
        )
    )
    def test_disk_layout_consistency(self, disk_usages):
        """
        **Feature: disk-monitor, Property 10: Disk layout consistency**
        **Validates: Requirements 3.4**
        
        For any sequence of display updates with the same set of disks, each disk 
        should appear in the same relative position across all updates.
        """
        # Capture output for first display
        captured_output1 = StringIO()
        with patch('sys.stdout', captured_output1), patch('os.system'):
            self.display.display_disk_metrics(disk_usages)
        
        output1_lines = captured_output1.getvalue().split('\n')
        # Clean ANSI escape sequences
        import re
        cleaned_lines1 = []
        for line in output1_lines:
            if line.strip():
                clean_line = re.sub(r'\x1b\[[0-9;]*[mJHK]', '', line)
                if clean_line.strip():
                    cleaned_lines1.append(clean_line)
        output1_lines = cleaned_lines1
        
        # Capture output for second display (same disks)
        captured_output2 = StringIO()
        with patch('sys.stdout', captured_output2), patch('os.system'):
            self.display.display_disk_metrics(disk_usages)
        
        output2_lines = captured_output2.getvalue().split('\n')
        # Clean ANSI escape sequences
        cleaned_lines2 = []
        for line in output2_lines:
            if line.strip():
                clean_line = re.sub(r'\x1b\[[0-9;]*[mJHK]', '', line)
                if clean_line.strip():
                    cleaned_lines2.append(clean_line)
        output2_lines = cleaned_lines2
        
        # Property: Both outputs should have the same number of lines
        assert len(output1_lines) == len(output2_lines), \
            f"Both displays should have same number of lines: {len(output1_lines)} vs {len(output2_lines)}"
        
        # Property: Header and separator should be identical
        assert output1_lines[0] == output2_lines[0], "Headers should be identical"
        assert output1_lines[1] == output2_lines[1], "Separators should be identical"
        
        # Property: Each disk should appear in the same position
        data_lines1 = output1_lines[2:]
        data_lines2 = output2_lines[2:]
        
        for i, (line1, line2) in enumerate(zip(data_lines1, data_lines2)):
            # Extract device name from each line (first column)
            device1 = line1.split()[0] if line1.split() else ""
            device2 = line2.split()[0] if line2.split() else ""
            
            assert device1 == device2, \
                f"Device at position {i} should be consistent: '{device1}' vs '{device2}'"
            
            # Extract mount point (second column) for additional consistency check
            mount1 = line1.split()[1] if len(line1.split()) > 1 else ""
            mount2 = line2.split()[1] if len(line2.split()) > 1 else ""
            
            assert mount1 == mount2, \
                f"Mount point at position {i} should be consistent: '{mount1}' vs '{mount2}'"
    
    @given(
        device=st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), whitelist_characters='/-_')),
        mountpoint=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), whitelist_characters='/-_')),
        total_bytes=st.integers(min_value=1, max_value=10**15),
        used_bytes=st.integers(min_value=0, max_value=10**15),
        available_bytes=st.integers(min_value=0, max_value=10**15),
        usage_percent=st.floats(min_value=0.0, max_value=100.0),
        io_rates=st.one_of(
            st.none(),
            st.builds(
                IORates,
                device=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                read_ops_per_sec=st.floats(min_value=0.0, max_value=10000.0),
                write_ops_per_sec=st.floats(min_value=0.0, max_value=10000.0),
                read_kb_per_sec=st.floats(min_value=0.0, max_value=1000000.0),
                write_kb_per_sec=st.floats(min_value=0.0, max_value=1000000.0)
            )
        )
    )
    def test_display_disk_row_structure(self, device, mountpoint, total_bytes, used_bytes, available_bytes, usage_percent, io_rates):
        """
        Property test for individual disk row display structure.
        
        For any disk usage data with optional I/O rates, the display row should 
        contain all expected columns with proper formatting.
        """
        disk_usage = DiskUsage(
            device=device,
            mountpoint=mountpoint,
            total_bytes=total_bytes,
            used_bytes=used_bytes,
            available_bytes=available_bytes,
            usage_percent=usage_percent
        )
        
        # Capture stdout to analyze the output
        captured_output = StringIO()
        
        with patch('sys.stdout', captured_output):
            self.display.display_disk_row(disk_usage, io_rates)
        
        output = captured_output.getvalue().strip()
        
        # Property: Output should not be empty
        assert len(output) > 0, "Display row output should not be empty"
        
        # Property: Output should contain the device name (truncated if necessary)
        expected_device = device[:14] if len(device) > 14 else device
        assert expected_device in output, f"Output should contain device '{expected_device}', got: '{output}'"
        
        # Property: Output should contain the mount point (truncated if necessary)
        expected_mountpoint = mountpoint[:19] if len(mountpoint) > 19 else mountpoint
        assert expected_mountpoint in output, f"Output should contain mountpoint '{expected_mountpoint}', got: '{output}'"
        
        # Property: Output should contain usage percentage
        usage_str = f"{usage_percent:.1f}%"
        assert usage_str in output, f"Output should contain usage '{usage_str}', got: '{output}'"
        
        # Property: If I/O rates provided, should contain rate information
        if io_rates:
            read_ops_str = f"{io_rates.read_ops_per_sec:.1f}"
            write_ops_str = f"{io_rates.write_ops_per_sec:.1f}"
            assert read_ops_str in output, f"Output should contain read ops '{read_ops_str}', got: '{output}'"
            assert write_ops_str in output, f"Output should contain write ops '{write_ops_str}', got: '{output}'"
        else:
            # Should contain "N/A" for missing I/O data
            assert "N/A" in output, f"Output should contain 'N/A' for missing I/O data, got: '{output}'"
    
    @given(error_message=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc',))))
    def test_error_display_structure(self, error_message):
        """
        Property test for error message display.
        
        For any error message, the display should show it with proper error formatting.
        """
        # Capture stderr to analyze the output
        captured_error = StringIO()
        
        with patch('sys.stderr', captured_error):
            self.display.display_error(error_message)
        
        output = captured_error.getvalue()
        
        # Property: Output should not be empty
        assert len(output) > 0, "Error display output should not be empty"
        
        # Property: Output should start with "ERROR:"
        assert output.startswith("ERROR:"), f"Error output should start with 'ERROR:', got: '{output}'"
        
        # Property: Output should contain the original error message
        assert error_message in output, f"Error output should contain '{error_message}', got: '{output}'"