"""
ComfyUI Substance Designer Integration Plugin

This plugin provides custom nodes for integrating Substance 3D Designer workflows
into ComfyUI through the Substance 3D Automation Toolkit command line tools.

Author: Manus AI
Version: 1.0.0
License: MIT
"""

from .nodes.substance_cooker import SubstanceCooker
from .nodes.substance_renderer import SubstanceRenderer
from .nodes.substance_parameter_controller import SubstanceParameterController
from .nodes.substance_batch_processor import SubstanceBatchProcessor
from .nodes.substance_info_extractor import SubstanceInfoExtractor

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "SubstanceCooker": SubstanceCooker,
    "SubstanceRenderer": SubstanceRenderer,
    "SubstanceParameterController": SubstanceParameterController,
    "SubstanceBatchProcessor": SubstanceBatchProcessor,
    "SubstanceInfoExtractor": SubstanceInfoExtractor,
}

# Display names for the ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS = {
    "SubstanceCooker": "Substance Cooker",
    "SubstanceRenderer": "Substance Renderer", 
    "SubstanceParameterController": "Substance Parameter Controller",
    "SubstanceBatchProcessor": "Substance Batch Processor",
    "SubstanceInfoExtractor": "Substance Info Extractor",
}

# Plugin metadata
__version__ = "1.0.0"
__author__ = "Manus AI"
__description__ = "ComfyUI integration for Substance 3D Designer workflows"

# Export the required mappings
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

