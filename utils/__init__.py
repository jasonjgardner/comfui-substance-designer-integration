"""
Base interface for Substance 3D Automation Toolkit command line tools.

This module provides a common interface for interacting with Substance tools
like sbscooker, sbsrender, etc.
"""

import os
import subprocess
import json
import logging
import tempfile
import shutil
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class SubstanceToolError(Exception):
    """Custom exception for Substance tool errors."""
    pass

class SubstanceToolBase:
    """Base class for Substance tool interfaces."""
    
    def __init__(self, tool_name: str, tool_path: Optional[str] = None):
        """
        Initialize the Substance tool interface.
        
        Args:
            tool_name: Name of the Substance tool (e.g., 'sbscooker', 'sbsrender')
            tool_path: Optional custom path to the tool executable
        """
        self.tool_name = tool_name
        self.tool_path = tool_path or self._find_tool_path()
        self._validate_tool()
    
    def _find_tool_path(self) -> str:
        """Find the path to the Substance tool executable."""
        # Common installation paths for Substance tools
        common_paths = [
            # Windows paths
            r"C:\Program Files\Adobe\Adobe Substance 3D Automation Toolkit\bin",
            r"C:\Program Files (x86)\Adobe\Adobe Substance 3D Automation Toolkit\bin",
            # macOS paths
            "/Applications/Adobe Substance 3D Automation Toolkit/bin",
            "/usr/local/bin",
            # Linux paths
            "/opt/Adobe/Adobe_Substance_3D_Automation_Toolkit/bin",
            "/usr/local/bin",
            "/usr/bin",
        ]
        
        # Check if tool is in PATH
        tool_path = shutil.which(self.tool_name)
        if tool_path:
            return tool_path
        
        # Check common installation paths
        for path in common_paths:
            full_path = os.path.join(path, self.tool_name)
            if os.name == 'nt':  # Windows
                full_path += '.exe'
            
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                return full_path
        
        raise SubstanceToolError(
            f"Could not find {self.tool_name}. Please ensure Substance 3D Automation Toolkit is installed."
        )
    
    def _validate_tool(self) -> None:
        """Validate that the tool exists and is executable."""
        if not os.path.isfile(self.tool_path):
            raise SubstanceToolError(f"Tool not found at path: {self.tool_path}")
        
        if not os.access(self.tool_path, os.X_OK):
            raise SubstanceToolError(f"Tool is not executable: {self.tool_path}")
        
        # Test tool by running with --version
        try:
            result = self._run_command(['--version'], capture_output=True)
            logger.info(f"{self.tool_name} version: {result.stdout.strip()}")
        except Exception as e:
            logger.warning(f"Could not get version for {self.tool_name}: {e}")
    
    def _run_command(self, args: List[str], capture_output: bool = True, 
                    timeout: Optional[int] = None, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """
        Run the Substance tool with the given arguments.
        
        Args:
            args: Command line arguments
            capture_output: Whether to capture stdout/stderr
            timeout: Command timeout in seconds
            cwd: Working directory for the command
            
        Returns:
            CompletedProcess object with the result
            
        Raises:
            SubstanceToolError: If the command fails
        """
        cmd = [self.tool_path] + args
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=cwd,
                check=False  # We'll handle return codes manually
            )
            
            if result.returncode != 0:
                error_msg = f"Command failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                raise SubstanceToolError(error_msg)
            
            return result
            
        except subprocess.TimeoutExpired:
            raise SubstanceToolError(f"Command timed out after {timeout} seconds")
        except FileNotFoundError:
            raise SubstanceToolError(f"Tool not found: {self.tool_path}")
        except Exception as e:
            raise SubstanceToolError(f"Command execution failed: {str(e)}")
    
    def _validate_file_path(self, file_path: str, must_exist: bool = True) -> str:
        """
        Validate and normalize a file path.
        
        Args:
            file_path: Path to validate
            must_exist: Whether the file must exist
            
        Returns:
            Normalized absolute path
            
        Raises:
            SubstanceToolError: If validation fails
        """
        if not file_path:
            raise SubstanceToolError("File path cannot be empty")
        
        path = Path(file_path).resolve()
        
        if must_exist and not path.exists():
            raise SubstanceToolError(f"File does not exist: {path}")
        
        return str(path)
    
    def _ensure_directory(self, dir_path: str) -> str:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            dir_path: Directory path
            
        Returns:
            Normalized absolute path
        """
        path = Path(dir_path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    def _create_temp_file(self, suffix: str = "", prefix: str = "substance_") -> str:
        """
        Create a temporary file and return its path.
        
        Args:
            suffix: File suffix/extension
            prefix: File prefix
            
        Returns:
            Path to the temporary file
        """
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(fd)  # Close the file descriptor, we just need the path
        return path
    
    def get_version(self) -> str:
        """Get the version of the Substance tool."""
        try:
            result = self._run_command(['--version'])
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Failed to get version for {self.tool_name}: {e}")
            return "Unknown"

