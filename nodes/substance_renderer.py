"""
ComfyUI custom node for rendering Substance Designer archives.

This node provides an interface for rendering .sbsar files to texture maps
using the sbsrender tool from Substance 3D Automation Toolkit.
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Any, Optional

from ..utils.sbsrender import SubstanceRenderTool, SubstanceToolError
from ..utils.image_utils import load_images_as_batch, get_image_info

# Configure logging
logger = logging.getLogger(__name__)

class SubstanceRenderer:
    """ComfyUI node for rendering Substance Designer archives."""
    
    # Node category in ComfyUI
    CATEGORY = "substance"
    
    # Node description
    DESCRIPTION = "Render Substance Designer .sbsar files to texture maps"
    
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
                "output_directory": ("STRING", {
                    "default": "./textures",
                    "multiline": False,
                    "placeholder": "Output directory path"
                }),
                "output_format": (["png", "tiff", "exr", "jpg", "tga", "hdr"], {
                    "default": "png"
                }),
                "bit_depth": (["8", "16", "16f", "32f"], {
                    "default": "8"
                }),
            },
            "optional": {
                "output_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Custom output name pattern (optional)"
                }),
                "graph_selection": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Specific graph to render (optional)"
                }),
                "output_selection": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Specific outputs to render (optional)"
                }),
                "parameters": ("STRING", {
                    "default": "{}",
                    "multiline": True,
                    "placeholder": "JSON parameters: {\"param_name\": value}"
                }),
                "preset_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Preset name (optional)"
                }),
                "cpu_count": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 32,
                    "step": 1,
                    "display": "slider"
                }),
                "memory_budget": ("INT", {
                    "default": 2000,
                    "min": 512,
                    "max": 16384,
                    "step": 256,
                    "display": "slider"
                }),
                "resolution": ("INT", {
                    "default": 1024,
                    "min": 256,
                    "max": 4096,
                    "step": 256,
                    "display": "slider",
                    "tooltip": "Output texture resolution (width and height)"
                }),
                "return_images": ("BOOLEAN", {
                    "default": True
                }),
                "verbose": ("BOOLEAN", {
                    "default": False
                }),
                # Image input parameters for dynamic material creation
                "input_image_1": ("IMAGE", {
                    "tooltip": "First input image for material parameters"
                }),
                "input_image_1_param": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Parameter name for input_image_1 (e.g., 'diffuse_input')"
                }),
                "input_image_2": ("IMAGE", {
                    "tooltip": "Second input image for material parameters"
                }),
                "input_image_2_param": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Parameter name for input_image_2"
                }),
                "input_image_3": ("IMAGE", {
                    "tooltip": "Third input image for material parameters"
                }),
                "input_image_3_param": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Parameter name for input_image_3"
                }),
                "input_image_4": ("IMAGE", {
                    "tooltip": "Fourth input image for material parameters"
                }),
                "input_image_4_param": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Parameter name for input_image_4"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("texture_paths", "texture_images", "organized_outputs", "render_log", "output_directory")
    
    FUNCTION = "render_substance"
    
    def render_substance(self, sbsar_file_path: str, output_directory: str,
                        output_format: str = "png", bit_depth: str = "8",
                        output_name: str = "", graph_selection: str = "",
                        output_selection: str = "", parameters: str = "{}",
                        preset_name: str = "", cpu_count: int = 0,
                        memory_budget: int = 2000, resolution: int = 1024,
                        return_images: bool = True, verbose: bool = False,
                        input_image_1: Optional[Any] = None, input_image_1_param: str = "",
                        input_image_2: Optional[Any] = None, input_image_2_param: str = "",
                        input_image_3: Optional[Any] = None, input_image_3_param: str = "",
                        input_image_4: Optional[Any] = None, input_image_4_param: str = "") -> Tuple[str, Any, str, str, str]:
        """
        Render a Substance Designer archive to texture maps.
        
        Args:
            sbsar_file_path: Path to the input .sbsar file
            output_directory: Directory where textures will be saved
            output_format: Output image format
            bit_depth: Output bit depth
            output_name: Custom output name pattern
            graph_selection: Specific graph to render
            output_selection: Specific outputs to render
            parameters: JSON string of parameter overrides
            preset_name: Name of preset to apply
            cpu_count: Maximum CPU cores (0 = auto)
            memory_budget: Maximum memory in MB
            resolution: Output texture resolution (width and height)
            return_images: Whether to return images as tensors
            verbose: Enable verbose logging
            input_image_1: First input image tensor from ComfyUI
            input_image_1_param: Parameter name for first input image
            input_image_2: Second input image tensor from ComfyUI
            input_image_2_param: Parameter name for second input image
            input_image_3: Third input image tensor from ComfyUI
            input_image_3_param: Parameter name for third input image
            input_image_4: Fourth input image tensor from ComfyUI
            input_image_4_param: Parameter name for fourth input image
            
        Returns:
            Tuple of (texture_paths, texture_images, organized_outputs, render_log, output_directory)
            
        Raises:
            Exception: If rendering fails
        """
        try:
            # Validate inputs
            if not sbsar_file_path or not sbsar_file_path.strip():
                raise ValueError("SBSAR file path cannot be empty")
            
            if not output_directory or not output_directory.strip():
                raise ValueError("Output directory cannot be empty")
            
            # Expand user paths and make absolute
            sbsar_path = os.path.expanduser(sbsar_file_path.strip())
            output_dir = os.path.expanduser(output_directory.strip())
            
            if not os.path.isabs(sbsar_path):
                sbsar_path = os.path.abspath(sbsar_path)
            
            if not os.path.isabs(output_dir):
                output_dir = os.path.abspath(output_dir)
            
            # Check if input file exists
            if not os.path.exists(sbsar_path):
                raise FileNotFoundError(f"SBSAR file not found: {sbsar_path}")
            
            # Check file extension
            if not sbsar_path.lower().endswith('.sbsar'):
                raise ValueError(f"Input file must have .sbsar extension: {sbsar_path}")
            
            # Parse parameters JSON
            param_dict = {}
            if parameters.strip():
                try:
                    param_dict = json.loads(parameters)
                    if not isinstance(param_dict, dict):
                        raise ValueError("Parameters must be a JSON object")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in parameters: {str(e)}")
            
            # Process input images and save them as temporary files for Substance input
            image_entries = {}
            temp_image_files = []
            
            # Helper function to process individual image inputs
            def process_input_image(image_tensor, param_name, image_index):
                if image_tensor is not None and param_name.strip():
                    try:
                        from ..utils.image_utils import save_tensor_as_image
                        import tempfile
                        
                        # Create temporary file for the input image
                        temp_dir = os.path.join(output_dir, "temp_inputs")
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        temp_file = os.path.join(temp_dir, f"input_image_{image_index}.png")
                        
                        # Save the ComfyUI tensor as an image file
                        save_tensor_as_image(image_tensor, temp_file, format="PNG")
                        
                        # Add to image entries for sbsrender --set-entry
                        image_entries[param_name.strip()] = temp_file
                        temp_image_files.append(temp_file)
                        
                        logger.info(f"Saved input image {image_index} to {temp_file} for parameter '{param_name.strip()}'")
                        
                    except Exception as e:
                        logger.warning(f"Failed to process input image {image_index}: {str(e)}")
            
            # Process all input images
            process_input_image(input_image_1, input_image_1_param, 1)
            process_input_image(input_image_2, input_image_2_param, 2)
            process_input_image(input_image_3, input_image_3_param, 3)
            process_input_image(input_image_4, input_image_4_param, 4)
            
            if image_entries:
                logger.info(f"Processing {len(image_entries)} input images: {list(image_entries.keys())}")
            
            # Initialize the renderer tool
            renderer = SubstanceRenderTool()
            
            # Prepare rendering parameters
            render_params = {
                'output_format': output_format,
                'bit_depth': bit_depth,
                'output_name': output_name.strip() if output_name.strip() else None,
                'graph_selection': graph_selection.strip() if graph_selection.strip() else None,
                'output_selection': output_selection.strip() if output_selection.strip() else None,
                'parameters': param_dict if param_dict else None,
                'image_entries': image_entries if image_entries else None,  # Add image entries
                'preset_name': preset_name.strip() if preset_name.strip() else None,
                'resolution': resolution,  # Add resolution parameter
                'cpu_count': cpu_count if cpu_count > 0 else None,
                'memory_budget': memory_budget,
                'verbose': verbose
            }
            
            # Log the rendering operation
            logger.info(f"Rendering SBSAR file: {sbsar_path}")
            logger.info(f"Output directory: {output_dir}")
            logger.info(f"Parameters: {render_params}")
            
            # Perform the rendering
            result = renderer.render(
                sbsar_file=sbsar_path,
                output_path=output_dir,
                **render_params
            )
            
            # Extract results
            if not result['success']:
                raise RuntimeError("Rendering failed - check logs for details")
            
            output_files = result.get('output_files', [])
            organized_outputs = result.get('organized_outputs', {})
            render_log = result.get('command_output', '')
            actual_output_dir = result.get('output_directory', output_dir)
            
            # Convert file lists to JSON strings for ComfyUI
            texture_paths_json = json.dumps(output_files)
            organized_outputs_json = json.dumps(organized_outputs)
            
            # Load images as tensors if requested
            texture_images = None
            if return_images and output_files:
                try:
                    # Load all generated textures as a batch
                    texture_images = load_images_as_batch(output_files)
                    logger.info(f"Loaded {len(output_files)} textures as image batch")
                except Exception as e:
                    logger.warning(f"Failed to load images as tensors: {str(e)}")
                    # Create a dummy tensor if image loading fails
                    import torch
                    texture_images = torch.zeros((1, 512, 512, 3))
            else:
                # Create a dummy tensor if no images or not requested
                import torch
                texture_images = torch.zeros((1, 512, 512, 3))
            
            logger.info(f"Successfully rendered {len(output_files)} textures")
            
            # Cleanup temporary image files
            for temp_file in temp_image_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        logger.debug(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temporary file {temp_file}: {str(e)}")
            
            # Remove temporary directory if empty
            try:
                temp_dir = os.path.join(output_dir, "temp_inputs")
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary directory: {str(e)}")
            
            return (texture_paths_json, texture_images, organized_outputs_json, 
                   render_log, actual_output_dir)
            
        except SubstanceToolError as e:
            # Cleanup temporary files on error
            for temp_file in temp_image_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            
            error_msg = f"Substance tool error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            # Cleanup temporary files on error
            for temp_file in temp_image_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            
            error_msg = f"Rendering failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """
        Determine if the node needs to be re-executed.
        """
        # Check if input file has been modified
        sbsar_file_path = kwargs.get('sbsar_file_path', '')
        if sbsar_file_path and os.path.exists(sbsar_file_path):
            return os.path.getmtime(sbsar_file_path)
        return float('inf')  # Always re-execute if file doesn't exist
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        """
        Validate inputs before execution.
        """
        sbsar_file_path = kwargs.get('sbsar_file_path', '')
        output_directory = kwargs.get('output_directory', '')
        parameters = kwargs.get('parameters', '{}')
        
        if not sbsar_file_path or not sbsar_file_path.strip():
            return "SBSAR file path cannot be empty"
        
        if not output_directory or not output_directory.strip():
            return "Output directory cannot be empty"
        
        # Expand and check file path
        expanded_path = os.path.expanduser(sbsar_file_path.strip())
        if not os.path.isabs(expanded_path):
            expanded_path = os.path.abspath(expanded_path)
        
        if not os.path.exists(expanded_path):
            return f"SBSAR file not found: {expanded_path}"
        
        if not expanded_path.lower().endswith('.sbsar'):
            return f"Input file must have .sbsar extension: {expanded_path}"
        
        # Validate parameters JSON
        if parameters.strip():
            try:
                param_dict = json.loads(parameters)
                if not isinstance(param_dict, dict):
                    return "Parameters must be a JSON object"
            except json.JSONDecodeError as e:
                return f"Invalid JSON in parameters: {str(e)}"
        
        return True

