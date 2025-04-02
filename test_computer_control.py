"""Test script for computer control functionality."""
import asyncio
import time

from app.logger import logger
from app.tool.computer_control_tools import (
    SystemInfo,
    ListRunningProcesses,
    MonitorSystem,
    FileSystemExplorer
)


async def test_system_info():
    """Test the SystemInfo tool."""
    logger.info("Testing SystemInfo tool...")
    
    tool = SystemInfo()
    result = await tool()
    
    logger.info("System Information:")
    logger.info(result.output)


async def test_list_processes():
    """Test the ListRunningProcesses tool."""
    logger.info("Testing ListRunningProcesses tool...")
    
    tool = ListRunningProcesses()
    
    # Test with default parameters
    logger.info("Listing processes sorted by CPU usage (default):")
    result = await tool()
    logger.info(result.output)
    
    # Test with different sort options
    logger.info("Listing processes sorted by memory usage:")
    result = await tool(sort_by="memory", limit=5)
    logger.info(result.output)


async def test_monitor_system():
    """Test the MonitorSystem tool."""
    logger.info("Testing MonitorSystem tool...")
    
    tool = MonitorSystem()
    
    # Monitor for 5 seconds with 1-second intervals
    logger.info("Monitoring system for 5 seconds...")
    result = await tool(duration=5, interval=1)
    
    logger.info("Monitoring Results:")
    logger.info(result.output)


async def test_file_explorer():
    """Test the FileSystemExplorer tool."""
    logger.info("Testing FileSystemExplorer tool...")
    
    tool = FileSystemExplorer()
    
    # Explore current directory
    logger.info("Exploring current directory:")
    result = await tool()
    logger.info(result.output)
    
    # Explore with pattern
    logger.info("Exploring for Python files:")
    result = await tool(pattern="*.py")
    logger.info(result.output)


async def main():
    """Run the tests."""
    logger.info("Testing computer control functionality...")
    
    # Test system info
    await test_system_info()
    
    # Test process listing
    await test_list_processes()
    
    # Test system monitoring
    await test_monitor_system()
    
    # Test file explorer
    await test_file_explorer()
    
    logger.info("Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())