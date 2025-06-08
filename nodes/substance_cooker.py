"""
ComfyUI custom node for cooking Substance Designer files.

This node provides an interface for converting .sbs files to .sbsar archives
using the sbscooker tool from Substance 3D Automation Toolkit.
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Any

from ..utils.sbscooker import SubstanceCookerTool, SubstanceToolError

# Configure logging
logger = logging.getLogger(__name__)

class SubstanceCooker:
    """ComfyUI node for cooking Substance Designer files."""
    
    # Node category in ComfyUI
    CATEGORY = "substance"
    
    # Node description
    DESCRIPTION = "Cook Substance Designer .sbs files to .sbsar archives"
    
    @classmethod
    def INPUT_TYPES(cls):
        """Define the input types for this node."""
        return {
            "required": {
                "sbs_file_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Path to .sbs file"
                }),
                "output_directory": ("STRING", {
                    "default": "./output",
                    "multiline": False,
                    "placeholder": "Output directory path"
                }),
            },
            "optional": {
                "output_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Custom output name (optional)"
                }),
                "optimization_level": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 3,
                    "step": 1,
                    "display": "slider"
                }),
                "enable_icons": ("BOOLEAN", {
                    "default": True
                }),
                "merge_graphs": ("BOOLEAN", {
                    "default": False
                }),
                "verbose": ("BOOLEAN", {
                    "default": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("sbsar_file_path", "cooking_log", "output_directory")
    
    FUNCTION = "cook_substance"
    
    def cook_substance(self, sbs_file_path: str, output_directory: str,
                      output_name: str = "", optimization_level: int = 1,
                      enable_icons: bool = True, merge_graphs: bool = False,
                      verbose: bool = False) -> Tuple[str, str, str]:
        """
        Cook a Substance Designer file to .sbsar archive.
        
        Args:
            sbs_file_path: Path to the input .sbs file
            output_directory: Directory where output will be saved
            output_name: Custom output name (optional)
            optimization_level: Cooking optimization level (0-3)
            enable_icons: Whether to include graph icons
            merge_graphs: Whether to merge all graphs into one file
            verbose: Enable verbose logging
            
        Returns:
            Tuple of (sbsar_file_path, cooking_log, output_directory)
            
        Raises:
            Exception: If cooking fails
        """
        try:
            # Validate inputs
            if not sbs_file_path or not sbs_file_path.strip():
                raise ValueError("SBS file path cannot be empty")
            
            if not output_directory or not output_directory.strip():
                raise ValueError("Output directory cannot be empty")
            
            # Expand user paths and make absolute
            sbs_path = os.path.expanduser(sbs_file_path.strip())
            output_dir = os.path.expanduser(output_directory.strip())
            
            if not os.path.isabs(sbs_path):
                sbs_path = os.path.abspath(sbs_path)
            
            if not os.path.isabs(output_dir):
                output_dir = os.path.abspath(output_dir)
            
            # Check if input file exists
            if not os.path.exists(sbs_path):
                raise FileNotFoundError(f"SBS file not found: {sbs_path}")
            
            # Check file extension
            if not sbs_path.lower().endswith('.sbs'):
                raise ValueError(f"Input file must have .sbs extension: {sbs_path}")
            
            # Initialize the cooker tool
            cooker = SubstanceCookerTool()
            
            # Prepare cooking parameters
            cook_params = {
                'output_name': output_name.strip() if output_name.strip() else None,
                'merge': merge_graphs,
                'enable_icons': enable_icons,
                'optimization_level': optimization_level,
                'verbose': verbose
            }
            
            # Log the cooking operation
            logger.info(f"Cooking SBS file: {sbs_path}")
            logger.info(f"Output directory: {output_dir}")
            logger.info(f"Parameters: {cook_params}")
            
            # Perform the cooking
            result = cooker.cook(
                input_files=[sbs_path],
                output_path=output_dir,
                **cook_params
            )
            
            # Extract results
            if not result['success']:
                raise RuntimeError("Cooking failed - check logs for details")
            
            output_files = result.get('output_files', [])
            if not output_files:
                raise RuntimeError("No output files were generated")
            
            # Return the first output file (or the only one if merged)
            sbsar_file_path = output_files[0]
            cooking_log = result.get('command_output', '')
            actual_output_dir = result.get('output_directory', output_dir)
            
            logger.info(f"Successfully cooked to: {sbsar_file_path}")
            
            return (sbsar_file_path, cooking_log, actual_output_dir)
            
        except SubstanceToolError as e:
            error_msg = f"Substance tool error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            error_msg = f"Cooking failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """
        Determine if the node needs to be re-executed.
        
        This method is called by ComfyUI to check if the node's output
        might have changed and needs to be recalculated.
        """
        # Check if input file has been modified
        sbs_file_path = kwargs.get('sbs_file_path', '')
        if sbs_file_path and os.path.exists(sbs_file_path):
            return os.path.getmtime(sbs_file_path)
        return float('inf')  # Always re-execute if file doesn't exist
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        """
        Validate inputs before execution.
        
        Returns:
            True if inputs are valid, error message string otherwise
        """
        sbs_file_path = kwargs.get('sbs_file_path', '')
        output_directory = kwargs.get('output_directory', '')
        
        if not sbs_file_path or not sbs_file_path.strip():
            return "SBS file path cannot be empty"
        
        if not output_directory or not output_directory.strip():
            return "Output directory cannot be empty"
        
        # Expand and check file path
        expanded_path = os.path.expanduser(sbs_file_path.strip())
        if not os.path.isabs(expanded_path):
            expanded_path = os.path.abspath(expanded_path)
        
        if not os.path.exists(expanded_path):
            return f"SBS file not found: {expanded_path}"
        
        if not expanded_path.lower().endswith('.sbs'):
            return f"Input file must have .sbs extension: {expanded_path}"
        
        return True

