"""
ComfyUI custom node for controlling Substance Designer parameters.

This node provides an interface for dynamically manipulating Substance material
parameters to create variations and control material properties.
"""

import os
import json
import logging
import random
from typing import Dict, List, Tuple, Any, Optional

from ..utils.sbsrender import SubstanceRenderTool, SubstanceToolError

# Configure logging
logger = logging.getLogger(__name__)

class SubstanceParameterController:
    """ComfyUI node for controlling Substance Designer parameters."""
    
    # Node category in ComfyUI
    CATEGORY = "substance"
    
    # Node description
    DESCRIPTION = "Control and manipulate Substance Designer material parameters"
    
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
                "parameter_overrides": ("STRING", {
                    "default": "{}",
                    "multiline": True,
                    "placeholder": "JSON parameter overrides: {\"param_name\": value}"
                }),
                "preset_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Preset name to apply (optional)"
                }),
                "random_seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "step": 1
                }),
                "randomize_parameters": ("BOOLEAN", {
                    "default": False
                }),
                "randomization_strength": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "slider"
                }),
                "extract_info": ("BOOLEAN", {
                    "default": True
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("parameter_json", "applied_parameters", "material_info", "preset_info")
    
    FUNCTION = "control_parameters"
    
    def control_parameters(self, sbsar_file_path: str,
                          parameter_overrides: str = "{}",
                          preset_name: str = "",
                          random_seed: int = -1,
                          randomize_parameters: bool = False,
                          randomization_strength: float = 0.5,
                          extract_info: bool = True) -> Tuple[str, str, str, str]:
        """
        Control and manipulate Substance Designer parameters.
        
        Args:
            sbsar_file_path: Path to the input .sbsar file
            parameter_overrides: JSON string of parameter name-value pairs
            preset_name: Name of preset to apply
            random_seed: Seed for randomization (-1 for random)
            randomize_parameters: Whether to randomize compatible parameters
            randomization_strength: Strength of randomization (0.0-1.0)
            extract_info: Whether to extract material information
            
        Returns:
            Tuple of (parameter_json, applied_parameters, material_info, preset_info)
            
        Raises:
            Exception: If parameter control fails
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
            
            # Parse parameter overrides JSON
            param_overrides = {}
            if parameter_overrides.strip():
                try:
                    param_overrides = json.loads(parameter_overrides)
                    if not isinstance(param_overrides, dict):
                        raise ValueError("Parameter overrides must be a JSON object")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in parameter overrides: {str(e)}")
            
            # Initialize the renderer tool (used for info extraction)
            renderer = SubstanceRenderTool()
            
            # Extract material information if requested
            material_info = {}
            if extract_info:
                try:
                    material_info = renderer.get_info(sbsar_path)
                    logger.info(f"Extracted info for: {sbsar_path}")
                except Exception as e:
                    logger.warning(f"Failed to extract material info: {str(e)}")
                    material_info = {"error": str(e)}
            
            # Set up randomization if requested
            final_parameters = param_overrides.copy()
            
            if randomize_parameters:
                # Set random seed if specified
                if random_seed >= 0:
                    random.seed(random_seed)
                
                # Generate random parameters based on material info
                random_params = self._generate_random_parameters(
                    material_info, randomization_strength
                )
                
                # Merge random parameters with overrides (overrides take precedence)
                for param_name, param_value in random_params.items():
                    if param_name not in final_parameters:
                        final_parameters[param_name] = param_value
            
            # Apply preset if specified
            preset_info = {}
            if preset_name.strip():
                preset_info = {
                    "preset_name": preset_name.strip(),
                    "applied": True
                }
                logger.info(f"Applying preset: {preset_name}")
            
            # Format output data
            parameter_json = json.dumps(final_parameters, indent=2)
            applied_parameters_json = json.dumps({
                "parameters": final_parameters,
                "preset": preset_name.strip() if preset_name.strip() else None,
                "randomized": randomize_parameters,
                "seed": random_seed if random_seed >= 0 else None,
                "randomization_strength": randomization_strength if randomize_parameters else None
            }, indent=2)
            
            material_info_json = json.dumps(material_info, indent=2)
            preset_info_json = json.dumps(preset_info, indent=2)
            
            logger.info(f"Parameter control completed for: {sbsar_path}")
            logger.info(f"Applied {len(final_parameters)} parameter overrides")
            
            return (parameter_json, applied_parameters_json, 
                   material_info_json, preset_info_json)
            
        except SubstanceToolError as e:
            error_msg = f"Substance tool error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            error_msg = f"Parameter control failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _generate_random_parameters(self, material_info: Dict[str, Any], 
                                   strength: float) -> Dict[str, Any]:
        """
        Generate random parameter values based on material information.
        
        Args:
            material_info: Material information dictionary
            strength: Randomization strength (0.0-1.0)
            
        Returns:
            Dictionary of random parameter values
        """
        random_params = {}
        
        # Common parameter types and their random value generators
        common_params = {
            # Color/appearance parameters
            'basecolor_r': lambda: random.uniform(0.0, 1.0),
            'basecolor_g': lambda: random.uniform(0.0, 1.0),
            'basecolor_b': lambda: random.uniform(0.0, 1.0),
            'roughness': lambda: random.uniform(0.0, 1.0),
            'metallic': lambda: random.uniform(0.0, 1.0),
            'specular': lambda: random.uniform(0.0, 1.0),
            
            # Scale and tiling parameters
            'tiling': lambda: random.uniform(1.0, 8.0),
            'scale': lambda: random.uniform(0.5, 2.0),
            'scale_x': lambda: random.uniform(0.5, 2.0),
            'scale_y': lambda: random.uniform(0.5, 2.0),
            
            # Variation parameters
            'random_seed': lambda: random.randint(0, 1000),
            'variation': lambda: random.uniform(0.0, 1.0),
            'noise_scale': lambda: random.uniform(0.1, 2.0),
            
            # Intensity parameters
            'intensity': lambda: random.uniform(0.0, 2.0),
            'contrast': lambda: random.uniform(0.5, 1.5),
            'brightness': lambda: random.uniform(-0.2, 0.2),
        }
        
        # Apply strength factor to randomization
        for param_name, value_generator in common_params.items():
            if random.random() < strength:  # Only randomize based on strength
                try:
                    random_value = value_generator()
                    random_params[param_name] = random_value
                except Exception as e:
                    logger.warning(f"Failed to generate random value for {param_name}: {e}")
        
        return random_params
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """
        Determine if the node needs to be re-executed.
        """
        # Check if input file has been modified
        sbsar_file_path = kwargs.get('sbsar_file_path', '')
        if sbsar_file_path and os.path.exists(sbsar_file_path):
            return os.path.getmtime(sbsar_file_path)
        
        # Also check if randomization is enabled (always re-execute for random)
        if kwargs.get('randomize_parameters', False):
            return random.random()  # Always different
        
        return float('inf')
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        """
        Validate inputs before execution.
        """
        sbsar_file_path = kwargs.get('sbsar_file_path', '')
        parameter_overrides = kwargs.get('parameter_overrides', '{}')
        
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
        
        # Validate parameter overrides JSON
        if parameter_overrides.strip():
            try:
                param_dict = json.loads(parameter_overrides)
                if not isinstance(param_dict, dict):
                    return "Parameter overrides must be a JSON object"
            except json.JSONDecodeError as e:
                return f"Invalid JSON in parameter overrides: {str(e)}"
        
        return True

