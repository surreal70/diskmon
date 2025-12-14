"""
Main entry point for the disk monitor application.
"""

from .monitor import DiskMonitor


def main():
    """Main entry point function."""
    monitor = DiskMonitor()
    monitor.run()


if __name__ == "__main__":
    main()