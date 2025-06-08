# Changelog

All notable changes to the ComfyUI Substance Designer Integration Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-12-08

### Fixed
- **Resolution Control Issue**: Fixed critical bug where output textures were stuck at 256x resolution
  - Added proper `resolution` parameter to Substance Renderer node (256-4096, default: 1024)
  - Fixed sbsrender utility to properly pass `--output-size` parameter to command line tool
  - Updated method signatures and parameter passing throughout the rendering pipeline
  - Added comprehensive resolution documentation and usage examples

### Enhanced
- **Substance Renderer Node**: Added resolution slider control with proper validation
- **Command Line Integration**: Enhanced sbsrender wrapper to handle resolution parameters correctly
- **Documentation**: Updated user guide and README with resolution control examples
- **Error Handling**: Improved validation for resolution parameter ranges

### Technical Improvements
- **Parameter Validation**: Added proper range checking for resolution values
- **Command Building**: Fixed command line argument construction for sbsrender tool
- **Method Signatures**: Updated all relevant method signatures to include resolution parameter
- **Logging**: Enhanced logging to show resolution settings in render operations

## [1.1.0] - 2024-12-08

### Added
- **Dynamic Image Input Support**: Substance Renderer node now accepts ComfyUI IMAGE inputs
  - Added 4 image input slots (input_image_1 through input_image_4) with corresponding parameter name fields
  - Images are automatically converted to temporary PNG files for Substance processing
  - Supports AI-generated images, processed textures, and any ComfyUI IMAGE output
  - Automatic cleanup of temporary files after rendering
  - Enhanced sbsrender utility to support --set-entry command line option
- **New Example Workflows**: 
  - `dynamic_image_inputs.json`: Basic workflow demonstrating image input functionality
  - `advanced_ai_material_workflow.json`: Complex workflow with multiple AI-generated inputs
- **Enhanced Documentation**: Updated user guide and README with image input usage examples

### Enhanced
- **Substance Renderer Node**: Extended input parameters to support dynamic material creation
- **Image Utilities**: Leveraged existing save_tensor_as_image function for ComfyUI integration
- **Error Handling**: Improved error management for image processing and temporary file operations

### Technical Improvements
- **Command Line Integration**: Enhanced sbsrender wrapper to handle image entry parameters
- **File Management**: Robust temporary file creation and cleanup system
- **Parameter Validation**: Added validation for image entry file existence
- **Logging**: Enhanced logging for image processing operations

## [1.0.0] - 2024-12-08

### Added
- Initial release of ComfyUI Substance Designer Integration Plugin
- **Substance Cooker Node**: Convert .sbs files to .sbsar archives
  - Configurable optimization levels (0-3)
  - Support for graph merging and icon inclusion
  - Comprehensive error handling and logging
- **Substance Renderer Node**: Render .sbsar files to texture maps
  - Multiple output formats (PNG, TIFF, EXR, JPG, TGA, HDR)
  - Configurable bit depth (8, 16, 16f, 32f)
  - Parameter override support via JSON
  - Automatic texture organization by type
  - ComfyUI image tensor integration
- **Substance Parameter Controller Node**: Dynamic parameter manipulation
  - JSON-based parameter overrides
  - Parameter randomization with controllable strength
  - Preset application support
  - Material information extraction
- **Substance Batch Processor Node**: Efficient multi-file processing
  - Parallel processing with configurable worker count
  - Multiple operation modes (cook_only, render_only, cook_and_render)
  - Batch parameter variation generation
  - Organized output structure
- **Substance Info Extractor Node**: Metadata and parameter discovery
  - Complete material analysis
  - Parameter type and range discovery
  - Output channel information
  - Human-readable summary generation
- **Automatic Tool Detection**: Smart detection of Substance 3D Automation Toolkit
  - Support for Windows, macOS, and Linux
  - Common installation path scanning
  - Manual configuration override support
- **Comprehensive Configuration System**: Flexible plugin configuration
  - JSON-based configuration files
  - Performance tuning options
  - Security and access control settings
  - Logging configuration
- **Advanced Error Handling**: Robust error management
  - Detailed error messages and logging
  - Graceful failure handling
  - Process timeout management
  - Resource usage monitoring
- **Caching System**: Intelligent operation caching
  - Automatic cache management
  - Configurable cache size limits
  - Cache invalidation on file changes
- **Documentation**: Comprehensive user and developer documentation
  - Installation and setup guide
  - Detailed user guide with examples
  - API reference documentation
  - Troubleshooting guide
- **Example Workflows**: Ready-to-use ComfyUI workflow examples
  - Basic cooking workflow
  - Parameter variation generation
  - Batch processing examples
  - Advanced pipeline demonstrations

### Technical Features
- **Multi-threading Support**: Parallel processing for batch operations
- **Memory Management**: Configurable memory budgets and resource limits
- **Cross-platform Compatibility**: Windows, macOS, and Linux support
- **ComfyUI Integration**: Native ComfyUI node implementation
- **Image Format Support**: Wide range of texture output formats
- **Parameter Validation**: Input validation and type checking
- **Process Management**: Robust external process handling
- **File System Safety**: Secure file operations and path validation

### Dependencies
- Python 3.7+
- PyTorch (for ComfyUI compatibility)
- NumPy (for image processing)
- Pillow (for image format support)
- Substance 3D Automation Toolkit (external dependency)

### Known Limitations
- Requires Substance 3D Automation Toolkit installation
- Command line tool licensing requirements apply
- Performance depends on system resources and material complexity
- Some advanced Substance features may not be exposed through command line tools

### Compatibility
- ComfyUI: Latest version with custom node support
- Substance 3D Automation Toolkit: 2023.1.0 and later
- Python: 3.7, 3.8, 3.9, 3.10, 3.11
- Operating Systems: Windows 10+, macOS 10.15+, Ubuntu 18.04+

## [Unreleased]

### Planned Features
- **Additional Substance Tools**: Support for sbsmutator, sbsbaker, sbsmtools
- **Real-time Preview**: Live parameter preview capabilities
- **Material Library Integration**: Built-in material browser and management
- **Advanced Batch Operations**: More sophisticated batch processing options
- **Performance Optimizations**: Enhanced caching and processing efficiency
- **UI Enhancements**: Improved node interfaces and user experience
- **Cloud Integration**: Support for cloud-based Substance processing
- **Version Control**: Integration with material versioning systems

### Future Considerations
- **GPU Acceleration**: Leverage GPU processing where available
- **Distributed Processing**: Multi-machine processing support
- **Advanced Analytics**: Processing statistics and optimization suggestions
- **Plugin Ecosystem**: Support for third-party extensions
- **API Extensions**: Additional programmatic interfaces
- **Mobile Support**: Compatibility with mobile ComfyUI deployments

