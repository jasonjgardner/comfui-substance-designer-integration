"""
ComfyUI custom node for batch processing Substance Designer files.

This node provides an interface for processing multiple Substance files
or generating multiple variations efficiently.
"""

import os
import json
import logging
import glob
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import concurrent.futures
import threading

from ..utils.sbscooker import SubstanceCookerTool, SubstanceToolError
from ..utils.sbsrender import SubstanceRenderTool

# Configure logging
logger = logging.getLogger(__name__)

class SubstanceBatchProcessor:
    """ComfyUI node for batch processing Substance Designer files."""
    
    # Node category in ComfyUI
    CATEGORY = "substance"
    
    # Node description
    DESCRIPTION = "Batch process multiple Substance Designer files or generate variations"
    
    @classmethod
    def INPUT_TYPES(cls):
        """Define the input types for this node."""
        return {
            "required": {
                "input_directory": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Directory containing .sbs files"
                }),
                "output_base_directory": ("STRING", {
                    "default": "./batch_output",
                    "multiline": False,
                    "placeholder": "Base output directory"
                }),
                "operation_mode": (["cook_only", "render_only", "cook_and_render"], {
                    "default": "cook_and_render"
                }),
            },
            "optional": {
                "file_pattern": ("STRING", {
                    "default": "*.sbs",
                    "multiline": False,
                    "placeholder": "File pattern for filtering"
                }),
                "batch_parameters": ("STRING", {
                    "default": "[]",
                    "multiline": True,
                    "placeholder": "JSON array of parameter sets for variations"
                }),
                "output_format": (["png", "tiff", "exr", "jpg"], {
                    "default": "png"
                }),
                "bit_depth": (["8", "16", "16f", "32f"], {
                    "default": "8"
                }),
                "optimization_level": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 3,
                    "step": 1,
                    "display": "slider"
                }),
                "max_workers": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 8,
                    "step": 1,
                    "display": "slider"
                }),
                "organize_by_material": ("BOOLEAN", {
                    "default": True
                }),
                "verbose": ("BOOLEAN", {
                    "default": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("processed_files", "batch_summary", "error_log", "output_structure")
    
    FUNCTION = "process_batch"
    
    def process_batch(self, input_directory: str, output_base_directory: str,
                     operation_mode: str = "cook_and_render",
                     file_pattern: str = "*.sbs",
                     batch_parameters: str = "[]",
                     output_format: str = "png",
                     bit_depth: str = "8",
                     optimization_level: int = 1,
                     max_workers: int = 2,
                     organize_by_material: bool = True,
                     verbose: bool = False) -> Tuple[str, str, str, str]:
        """
        Process multiple Substance Designer files in batch.
        
        Args:
            input_directory: Directory containing input files
            output_base_directory: Base directory for outputs
            operation_mode: Type of operation to perform
            file_pattern: Pattern for filtering input files
            batch_parameters: JSON array of parameter sets
            output_format: Output image format for rendering
            bit_depth: Output bit depth for rendering
            optimization_level: Cooking optimization level
            max_workers: Maximum parallel workers
            organize_by_material: Whether to organize outputs by material
            verbose: Enable verbose logging
            
        Returns:
            Tuple of (processed_files, batch_summary, error_log, output_structure)
            
        Raises:
            Exception: If batch processing fails
        """
        try:
            # Validate inputs
            if not input_directory or not input_directory.strip():
                raise ValueError("Input directory cannot be empty")
            
            if not output_base_directory or not output_base_directory.strip():
                raise ValueError("Output base directory cannot be empty")
            
            # Expand user paths and make absolute
            input_dir = os.path.expanduser(input_directory.strip())
            output_base_dir = os.path.expanduser(output_base_directory.strip())
            
            if not os.path.isabs(input_dir):
                input_dir = os.path.abspath(input_dir)
            
            if not os.path.isabs(output_base_dir):
                output_base_dir = os.path.abspath(output_base_dir)
            
            # Check if input directory exists
            if not os.path.exists(input_dir):
                raise FileNotFoundError(f"Input directory not found: {input_dir}")
            
            if not os.path.isdir(input_dir):
                raise ValueError(f"Input path is not a directory: {input_dir}")
            
            # Parse batch parameters
            parameter_sets = []
            if batch_parameters.strip():
                try:
                    parameter_sets = json.loads(batch_parameters)
                    if not isinstance(parameter_sets, list):
                        raise ValueError("Batch parameters must be a JSON array")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in batch parameters: {str(e)}")
            
            # Find input files
            search_pattern = os.path.join(input_dir, file_pattern)
            input_files = glob.glob(search_pattern)
            
            if not input_files:
                raise ValueError(f"No files found matching pattern: {search_pattern}")
            
            # Filter for .sbs files if cooking is involved
            if operation_mode in ["cook_only", "cook_and_render"]:
                input_files = [f for f in input_files if f.lower().endswith('.sbs')]
            elif operation_mode == "render_only":
                input_files = [f for f in input_files if f.lower().endswith('.sbsar')]
            
            if not input_files:
                raise ValueError(f"No valid files found for operation mode: {operation_mode}")
            
            logger.info(f"Found {len(input_files)} files to process")
            logger.info(f"Operation mode: {operation_mode}")
            logger.info(f"Parameter sets: {len(parameter_sets)}")
            
            # Initialize tools
            cooker = None
            renderer = None
            
            if operation_mode in ["cook_only", "cook_and_render"]:
                cooker = SubstanceCookerTool()
            
            if operation_mode in ["render_only", "cook_and_render"]:
                renderer = SubstanceRenderTool()
            
            # Process files
            processed_files = []
            errors = []
            output_structure = {}
            
            # Use thread pool for parallel processing
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all processing tasks
                future_to_file = {}
                
                for input_file in input_files:
                    if parameter_sets:
                        # Process with each parameter set
                        for i, params in enumerate(parameter_sets):
                            future = executor.submit(
                                self._process_single_file,
                                input_file, output_base_dir, operation_mode,
                                params, i, output_format, bit_depth,
                                optimization_level, organize_by_material,
                                verbose, cooker, renderer
                            )
                            future_to_file[future] = (input_file, i)
                    else:
                        # Process with default parameters
                        future = executor.submit(
                            self._process_single_file,
                            input_file, output_base_dir, operation_mode,
                            {}, 0, output_format, bit_depth,
                            optimization_level, organize_by_material,
                            verbose, cooker, renderer
                        )
                        future_to_file[future] = (input_file, 0)
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_file):
                    input_file, param_index = future_to_file[future]
                    try:
                        result = future.result()
                        processed_files.append(result)
                        
                        # Update output structure
                        material_name = Path(input_file).stem
                        if material_name not in output_structure:
                            output_structure[material_name] = []
                        output_structure[material_name].append(result)
                        
                    except Exception as e:
                        error_msg = f"Failed to process {input_file} (params {param_index}): {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
            
            # Generate summary
            total_files = len(input_files)
            total_variations = len(parameter_sets) if parameter_sets else 1
            total_expected = total_files * total_variations
            total_processed = len(processed_files)
            total_errors = len(errors)
            
            batch_summary = {
                "input_directory": input_dir,
                "output_directory": output_base_dir,
                "operation_mode": operation_mode,
                "total_input_files": total_files,
                "parameter_variations": total_variations,
                "total_expected_outputs": total_expected,
                "successfully_processed": total_processed,
                "errors": total_errors,
                "success_rate": f"{(total_processed / total_expected * 100):.1f}%" if total_expected > 0 else "0%"
            }
            
            # Format outputs
            processed_files_json = json.dumps(processed_files, indent=2)
            batch_summary_json = json.dumps(batch_summary, indent=2)
            error_log_json = json.dumps(errors, indent=2)
            output_structure_json = json.dumps(output_structure, indent=2)
            
            logger.info(f"Batch processing completed: {total_processed}/{total_expected} successful")
            
            return (processed_files_json, batch_summary_json, 
                   error_log_json, output_structure_json)
            
        except Exception as e:
            error_msg = f"Batch processing failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _process_single_file(self, input_file: str, output_base_dir: str,
                           operation_mode: str, parameters: Dict[str, Any],
                           param_index: int, output_format: str, bit_depth: str,
                           optimization_level: int, organize_by_material: bool,
                           verbose: bool, cooker: Optional[SubstanceCookerTool],
                           renderer: Optional[SubstanceRenderTool]) -> Dict[str, Any]:
        """
        Process a single file with the given parameters.
        
        Args:
            input_file: Path to input file
            output_base_dir: Base output directory
            operation_mode: Processing mode
            parameters: Parameter overrides
            param_index: Index of parameter set
            output_format: Output image format
            bit_depth: Output bit depth
            optimization_level: Cooking optimization level
            organize_by_material: Whether to organize by material
            verbose: Enable verbose logging
            cooker: Cooker tool instance
            renderer: Renderer tool instance
            
        Returns:
            Dictionary containing processing results
        """
        material_name = Path(input_file).stem
        
        # Create output directory structure
        if organize_by_material:
            if parameters:
                material_output_dir = os.path.join(
                    output_base_dir, material_name, f"variation_{param_index:03d}"
                )
            else:
                material_output_dir = os.path.join(output_base_dir, material_name)
        else:
            material_output_dir = output_base_dir
        
        os.makedirs(material_output_dir, exist_ok=True)
        
        result = {
            "input_file": input_file,
            "material_name": material_name,
            "parameter_index": param_index,
            "parameters": parameters,
            "output_directory": material_output_dir,
            "cooked_file": None,
            "rendered_files": [],
            "success": False,
            "error": None
        }
        
        try:
            current_file = input_file
            
            # Cooking phase
            if operation_mode in ["cook_only", "cook_and_render"] and cooker:
                cook_result = cooker.cook(
                    input_files=[input_file],
                    output_path=material_output_dir,
                    optimization_level=optimization_level,
                    verbose=verbose
                )
                
                if cook_result['success'] and cook_result['output_files']:
                    current_file = cook_result['output_files'][0]
                    result["cooked_file"] = current_file
                else:
                    raise RuntimeError("Cooking failed")
            
            # Rendering phase
            if operation_mode in ["render_only", "cook_and_render"] and renderer:
                render_result = renderer.render(
                    sbsar_file=current_file,
                    output_path=material_output_dir,
                    output_format=output_format,
                    bit_depth=bit_depth,
                    parameters=parameters,
                    verbose=verbose
                )
                
                if render_result['success']:
                    result["rendered_files"] = render_result['output_files']
                else:
                    raise RuntimeError("Rendering failed")
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Failed to process {input_file}: {str(e)}")
        
        return result
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        """
        Validate inputs before execution.
        """
        input_directory = kwargs.get('input_directory', '')
        output_base_directory = kwargs.get('output_base_directory', '')
        batch_parameters = kwargs.get('batch_parameters', '[]')
        
        if not input_directory or not input_directory.strip():
            return "Input directory cannot be empty"
        
        if not output_base_directory or not output_base_directory.strip():
            return "Output base directory cannot be empty"
        
        # Check if input directory exists
        expanded_input_dir = os.path.expanduser(input_directory.strip())
        if not os.path.isabs(expanded_input_dir):
            expanded_input_dir = os.path.abspath(expanded_input_dir)
        
        if not os.path.exists(expanded_input_dir):
            return f"Input directory not found: {expanded_input_dir}"
        
        if not os.path.isdir(expanded_input_dir):
            return f"Input path is not a directory: {expanded_input_dir}"
        
        # Validate batch parameters JSON
        if batch_parameters.strip():
            try:
                param_sets = json.loads(batch_parameters)
                if not isinstance(param_sets, list):
                    return "Batch parameters must be a JSON array"
            except json.JSONDecodeError as e:
                return f"Invalid JSON in batch parameters: {str(e)}"
        
        return True

