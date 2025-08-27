"""
Image Processing Service
Handles image resizing, compression, format conversion, and enhancement
"""

import io
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List
from PIL import Image, ImageEnhance, ImageFilter, ExifTags
import cv2
import numpy as np

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.settings import settings
from config.storage_config import ProcessingConfig


class ImageProcessor:
    """Image processing engine with various transformation capabilities"""
    
    def __init__(self):
        self.config = ProcessingConfig.get_image_config()
        self.supported_formats = self.config["allowed_formats"]
        self.default_quality = self.config["quality"]
        self.max_dimensions = self.config["max_dimensions"]
    
    async def process_image(self, image_data: bytes, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process image based on operation type and parameters"""
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Handle EXIF orientation
            image = self._fix_orientation(image)
            
            # Process based on operation
            if operation == "resize":
                result_image = await self._resize_image(image, parameters)
            elif operation == "compress":
                result_image = await self._compress_image(image, parameters)
            elif operation == "convert":
                result_image = await self._convert_format(image, parameters)
            elif operation == "enhance":
                result_image = await self._enhance_image(image, parameters)
            elif operation == "thumbnail":
                result_image = await self._create_thumbnail(image, parameters)
            elif operation == "crop":
                result_image = await self._crop_image(image, parameters)
            elif operation == "rotate":
                result_image = await self._rotate_image(image, parameters)
            elif operation == "filter":
                result_image = await self._apply_filter(image, parameters)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Convert result to bytes
            output_buffer = io.BytesIO()
            
            # Determine output format
            output_format = parameters.get("output_format", "JPEG")
            if output_format.upper() not in self.supported_formats:
                output_format = "JPEG"
            
            # Save with appropriate settings
            save_kwargs = self._get_save_kwargs(output_format, parameters)
            result_image.save(output_buffer, format=output_format, **save_kwargs)
            
            output_data = output_buffer.getvalue()
            
            return {
                "success": True,
                "data": output_data,
                "format": output_format,
                "size": len(output_data),
                "dimensions": result_image.size,
                "operation": operation,
                "parameters": parameters
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation,
                "parameters": parameters
            }
    
    async def _resize_image(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        """Resize image to specified dimensions"""
        width = parameters.get("width")
        height = parameters.get("height")
        maintain_aspect_ratio = parameters.get("maintain_aspect_ratio", True)
        resample_method = parameters.get("resample", "LANCZOS")
        
        if not width or not height:
            raise ValueError("Width and height are required for resize operation")
        
        # Validate dimensions
        if width > self.max_dimensions[0] or height > self.max_dimensions[1]:
            raise ValueError(f"Dimensions exceed maximum allowed: {self.max_dimensions}")
        
        # Get resample method
        resample = getattr(Image.Resampling, resample_method, Image.Resampling.LANCZOS)
        
        if maintain_aspect_ratio:
            # Calculate aspect ratio preserving dimensions
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height
            
            if width / height > aspect_ratio:
                width = int(height * aspect_ratio)
            else:
                height = int(width / aspect_ratio)
        
        return image.resize((width, height), resample)
    
    async def _compress_image(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        """Compress image by adjusting quality and optimization"""
        # Compression is handled during save, return original image
        # The compression parameters will be used in _get_save_kwargs
        return image
    
    async def _convert_format(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        """Convert image to different format"""
        target_format = parameters.get("format", "JPEG").upper()
        
        if target_format not in self.supported_formats:
            raise ValueError(f"Unsupported target format: {target_format}")
        
        # Handle format-specific conversions
        if target_format == "JPEG" and image.mode in ("RGBA", "P"):
            # Convert to RGB for JPEG
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = background
        elif target_format == "PNG" and image.mode != "RGBA":
            image = image.convert("RGBA")
        
        return image
    
    async def _enhance_image(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        """Apply image enhancements"""
        enhanced_image = image.copy()
        
        # Brightness adjustment
        if "brightness" in parameters:
            brightness = max(0.1, min(2.0, parameters["brightness"]))
            enhancer = ImageEnhance.Brightness(enhanced_image)
            enhanced_image = enhancer.enhance(brightness)
        
        # Contrast adjustment
        if "contrast" in parameters:
            contrast = max(0.1, min(2.0, parameters["contrast"]))
            enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = enhancer.enhance(contrast)
        
        # Saturation adjustment
        if "saturation" in parameters:
            saturation = max(0.0, min(2.0, parameters["saturation"]))
            enhancer = ImageEnhance.Color(enhanced_image)
            enhanced_image = enhancer.enhance(saturation)
        
        # Sharpness adjustment
        if "sharpness" in parameters:
            sharpness = max(0.0, min(2.0, parameters["sharpness"]))
            enhancer = ImageEnhance.Sharpness(enhanced_image)
            enhanced_image = enhancer.enhance(sharpness)
        
        return enhanced_image
    
    async def _create_thumbnail(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        """Create thumbnail with specified size"""
        size = parameters.get("size", (300, 300))
        
        if isinstance(size, str):
            # Parse size string like "300x300"
            width, height = map(int, size.split("x"))
            size = (width, height)
        
        # Create thumbnail maintaining aspect ratio
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        
        return thumbnail
    
    async def _crop_image(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        """Crop image to specified coordinates"""
        x = parameters.get("x", 0)
        y = parameters.get("y", 0)
        width = parameters.get("width")
        height = parameters.get("height")
        
        if not width or not height:
            raise ValueError("Width and height are required for crop operation")
        
        # Validate crop coordinates
        img_width, img_height = image.size
        if x + width > img_width or y + height > img_height:
            raise ValueError("Crop coordinates exceed image dimensions")
        
        return image.crop((x, y, x + width, y + height))
    
    async def _rotate_image(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        """Rotate image by specified angle"""
        angle = parameters.get("angle", 0)
        expand = parameters.get("expand", True)
        fillcolor = parameters.get("fillcolor", (255, 255, 255))
        
        return image.rotate(angle, expand=expand, fillcolor=fillcolor)
    
    async def _apply_filter(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        """Apply image filters"""
        filter_type = parameters.get("filter_type", "").lower()
        
        if filter_type == "blur":
            radius = parameters.get("radius", 1)
            return image.filter(ImageFilter.GaussianBlur(radius=radius))
        elif filter_type == "sharpen":
            return image.filter(ImageFilter.SHARPEN)
        elif filter_type == "edge_enhance":
            return image.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_type == "emboss":
            return image.filter(ImageFilter.EMBOSS)
        elif filter_type == "find_edges":
            return image.filter(ImageFilter.FIND_EDGES)
        else:
            # No filter applied
            return image
    
    def _fix_orientation(self, image: Image.Image) -> Image.Image:
        """Fix image orientation based on EXIF data"""
        try:
            exif = image.getexif()
            if exif:
                orientation = exif.get(274)  # Orientation tag
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, TypeError):
            # No EXIF data or orientation info
            pass
        
        return image
    
    def _get_save_kwargs(self, format: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get format-specific save parameters"""
        kwargs = {}
        
        if format.upper() == "JPEG":
            kwargs["quality"] = parameters.get("quality", self.default_quality)
            kwargs["optimize"] = parameters.get("optimize", True)
            kwargs["progressive"] = parameters.get("progressive", False)
        
        elif format.upper() == "PNG":
            kwargs["optimize"] = parameters.get("optimize", True)
            kwargs["compress_level"] = parameters.get("compress_level", 6)
        
        elif format.upper() == "WEBP":
            kwargs["quality"] = parameters.get("quality", self.default_quality)
            kwargs["method"] = parameters.get("method", 4)
            kwargs["lossless"] = parameters.get("lossless", False)
        
        return kwargs
    
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image properties and extract metadata"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Basic properties
            analysis = {
                "dimensions": image.size,
                "format": image.format,
                "mode": image.mode,
                "size_bytes": len(image_data),
                "has_transparency": image.mode in ("RGBA", "LA") or "transparency" in image.info
            }
            
            # EXIF data
            try:
                exif = image.getexif()
                if exif:
                    analysis["exif"] = {
                        ExifTags.TAGS.get(tag, str(tag)): str(value)
                        for tag, value in exif.items()
                        if isinstance(value, (str, int, float))
                    }
            except (AttributeError, KeyError):
                analysis["exif"] = {}
            
            # Color analysis
            analysis["colors"] = await self._analyze_colors(image)
            
            # Quality assessment
            analysis["quality_score"] = await self._assess_quality(image)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_colors(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze color properties of the image"""
        # Convert to RGB if necessary
        if image.mode != "RGB":
            rgb_image = image.convert("RGB")
        else:
            rgb_image = image
        
        # Get dominant colors
        colors = rgb_image.getcolors(maxcolors=256*256*256)
        if colors:
            # Sort by frequency and get top colors
            colors.sort(reverse=True)
            dominant_colors = [color[1] for color in colors[:5]]
        else:
            dominant_colors = []
        
        # Calculate average color
        np_image = np.array(rgb_image)
        avg_color = np.mean(np_image.reshape(-1, 3), axis=0).astype(int).tolist()
        
        return {
            "dominant_colors": dominant_colors,
            "average_color": avg_color,
            "is_grayscale": len(set(avg_color)) == 1
        }
    
    async def _assess_quality(self, image: Image.Image) -> float:
        """Assess image quality using basic metrics"""
        # Convert to OpenCV format for analysis
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Calculate sharpness using Laplacian variance
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Normalize to 0-1 scale (rough estimate)
        sharpness_score = min(1.0, laplacian_var / 1000.0)
        
        return sharpness_score
    
    async def generate_responsive_variants(self, image_data: bytes, 
                                         sizes: Optional[List[Tuple[int, int]]] = None) -> Dict[str, bytes]:
        """Generate multiple responsive image variants"""
        if sizes is None:
            sizes = [(150, 150), (300, 300), (600, 600), (1200, 1200)]
        
        variants = {}
        
        for width, height in sizes:
            parameters = {
                "width": width,
                "height": height,
                "maintain_aspect_ratio": True,
                "quality": 85,
                "optimize": True
            }
            
            result = await self.process_image(image_data, "resize", parameters)
            
            if result["success"]:
                variant_name = f"{width}x{height}"
                variants[variant_name] = result["data"]
        
        return variants


# Global image processor instance
image_processor = ImageProcessor()
