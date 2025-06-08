# Installation and Setup Guide

This guide provides detailed instructions for installing and configuring the ComfyUI Substance Designer Integration Plugin.

## Prerequisites

### System Requirements

#### Minimum Requirements
- **Operating System**: Windows 10, macOS 10.15, or Linux (Ubuntu 18.04+)
- **RAM**: 8GB minimum
- **Storage**: 2GB free space for plugin and cache
- **CPU**: Dual-core processor

#### Recommended Requirements
- **Operating System**: Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **RAM**: 16GB or more for batch processing
- **Storage**: 10GB+ free space for materials and outputs
- **CPU**: Quad-core or higher for parallel processing
- **GPU**: Dedicated graphics card for faster ComfyUI operations

### Required Software

#### ComfyUI
1. **Download ComfyUI**: Get the latest version from [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
2. **Install Dependencies**: Follow ComfyUI's installation instructions for your platform
3. **Verify Installation**: Ensure ComfyUI runs correctly before installing this plugin

#### Substance 3D Automation Toolkit
1. **Adobe Account**: You need an Adobe account with Substance 3D access
2. **Download**: Get the toolkit from [Adobe Substance 3D](https://www.adobe.com/products/substance3d-automation-toolkit.html)
3. **Install**: Follow Adobe's installation instructions for your platform
4. **License**: Ensure you have appropriate licensing for command line usage

## Installation Methods

### Method 1: Git Clone (Recommended)

1. **Navigate to ComfyUI custom nodes directory**:
   ```bash
   cd /path/to/ComfyUI/custom_nodes/
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/comfyui-substance-designer-integration.git
   ```

3. **Install Python dependencies**:
   ```bash
   cd comfyui-substance-designer-integration
   pip install -r requirements.txt
   ```

4. **Restart ComfyUI** to load the new nodes

### Method 2: Manual Download

1. **Download ZIP**: Download the plugin as a ZIP file from the repository
2. **Extract**: Extract to your ComfyUI custom_nodes directory
3. **Rename**: Ensure the folder is named `comfyui-substance-designer-integration`
4. **Install Dependencies**: Run `pip install -r requirements.txt` in the plugin directory
5. **Restart ComfyUI**

### Method 3: ComfyUI Manager (If Available)

1. **Open ComfyUI Manager** in your ComfyUI interface
2. **Search**: Look for "Substance Designer Integration"
3. **Install**: Click the install button
4. **Restart**: Restart ComfyUI when prompted

## Configuration

### Automatic Tool Detection

The plugin automatically searches for Substance tools in these locations:

#### Windows
- `C:\\Program Files\\Adobe\\Adobe Substance 3D Automation Toolkit\\bin`
- `C:\\Program Files (x86)\\Adobe\\Adobe Substance 3D Automation Toolkit\\bin`

#### macOS
- `/Applications/Adobe Substance 3D Automation Toolkit/bin`
- `/usr/local/bin`

#### Linux
- `/opt/Adobe/Adobe_Substance_3D_Automation_Toolkit/bin`
- `/usr/local/bin`
- `/usr/bin`

### Manual Configuration

If automatic detection fails, create a configuration file:

1. **Create config directory**:
   - Windows: `%USERPROFILE%\\.comfyui\\substance_designer\\`
   - macOS/Linux: `~/.comfyui/substance_designer/`

2. **Create config.json**:
   ```json
   {
     "tool_paths": {
       "sbscooker": "/path/to/sbscooker",
       "sbsrender": "/path/to/sbsrender"
     },
     "defaults": {
       "cooking": {
         "optimization_level": 1,
         "enable_icons": true,
         "timeout": 300
       },
       "rendering": {
         "output_format": "png",
         "bit_depth": "8",
         "memory_budget": 2000,
         "timeout": 600
       },
       "batch_processing": {
         "max_workers": 2,
         "organize_by_material": true
       }
     },
     "cache": {
       "enabled": true,
       "max_size_mb": 1024
     },
     "logging": {
       "level": "INFO",
       "log_to_file": false
     }
   }
   ```

### Environment Variables

You can also set tool paths using environment variables:

```bash
# Windows (Command Prompt)
set SUBSTANCE_SBSCOOKER_PATH=C:\\path\\to\\sbscooker.exe
set SUBSTANCE_SBSRENDER_PATH=C:\\path\\to\\sbsrender.exe

# Windows (PowerShell)
$env:SUBSTANCE_SBSCOOKER_PATH="C:\\path\\to\\sbscooker.exe"
$env:SUBSTANCE_SBSRENDER_PATH="C:\\path\\to\\sbsrender.exe"

# macOS/Linux
export SUBSTANCE_SBSCOOKER_PATH=/path/to/sbscooker
export SUBSTANCE_SBSRENDER_PATH=/path/to/sbsrender
```

## Verification

### Check Node Installation

1. **Start ComfyUI**
2. **Add Node**: Right-click in the workflow area and select "Add Node"
3. **Navigate**: Go to the "substance" category
4. **Verify**: You should see these nodes:
   - Substance Cooker
   - Substance Renderer
   - Substance Parameter Controller
   - Substance Batch Processor
   - Substance Info Extractor

### Test Tool Detection

1. **Add Substance Cooker node**
2. **Set invalid path**: Use a non-existent .sbs file path
3. **Execute**: The node should show a clear error about tool detection
4. **Check logs**: ComfyUI console should show tool version information

### Basic Functionality Test

1. **Create test material**: Use Substance Designer to create a simple .sbs file
2. **Add Cooker node**: Set the path to your test .sbs file
3. **Add Renderer node**: Connect it to the cooker output
4. **Execute workflow**: Verify that textures are generated

## Troubleshooting

### Common Installation Issues

#### "Module not found" errors
- **Cause**: Python dependencies not installed
- **Solution**: Run `pip install -r requirements.txt` in the plugin directory
- **Alternative**: Install dependencies manually: `pip install torch numpy Pillow`

#### "Tool not found" errors
- **Cause**: Substance tools not detected
- **Solution**: 
  1. Verify Substance 3D Automation Toolkit is installed
  2. Check tool paths in configuration
  3. Test tools manually from command line

#### Nodes not appearing in ComfyUI
- **Cause**: Plugin not loaded correctly
- **Solution**:
  1. Check plugin directory name is correct
  2. Verify all Python files are present
  3. Check ComfyUI console for error messages
  4. Restart ComfyUI completely

### Performance Issues

#### Slow cooking/rendering
- **Cause**: Resource limitations or suboptimal settings
- **Solutions**:
  1. Reduce optimization level for faster cooking
  2. Lower memory budget if system is constrained
  3. Use fewer parallel workers in batch processing
  4. Enable caching to avoid reprocessing

#### Memory errors
- **Cause**: Insufficient system memory
- **Solutions**:
  1. Reduce memory_budget setting
  2. Process smaller batches
  3. Lower output resolution/bit depth
  4. Close other applications

### File Path Issues

#### Path not found errors
- **Cause**: Incorrect file paths or permissions
- **Solutions**:
  1. Use absolute paths instead of relative paths
  2. Check file permissions
  3. Verify files exist at specified locations
  4. Use forward slashes (/) in paths, even on Windows

#### Permission denied errors
- **Cause**: Insufficient file system permissions
- **Solutions**:
  1. Run ComfyUI with appropriate permissions
  2. Check output directory write permissions
  3. Avoid system directories for output

## Advanced Configuration

### Custom Tool Locations

If you have multiple Substance installations or custom builds:

```json
{
  "tool_paths": {
    "sbscooker": "/custom/path/to/sbscooker",
    "sbsrender": "/custom/path/to/sbsrender",
    "sbsmutator": "/custom/path/to/sbsmutator"
  }
}
```

### Performance Tuning

For high-performance systems:

```json
{
  "defaults": {
    "rendering": {
      "memory_budget": 8000,
      "cpu_count": 8
    },
    "batch_processing": {
      "max_workers": 6
    }
  },
  "cache": {
    "max_size_mb": 4096
  }
}
```

For resource-constrained systems:

```json
{
  "defaults": {
    "rendering": {
      "memory_budget": 1000,
      "cpu_count": 2
    },
    "batch_processing": {
      "max_workers": 1
    }
  },
  "cache": {
    "enabled": false
  }
}
```

### Logging Configuration

For debugging:

```json
{
  "logging": {
    "level": "DEBUG",
    "log_to_file": true,
    "log_file": "substance_debug.log",
    "max_log_size_mb": 50
  }
}
```

## Security Considerations

### File Access Restrictions

To restrict file access to specific directories:

```json
{
  "security": {
    "allow_absolute_paths": false,
    "restrict_to_directories": [
      "/safe/materials/directory",
      "/safe/output/directory"
    ],
    "max_file_size_mb": 50
  }
}
```

### Network Security

If using ComfyUI over a network:
1. Ensure proper firewall configuration
2. Use secure file paths
3. Avoid exposing sensitive material files
4. Consider using VPN for remote access

## Getting Help

### Log Files

Check these locations for log information:
- ComfyUI console output
- Plugin log files (if enabled)
- System logs for Substance tool errors

### Diagnostic Information

When reporting issues, include:
1. Operating system and version
2. ComfyUI version
3. Substance 3D Automation Toolkit version
4. Plugin version
5. Error messages and logs
6. Configuration file contents
7. Steps to reproduce the issue

### Support Channels

1. **GitHub Issues**: Report bugs and feature requests
2. **ComfyUI Community**: General ComfyUI questions
3. **Adobe Support**: Substance tool-specific issues

## Updates and Maintenance

### Updating the Plugin

1. **Backup configuration**: Save your config.json file
2. **Update code**: Pull latest changes or download new version
3. **Update dependencies**: Run `pip install -r requirements.txt`
4. **Restore configuration**: Replace config.json if needed
5. **Restart ComfyUI**

### Cache Maintenance

The plugin automatically manages cache, but you can:
1. **Clear cache**: Delete contents of cache directory
2. **Adjust size**: Modify max_size_mb in configuration
3. **Disable caching**: Set enabled to false for debugging

### Regular Maintenance

1. **Monitor disk space**: Cache and output directories can grow large
2. **Update tools**: Keep Substance tools updated
3. **Review logs**: Check for recurring errors or warnings
4. **Optimize settings**: Adjust configuration based on usage patterns

