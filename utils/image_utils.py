"""
Utilities for handling image conversion between ComfyUI and external formats.

This module provides functions for converting between ComfyUI's internal
image tensor format and standard image files.
"""

import torch
import numpy as np
from PIL import Image
import os
from typing import List, Tuple, Optional, Union
from pathlib import Path

def load_image_as_tensor(image_path: str) -> torch.Tensor:
    """
    Load an image file and convert it to ComfyUI's tensor format.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Image tensor in ComfyUI format [B, H, W, C] with values in [0, 1]
        
    Raises:
        ValueError: If the image cannot be loaded
    """
    if not os.path.exists(image_path):
        raise ValueError(f"Image file does not exist: {image_path}")
    
    try:
        # Load image with PIL
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image, dtype=np.float32)
        
        # Normalize to [0, 1] range
        image_array = image_array / 255.0
        
        # Convert to tensor and add batch dimension
        # ComfyUI expects [B, H, W, C] format
        tensor = torch.from_numpy(image_array).unsqueeze(0)
        
        return tensor
        
    except Exception as e:
        raise ValueError(f"Failed to load image {image_path}: {str(e)}")

def load_images_as_batch(image_paths: List[str]) -> torch.Tensor:
    """
    Load multiple images and combine them into a batch tensor.
    
    Args:
        image_paths: List of paths to image files
        
    Returns:
        Batch tensor in ComfyUI format [B, H, W, C]
        
    Raises:
        ValueError: If images cannot be loaded or have different sizes
    """
    if not image_paths:
        raise ValueError("No image paths provided")
    
    tensors = []
    reference_size = None
    
    for path in image_paths:
        tensor = load_image_as_tensor(path)
        
        # Check that all images have the same size
        if reference_size is None:
            reference_size = tensor.shape[1:3]  # H, W
        elif tensor.shape[1:3] != reference_size:
            raise ValueError(f"Image size mismatch: expected {reference_size}, got {tensor.shape[1:3]} for {path}")
        
        tensors.append(tensor)
    
    # Concatenate along batch dimension
    batch_tensor = torch.cat(tensors, dim=0)
    return batch_tensor

def save_tensor_as_image(tensor: torch.Tensor, output_path: str, 
                        format: str = "PNG", quality: int = 95) -> None:
    """
    Save a ComfyUI tensor as an image file.
    
    Args:
        tensor: Image tensor in ComfyUI format [B, H, W, C] or [H, W, C]
        output_path: Path where the image will be saved
        format: Image format (PNG, JPEG, TIFF, etc.)
        quality: JPEG quality (1-100, ignored for other formats)
        
    Raises:
        ValueError: If tensor format is invalid
    """
    # Handle batch dimension
    if tensor.dim() == 4:
        if tensor.shape[0] != 1:
            raise ValueError(f"Expected single image, got batch size {tensor.shape[0]}")
        tensor = tensor.squeeze(0)  # Remove batch dimension
    elif tensor.dim() != 3:
        raise ValueError(f"Expected 3D or 4D tensor, got {tensor.dim()}D")
    
    # Ensure tensor is in [0, 1] range
    tensor = torch.clamp(tensor, 0.0, 1.0)
    
    # Convert to numpy and scale to [0, 255]
    image_array = (tensor.cpu().numpy() * 255).astype(np.uint8)
    
    # Convert to PIL Image
    image = Image.fromarray(image_array, mode='RGB')
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save with appropriate options
    save_kwargs = {}
    if format.upper() == 'JPEG':
        save_kwargs['quality'] = quality
        save_kwargs['optimize'] = True
    elif format.upper() == 'PNG':
        save_kwargs['optimize'] = True
    
    image.save(output_path, format=format.upper(), **save_kwargs)

def save_batch_as_images(batch_tensor: torch.Tensor, output_dir: str,
                        base_name: str = "image", format: str = "PNG") -> List[str]:
    """
    Save a batch of images as separate files.
    
    Args:
        batch_tensor: Batch tensor in ComfyUI format [B, H, W, C]
        output_dir: Directory where images will be saved
        base_name: Base name for output files
        format: Image format
        
    Returns:
        List of paths to saved images
        
    Raises:
        ValueError: If tensor format is invalid
    """
    if batch_tensor.dim() != 4:
        raise ValueError(f"Expected 4D batch tensor, got {batch_tensor.dim()}D")
    
    batch_size = batch_tensor.shape[0]
    output_paths = []
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(batch_size):
        # Generate output filename
        if batch_size == 1:
            filename = f"{base_name}.{format.lower()}"
        else:
            filename = f"{base_name}_{i:04d}.{format.lower()}"
        
        output_path = os.path.join(output_dir, filename)
        
        # Save individual image
        save_tensor_as_image(batch_tensor[i:i+1], output_path, format)
        output_paths.append(output_path)
    
    return output_paths

def resize_tensor(tensor: torch.Tensor, size: Tuple[int, int], 
                 mode: str = "bilinear") -> torch.Tensor:
    """
    Resize an image tensor to the specified size.
    
    Args:
        tensor: Image tensor in ComfyUI format [B, H, W, C]
        size: Target size as (height, width)
        mode: Interpolation mode (bilinear, nearest, bicubic)
        
    Returns:
        Resized tensor
    """
    # Convert from [B, H, W, C] to [B, C, H, W] for torch.nn.functional.interpolate
    tensor_permuted = tensor.permute(0, 3, 1, 2)
    
    # Resize
    resized = torch.nn.functional.interpolate(
        tensor_permuted, 
        size=size, 
        mode=mode, 
        align_corners=False if mode == 'bilinear' else None
    )
    
    # Convert back to [B, H, W, C]
    return resized.permute(0, 2, 3, 1)

def get_image_info(image_path: str) -> dict:
    """
    Get information about an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing image information
    """
    try:
        with Image.open(image_path) as img:
            return {
                'path': image_path,
                'size': img.size,  # (width, height)
                'mode': img.mode,
                'format': img.format,
                'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
            }
    except Exception as e:
        return {
            'path': image_path,
            'error': str(e)
        }

