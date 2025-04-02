"""Tools for controlling and interacting with the computer system."""
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

import psutil
from PIL import ImageGrab

from app.logger import logger
from app.tool.base import BaseTool, ToolResult


class SystemInfo(BaseTool):
    """Tool for getting detailed system information."""
    
    name: str = "system_info"
    description: str = "Get detailed information about the computer system"
    
    parameters: Dict = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    async def __call__(self) -> ToolResult:
        """Get detailed system information.
        
        Returns:
            ToolResult with system information
        """
        try:
            info = {
                "system": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(logical=False),
                "logical_cpu_count": psutil.cpu_count(logical=True),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent_used": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent_used": psutil.disk_usage('/').percent
                }
            }
            
            # Format the output
            output = "System Information:\n\n"
            output += f"OS: {info['system']} {info['release']} {info['version']}\n"
            output += f"Hostname: {info['node']}\n"
            output += f"Machine: {info['machine']}\n"
            output += f"Processor: {info['processor']}\n"
            output += f"CPU Cores: {info['cpu_count']} (Physical), {info['logical_cpu_count']} (Logical)\n\n"
            
            # Memory
            total_gb = info['memory']['total'] / (1024 ** 3)
            available_gb = info['memory']['available'] / (1024 ** 3)
            output += f"Memory: {total_gb:.2f} GB total, {available_gb:.2f} GB available ({info['memory']['percent_used']}% used)\n\n"
            
            # Disk
            total_gb = info['disk']['total'] / (1024 ** 3)
            used_gb = info['disk']['used'] / (1024 ** 3)
            free_gb = info['disk']['free'] / (1024 ** 3)
            output += f"Disk: {total_gb:.2f} GB total, {used_gb:.2f} GB used, {free_gb:.2f} GB free ({info['disk']['percent_used']}% used)\n"
            
            return ToolResult(
                output=output
            )
        except Exception as e:
            logger.error(f"Error getting system information: {str(e)}")
            return ToolResult(
                output=f"Error getting system information: {str(e)}"
            )


