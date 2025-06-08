# User Guide

This comprehensive guide explains how to use each node in the ComfyUI Substance Designer Integration Plugin, with detailed examples and best practices.

## Overview

The plugin provides five main nodes that work together to create complete Substance Designer workflows within ComfyUI:

1. **Substance Cooker**: Converts .sbs files to .sbsar archives
2. **Substance Renderer**: Renders .sbsar files to texture maps
3. **Substance Parameter Controller**: Manipulates material parameters
4. **Substance Batch Processor**: Processes multiple files efficiently
5. **Substance Info Extractor**: Extracts metadata from .sbsar files

## Substance Cooker Node

The Substance Cooker node is your starting point for working with Substance Designer files in ComfyUI. It converts source .sbs files into .sbsar archives that can be rendered.

### Input Parameters

#### Required Inputs
- **sbs_file_path** (STRING): Path to your input .sbs file
  - Use absolute paths for reliability
  - Supports environment variables like `${HOME}/materials/wood.sbs`
  - File must exist and be readable

- **output_directory** (STRING): Directory where the .sbsar file will be saved
  - Directory will be created if it doesn't exist
  - Use descriptive names like `./cooked_materials/`

#### Optional Inputs
- **output_name** (STRING): Custom name for the output file
  - If empty, uses the input filename
  - Don't include the .sbsar extension
  - Example: "wood_planks_v2"

- **optimization_level** (INT, 0-3): Controls cooking optimization
  - **0**: Fastest cooking, largest files, no optimization
  - **1**: Balanced performance and size (recommended)
  - **2**: Better compression, slower cooking
  - **3**: Maximum compression, slowest cooking

- **enable_icons** (BOOLEAN): Include graph icons in the output
  - **True**: Includes preview icons (recommended)
  - **False**: Smaller files, no previews

- **merge_graphs** (BOOLEAN): Combine multiple graphs into one file
  - **True**: Single .sbsar with all graphs
  - **False**: Separate files for each graph

- **verbose** (BOOLEAN): Enable detailed logging
  - **True**: Detailed output for debugging
  - **False**: Minimal output

### Output Values

- **sbsar_file_path** (STRING): Path to the generated .sbsar file
- **cooking_log** (STRING): Command output and processing information
- **output_directory** (STRING): Actual directory used for output

### Usage Examples

#### Basic Cooking
```
Input: ./materials/wood_planks.sbs
Output Directory: ./cooked/
Optimization Level: 1
Result: ./cooked/wood_planks.sbsar
```

#### High-Quality Cooking
```
Input: ./materials/metal_surface.sbs
Output Directory: ./production/
Output Name: metal_surface_hq
Optimization Level: 3
Enable Icons: True
Result: ./production/metal_surface_hq.sbsar
```

### Best Practices

1. **Use descriptive output directories** to organize your materials
2. **Start with optimization level 1** and increase only if needed
3. **Enable icons** unless file size is critical
4. **Use absolute paths** to avoid path resolution issues
5. **Check the cooking log** for warnings or optimization suggestions

### Common Issues

- **File not found**: Verify the .sbs file path is correct
- **Permission denied**: Check write permissions on output directory
- **Cooking failed**: Review the cooking log for specific error messages
- **Large file sizes**: Increase optimization level or disable icons

## Substance Renderer Node

The Substance Renderer node converts .sbsar archives into actual texture maps that can be used in your workflows.

### Input Parameters

#### Required Inputs
- **sbsar_file_path** (STRING): Path to the .sbsar file to render
  - Can be connected from Substance Cooker output
  - Must be a valid .sbsar file

- **output_directory** (STRING): Directory for texture outputs
  - Textures will be organized by type (diffuse, normal, etc.)
  - Use descriptive names like `./textures/wood_planks/`

- **output_format** (COMBO): Image format for textures
  - **PNG**: Best for most uses, good compression
  - **TIFF**: High quality, larger files
  - **EXR**: HDR support, professional workflows
  - **JPG**: Smallest files, some quality loss
  - **TGA**: Good for game development
  - **HDR**: High dynamic range images

- **bit_depth** (COMBO): Color depth for output images
  - **8**: Standard 8-bit per channel (0-255)
  - **16**: 16-bit per channel for higher precision
  - **16f**: 16-bit floating point
  - **32f**: 32-bit floating point for HDR

