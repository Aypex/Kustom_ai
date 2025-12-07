"""AI Preset Generator - Creates KLWP/KLCK/KWGT presets from natural language."""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class PresetGenerator:
    """Generate Kustom presets from natural language descriptions."""

    # Theme color palettes
    THEMES = {
        'cyberpunk': {
            'colors': ['#000000', '#00FFFF', '#FF00FF', '#00FF00'],
            'font': 'Orbitron',
            'style': 'digital',
            'glow': True
        },
        'minimal': {
            'colors': ['#FFFFFF', '#000000', '#333333', '#666666'],
            'font': 'Roboto Thin',
            'style': 'clean',
            'glow': False
        },
        'neon': {
            'colors': ['#0A0A0A', '#FF006E', '#00F5FF', '#FFBE0B'],
            'font': 'Roboto',
            'style': 'bright',
            'glow': True
        },
        'dark': {
            'colors': ['#000000', '#FFFFFF', '#888888', '#444444'],
            'font': 'Roboto',
            'style': 'modern',
            'glow': False
        },
        'pastel': {
            'colors': ['#FFE5E5', '#E5F5FF', '#FFF5E5', '#E5FFE5'],
            'font': 'Roboto Light',
            'style': 'soft',
            'glow': False
        },
        'gruvbox': {
            'colors': ['#282828', '#EBDBB2', '#FB4934', '#B8BB26'],
            'font': 'Roboto',
            'style': 'retro',
            'glow': False
        }
    }

    def __init__(self):
        """Initialize preset generator."""
        self.preset_cache = {}

    def generate_from_description(self, description: str,
                                 preset_type: str = 'klwp',
                                 use_ai: bool = True) -> Dict[str, Any]:
        """
        Generate preset from natural language description.

        Args:
            description: User's description (e.g., "cyberpunk wallpaper with digital clock")
            preset_type: Type of preset ('klwp', 'klck', 'kwgt')
            use_ai: If True, use AI model; if False, use template-based generation

        Returns:
            Complete preset structure ready to save
        """
        # Try AI generation first if enabled
        if use_ai:
            try:
                from app.ai_client import create_ai_client
                client = create_ai_client()
                return client.generate_preset(description, preset_type)
            except Exception as e:
                print(f"⚠️ AI generation failed: {e}")
                print("Falling back to template-based generation...")

        # Fallback: Template-based generation
        specs = self._parse_description(description)

        # Generate based on type
        if preset_type == 'klwp':
            return self._generate_wallpaper(specs)
        elif preset_type == 'klck':
            return self._generate_lockscreen(specs)
        elif preset_type == 'kwgt':
            return self._generate_widget(specs)
        else:
            raise ValueError(f"Unknown preset type: {preset_type}")

    def _parse_description(self, description: str) -> Dict[str, Any]:
        """
        Parse natural language into structured specifications.

        Args:
            description: User description

        Returns:
            Structured specs dict
        """
        desc_lower = description.lower()

        # Detect theme
        theme = 'minimal'  # default
        for theme_name in self.THEMES:
            if theme_name in desc_lower:
                theme = theme_name
                break

        # Detect colors (hex codes)
        custom_colors = re.findall(r'#[0-9A-Fa-f]{6}', description)

        # Detect elements
        elements = []
        if any(word in desc_lower for word in ['clock', 'time']):
            elements.append('clock')
        if any(word in desc_lower for word in ['date', 'calendar']):
            elements.append('date')
        if any(word in desc_lower for word in ['weather', 'temperature']):
            elements.append('weather')
        if any(word in desc_lower for word in ['battery']):
            elements.append('battery')
        if any(word in desc_lower for word in ['music', 'player']):
            elements.append('music')

        # Default to clock if no elements specified
        if not elements:
            elements.append('clock')

        # Detect style keywords
        style_hints = {
            'digital': 'digital' in desc_lower or 'lcd' in desc_lower,
            'analog': 'analog' in desc_lower or 'traditional' in desc_lower,
            'minimal': 'minimal' in desc_lower or 'simple' in desc_lower,
            'complex': 'complex' in desc_lower or 'detailed' in desc_lower,
            'large': 'large' in desc_lower or 'big' in desc_lower,
            'small': 'small' in desc_lower or 'compact' in desc_lower,
        }

        # Build specs
        theme_config = self.THEMES[theme]
        specs = {
            'theme': theme,
            'colors': custom_colors if custom_colors else theme_config['colors'],
            'font': theme_config['font'],
            'elements': elements,
            'style': theme_config['style'],
            'glow': theme_config['glow'],
            'hints': style_hints
        }

        return specs

    def _generate_wallpaper(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate KLWP wallpaper preset."""
        preset = {
            'version': 1,
            'width': 1080,
            'height': 1920,
            'items': []
        }

        # Add background
        preset['items'].append({
            'type': 'SHAPE',
            'internal_type': 'RectModule',
            'id': 'background',
            'shape_type': 'rectangle',
            'color': specs['colors'][0],
            'width': 1080,
            'height': 1920,
            'position': {'x': 0, 'y': 0}
        })

        # Add elements
        y_offset = 800  # Starting Y position

        for element in specs['elements']:
            if element == 'clock':
                preset['items'].append(self._create_clock(specs, y_offset))
                y_offset += 120
            elif element == 'date':
                preset['items'].append(self._create_date(specs, y_offset))
                y_offset += 60
            elif element == 'weather':
                preset['items'].append(self._create_weather(specs, y_offset))
                y_offset += 80
            elif element == 'battery':
                preset['items'].append(self._create_battery(specs, y_offset))
                y_offset += 80
            elif element == 'music':
                preset['items'].append(self._create_music(specs, y_offset))
                y_offset += 100

        return preset

    def _generate_lockscreen(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate KLCK lock screen preset."""
        preset = {
            'version': 1,
            'width': 1080,
            'height': 1920,
            'items': []
        }

        # Background
        preset['items'].append({
            'type': 'SHAPE',
            'id': 'background',
            'shape_type': 'rectangle',
            'color': specs['colors'][0],
            'width': 1080,
            'height': 1920,
            'position': {'x': 0, 'y': 0}
        })

        # Large clock for lock screen
        preset['items'].append(self._create_clock(specs, 700, size=100))

        # Date below
        preset['items'].append(self._create_date(specs, 850))

        # Battery indicator
        preset['items'].append(self._create_battery(specs, 1600))

        return preset

    def _generate_widget(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate KWGT widget preset."""
        preset = {
            'version': 1,
            'width': 400,
            'height': 200,
            'items': []
        }

        # Background card
        preset['items'].append({
            'type': 'SHAPE',
            'id': 'widget_bg',
            'shape_type': 'rectangle',
            'color': specs['colors'][0],
            'width': 400,
            'height': 200,
            'corner_radius': 20,
            'position': {'x': 0, 'y': 0}
        })

        # Compact clock
        preset['items'].append(self._create_clock(specs, 80, size=48, centered=True))

        return preset

    def _create_clock(self, specs: Dict[str, Any], y_pos: int,
                     size: int = 96, centered: bool = True) -> Dict[str, Any]:
        """Create clock element."""
        clock = {
            'type': 'TEXT',
            'id': 'clock',
            'text': '$df(hh:mm)$',
            'font_size': size,
            'color': specs['colors'][1] if len(specs['colors']) > 1 else '#FFFFFF',
            'font': specs['font'],
            'position': {
                'x': 'center' if centered else 540,
                'y': y_pos
            },
            'align': 'center' if centered else 'left'
        }

        # Add glow effect if theme supports it
        if specs['glow']:
            clock['shadow'] = {
                'color': specs['colors'][1] if len(specs['colors']) > 1 else '#FFFFFF',
                'radius': 20,
                'dx': 0,
                'dy': 0
            }

        return clock

    def _create_date(self, specs: Dict[str, Any], y_pos: int) -> Dict[str, Any]:
        """Create date element."""
        return {
            'type': 'TEXT',
            'id': 'date',
            'text': '$df(EEEE, MMMM d)$',
            'font_size': 24,
            'color': specs['colors'][2] if len(specs['colors']) > 2 else '#CCCCCC',
            'font': specs['font'],
            'position': {
                'x': 'center',
                'y': y_pos
            },
            'align': 'center'
        }

    def _create_weather(self, specs: Dict[str, Any], y_pos: int) -> Dict[str, Any]:
        """Create weather element."""
        return {
            'type': 'TEXT',
            'id': 'weather',
            'text': '$wi(temp)$°',
            'font_size': 36,
            'color': specs['colors'][1] if len(specs['colors']) > 1 else '#FFFFFF',
            'font': specs['font'],
            'position': {
                'x': 'center',
                'y': y_pos
            },
            'align': 'center'
        }

    def _create_battery(self, specs: Dict[str, Any], y_pos: int) -> Dict[str, Any]:
        """Create battery indicator."""
        return {
            'type': 'SHAPE',
            'id': 'battery',
            'shape_type': 'arc',
            'color': specs['colors'][1] if len(specs['colors']) > 1 else '#FFFFFF',
            'formula': '$bi(level)$',
            'width': 100,
            'height': 100,
            'position': {
                'x': 'center',
                'y': y_pos
            }
        }

    def _create_music(self, specs: Dict[str, Any], y_pos: int) -> Dict[str, Any]:
        """Create music player element."""
        return {
            'type': 'TEXT',
            'id': 'music',
            'text': '$mi(title)$',
            'font_size': 20,
            'color': specs['colors'][1] if len(specs['colors']) > 1 else '#FFFFFF',
            'font': specs['font'],
            'position': {
                'x': 'center',
                'y': y_pos
            },
            'align': 'center',
            'max_lines': 1
        }

    def extract_theme_colors(self, preset_data: Dict[str, Any]) -> List[str]:
        """
        Extract color palette from a preset for theme matching.

        Args:
            preset_data: Parsed preset structure

        Returns:
            List of hex color codes used in preset
        """
        colors = set()

        def traverse(obj):
            if isinstance(obj, dict):
                # Extract colors
                for key in ['color', 'bgcolor', 'stroke_color', 'shadow_color']:
                    if key in obj and obj[key]:
                        colors.add(obj[key])

                # Recurse
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        traverse(value)

            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)

        traverse(preset_data)
        return sorted(list(colors))

    def generate_matching_preset(self, source_preset: Dict[str, Any],
                                 target_type: str) -> Dict[str, Any]:
        """
        Generate a matching preset in different format.

        Args:
            source_preset: Source preset data
            target_type: Target type ('klwp', 'klck', 'kwgt')

        Returns:
            New preset matching the source style
        """
        # Extract style from source
        colors = self.extract_theme_colors(source_preset)

        # Create specs matching source
        specs = {
            'theme': 'custom',
            'colors': colors if colors else ['#000000', '#FFFFFF'],
            'font': 'Roboto',
            'elements': ['clock', 'date'],
            'style': 'modern',
            'glow': False,
            'hints': {}
        }

        # Generate matching preset
        if target_type == 'klwp':
            return self._generate_wallpaper(specs)
        elif target_type == 'klck':
            return self._generate_lockscreen(specs)
        elif target_type == 'kwgt':
            return self._generate_widget(specs)
        else:
            raise ValueError(f"Unknown target type: {target_type}")

    def edit_preset(self, preset: Dict[str, Any], command: str) -> tuple[Dict[str, Any], str]:
        """
        Edit preset based on natural language command.

        Args:
            preset: Current preset JSON
            command: Natural language edit

        Returns:
            (updated_preset, edit_type) - edit_type for molt animation
        """
        cmd = command.lower()
        items = preset.get('items', [])
        edit_type = "transform"

        # Color changes
        if any(w in cmd for w in ['color', 'blue', 'red', 'green', 'orange', 'purple']):
            color_map = {'blue': '#00D9FF', 'red': '#FF4136', 'green': '#2ECC40',
                        'orange': '#FF851B', 'purple': '#B10DC9', 'pink': '#FF00FF'}
            new_color = next((v for k, v in color_map.items() if k in cmd), '#00FFFF')

            for item in items:
                if item.get('id') != 'background' and 'color' in item:
                    item['color'] = new_color
            edit_type = "color"

        # Size changes
        elif any(w in cmd for w in ['bigger', 'smaller', 'larger']):
            mult = 1.3 if 'bigger' in cmd or 'larger' in cmd else 0.7
            for item in items:
                if item.get('type') == 'TEXT':
                    item['font_size'] = int(item.get('font_size', 24) * mult)
                elif item.get('type') == 'SHAPE' and item.get('id') != 'background':
                    item['width'] = int(item.get('width', 100) * mult)
                    item['height'] = int(item.get('height', 100) * mult)
            edit_type = "scale"

        # Add elements
        elif 'add' in cmd:
            if 'battery' in cmd:
                items.append(self._create_battery(
                    {'colors': [preset['items'][0]['color'], '#00FFFF']}, 1600))
                edit_type = "birth"

        # Remove elements
        elif 'remove' in cmd or 'delete' in cmd:
            target = None
            if 'clock' in cmd: target = 'clock'
            elif 'date' in cmd: target = 'date'
            elif 'battery' in cmd: target = 'battery'

            if target:
                items = [i for i in items if i.get('id') != target]
                edit_type = "fade"

        preset['items'] = items
        return preset, edit_type