class ListRunningProcesses(BaseTool):
    """Tool for listing running processes."""
    
    name: str = "list_processes"
    description: str = "List running processes on the computer"
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "sort_by": {
                "type": "string",
                "description": "Sort processes by: 'cpu', 'memory', 'name', or 'pid'",
                "enum": ["cpu", "memory", "name", "pid"]
            },
            "limit": {
                "type": "integer",
                "description": "Limit the number of processes to return"
            }
        },
        "required": []
    }
    
    async def __call__(
        self, sort_by: str = "cpu", limit: Optional[int] = 10
    ) -> ToolResult:
        """List running processes.
        
        Args:
            sort_by: Field to sort by (cpu, memory, name, pid)
            limit: Maximum number of processes to return
            
        Returns:
            ToolResult with the list of processes
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    # Get process info
                    proc_info = proc.info
                    # Add to list
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'username': proc_info['username'],
                        'cpu_percent': proc_info['cpu_percent'],
                        'memory_percent': proc_info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes
            if sort_by == "cpu":
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            elif sort_by == "name":
                processes.sort(key=lambda x: x['name'].lower())
            elif sort_by == "pid":
                processes.sort(key=lambda x: x['pid'])
            
            # Limit the number of processes
            if limit:
                processes = processes[:limit]
            
            # Format the output
            output = f"Running Processes (sorted by {sort_by}):\n\n"
            output += f"{'PID':<8} {'CPU %':<8} {'MEM %':<8} {'USER':<15} {'NAME':<30}\n"
            output += "-" * 70 + "\n"
            
            for proc in processes:
                output += f"{proc['pid']:<8} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f} {proc['username'][:15]:<15} {proc['name'][:30]:<30}\n"
            
            return ToolResult(
                output=output
            )
        except Exception as e:
            logger.error(f"Error listing processes: {str(e)}")
            return ToolResult(
                output=f"Error listing processes: {str(e)}"
            )


class MonitorSystem(BaseTool):
    """Tool for monitoring system resources over time."""
    
    name: str = "monitor_system"
    description: str = "Monitor system resources (CPU, memory, disk) over a period of time"
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "duration": {
                "type": "integer",
                "description": "Duration to monitor in seconds"
            },
            "interval": {
                "type": "integer",
                "description": "Sampling interval in seconds"
            }
        },
        "required": ["duration"]
    }
    
    async def __call__(
        self, duration: int = 10, interval: int = 1
    ) -> ToolResult:
        """Monitor system resources.
        
        Args:
            duration: Duration to monitor in seconds
            interval: Sampling interval in seconds
            
        Returns:
            ToolResult with the monitoring results
        """
        try:
            # Validate parameters
            if duration < 1:
                return ToolResult(
                    output="Duration must be at least 1 second."
                )
            if interval < 1:
                return ToolResult(
                    output="Interval must be at least 1 second."
                )
            if duration < interval:
                return ToolResult(
                    output="Duration must be greater than or equal to interval."
                )
            
            # Initialize data structures
            timestamps = []
            cpu_percentages = []
            memory_percentages = []
            
            # Monitor for the specified duration
            start_time = time.time()
            end_time = start_time + duration
            
            while time.time() < end_time:
                current_time = time.time()
                timestamps.append(current_time - start_time)
                
                # Get CPU and memory usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_percent = psutil.virtual_memory().percent
                
                cpu_percentages.append(cpu_percent)
                memory_percentages.append(memory_percent)
                
                # Sleep for the interval
                time.sleep(max(0, interval - 0.1))
            
            # Calculate averages
            avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
            avg_memory = sum(memory_percentages) / len(memory_percentages)
            max_cpu = max(cpu_percentages)
            max_memory = max(memory_percentages)
            
            # Format the output
            output = f"System Monitoring Results (Duration: {duration}s, Interval: {interval}s):\n\n"
            output += f"CPU Usage: Avg {avg_cpu:.1f}%, Max {max_cpu:.1f}%\n"
            output += f"Memory Usage: Avg {avg_memory:.1f}%, Max {max_memory:.1f}%\n\n"
            
            output += "Detailed Measurements:\n"
            output += f"{'Time (s)':<10} {'CPU %':<10} {'Memory %':<10}\n"
            output += "-" * 30 + "\n"
            
            for i in range(len(timestamps)):
                output += f"{timestamps[i]:<10.1f} {cpu_percentages[i]:<10.1f} {memory_percentages[i]:<10.1f}\n"
            
            return ToolResult(
                output=output
            )
        except Exception as e:
            logger.error(f"Error monitoring system: {str(e)}")
            return ToolResult(
                output=f"Error monitoring system: {str(e)}"
            )


class FileSystemExplorer(BaseTool):
    """Tool for exploring the file system."""
    
    name: str = "explore_files"
    description: str = "Explore files and directories on the computer"
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to explore (default: current directory)"
            },
            "show_hidden": {
                "type": "boolean",
                "description": "Whether to show hidden files"
            },
            "pattern": {
                "type": "string",
                "description": "File pattern to match (e.g., '*.txt')"
            }
        },
        "required": []
    }
    
    async def __call__(
        self, path: str = ".", show_hidden: bool = False, pattern: Optional[str] = None
    ) -> ToolResult:
        """Explore files and directories.
        
        Args:
            path: Path to explore
            show_hidden: Whether to show hidden files
            pattern: File pattern to match
            
        Returns:
            ToolResult with the file listing
        """
        try:
            # Resolve the path
            resolved_path = Path(path).resolve()
            
            if not resolved_path.exists():
                return ToolResult(
                    output=f"Path does not exist: {resolved_path}"
                )
            
            if resolved_path.is_file():
                # Get file info
                stat = resolved_path.stat()
                size = stat.st_size
                modified = time.ctime(stat.st_mtime)
                
                output = f"File: {resolved_path}\n"
                output += f"Size: {size} bytes\n"
                output += f"Modified: {modified}\n"
                
                return ToolResult(
                    output=output
                )
            
            # List directory contents
            files = []
            dirs = []
            
            for item in resolved_path.iterdir():
                # Skip hidden files if not requested
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                # Apply pattern filter if specified
                if pattern and not item.match(pattern):
                    continue
                
                if item.is_dir():
                    dirs.append(item)
                else:
                    files.append(item)
            
            # Sort alphabetically
            dirs.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())
            
            # Format the output
            output = f"Directory: {resolved_path}\n\n"
            
            if dirs:
                output += "Directories:\n"
                for d in dirs:
                    output += f"  {d.name}/\n"
                output += "\n"
            
            if files:
                output += "Files:\n"
                for f in files:
                    size = f.stat().st_size
                    modified = time.ctime(f.stat().st_mtime)
                    output += f"  {f.name} ({size} bytes, modified: {modified})\n"
            
            if not dirs and not files:
                output += "Directory is empty.\n"
            
            return ToolResult(
                output=output
            )
        except Exception as e:
            logger.error(f"Error exploring files: {str(e)}")
            return ToolResult(
                output=f"Error exploring files: {str(e)}"
            )