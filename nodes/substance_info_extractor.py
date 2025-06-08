"""
ComfyUI custom node for extracting information from Substance Designer archives.

This node provides an interface for extracting metadata, parameter information,
and output details from .sbsar files.
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Any, Optional

from ..utils.sbsrender import SubstanceRenderTool, SubstanceToolError

# Configure logging
logger = logging.getLogger(__name__)

class SubstanceInfoExtractor:
    """ComfyUI node for extracting information from Substance Designer archives."""
    
    # Node category in ComfyUI
    CATEGORY = "substance"
    
    # Node description
    DESCRIPTION = "Extract metadata and parameter information from Substance Designer .sbsar files"
    
    @classmethod
    def INPUT_TYPES(cls):
        """Define the input types for this node."""
        return {
            "required": {
                "sbsar_file_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Path to .sbsar file"
                }),
            },
            "optional": {
                "extract_parameters": ("BOOLEAN", {
                    "default": True
                }),
                "extract_outputs": ("BOOLEAN", {
                    "default": True
                }),
                "extract_graphs": ("BOOLEAN", {
                    "default": True
                }),
                "format_output": ("BOOLEAN", {
                    "default": True
                }),
                "verbose": ("BOOLEAN", {
                    "default": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("file_info", "graph_info", "parameter_info", "output_info", "formatted_summary")
    
    FUNCTION = "extract_info"
    
    def extract_info(self, sbsar_file_path: str,
                    extract_parameters: bool = True,
                    extract_outputs: bool = True,
                    extract_graphs: bool = True,
                    format_output: bool = True,
                    verbose: bool = False) -> Tuple[str, str, str, str, str]:
        """
        Extract information from a Substance Designer archive.
        
        Args:
            sbsar_file_path: Path to the input .sbsar file
            extract_parameters: Whether to extract parameter information
            extract_outputs: Whether to extract output information
            extract_graphs: Whether to extract graph information
            format_output: Whether to format output for readability
            verbose: Enable verbose logging
            
        Returns:
            Tuple of (file_info, graph_info, parameter_info, output_info, formatted_summary)
            
        Raises:
            Exception: If information extraction fails
        """
        try:
            # Validate inputs
            if not sbsar_file_path or not sbsar_file_path.strip():
                raise ValueError("SBSAR file path cannot be empty")
            
            # Expand user paths and make absolute
            sbsar_path = os.path.expanduser(sbsar_file_path.strip())
            if not os.path.isabs(sbsar_path):
                sbsar_path = os.path.abspath(sbsar_path)
            
            # Check if input file exists
            if not os.path.exists(sbsar_path):
                raise FileNotFoundError(f"SBSAR file not found: {sbsar_path}")
            
            # Check file extension
            if not sbsar_path.lower().endswith('.sbsar'):
                raise ValueError(f"Input file must have .sbsar extension: {sbsar_path}")
            
            # Initialize the renderer tool for info extraction
            renderer = SubstanceRenderTool()
            
            logger.info(f"Extracting information from: {sbsar_path}")
            
            # Extract basic file information
            file_info = self._get_file_info(sbsar_path)
            
            # Extract detailed information using sbsrender
            detailed_info = renderer.get_info(sbsar_path)
            
            # Process and organize the extracted information
            graph_info = {}
            parameter_info = {}
            output_info = {}
            
            if extract_graphs:
                graph_info = self._extract_graph_info(detailed_info)
            
            if extract_parameters:
                parameter_info = self._extract_parameter_info(detailed_info)
            
            if extract_outputs:
                output_info = self._extract_output_info(detailed_info)
            
            # Create formatted summary if requested
            formatted_summary = ""
            if format_output:
                formatted_summary = self._create_formatted_summary(
                    file_info, graph_info, parameter_info, output_info
                )
            
            # Convert to JSON strings
            file_info_json = json.dumps(file_info, indent=2 if format_output else None)
            graph_info_json = json.dumps(graph_info, indent=2 if format_output else None)
            parameter_info_json = json.dumps(parameter_info, indent=2 if format_output else None)
            output_info_json = json.dumps(output_info, indent=2 if format_output else None)
            
            logger.info(f"Successfully extracted information from: {sbsar_path}")
            
            return (file_info_json, graph_info_json, parameter_info_json, 
                   output_info_json, formatted_summary)
            
        except SubstanceToolError as e:
            error_msg = f"Substance tool error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            error_msg = f"Information extraction failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic file information.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information
        """
        import os
        from pathlib import Path
        
        stat = os.stat(file_path)
        path_obj = Path(file_path)
        
        return {
            "file_path": file_path,
            "file_name": path_obj.name,
            "file_stem": path_obj.stem,
            "file_size": stat.st_size,
            "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified_time": stat.st_mtime,
            "created_time": stat.st_ctime,
            "is_readable": os.access(file_path, os.R_OK),
            "directory": str(path_obj.parent)
        }
    
    def _extract_graph_info(self, detailed_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract graph information from detailed info.
        
        Args:
            detailed_info: Detailed information from sbsrender
            
        Returns:
            Dictionary containing graph information
        """
        graph_info = {
            "graphs": detailed_info.get('graphs', []),
            "graph_count": len(detailed_info.get('graphs', [])),
            "graph_details": {}
        }
        
        # Add more detailed graph parsing here based on actual sbsrender output format
        for graph in detailed_info.get('graphs', []):
            graph_info["graph_details"][graph] = {
                "name": graph,
                "type": "unknown",  # Would be extracted from actual output
                "description": ""   # Would be extracted from actual output
            }
        
        return graph_info
    
    def _extract_parameter_info(self, detailed_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract parameter information from detailed info.
        
        Args:
            detailed_info: Detailed information from sbsrender
            
        Returns:
            Dictionary containing parameter information
        """
        parameters = detailed_info.get('parameters', {})
        
        parameter_info = {
            "parameters": parameters,
            "parameter_count": len(parameters),
            "parameter_types": {},
            "parameter_summary": []
        }
        
        # Analyze parameter types and create summary
        for param_name, param_data in parameters.items():
            param_type = "unknown"
            param_range = None
            param_default = None
            
            # This would be enhanced based on actual sbsrender output format
            if isinstance(param_data, dict):
                param_type = param_data.get('type', 'unknown')
                param_range = param_data.get('range', None)
                param_default = param_data.get('default', None)
            
            parameter_info["parameter_summary"].append({
                "name": param_name,
                "type": param_type,
                "range": param_range,
                "default": param_default
            })
            
            # Count parameter types
            if param_type not in parameter_info["parameter_types"]:
                parameter_info["parameter_types"][param_type] = 0
            parameter_info["parameter_types"][param_type] += 1
        
        return parameter_info
    
    def _extract_output_info(self, detailed_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract output information from detailed info.
        
        Args:
            detailed_info: Detailed information from sbsrender
            
        Returns:
            Dictionary containing output information
        """
        outputs = detailed_info.get('outputs', {})
        
        output_info = {
            "outputs": outputs,
            "output_count": len(outputs),
            "output_types": {},
            "output_summary": []
        }
        
        # Common output types in Substance materials
        common_output_types = {
            'diffuse': ['diffuse', 'albedo', 'basecolor', 'color'],
            'normal': ['normal', 'normalmap'],
            'roughness': ['roughness', 'rough'],
            'metallic': ['metallic', 'metal'],
            'height': ['height', 'displacement'],
            'ambient_occlusion': ['ao', 'ambient', 'occlusion'],
            'emission': ['emission', 'emissive'],
            'opacity': ['opacity', 'alpha']
        }
        
        # Analyze outputs
        for output_name, output_data in outputs.items():
            output_type = "other"
            
            # Try to determine output type from name
            output_name_lower = output_name.lower()
            for type_name, keywords in common_output_types.items():
                if any(keyword in output_name_lower for keyword in keywords):
                    output_type = type_name
                    break
            
            output_info["output_summary"].append({
                "name": output_name,
                "type": output_type,
                "data": output_data
            })
            
            # Count output types
            if output_type not in output_info["output_types"]:
                output_info["output_types"][output_type] = 0
            output_info["output_types"][output_type] += 1
        
        return output_info
    
    def _create_formatted_summary(self, file_info: Dict[str, Any],
                                 graph_info: Dict[str, Any],
                                 parameter_info: Dict[str, Any],
                                 output_info: Dict[str, Any]) -> str:
        """
        Create a formatted text summary of the extracted information.
        
        Args:
            file_info: File information
            graph_info: Graph information
            parameter_info: Parameter information
            output_info: Output information
            
        Returns:
            Formatted summary string
        """
        summary_lines = []
        
        # File information
        summary_lines.append("=== SUBSTANCE ARCHIVE INFORMATION ===")
        summary_lines.append(f"File: {file_info.get('file_name', 'Unknown')}")
        summary_lines.append(f"Size: {file_info.get('file_size_mb', 0)} MB")
        summary_lines.append("")
        
        # Graph information
        if graph_info:
            summary_lines.append("=== GRAPHS ===")
            summary_lines.append(f"Graph Count: {graph_info.get('graph_count', 0)}")
            for graph in graph_info.get('graphs', []):
                summary_lines.append(f"  - {graph}")
            summary_lines.append("")
        
        # Parameter information
        if parameter_info:
            summary_lines.append("=== PARAMETERS ===")
            summary_lines.append(f"Parameter Count: {parameter_info.get('parameter_count', 0)}")
            
            param_types = parameter_info.get('parameter_types', {})
            if param_types:
                summary_lines.append("Parameter Types:")
                for param_type, count in param_types.items():
                    summary_lines.append(f"  - {param_type}: {count}")
            
            summary_lines.append("")
        
        # Output information
        if output_info:
            summary_lines.append("=== OUTPUTS ===")
            summary_lines.append(f"Output Count: {output_info.get('output_count', 0)}")
            
            output_types = output_info.get('output_types', {})
            if output_types:
                summary_lines.append("Output Types:")
                for output_type, count in output_types.items():
                    summary_lines.append(f"  - {output_type}: {count}")
            
            summary_lines.append("")
        
        return "\\n".join(summary_lines)
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        """
        Validate inputs before execution.
        """
        sbsar_file_path = kwargs.get('sbsar_file_path', '')
        
        if not sbsar_file_path or not sbsar_file_path.strip():
            return "SBSAR file path cannot be empty"
        
        # Expand and check file path
        expanded_path = os.path.expanduser(sbsar_file_path.strip())
        if not os.path.isabs(expanded_path):
            expanded_path = os.path.abspath(expanded_path)
        
        if not os.path.exists(expanded_path):
            return f"SBSAR file not found: {expanded_path}"
        
        if not expanded_path.lower().endswith('.sbsar'):
            return f"Input file must have .sbsar extension: {expanded_path}"
        
        return True

