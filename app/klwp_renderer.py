"""
Simple KLWP Preview Renderer

Renders KLWP preset JSON to visual preview images.
This is a simplified renderer for preview purposes - doesn't need full KLWP accuracy,
just needs to look good enough to show molting effects.

Uses PIL/Pillow for image generation.
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List, Tuple, Optional
import os
from pathlib import Path


class KLWPRenderer:
    """Render KLWP preset JSON to preview images."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize renderer.

        Args:
            cache_dir: Directory to cache rendered previews
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path("/tmp/chameleon_previews")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Default dimensions (mobile portrait)
        self.default_width = 360
        self.default_height = 640

    def render_preset(self, preset_data: Dict[str, Any],
                     width: Optional[int] = None,
                     height: Optional[int] = None,
                     output_path: Optional[str] = None) -> str:
        """
        Render KLWP preset to image.

        Args:
            preset_data: Parsed KLWP JSON
            width: Output width (defaults to 360)
            height: Output height (defaults to 640)
            output_path: Where to save image (auto-generated if None)

        Returns:
            Path to rendered image file
        """
        width = width or self.default_width
        height = height or self.default_height

        # Create canvas
        canvas = Image.new('RGB', (width, height), color='#000000')
        draw = ImageDraw.Draw(canvas)

        # Extract items from preset
        items = preset_data.get('items', [])

        # Render each item
        for item in items:
            self._render_item(canvas, draw, item, width, height)

        # Save to file
        if not output_path:
            # Generate cache filename
            import hashlib
            preset_hash = hashlib.md5(str(preset_data).encode()).hexdigest()[:8]
            output_path = self.cache_dir / f"preview_{preset_hash}.png"

        canvas.save(str(output_path))
        return str(output_path)

    def _render_item(self, canvas: Image.Image, draw: ImageDraw.Draw,
                    item: Dict[str, Any], canvas_width: int, canvas_height: int):
        """
        Render a single KLWP item.

        Args:
            canvas: PIL Image canvas
            draw: PIL ImageDraw instance
            item: Item data from KLWP JSON
            canvas_width: Canvas width
            canvas_height: Canvas height
        """
        item_type = item.get('type', '').upper()

        if item_type == 'SHAPE':
            self._render_shape(draw, item, canvas_width, canvas_height)
        elif item_type == 'TEXT':
            self._render_text(draw, item, canvas_width, canvas_height)
        elif item_type == 'IMAGE':
            self._render_image(canvas, item, canvas_width, canvas_height)

    def _render_shape(self, draw: ImageDraw.Draw, item: Dict[str, Any],
                     canvas_width: int, canvas_height: int):
        """Render SHAPE element."""
        shape_type = item.get('shape_type', 'rectangle')
        color = item.get('color', '#FFFFFF')

        # Parse position
        position = item.get('position', {'x': 0, 'y': 0})
        x = self._parse_position(position.get('x', 0), canvas_width)
        y = self._parse_position(position.get('y', 0), canvas_height)

        # Parse size
        w = item.get('width', 100)
        h = item.get('height', 100)

        # Convert hex color to RGB tuple
        rgb_color = self._hex_to_rgb(color)

        if shape_type == 'rectangle':
            draw.rectangle(
                [x, y, x + w, y + h],
                fill=rgb_color
            )
        elif shape_type == 'circle':
            draw.ellipse(
                [x, y, x + w, y + h],
                fill=rgb_color
            )
        elif shape_type == 'arc':
            # Simple arc/progress bar
            draw.arc(
                [x, y, x + w, y + h],
                start=0,
                end=270,  # 75% progress
                fill=rgb_color,
                width=5
            )

    def _render_text(self, draw: ImageDraw.Draw, item: Dict[str, Any],
                    canvas_width: int, canvas_height: int):
        """Render TEXT element."""
        text = item.get('text', '')
        color = item.get('color', '#FFFFFF')
        font_size = item.get('font_size', 24)

        # Parse position
        position = item.get('position', {'x': 'center', 'y': 300})
        x = self._parse_position(position.get('x', 'center'), canvas_width)
        y = self._parse_position(position.get('y', 300), canvas_height)

        # Convert hex color
        rgb_color = self._hex_to_rgb(color)

        # Try to load font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Handle center alignment
        if position.get('x') == 'center':
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (canvas_width - text_width) // 2

        # Draw text
        draw.text((x, y), text, fill=rgb_color, font=font)

    def _render_image(self, canvas: Image.Image, item: Dict[str, Any],
                     canvas_width: int, canvas_height: int):
        """Render IMAGE element (placeholder for now)."""
        # For preview purposes, just draw a colored rectangle as placeholder
        position = item.get('position', {'x': 0, 'y': 0})
        x = self._parse_position(position.get('x', 0), canvas_width)
        y = self._parse_position(position.get('y', 0), canvas_height)

        w = item.get('width', 50)
        h = item.get('height', 50)

        # Draw placeholder box
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([x, y, x + w, y + h], outline='#888888', width=2)

    def _parse_position(self, value, canvas_size: int) -> int:
        """
        Parse position value (can be int, 'center', or percentage).

        Args:
            value: Position value
            canvas_size: Canvas dimension (width or height)

        Returns:
            Pixel position
        """
        if value == 'center':
            return canvas_size // 2

        if isinstance(value, str):
            if '%' in value:
                percent = float(value.replace('%', ''))
                return int(canvas_size * (percent / 100.0))
            return int(value)

        return int(value)

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')

        # Handle ARGB (8 digits)
        if len(hex_color) == 8:
            hex_color = hex_color[2:]  # Skip alpha

        # Handle RGB (6 digits)
        if len(hex_color) == 6:
            return (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16)
            )

        # Fallback to white
        return (255, 255, 255)