#### Optional Inputs
- **output_name** (STRING): Custom naming pattern for outputs
  - Uses Substance naming conventions if empty
  - Example: "material_{outputName}_{resolution}"

- **graph_selection** (STRING): Specific graph to render
  - Leave empty to render all graphs
  - Use exact graph name from the .sbsar file

- **output_selection** (STRING): Specific outputs to render
  - Leave empty to render all outputs
  - Comma-separated list: "diffuse,normal,roughness"

- **parameters** (STRING): JSON parameter overrides
  - Format: `{"parameter_name": value}`
  - Example: `{"roughness": 0.7, "metallic": 0.9}`

- **preset_name** (STRING): Preset to apply before rendering
  - Must exist in the .sbsar file
  - Applied before parameter overrides

- **cpu_count** (INT): Maximum CPU cores to use
  - 0 = auto-detect and use all available
  - Reduce for system stability

- **memory_budget** (INT): Maximum memory in MB
  - Default: 2000 MB
  - Increase for high-resolution textures
  - Reduce if experiencing memory issues

- **resolution** (INT): Output texture resolution (width and height)
  - Range: 256-4096 pixels
  - Default: 1024
  - Higher values produce better quality but larger files
  - Must be power of 2 for optimal performance

- **return_images** (BOOLEAN): Load textures as ComfyUI tensors
  - **True**: Images available for further processing
  - **False**: Only file paths returned

- **verbose** (BOOLEAN): Enable detailed logging

#### Image Input Parameters (New Feature)
The Substance Renderer now supports dynamic image inputs from ComfyUI workflows, enabling AI-generated content to be used as input textures for procedural materials.

- **input_image_1** (IMAGE): First input image tensor from ComfyUI
  - Connect any ComfyUI IMAGE output (generated, processed, or loaded)
  - Will be saved as temporary PNG file for Substance processing

- **input_image_1_param** (STRING): Parameter name for first input image
  - Must match the exact parameter name in your .sbsar file
  - Example: "diffuse_input", "height_input", "mask_input"

- **input_image_2** (IMAGE): Second input image tensor from ComfyUI
- **input_image_2_param** (STRING): Parameter name for second input image

- **input_image_3** (IMAGE): Third input image tensor from ComfyUI  
- **input_image_3_param** (STRING): Parameter name for third input image

- **input_image_4** (IMAGE): Fourth input image tensor from ComfyUI
- **input_image_4_param** (STRING): Parameter name for fourth input image

**Image Input Usage Notes:**
- Only provide parameter names for images you want to use
- Leave parameter name empty to ignore that image slot
- Images are automatically converted to PNG format for Substance compatibility
- Temporary files are cleaned up after rendering
- Use the Info Extractor node to discover available input parameter names

### Output Values

- **texture_paths** (STRING): JSON list of all generated texture files
- **texture_images** (IMAGE): ComfyUI image tensors (if return_images is True)
- **organized_outputs** (STRING): JSON organized by texture type
- **render_log** (STRING): Command output and processing information
- **output_directory** (STRING): Actual directory used for output

### Usage Examples

#### Basic Rendering
```
SBSAR File: ./cooked/wood_planks.sbsar
Output Directory: ./textures/
Output Format: PNG
Bit Depth: 8
Result: Multiple texture files (diffuse, normal, roughness, etc.)
```

#### High-Quality Rendering
```
SBSAR File: ./cooked/metal_surface.sbsar
Output Directory: ./textures/metal/
Output Format: EXR
Bit Depth: 32f
Resolution: 2048
Memory Budget: 4000
CPU Count: 6
Result: High-quality 2K HDR textures
```

#### High-Resolution Rendering (Fixed in v1.2.0)
```
SBSAR File: ./cooked/detailed_material.sbsar
Output Directory: ./textures/4k/
Output Format: PNG
Bit Depth: 16
Resolution: 4096
Memory Budget: 8000
CPU Count: 8
Result: Ultra-high quality 4K textures
```

#### Parameter-Controlled Rendering
```
SBSAR File: ./cooked/fabric.sbsar
Parameters: {"color_r": 0.8, "color_g": 0.2, "color_b": 0.1, "roughness": 0.6}
Output Directory: ./textures/fabric_red/
Result: Red fabric variant textures
```

