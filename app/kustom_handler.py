"""
Universal handler for KLWP, KLCK, and KWGT presets
"""

import json
import os
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class KustomHandler:
    """Handles all Kustom preset types (KLWP, KLCK, KWGT)."""
    
    PRESET_TYPES = {
        'klwp': {
            'extension': '.klwp',
            'base_dir': '/storage/emulated/0/Kustom/wallpapers',
            'app_name': 'Live Wallpaper',
            'typical_size': (1080, 1920)
        },
        'klck': {
            'extension': '.klck',
            'base_dir': '/storage/emulated/0/Kustom/lockscreens',
            'app_name': 'Lock Screen',
            'typical_size': (1080, 1920)
        },
        'kwgt': {
            'extension': '.kwgt',
            'base_dir': '/storage/emulated/0/Kustom/widgets',
            'app_name': 'Widget',
            'typical_size': (400, 200)  # Variable
        }
    }
    
    def __init__(self, preset_type='klwp'):
        """
        Initialize handler for a specific Kustom type.
        
        Args:
            preset_type: 'klwp', 'klck', or 'kwgt'
        """
        if preset_type not in self.PRESET_TYPES:
            raise ValueError(f"Invalid preset type: {preset_type}")
        
        self.preset_type = preset_type
        self.config = self.PRESET_TYPES[preset_type]
        self.presets_dir = Path(self.config['base_dir'])
        self._cache = {}
    
    def list_presets(self) -> List[Dict[str, Any]]:
        """
        List all presets of this type.
        
        Returns:
            List of preset info dicts with name, path, size
        """
        if not self.presets_dir.exists():
            return []
        
        presets = []
        ext = self.config['extension']
        
        for preset_file in self.presets_dir.glob(f'*{ext}'):
            presets.append({
                'name': preset_file.stem,
                'filename': preset_file.name,
                'path': str(preset_file),
                'size': preset_file.stat().st_size,
                'type': self.preset_type
            })
        
        return sorted(presets, key=lambda x: x['name'].lower())
    
    def read_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Read and parse a preset file.
        
        Args:
            preset_name: Name of preset (with or without extension)
        
        Returns:
            Parsed preset JSON data
        """
        if not preset_name.endswith(self.config['extension']):
            preset_name += self.config['extension']
        
        preset_path = self.presets_dir / preset_name
        
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {preset_path}")
        
        with zipfile.ZipFile(preset_path, 'r') as zf:
            if 'preset.json' not in zf.namelist():
                raise ValueError(f"No preset.json found in {preset_name}")
            
            with zf.open('preset.json') as f:
                data = json.load(f)
        
        self._cache[preset_name] = {'data': data, 'modified': False}
        return data
    
    def save_preset(self, preset_name: str, data: Dict[str, Any],
                   backup: bool = True) -> str:
        """
        Save preset data back to file.
        
        Args:
            preset_name: Name of preset
            data: Modified preset data
            backup: Whether to create backup first
        
        Returns:
            Path to saved file
        """
        if not preset_name.endswith(self.config['extension']):
            preset_name += self.config['extension']
        
        preset_path = self.presets_dir / preset_name
        
        # Create backup if requested
        if backup and preset_path.exists():
            backup_path = preset_path.with_suffix(f'{self.config["extension"]}.backup')
            import shutil
            shutil.copy2(preset_path, backup_path)
        
        # Create new ZIP with modified preset.json
        temp_path = preset_path.with_suffix('.tmp')
        
        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Write modified preset.json
            zf.writestr('preset.json', json.dumps(data, indent=2))
            
            # Copy other files from original if it exists
            if preset_path.exists():
                with zipfile.ZipFile(preset_path, 'r') as old_zf:
                    for item in old_zf.namelist():
                        if item != 'preset.json':
                            zf.writestr(item, old_zf.read(item))
        
        # Replace original
        temp_path.replace(preset_path)
        
        return str(preset_path)
    
    def create_matching_preset(self, source_name: str, target_type: str,
                               target_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a matching preset in a different Kustom format.
        
        Args:
            source_name: Source preset name
            target_type: 'klwp', 'klck', or 'kwgt'
            target_name: Optional name for new preset
        
        Returns:
            New preset data structure
        """
        # Read source preset
        source_data = self.read_preset(source_name)
        
        # Extract visual style
        style = self._extract_visual_style(source_data)
        
        # Create target preset structure
        target_config = self.PRESET_TYPES[target_type]
        
        # Generate appropriate structure for target type
        if target_type == 'klck':
            target_data = self._create_lock_screen_layout(style)
        elif target_type == 'kwgt':
            target_data = self._create_widget_layout(style)
        else:  # klwp
            target_data = self._create_wallpaper_layout(style)
        
        return target_data
    
    def _extract_visual_style(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract color palette, fonts, and design patterns from preset."""
        style = {
            'colors': set(),
            'fonts': set(),
            'shadows': [],
            'background': None
        }
        
        def traverse(obj, depth=0):
            if depth > 15:
                return
            
            if isinstance(obj, dict):
                # Extract colors
                for key in ['color', 'bgcolor', 'stroke_color', 'shadow_color']:
                    if key in obj and obj[key]:
                        style['colors'].add(obj[key])
                
                # Extract fonts
                if 'font' in obj:
                    style['fonts'].add(obj['font'])
                
                # Extract shadow settings
                if 'shadow' in obj and obj['shadow']:
                    style['shadows'].append(obj['shadow'])
                
                # Recurse
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        traverse(value, depth + 1)
            
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item, depth + 1)
        
        traverse(data)
        
        # Convert sets to lists
        style['colors'] = list(style['colors'])
        style['fonts'] = list(style['fonts'])
        
        return style
    
    def _create_lock_screen_layout(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Create KLCK preset structure with the given style."""
        # Simplified KLCK structure focusing on essentials
        return {
            'version': 1,
            'items': [
                {
                    'type': 'TEXT',
                    'text': '$df(hh:mm)$',  # Time
                    'font_size': 72,
                    'color': style['colors'][0] if style['colors'] else '#FFFFFF',
                    'font': style['fonts'][0] if style['fonts'] else 'Roboto',
                    'position': {'x': 'center', 'y': 300}
                },
                {
                    'type': 'TEXT',
                    'text': '$df(EEEE, MMMM d)$',  # Date
                    'font_size': 18,
                    'color': style['colors'][1] if len(style['colors']) > 1 else '#CCCCCC',
                    'position': {'x': 'center', 'y': 400}
                },
                {
                    'type': 'SHAPE',
                    'shape_type': 'arc',
                    'color': style['colors'][0] if style['colors'] else '#FFFFFF',
                    'formula': '$bi(level)$',  # Battery
                    'position': {'x': 'center', 'y': 600}
                }
            ]
        }
    
    def _create_widget_layout(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Create KWGT preset structure with the given style."""
        return {
            'version': 1,
            'width': 400,
            'height': 200,
            'items': [
                {
                    'type': 'SHAPE',
                    'shape_type': 'rectangle',
                    'color': style['colors'][0] if style['colors'] else '#333333',
                    'width': 400,
                    'height': 200,
                    'corner_radius': 20
                },
                {
                    'type': 'TEXT',
                    'text': '$df(hh:mm)$',
                    'font_size': 48,
                    'color': style['colors'][1] if len(style['colors']) > 1 else '#FFFFFF',
                    'font': style['fonts'][0] if style['fonts'] else 'Roboto',
                    'position': {'x': 'center', 'y': 'center'}
                }
            ]
        }
    
    def _create_wallpaper_layout(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Create KLWP preset structure with the given style."""
        return {
            'version': 1,
            'width': 1080,
            'height': 1920,
            'items': [
                # Background
                {
                    'type': 'SHAPE',
                    'shape_type': 'rectangle',
                    'color': style['colors'][0] if style['colors'] else '#000000',
                    'width': 1080,
                    'height': 1920
                },
                # Clock
                {
                    'type': 'TEXT',
                    'text': '$df(hh:mm)$',
                    'font_size': 96,
                    'color': style['colors'][1] if len(style['colors']) > 1 else '#FFFFFF',
                    'font': style['fonts'][0] if style['fonts'] else 'Roboto',
                    'position': {'x': 'center', 'y': 800}
                },
                # Date
                {
                    'type': 'TEXT',
                    'text': '$df(EEEE, MMMM d)$',
                    'font_size': 24,
                    'color': style['colors'][1] if len(style['colors']) > 1 else '#CCCCCC',
                    'position': {'x': 'center', 'y': 920}
                }
            ]
        }