def generate_example_preset(preset_type: str = 'klwp',
                           theme: str = 'cyberpunk') -> Dict[str, Any]:
    """
    Generate example preset data for testing.

    Args:
        preset_type: 'klwp', 'klck', or 'kwgt'
        theme: 'cyberpunk', 'minimal', 'dark', etc.

    Returns:
        Preset data dict
    """
    themes = {
        'cyberpunk': {
            'bg': '#000000',
            'primary': '#00FFFF',
            'secondary': '#FF00FF',
            'accent': '#00FF00'
        },
        'minimal': {
            'bg': '#FFFFFF',
            'primary': '#000000',
            'secondary': '#666666',
            'accent': '#333333'
        },
        'dark': {
            'bg': '#0D0D0D',
            'primary': '#FFFFFF',
            'secondary': '#888888',
            'accent': '#00D9FF'
        },
        'neon': {
            'bg': '#0A0A0A',
            'primary': '#FF006E',
            'secondary': '#00F5FF',
            'accent': '#FFBE0B'
        }
    }

    colors = themes.get(theme, themes['cyberpunk'])

    if preset_type == 'klwp':
        return {
            'version': 1,
            'width': 360,
            'height': 640,
            'items': [
                # Background
                {
                    'type': 'SHAPE',
                    'id': 'background',
                    'shape_type': 'rectangle',
                    'color': colors['bg'],
                    'width': 360,
                    'height': 640,
                    'position': {'x': 0, 'y': 0}
                },
                # Clock
                {
                    'type': 'TEXT',
                    'id': 'clock',
                    'text': '23:45',
                    'font_size': 72,
                    'color': colors['primary'],
                    'position': {'x': 'center', 'y': 200}
                },
                # Date
                {
                    'type': 'TEXT',
                    'id': 'date',
                    'text': 'Friday, December 7',
                    'font_size': 20,
                    'color': colors['secondary'],
                    'position': {'x': 'center', 'y': 290}
                },
                # Battery arc
                {
                    'type': 'SHAPE',
                    'id': 'battery',
                    'shape_type': 'arc',
                    'color': colors['accent'],
                    'width': 100,
                    'height': 100,
                    'position': {'x': 130, 'y': 400}
                }
            ]
        }

    elif preset_type == 'klck':
        return {
            'version': 1,
            'width': 360,
            'height': 640,
            'items': [
                # Background
                {
                    'type': 'SHAPE',
                    'id': 'background',
                    'shape_type': 'rectangle',
                    'color': colors['bg'],
                    'width': 360,
                    'height': 640,
                    'position': {'x': 0, 'y': 0}
                },
                # Large clock for lock screen
                {
                    'type': 'TEXT',
                    'id': 'clock',
                    'text': '23:45',
                    'font_size': 96,
                    'color': colors['primary'],
                    'position': {'x': 'center', 'y': 250}
                },
                # Date
                {
                    'type': 'TEXT',
                    'id': 'date',
                    'text': 'Friday, December 7',
                    'font_size': 24,
                    'color': colors['secondary'],
                    'position': {'x': 'center', 'y': 370}
                }
            ]
        }

    return {}


# Test/Example usage
if __name__ == "__main__":
    print("🦎 KLWP RENDERER TEST\n")

    renderer = KLWPRenderer()

    # Generate example presets
    themes = ['cyberpunk', 'minimal', 'dark', 'neon']

    for theme in themes:
        preset = generate_example_preset('klwp', theme)
        output = renderer.render_preset(preset)
        print(f"✅ Rendered {theme} theme: {output}")

    print("\n✨ Preview images generated!")
    print(f"📁 Check: {renderer.cache_dir}")
