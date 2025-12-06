"""KLWP preset file handler for ZIP operations and JSON manipulation."""

import json
import os
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class KLWPHandler:
    """Handles KLWP preset file operations (ZIP and JSON)."""

    def __init__(self, presets_dir: str = "/storage/emulated/0/Kustom/wallpapers"):
        """Initialize KLWP handler.

        Args:
            presets_dir: Directory where KLWP preset files are stored
        """
        self.presets_dir = Path(presets_dir)

        # Common KLWP preset locations (including Play Store downloads)
        self.search_dirs = [
            Path(presets_dir),
            Path("/storage/emulated/0/Kustom/wallpapers"),
            Path("/sdcard/Kustom/wallpapers"),
            Path("/storage/emulated/0/Android/data/org.kustom.wallpaper/files"),
            Path.home() / "storage/shared/Kustom/wallpapers",
        ]

        # Remove duplicates and non-existent/inaccessible directories
        seen = set()
        valid_dirs = []
        for d in self.search_dirs:
            try:
                resolved = str(d.resolve()) if d.exists() else str(d)
                if resolved not in seen:
                    seen.add(resolved)
                    valid_dirs.append(d)
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
        self.search_dirs = valid_dirs

        self._cache: Dict[str, Dict[str, Any]] = {}  # Cache loaded presets

    def _get_preset_path(self, preset_name: str) -> Path:
        """Get full path to preset file.

        Searches all known KLWP directories for the preset.

        Args:
            preset_name: Name of preset (with or without .klwp extension)

        Returns:
            Path to preset file

        Raises:
            FileNotFoundError: If preset not found in any directory
        """
        if not preset_name.endswith('.klwp'):
            preset_name += '.klwp'

        # Search all directories for the preset
        for search_dir in self.search_dirs:
            preset_path = search_dir / preset_name
            if preset_path.exists():
                return preset_path

        # Not found in any directory
        raise FileNotFoundError(
            f"Preset '{preset_name}' not found in any KLWP directory. "
            f"Searched: {[str(d) for d in self.search_dirs]}"
        )

    def read_preset(self, preset_name: str) -> Dict[str, Any]:
        """Read and parse KLWP preset file.

        Args:
            preset_name: Name of preset to read

        Returns:
            Parsed preset JSON data

        Raises:
            FileNotFoundError: If preset file doesn't exist
            zipfile.BadZipFile: If file is not a valid ZIP
            json.JSONDecodeError: If preset.json is invalid
        """
        preset_path = self._get_preset_path(preset_name)

        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {preset_path}")

        # Extract preset.json from ZIP
        with zipfile.ZipFile(preset_path, 'r') as zf:
            if 'preset.json' not in zf.namelist():
                raise ValueError(f"No preset.json found in {preset_name}")

            with zf.open('preset.json') as f:
                data = json.load(f)

        # Cache the loaded preset
        self._cache[preset_name] = {
            'data': data,
            'modified': False
        }

        return data

    def get_cached_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """Get cached preset data if available.

        Args:
            preset_name: Name of preset

        Returns:
            Cached preset data or None
        """
        cache_entry = self._cache.get(preset_name)
        return cache_entry['data'] if cache_entry else None

    def list_elements(self, preset_name: str, element_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all elements in a preset, optionally filtered by type.

        Args:
            preset_name: Name of preset
            element_type: Optional type filter (e.g., 'TEXT', 'SHAPE', 'IMAGE')

        Returns:
            List of elements with their properties
        """
        data = self.get_cached_preset(preset_name)
        if data is None:
            data = self.read_preset(preset_name)

        elements = []

        # Navigate KLWP structure: preset.json typically has a root object with layers
        # Common structure: {"layers": [...]} or {"items": [...]}
        root_items = self._find_elements_recursive(data, element_type)

        return root_items

    def _find_elements_recursive(self, obj: Any, element_type: Optional[str] = None,
                                  path: str = "") -> List[Dict[str, Any]]:
        """Recursively find elements in the preset structure.

        Args:
            obj: Current object to search
            element_type: Optional type filter
            path: Current path in structure

        Returns:
            List of found elements
        """
        elements = []

        if isinstance(obj, dict):
            # Check if this is an element
            if 'type' in obj or 'internal_type' in obj:
                elem_type = obj.get('type') or obj.get('internal_type')

                # Add if no filter or type matches
                if element_type is None or elem_type == element_type:
                    element_info = {
                        'id': obj.get('id', obj.get('internal_id', 'unknown')),
                        'type': elem_type,
                        'path': path,
                        'data': obj
                    }

                    # Add common properties if available
                    if 'text' in obj:
                        element_info['text'] = obj['text']
                    if 'position' in obj:
                        element_info['position'] = obj['position']
                    if 'title' in obj:
                        element_info['title'] = obj['title']

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

    def find_element(self, preset_name: str, search_term: str) -> List[Dict[str, Any]]:
        """Find elements by name, text, or ID.

        Args:
            preset_name: Name of preset
            search_term: Term to search for (case-insensitive)

        Returns:
            List of matching elements
        """
        all_elements = self.list_elements(preset_name)
        search_lower = search_term.lower()

        matching = []
        for elem in all_elements:
            # Search in various fields
            if (search_lower in str(elem.get('id', '')).lower() or
                search_lower in str(elem.get('text', '')).lower() or
                search_lower in str(elem.get('title', '')).lower() or
                search_lower in str(elem.get('type', '')).lower()):
                matching.append(elem)

        return matching

    def modify_element(self, preset_name: str, element_id: str,
                      properties: Dict[str, Any]) -> Dict[str, Any]:
        """Modify an element's properties.

        Args:
            preset_name: Name of preset
            element_id: ID of element to modify
            properties: Dictionary of properties to update

        Returns:
            Updated element data

        Raises:
            ValueError: If element not found
        """
        data = self.get_cached_preset(preset_name)
        if data is None:
            data = self.read_preset(preset_name)

        # Find and update the element
        element = self._find_and_update_element(data, element_id, properties)

        if element is None:
            raise ValueError(f"Element with ID '{element_id}' not found")

        # Mark as modified
        self._cache[preset_name]['modified'] = True

        return element

    def _find_and_update_element(self, obj: Any, element_id: str,
                                 properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recursively find and update an element.

        Args:
            obj: Current object to search
            element_id: ID to find
            properties: Properties to update

        Returns:
            Updated element or None if not found
        """
        if isinstance(obj, dict):
            # Check if this is the target element
            elem_id = obj.get('id') or obj.get('internal_id')
            if elem_id == element_id:
                # Update properties
                obj.update(properties)
                return obj

            # Recurse into nested structures
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

    def save_preset(self, preset_name: str, backup: bool = True) -> str:
        """Save modified preset back to ZIP file.

        Args:
            preset_name: Name of preset to save
            backup: Whether to create a backup of original

        Returns:
            Path to saved file

        Raises:
            ValueError: If preset not loaded or not modified
        """
        cache_entry = self._cache.get(preset_name)
        if cache_entry is None:
            raise ValueError(f"Preset '{preset_name}' not loaded")

        if not cache_entry['modified']:
            return str(self._get_preset_path(preset_name))

        preset_path = self._get_preset_path(preset_name)

        # Create backup if requested
        if backup and preset_path.exists():
            backup_path = preset_path.with_suffix('.klwp.bak')
            shutil.copy2(preset_path, backup_path)

        # Create temporary directory for repacking
        temp_dir = Path(f"/tmp/klwp_{preset_name.replace('.klwp', '')}")
        temp_dir.mkdir(exist_ok=True)

        try:
            # Extract all files from original ZIP
            with zipfile.ZipFile(preset_path, 'r') as zf:
                zf.extractall(temp_dir)

            # Write updated preset.json
            preset_json_path = temp_dir / 'preset.json'
            with open(preset_json_path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry['data'], f, indent=2, ensure_ascii=False)

            # Repack ZIP
            with zipfile.ZipFile(preset_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zf.write(file_path, arcname)

            # Mark as no longer modified
            cache_entry['modified'] = False

            return str(preset_path)

        finally:
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def list_presets(self) -> List[str]:
        """List all available KLWP preset files from all search directories.

        Returns:
            List of preset filenames (deduplicated)
        """
        presets = {}  # Use dict to track preset -> directory mapping

        # Search all directories
        for search_dir in self.search_dirs:
            try:
                if search_dir.exists():
                    for preset_file in search_dir.glob('*.klwp'):
                        # Only add if we haven't seen this preset name yet
                        if preset_file.name not in presets:
                            presets[preset_file.name] = str(search_dir)
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass

        return sorted(presets.keys())

    def list_presets_with_locations(self) -> List[Dict[str, str]]:
        """List all available KLWP preset files with their locations.

        Returns:
            List of dicts with 'name' and 'directory' keys
        """
        presets = []
        seen_names = set()

        # Search all directories
        for search_dir in self.search_dirs:
            try:
                if search_dir.exists():
                    for preset_file in search_dir.glob('*.klwp'):
                        if preset_file.name not in seen_names:
                            seen_names.add(preset_file.name)
                            presets.append({
                                'name': preset_file.name,
                                'directory': str(search_dir),
                                'path': str(preset_file)
                            })
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass

        return sorted(presets, key=lambda x: x['name'])
