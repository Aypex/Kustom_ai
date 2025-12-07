"""Kustom plugin for KLWP/KLCK/KWGT support."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .plugin_interface import CustomizationPlugin
from ..kustom_handler import KustomHandler


class KustomPlugin(CustomizationPlugin):
    """Plugin for Kustom apps (KLWP, KLCK, KWGT)."""

    def __init__(self):
        """Initialize Kustom plugin."""
        self.handlers = {
            'klwp': KustomHandler('klwp'),
            'klck': KustomHandler('klck'),
            'kwgt': KustomHandler('kwgt')
        }
        self.current_type = 'klwp'  # Default
        self._cache: Dict[str, Any] = {}

    def get_plugin_name(self) -> str:
        """Return plugin name."""
        return "Kustom Suite Support"

    def get_plugin_version(self) -> str:
        """Return plugin version."""
        return "1.0.0"

    def get_supported_app(self) -> str:
        """Return supported app name."""
        return "Kustom (KLWP/KLCK/KWGT)"

    def get_app_package(self) -> str:
        """Return Android package name."""
        return "org.kustom.wallpaper"  # KLWP package (main one)

    def is_app_installed(self) -> bool:
        """Check if Kustom apps are installed."""
        # On Android, check via package manager
        # For now, check if directories exist
        for handler in self.handlers.values():
            if handler.presets_dir.exists():
                return True
        return False

    def get_config_directory(self) -> Path:
        """Return config directory for current type."""
        return self.handlers[self.current_type].presets_dir

    def set_preset_type(self, preset_type: str) -> None:
        """
        Set current preset type (klwp, klck, or kwgt).

        Args:
            preset_type: Type to switch to
        """
        if preset_type in self.handlers:
            self.current_type = preset_type

    def list_configs(self) -> List[Dict[str, Any]]:
        """List all Kustom presets across all types."""
        configs = []
        for preset_type, handler in self.handlers.items():
            presets = handler.list_presets()
            configs.extend(presets)
        return configs

    def read_config(self, config_name: str) -> Dict[str, Any]:
        """
        Read Kustom preset.

        Args:
            config_name: Preset filename

        Returns:
            Parsed preset data
        """
        # Determine type from extension
        if config_name.endswith('.klwp'):
            handler = self.handlers['klwp']
        elif config_name.endswith('.klck'):
            handler = self.handlers['klck']
        elif config_name.endswith('.kwgt'):
            handler = self.handlers['kwgt']
        else:
            handler = self.handlers[self.current_type]

        data = handler.read_preset(config_name)
        self._cache[config_name] = {'data': data, 'modified': False}
        return data

    def list_elements(self, config_name: str,
                     element_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List elements in a Kustom preset.

        Args:
            config_name: Preset filename
            element_type: Optional filter (e.g., 'TEXT', 'SHAPE')

        Returns:
            List of element info dicts
        """
        data = self._cache.get(config_name, {}).get('data')
        if data is None:
            data = self.read_config(config_name)

        elements = self._find_elements_recursive(data, element_type)
        return elements

    def _find_elements_recursive(self, obj: Any, element_type: Optional[str] = None,
                                 path: str = "") -> List[Dict[str, Any]]:
        """Recursively find elements in Kustom structure."""
        elements = []

        if isinstance(obj, dict):
            # Check if this is an element
            if 'type' in obj:
                elem_type = obj.get('type')

                if element_type is None or elem_type == element_type:
                    element_info = {
                        'id': obj.get('id', f'element_{len(elements)}'),
                        'type': elem_type,
                        'path': path,
                        'data': obj
                    }

                    # Add common properties
                    for key in ['text', 'position', 'color', 'font']:
                        if key in obj:
                            element_info[key] = obj[key]

                    elements.append(element_info)

            # Recurse into nested structures
            for key, value in obj.items():
                if key in ['items', 'layers', 'children', 'modules']:
                    new_path = f"{path}/{key}" if path else key
                    elements.extend(self._find_elements_recursive(value, element_type, new_path))

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                elements.extend(self._find_elements_recursive(item, element_type, new_path))

        return elements

    def find_element(self, config_name: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for elements by term.

        Args:
            config_name: Preset filename
            search_term: Search term

        Returns:
            List of matching elements
        """
        all_elements = self.list_elements(config_name)
        search_lower = search_term.lower()

        matching = []
        for elem in all_elements:
            # Search in various fields
            if (search_lower in str(elem.get('id', '')).lower() or
                search_lower in str(elem.get('text', '')).lower() or
                search_lower in str(elem.get('type', '')).lower()):
                matching.append(elem)

        return matching

    def modify_element(self, config_name: str, element_id: str,
                      properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify element properties.

        Args:
            config_name: Preset filename
            element_id: Element ID
            properties: Properties to update

        Returns:
            Updated element info
        """
        data = self._cache.get(config_name, {}).get('data')
        if data is None:
            data = self.read_config(config_name)

        # Find and update element
        element = self._find_and_update_element(data, element_id, properties)

        if element is None:
            raise ValueError(f"Element '{element_id}' not found")

        # Mark as modified
        self._cache[config_name]['modified'] = True

        return element

    def _find_and_update_element(self, obj: Any, element_id: str,
                                 properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recursively find and update element."""
        if isinstance(obj, dict):
            # Check if this is the target element
            if obj.get('id') == element_id:
                obj.update(properties)
                return obj

            # Recurse
            for key, value in obj.items():
                if key in ['items', 'layers', 'children', 'modules']:
                    result = self._find_and_update_element(value, element_id, properties)
                    if result is not None:
                        return result

        elif isinstance(obj, list):
            for item in obj:
                result = self._find_and_update_element(item, element_id, properties)
                if result is not None:
                    return result

        return None

    def save_config(self, config_name: str, data: Dict[str, Any],
                   backup: bool = True) -> str:
        """
        Save Kustom preset.

        Args:
            config_name: Preset filename
            data: Modified data
            backup: Create backup

        Returns:
            Path to saved file
        """
        # Determine handler by extension
        if config_name.endswith('.klwp'):
            handler = self.handlers['klwp']
        elif config_name.endswith('.klck'):
            handler = self.handlers['klck']
        elif config_name.endswith('.kwgt'):
            handler = self.handlers['kwgt']
        else:
            handler = self.handlers[self.current_type]

        saved_path = handler.save_preset(config_name, data, backup)

        # Clear cache
        if config_name in self._cache:
            del self._cache[config_name]

        return saved_path

    def reload_app(self) -> bool:
        """
        Trigger Kustom to reload.

        Returns:
            True if signal sent successfully
        """
        try:
            # Try to send broadcast intent
            import subprocess
            result = subprocess.run(
                ['am', 'broadcast', '-a', 'org.kustom.ACTION_RELOAD'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_element_types(self) -> List[str]:
        """Get supported Kustom element types."""
        return ['TEXT', 'SHAPE', 'IMAGE', 'OVERLAP', 'KOMPONENT',
                'PROGRESS', 'SERIES', 'CURVE', 'MAP']