#### Dynamic Image Input Rendering (New Feature)
```
SBSAR File: ./cooked/material_with_inputs.sbsar
Input Image 1: Connected from AI image generator
Input Image 1 Param: "diffuse_input"
Input Image 2: Connected from processed texture
Input Image 2 Param: "height_input"
Output Directory: ./textures/dynamic_material/
Result: Material textures using AI-generated content as inputs
```

**Workflow Example for Image Inputs:**
1. Generate or load an image using ComfyUI nodes
2. Connect the image output to input_image_1 on Substance Renderer
3. Set input_image_1_param to the exact parameter name from your .sbsar
4. The image will be automatically saved as a temporary file and passed to Substance
5. Generated textures will incorporate your input image data

### Texture Organization

The renderer automatically organizes outputs by type:

- **diffuse**: Base color/albedo maps
- **normal**: Normal maps for surface detail
- **roughness**: Surface roughness maps
- **metallic**: Metallic/non-metallic masks
- **height**: Height/displacement maps
- **ambient_occlusion**: Ambient occlusion maps
- **emission**: Emissive/glow maps
- **opacity**: Alpha/transparency maps
- **other**: Unrecognized output types

### Best Practices

1. **Use PNG for most applications** unless you need HDR
2. **Start with 8-bit depth** and increase only if needed
3. **Set appropriate memory budget** based on your system
4. **Use parameter overrides** to create material variations
5. **Enable return_images** if you plan to process textures further
6. **Organize outputs by material** using descriptive directory names

### Common Issues

- **Out of memory**: Reduce memory_budget or use lower bit depth
- **Slow rendering**: Reduce cpu_count or memory_budget
- **Missing textures**: Check graph_selection and output_selection
- **Parameter errors**: Verify parameter names and value ranges

## Substance Parameter Controller Node

The Parameter Controller node allows you to manipulate Substance material parameters to create variations and control material properties dynamically.

### Input Parameters

#### Required Inputs
- **sbsar_file_path** (STRING): Path to the .sbsar file to analyze/control

#### Optional Inputs
- **parameter_overrides** (STRING): JSON object with parameter values
  - Format: `{"param_name": value, "another_param": value}`
  - Values must match parameter types and ranges

- **preset_name** (STRING): Name of preset to apply
  - Must exist in the .sbsar file
  - Applied before parameter overrides

- **random_seed** (INT): Seed for randomization
  - -1 for random seed
  - Use specific values for reproducible results

- **randomize_parameters** (BOOLEAN): Enable parameter randomization
  - Generates random values for compatible parameters
  - Controlled by randomization_strength

- **randomization_strength** (FLOAT, 0.0-1.0): Intensity of randomization
  - 0.0: No randomization
  - 1.0: Maximum randomization
  - 0.5: Moderate variation (recommended)

- **extract_info** (BOOLEAN): Extract material information
  - Provides detailed parameter and graph information

### Output Values

- **parameter_json** (STRING): Final parameter values as JSON
- **applied_parameters** (STRING): Complete parameter application information
- **material_info** (STRING): Extracted material metadata
- **preset_info** (STRING): Information about applied presets

### Usage Examples

#### Manual Parameter Control
```
SBSAR File: ./cooked/metal.sbsar
Parameter Overrides: {
  "roughness": 0.3,
  "metallic": 0.9,
  "basecolor_r": 0.7,
  "basecolor_g": 0.7,
  "basecolor_b": 0.8
}
Result: Specific metal appearance
```

#### Random Variation Generation
```
SBSAR File: ./cooked/fabric.sbsar
Randomize Parameters: True
Random Seed: 42
Randomization Strength: 0.7
Result: Reproducible fabric variation
```

#### Preset Application
```
SBSAR File: ./cooked/wood.sbsar
Preset Name: "Oak_Aged"
Parameter Overrides: {"tiling": 2.0}
Result: Oak preset with custom tiling
```

### Parameter Types and Ranges

Common parameter types you'll encounter:

#### Color Parameters
- **basecolor_r/g/b**: RGB color components (0.0-1.0)
- **color_r/g/b**: Alternative color naming
- **hue**: Hue shift (-1.0 to 1.0)
- **saturation**: Color saturation (0.0-2.0)

#### Surface Properties
- **roughness**: Surface roughness (0.0-1.0)
- **metallic**: Metallic property (0.0-1.0)
- **specular**: Specular reflection (0.0-1.0)
- **normal_intensity**: Normal map strength (0.0-2.0)

