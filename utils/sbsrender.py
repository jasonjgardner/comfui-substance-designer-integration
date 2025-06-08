"""
Interface for the sbsrender tool from Substance 3D Automation Toolkit.

This module provides a Python interface for rendering .sbsar files to texture maps.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from . import SubstanceToolBase, SubstanceToolError

class SubstanceRenderTool(SubstanceToolBase):
    """Interface for the sbsrender command line tool."""
    
    def __init__(self, tool_path: Optional[str] = None):
        """Initialize the sbsrender interface."""
        super().__init__("sbsrender", tool_path)
    
    def get_info(self, sbsar_file: str) -> Dict[str, Any]:
        """
        Get information about a .sbsar file.
        
        Args:
            sbsar_file: Path to the .sbsar file
            
        Returns:
            Dictionary containing file information
            
        Raises:
            SubstanceToolError: If info extraction fails
        """
        validated_path = self._validate_file_path(sbsar_file, must_exist=True)
        
        if not validated_path.lower().endswith('.sbsar'):
            raise SubstanceToolError(f"Input file must be .sbsar format: {sbsar_file}")
        
        args = ['info', validated_path]
        result = self._run_command(args)
        
        # Parse the output to extract structured information
        info = {
            'file_path': validated_path,
            'raw_output': result.stdout,
            'graphs': [],
            'parameters': {},
            'outputs': {}
        }
        
        # Basic parsing of sbsrender info output
        # This would need to be enhanced based on actual sbsrender output format
        lines = result.stdout.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'Graph:' in line:
                current_section = 'graph'
                graph_name = line.split('Graph:')[-1].strip()
                info['graphs'].append(graph_name)
            elif 'Parameter:' in line:
                current_section = 'parameter'
                # Parse parameter information
            elif 'Output:' in line:
                current_section = 'output'
                # Parse output information
        
        return info
    
    def render(self,
               sbsar_file: str,
               output_path: str,
               output_format: str = "png",
               output_name: Optional[str] = None,
               bit_depth: str = "8",
               resolution: Optional[int] = None,
               graph_selection: Optional[str] = None,
               output_selection: Optional[str] = None,
               parameters: Optional[Dict[str, Any]] = None,
               image_entries: Optional[Dict[str, str]] = None,
               preset_name: Optional[str] = None,
               cpu_count: Optional[int] = None,
               memory_budget: Optional[int] = None,
               verbose: bool = False,
               **kwargs) -> Dict[str, Any]:
        """
        Render textures from a .sbsar file.
        
        Args:
            sbsar_file: Path to the .sbsar file
            output_path: Directory where output files will be saved
            output_format: Output image format (png, tiff, exr, etc.)
            output_name: Custom output name pattern
            bit_depth: Output bit depth (8, 16, 16f, 32f)
            resolution: Output resolution (will set both width and height)
            graph_selection: Specific graph to render
            output_selection: Specific outputs to render
            parameters: Dictionary of parameter name-value pairs
            image_entries: Dictionary of parameter name to image file path mappings
            preset_name: Name of preset to apply
            cpu_count: Maximum CPU cores to use
            memory_budget: Maximum memory in MB
            verbose: Enable verbose output
            **kwargs: Additional rendering options
            
        Returns:
            Dictionary containing rendering results and metadata
            
        Raises:
            SubstanceToolError: If rendering fails
        """
        # Validate inputs
        validated_sbsar = self._validate_file_path(sbsar_file, must_exist=True)
        if not validated_sbsar.lower().endswith('.sbsar'):
            raise SubstanceToolError(f"Input file must be .sbsar format: {sbsar_file}")
        
        # Ensure output directory exists
        output_dir = self._ensure_directory(output_path)
        
        # Build command arguments
        args = ['render']
        
        # Add input file
        args.extend(['--input', validated_sbsar])
        
        # Add output settings
        args.extend(['--output-path', output_dir])
        args.extend(['--output-format', output_format])
        
        if output_name:
            args.extend(['--output-name', output_name])
        
        if bit_depth:
            args.extend(['--output-bit-depth', bit_depth])
        
        # Graph and output selection
        if graph_selection:
            args.extend(['--input-graph', graph_selection])
        
        if output_selection:
            args.extend(['--input-graph-output', output_selection])
        
        # Parameter settings
        if parameters:
            for param_name, param_value in parameters.items():
                args.extend(['--set-value', f"{param_name}@{param_value}"])
        
        # Image entry settings (for input images)
        if image_entries:
            for param_name, image_path in image_entries.items():
                # Validate that the image file exists
                if not os.path.exists(image_path):
                    raise SubstanceToolError(f"Image entry file not found: {image_path}")
                args.extend(['--set-entry', f"{param_name}@{image_path}"])
        
        if preset_name:
            args.extend(['--use-preset', preset_name])
        
        # Performance settings
        if cpu_count:
            args.extend(['--cpu-count', str(cpu_count)])
        
        if memory_budget:
            args.extend(['--memory-budget', str(memory_budget)])
        
        # Resolution setting
        if resolution:
            # Set output resolution using --output-size parameter
            args.extend(['--output-size', f"{resolution},{resolution}"])
        
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
        
        # Execute the rendering command
        result = self._run_command(args, timeout=600)  # 10 minute timeout
        
        # Find generated output files
        output_files = []
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.lower().endswith(f'.{output_format.lower()}'):
                    output_files.append(os.path.join(output_dir, file))
        
        # Organize outputs by type (diffuse, normal, roughness, etc.)
        organized_outputs = self._organize_output_files(output_files)
        
        return {
            'success': True,
            'output_files': output_files,
            'organized_outputs': organized_outputs,
            'output_directory': output_dir,
            'command_output': result.stdout,
            'command_args': args,
            'input_file': validated_sbsar,
            'format': output_format,
            'bit_depth': bit_depth
        }
    
    def _organize_output_files(self, output_files: List[str]) -> Dict[str, List[str]]:
        """
        Organize output files by their type (diffuse, normal, etc.).
        
        Args:
            output_files: List of output file paths
            
        Returns:
            Dictionary mapping output types to file lists
        """
        organized = {
            'diffuse': [],
            'normal': [],
            'roughness': [],
            'metallic': [],
            'height': [],
            'ambient_occlusion': [],
            'emission': [],
            'opacity': [],
            'other': []
        }
        
        # Common naming patterns for different map types
        patterns = {
            'diffuse': [r'diffuse', r'albedo', r'basecolor', r'color'],
            'normal': [r'normal', r'normalmap'],
            'roughness': [r'roughness', r'rough'],
            'metallic': [r'metallic', r'metal'],
            'height': [r'height', r'displacement', r'disp'],
            'ambient_occlusion': [r'ao', r'ambient', r'occlusion'],
            'emission': [r'emission', r'emissive'],
            'opacity': [r'opacity', r'alpha', r'transparency']
        }
        
        for file_path in output_files:
            filename = Path(file_path).stem.lower()
            categorized = False
            
            for category, category_patterns in patterns.items():
                for pattern in category_patterns:
                    if re.search(pattern, filename):
                        organized[category].append(file_path)
                        categorized = True
                        break
                if categorized:
                    break
            
            if not categorized:
                organized['other'].append(file_path)
        
        # Remove empty categories
        return {k: v for k, v in organized.items() if v}
    
    def get_help(self) -> str:
        """Get help information for sbsrender."""
        try:
            result = self._run_command(['--help'])
            return result.stdout
        except Exception as e:
            return f"Failed to get help: {e}"

