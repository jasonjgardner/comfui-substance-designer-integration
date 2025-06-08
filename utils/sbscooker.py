"""
Interface for the sbscooker tool from Substance 3D Automation Toolkit.

This module provides a Python interface for cooking .sbs files to .sbsar archives.
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from . import SubstanceToolBase, SubstanceToolError

class SubstanceCookerTool(SubstanceToolBase):
    """Interface for the sbscooker command line tool."""
    
    def __init__(self, tool_path: Optional[str] = None):
        """Initialize the sbscooker interface."""
        super().__init__("sbscooker", tool_path)
    
    def cook(self, 
             input_files: List[str],
             output_path: str,
             output_name: Optional[str] = None,
             merge: bool = False,
             enable_icons: bool = True,
             no_archive: bool = False,
             optimization_level: int = 1,
             verbose: bool = False,
             **kwargs) -> Dict[str, Any]:
        """
        Cook .sbs files to .sbsar archives.
        
        Args:
            input_files: List of .sbs file paths to cook
            output_path: Directory where output files will be saved
            output_name: Custom output name (optional)
            merge: Whether to merge all results in one file
            enable_icons: Whether to include graph icons
            no_archive: Generate non-packaged SBSASM and XML
            optimization_level: Optimization level (0-3)
            verbose: Enable verbose output
            **kwargs: Additional cooking options
            
        Returns:
            Dictionary containing cooking results and metadata
            
        Raises:
            SubstanceToolError: If cooking fails
        """
        # Validate inputs
        validated_inputs = []
        for input_file in input_files:
            validated_path = self._validate_file_path(input_file, must_exist=True)
            if not validated_path.lower().endswith('.sbs'):
                raise SubstanceToolError(f"Input file must be .sbs format: {input_file}")
            validated_inputs.append(validated_path)
        
        # Ensure output directory exists
        output_dir = self._ensure_directory(output_path)
        
        # Build command arguments
        args = ['cook']
        
        # Add input files
        args.extend(['--inputs'] + validated_inputs)
        
        # Add output path
        args.extend(['--output-path', output_dir])
        
        # Add optional parameters
        if output_name:
            args.extend(['--output-name', output_name])
        
        if merge:
            args.append('--merge')
        
        if enable_icons:
            args.append('--enable-icons')
        
        if no_archive:
            args.append('--no-archive')
        
        # Optimization options
        if optimization_level == 0:
            args.extend(['--crc', '1', '--full', '0'])
        elif optimization_level == 1:
            args.extend(['--full', '1'])
        elif optimization_level == 2:
            args.extend(['--full', '1', '--merge-graph', '1'])
        elif optimization_level == 3:
            args.extend(['--full', '1', '--merge-graph', '1', '--merge-data', '1', '--reordering', '1'])
        
        if verbose:
            args.append('--verbose')
        else:
            args.append('--quiet')
        
        # Add any additional arguments from kwargs
        for key, value in kwargs.items():
            if isinstance(value, bool):
                if value:
                    args.append(f'--{key.replace("_", "-")}')
            else:
                args.extend([f'--{key.replace("_", "-")}', str(value)])
        
        # Execute the cooking command
        result = self._run_command(args, timeout=300)  # 5 minute timeout
        
        # Determine output files
        output_files = []
        if merge and output_name:
            # Single merged output
            output_file = os.path.join(output_dir, f"{output_name}.sbsar")
            if os.path.exists(output_file):
                output_files.append(output_file)
        else:
            # Multiple outputs based on input files
            for input_file in validated_inputs:
                base_name = Path(input_file).stem
                if output_name:
                    base_name = output_name
                output_file = os.path.join(output_dir, f"{base_name}.sbsar")
                if os.path.exists(output_file):
                    output_files.append(output_file)
        
        return {
            'success': True,
            'output_files': output_files,
            'output_directory': output_dir,
            'command_output': result.stdout,
            'command_args': args,
            'input_files': validated_inputs
        }
    
    def get_help(self) -> str:
        """Get help information for sbscooker."""
        try:
            result = self._run_command(['--help'])
            return result.stdout
        except Exception as e:
            return f"Failed to get help: {e}"