#### Scale and Tiling
- **tiling**: Overall scale multiplier (0.1-10.0)
- **scale**: Alternative scale parameter
- **scale_x/y**: Separate X/Y scaling
- **offset_x/y**: UV offset (-1.0 to 1.0)

#### Variation Parameters
- **random_seed**: Variation seed (0-1000)
- **variation**: Variation amount (0.0-1.0)
- **noise_scale**: Noise scaling (0.1-5.0)

#### Intensity Controls
- **intensity**: Overall intensity (0.0-2.0)
- **contrast**: Contrast adjustment (0.0-2.0)
- **brightness**: Brightness offset (-1.0 to 1.0)

### Best Practices

1. **Start with extract_info enabled** to discover available parameters
2. **Use moderate randomization strength** (0.3-0.7) for natural variations
3. **Set specific seeds** for reproducible results
4. **Combine presets with overrides** for fine control
5. **Test parameter ranges** before batch processing
6. **Use descriptive parameter names** in your JSON

### Common Issues

- **Invalid parameter names**: Use Info Extractor to discover correct names
- **Value out of range**: Check parameter definitions for valid ranges
- **JSON syntax errors**: Validate JSON format before execution
- **Preset not found**: Verify preset exists in the .sbsar file

## Substance Batch Processor Node

The Batch Processor node efficiently handles multiple Substance files or generates multiple variations of the same material.

### Input Parameters

#### Required Inputs
- **input_directory** (STRING): Directory containing input files
  - Must contain .sbs files (for cooking) or .sbsar files (for rendering)
  - Supports nested directories

- **output_base_directory** (STRING): Base directory for all outputs
  - Organized by material and variation
  - Created automatically if it doesn't exist

- **operation_mode** (COMBO): Type of processing to perform
  - **cook_only**: Convert .sbs to .sbsar files only
  - **render_only**: Render .sbsar files to textures only
  - **cook_and_render**: Complete pipeline from .sbs to textures

#### Optional Inputs
- **file_pattern** (STRING): Pattern for filtering input files
  - Default: "*.sbs" for cooking operations
  - Examples: "*.sbsar", "wood_*.sbs", "*_v2.sbs"

- **batch_parameters** (STRING): JSON array of parameter sets
  - Each set creates a separate variation
  - Format: `[{"param1": value1}, {"param2": value2}]`

- **output_format** (COMBO): Image format for rendered textures
- **bit_depth** (COMBO): Color depth for rendered textures
- **optimization_level** (INT): Cooking optimization level
- **max_workers** (INT): Maximum parallel processing threads
  - Balance between speed and system stability
  - Recommended: 2-4 for most systems

- **organize_by_material** (BOOLEAN): Organize outputs by material name
  - **True**: Separate folders for each material
  - **False**: All outputs in the base directory

- **verbose** (BOOLEAN): Enable detailed logging

### Output Values

- **processed_files** (STRING): JSON list of all processing results
- **batch_summary** (STRING): Processing statistics and summary
- **error_log** (STRING): JSON list of any errors encountered
- **output_structure** (STRING): JSON organization of output files

### Usage Examples

#### Simple Batch Cooking
```
Input Directory: ./materials/
Output Directory: ./batch_cooked/
Operation Mode: cook_only
File Pattern: *.sbs
Max Workers: 3
Result: All .sbs files converted to .sbsar
```

#### Batch Rendering with Variations
```
Input Directory: ./cooked_materials/
Output Directory: ./texture_variations/
Operation Mode: render_only
Batch Parameters: [
  {"roughness": 0.2, "metallic": 0.9},
  {"roughness": 0.5, "metallic": 0.5},
  {"roughness": 0.8, "metallic": 0.1}
]
Result: 3 variations of each material
```

#### Complete Pipeline Processing
```
Input Directory: ./source_materials/
Output Directory: ./production_ready/
Operation Mode: cook_and_render
File Pattern: *_final.sbs
Optimization Level: 2
Output Format: PNG
Organize by Material: True
Result: Complete processing pipeline
```

### Output Organization

With `organize_by_material` enabled:
```
output_base_directory/
├── material1/
│   ├── variation_000/
│   │   ├── material1_diffuse.png
│   │   ├── material1_normal.png
│   │   └── material1_roughness.png
│   └── variation_001/
│       ├── material1_diffuse.png
│       └── ...
└── material2/
    └── ...
```

