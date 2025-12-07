"""
Theme Matcher - Extract colors from presets and apply to app theme.

This is the magic that makes Chameleon "become part of your ecosystem."
"""

from typing import Dict, List, Tuple, Optional
import re
from pathlib import Path


class ThemeMatcher:
    """Extract theme colors from presets and apply to app interface."""

    def __init__(self):
        """Initialize theme matcher."""
        self.current_theme = None

    def extract_color_palette(self, preset_data: Dict) -> Dict[str, str]:
        """
        Extract a complete color palette from a preset.

        Args:
            preset_data: Parsed preset structure

        Returns:
            Dict with named colors (primary, secondary, background, etc.)
        """
        # Collect all colors from preset
        all_colors = self._collect_all_colors(preset_data)

        if not all_colors:
            return self._get_default_palette()

        # Analyze and categorize colors
        palette = self._categorize_colors(all_colors)

        return palette

    def _collect_all_colors(self, preset_data: Dict) -> List[str]:
        """
        Recursively collect all color hex codes from preset.

        Args:
            preset_data: Preset data structure

        Returns:
            List of unique hex color codes
        """
        colors = set()

        def traverse(obj, depth=0):
            """Recursively traverse and extract colors."""
            if depth > 20:  # Prevent infinite recursion
                return

            if isinstance(obj, dict):
                # Extract color fields
                for key in ['color', 'bgcolor', 'background_color', 'stroke_color',
                           'shadow_color', 'text_color', 'fill_color']:
                    if key in obj and obj[key]:
                        color = obj[key]
                        if isinstance(color, str) and color.startswith('#'):
                            colors.add(color.upper())

                # Recurse through values
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        traverse(value, depth + 1)

            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        traverse(item, depth + 1)

        traverse(preset_data)
        return list(colors)

    def _categorize_colors(self, colors: List[str]) -> Dict[str, str]:
        """
        Categorize colors into theme roles (primary, secondary, background, etc.).

        Args:
            colors: List of hex color codes

        Returns:
            Dict mapping role names to colors
        """
        if not colors:
            return self._get_default_palette()

        # Convert to RGB for analysis
        color_rgb = [(c, self._hex_to_rgb(c)) for c in colors]

        # Sort by brightness
        color_rgb.sort(key=lambda x: self._get_brightness(x[1]))

        # Categorize
        palette = {}

        # Background: darkest or lightest color
        if self._get_brightness(color_rgb[0][1]) < 128:
            # Dark theme
            palette['background'] = color_rgb[0][0]  # Darkest
            palette['surface'] = self._lighten_color(color_rgb[0][0], 0.1)

            # Find brightest color for primary
            palette['primary'] = color_rgb[-1][0]  # Brightest

            # Find mid-brightness accent
            mid_idx = len(color_rgb) // 2
            palette['secondary'] = color_rgb[mid_idx][0] if len(color_rgb) > 2 else color_rgb[-1][0]

            # Text colors
            palette['text_primary'] = '#FFFFFF'
            palette['text_secondary'] = '#B0B0B0'

        else:
            # Light theme
            palette['background'] = color_rgb[-1][0]  # Lightest
            palette['surface'] = self._darken_color(color_rgb[-1][0], 0.1)

            # Darkest for primary
            palette['primary'] = color_rgb[0][0]

            # Mid-brightness accent
            mid_idx = len(color_rgb) // 2
            palette['secondary'] = color_rgb[mid_idx][0] if len(color_rgb) > 2 else color_rgb[0][0]

            # Text colors
            palette['text_primary'] = '#000000'
            palette['text_secondary'] = '#505050'

        # Ensure we have accent color (brightest saturated color)
        palette['accent'] = self._find_most_saturated(color_rgb)

        return palette

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')

        # Handle ARGB format (8 digits)
        if len(hex_color) == 8:
            hex_color = hex_color[2:]  # Skip alpha

        # Handle RGB format (6 digits)
        if len(hex_color) == 6:
            return (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16)
            )

        # Fallback
        return (128, 128, 128)

    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color."""
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    def _get_brightness(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate perceived brightness of RGB color (0-255)."""
        # Use perceived brightness formula
        return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])

    def _get_saturation(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate saturation of RGB color (0-1)."""
        r, g, b = [x / 255.0 for x in rgb]
        max_c = max(r, g, b)
        min_c = min(r, g, b)

        if max_c == 0:
            return 0

        return (max_c - min_c) / max_c

    def _find_most_saturated(self, color_rgb: List[Tuple[str, Tuple[int, int, int]]]) -> str:
        """Find the most saturated color from list."""
        if not color_rgb:
            return '#00FFFF'  # Default accent

        most_saturated = max(
            color_rgb,
            key=lambda x: self._get_saturation(x[1])
        )

        return most_saturated[0]

    def _lighten_color(self, hex_color: str, amount: float) -> str:
        """Lighten a hex color by amount (0-1)."""
        rgb = self._hex_to_rgb(hex_color)
        new_rgb = tuple(min(255, int(c + (255 - c) * amount)) for c in rgb)
        return self._rgb_to_hex(new_rgb)

    def _darken_color(self, hex_color: str, amount: float) -> str:
        """Darken a hex color by amount (0-1)."""
        rgb = self._hex_to_rgb(hex_color)
        new_rgb = tuple(max(0, int(c * (1 - amount))) for c in rgb)
        return self._rgb_to_hex(new_rgb)

    def _get_default_palette(self) -> Dict[str, str]:
        """Get default color palette."""
        return {
            'primary': '#2196F3',
            'secondary': '#00BCD4',
            'accent': '#FF4081',
            'background': '#121212',
            'surface': '#1E1E1E',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B0B0B0'
        }

    def apply_theme_to_kivy(self, palette: Dict[str, str]) -> None:
        """
        Apply color palette to Kivy app theme.

        Args:
            palette: Color palette dict
        """
        try:
            from kivymd.app import MDApp

            app = MDApp.get_running_app()

            if not app:
                return

            # Convert hex to RGB normalized (0-1)
            def hex_to_kivy_color(hex_color: str) -> List[float]:
                rgb = self._hex_to_rgb(hex_color)
                return [c / 255.0 for c in rgb] + [1.0]  # Add alpha

            # Apply theme
            theme_style = 'Dark' if self._get_brightness(
                self._hex_to_rgb(palette['background'])
            ) < 128 else 'Light'

            app.theme_cls.theme_style = theme_style

            # Map primary color
            app.theme_cls.primary_palette = self._closest_md_palette(palette['primary'])

            # Store current theme
            self.current_theme = palette

        except Exception as e:
            print(f"Error applying theme: {e}")

    def _closest_md_palette(self, hex_color: str) -> str:
        """
        Find closest Material Design palette name for a color.

        Args:
            hex_color: Hex color code

        Returns:
            MD palette name (e.g., 'Blue', 'Red', etc.)
        """
        # MD color names and representative hex values
        md_colors = {
            'Red': '#F44336',
            'Pink': '#E91E63',
            'Purple': '#9C27B0',
            'DeepPurple': '#673AB7',
            'Indigo': '#3F51B5',
            'Blue': '#2196F3',
            'LightBlue': '#03A9F4',
            'Cyan': '#00BCD4',
            'Teal': '#009688',
            'Green': '#4CAF50',
            'LightGreen': '#8BC34A',
            'Lime': '#CDDC39',
            'Yellow': '#FFEB3B',
            'Amber': '#FFC107',
            'Orange': '#FF9800',
            'DeepOrange': '#FF5722',
            'Brown': '#795548',
            'Gray': '#9E9E9E',
            'BlueGray': '#607D8B'
        }

        # Calculate distance to each MD color
        target_rgb = self._hex_to_rgb(hex_color)

        def color_distance(rgb1, rgb2):
            """Calculate Euclidean distance between two RGB colors."""
            return sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5

        closest = min(
            md_colors.items(),
            key=lambda item: color_distance(target_rgb, self._hex_to_rgb(item[1]))
        )

        return closest[0]

    def create_smooth_transition(self, from_palette: Dict[str, str],
                                 to_palette: Dict[str, str],
                                 duration: float = 0.5) -> None:
        """
        Create a smooth animated transition between color palettes.

        Args:
            from_palette: Starting palette
            to_palette: Target palette
            duration: Transition duration in seconds
        """
        # TODO: Implement animated color transition
        # For now, just apply directly
        self.apply_theme_to_kivy(to_palette)

    def save_theme_preset(self, preset_name: str, palette: Dict[str, str]) -> None:
        """
        Save a color palette as a theme preset.

        Args:
            preset_name: Name for the theme
            palette: Color palette to save
        """
        from app.secure_storage import SecureStorage

        storage = SecureStorage()

        # Save palette
        storage.set(f'theme_{preset_name}', palette)

    def load_theme_preset(self, preset_name: str) -> Optional[Dict[str, str]]:
        """
        Load a saved theme preset.

        Args:
            preset_name: Name of theme to load

        Returns:
            Color palette or None
        """
        from app.secure_storage import SecureStorage

        storage = SecureStorage()
        return storage.get(f'theme_{preset_name}', None)

    def get_saved_themes(self) -> List[str]:
        """
        Get list of saved theme names.

        Returns:
            List of theme names
        """
        from app.secure_storage import SecureStorage

        storage = SecureStorage()

        # Get all keys starting with 'theme_'
        all_keys = storage.storage.keys() if hasattr(storage.storage, 'keys') else []

        themes = [
            key.replace('theme_', '')
            for key in all_keys
            if key.startswith('theme_')
        ]

        return themes