### Performance Considerations

#### Worker Count Guidelines
- **Single-core systems**: max_workers = 1
- **Dual-core systems**: max_workers = 2
- **Quad-core systems**: max_workers = 2-3
- **8+ core systems**: max_workers = 3-6

#### Memory Management
- Monitor system memory usage during batch operations
- Reduce worker count if experiencing memory pressure
- Process smaller batches for very large materials

#### I/O Optimization
- Use fast storage (SSD) for input and output directories
- Avoid network drives for large batch operations
- Consider separate drives for input and output

### Best Practices

1. **Test with small batches** before processing large sets
2. **Monitor system resources** during processing
3. **Use descriptive output directories** for organization
4. **Set appropriate worker counts** for your system
5. **Enable verbose logging** for debugging
6. **Backup important materials** before batch processing

### Common Issues

- **Out of memory**: Reduce max_workers or process smaller batches
- **Slow performance**: Check I/O bottlenecks and worker count
- **Partial failures**: Review error_log for specific issues
- **Disk space**: Monitor available space during large operations

## Substance Info Extractor Node

The Info Extractor node provides detailed information about .sbsar files, including parameters, outputs, and metadata.

### Input Parameters

#### Required Inputs
- **sbsar_file_path** (STRING): Path to the .sbsar file to analyze

#### Optional Inputs
- **extract_parameters** (BOOLEAN): Extract parameter information
- **extract_outputs** (BOOLEAN): Extract output information
- **extract_graphs** (BOOLEAN): Extract graph information
- **format_output** (BOOLEAN): Format JSON for readability
- **verbose** (BOOLEAN): Enable detailed logging

### Output Values

- **file_info** (STRING): Basic file information as JSON
- **graph_info** (STRING): Graph metadata as JSON
- **parameter_info** (STRING): Parameter definitions as JSON
- **output_info** (STRING): Output channel information as JSON
- **formatted_summary** (STRING): Human-readable summary

### Usage Examples

#### Complete Information Extraction
```
SBSAR File: ./materials/wood_planks.sbsar
Extract Parameters: True
Extract Outputs: True
Extract Graphs: True
Format Output: True
Result: Complete material analysis
```

#### Parameter Discovery
```
SBSAR File: ./materials/metal_surface.sbsar
Extract Parameters: True
Extract Outputs: False
Extract Graphs: False
Result: Parameter names and types for scripting
```

### Information Types

#### File Information
- File size and modification dates
- Basic metadata
- File format version

#### Graph Information
- Available graphs in the material
- Graph types and descriptions
- Rendering capabilities

#### Parameter Information
- Parameter names and types
- Value ranges and defaults
- Parameter categories

#### Output Information
- Available output channels
- Output types (diffuse, normal, etc.)
- Resolution and format capabilities

### Best Practices

1. **Use Info Extractor first** when working with new materials
2. **Enable all extraction options** for complete analysis
3. **Format output for readability** when reviewing manually
4. **Save extraction results** for reference in complex workflows
5. **Use parameter info** to build automated workflows

## Workflow Patterns

### Basic Material Processing
1. **Substance Cooker** → **Substance Renderer** → **Preview/Save**
2. Simple linear workflow for single materials

### Parameter Variation Workflow
1. **Substance Cooker** → **Parameter Controller** → **Substance Renderer**
2. Generate multiple variations of the same base material

### Batch Processing Workflow
1. **Substance Batch Processor** → **Results Analysis**
2. Process multiple materials efficiently

### Analysis and Development Workflow
1. **Info Extractor** → **Parameter Controller** → **Renderer**
2. Discover capabilities, then create controlled variations

### Production Pipeline
1. **Batch Processor** (cook_and_render) → **Quality Control** → **Asset Integration**
2. Complete production-ready processing

## Tips and Tricks

### Performance Optimization
- Use caching for repeated operations
- Process materials in order of complexity
- Monitor system resources during batch operations
- Use appropriate optimization levels for your needs

### Quality Control
- Always preview results before batch processing
- Use consistent naming conventions
- Validate parameter ranges before automation
- Keep backups of source materials

### Workflow Organization
- Use descriptive directory names
- Organize by project or material type
- Document parameter sets for reuse
- Version control your workflow files

### Debugging
- Enable verbose logging when troubleshooting
- Test with simple materials first
- Check file permissions and paths
- Verify Substance tool installation and licensing

