"""
Preset Storage Manager

Handles saving, loading, and managing KLWP/KLCK/KWGT presets on device.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PresetMetadata:
    """Metadata for a saved preset."""
    name: str
    preset_type: str  # 'klwp', 'klck', 'kwgt'
    created_at: str
    modified_at: str
    file_path: str
    thumbnail_path: Optional[str] = None
    colors: List[str] = None

    def __post_init__(self):
        if self.colors is None:
            self.colors = []


class PresetStorage:
    """Manages preset files on device storage."""

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize preset storage.

        Args:
            storage_dir: Directory for preset storage (defaults to app-specific)
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            # Default: Use app-specific external storage
            # On Android: /storage/emulated/0/Android/data/com.chameleon/files/presets
            # For development: Local directory
            self.storage_dir = Path.home() / '.chameleon' / 'presets'

        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories by type
        self.klwp_dir = self.storage_dir / 'klwp'
        self.klck_dir = self.storage_dir / 'klck'
        self.kwgt_dir = self.storage_dir / 'kwgt'
        self.thumbnails_dir = self.storage_dir / 'thumbnails'

        for dir_path in [self.klwp_dir, self.klck_dir, self.kwgt_dir, self.thumbnails_dir]:
            dir_path.mkdir(exist_ok=True)

    def save_preset(self, name: str, preset_data: Dict[str, Any],
                   preset_type: str, thumbnail_path: Optional[str] = None) -> PresetMetadata:
        """
        Save preset to storage.

        Args:
            name: Preset name (will be sanitized)
            preset_data: Complete preset JSON
            preset_type: 'klwp', 'klck', or 'kwgt'
            thumbnail_path: Optional path to rendered preview image

        Returns:
            PresetMetadata for saved preset

        Raises:
            ValueError: If preset_type is invalid
        """
        # Validate type
        if preset_type not in ['klwp', 'klck', 'kwgt']:
            raise ValueError(f"Invalid preset type: {preset_type}")

        # Sanitize name
        safe_name = self._sanitize_name(name)

        # Determine directory
        type_dir = getattr(self, f'{preset_type}_dir')

        # Create file path
        file_path = type_dir / f"{safe_name}.json"

        # Add metadata to preset
        now = datetime.now().isoformat()
        preset_with_meta = {
            **preset_data,
            'metadata': {
                'name': safe_name,
                'created_at': now,
                'modified_at': now,
                'app': 'Chameleon',
                'version': '0.2.1'
            }
        }

        # Save JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(preset_with_meta, f, indent=2)

        # Copy thumbnail if provided
        thumbnail_dest = None
        if thumbnail_path and os.path.exists(thumbnail_path):
            thumbnail_dest = self.thumbnails_dir / f"{safe_name}.png"
            import shutil
            shutil.copy(thumbnail_path, thumbnail_dest)

        # Extract colors
        colors = self._extract_colors(preset_data)

        return PresetMetadata(
            name=safe_name,
            preset_type=preset_type,
            created_at=now,
            modified_at=now,
            file_path=str(file_path),
            thumbnail_path=str(thumbnail_dest) if thumbnail_dest else None,
            colors=colors
        )

    def load_preset(self, name: str, preset_type: str) -> Dict[str, Any]:
        """
        Load preset from storage.

        Args:
            name: Preset name
            preset_type: 'klwp', 'klck', or 'kwgt'

        Returns:
            Preset JSON dict

        Raises:
            FileNotFoundError: If preset doesn't exist
        """
        type_dir = getattr(self, f'{preset_type}_dir')
        file_path = type_dir / f"{name}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Preset not found: {name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_presets(self, preset_type: Optional[str] = None) -> List[PresetMetadata]:
        """
        List all saved presets.

        Args:
            preset_type: Filter by type, or None for all

        Returns:
            List of PresetMetadata
        """
        presets = []

        types_to_scan = [preset_type] if preset_type else ['klwp', 'klck', 'kwgt']

        for ptype in types_to_scan:
            type_dir = getattr(self, f'{ptype}_dir')

            for file_path in type_dir.glob('*.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    meta = data.get('metadata', {})
                    name = file_path.stem
                    thumbnail = self.thumbnails_dir / f"{name}.png"

                    presets.append(PresetMetadata(
                        name=name,
                        preset_type=ptype,
                        created_at=meta.get('created_at', ''),
                        modified_at=meta.get('modified_at', ''),
                        file_path=str(file_path),
                        thumbnail_path=str(thumbnail) if thumbnail.exists() else None,
                        colors=self._extract_colors(data)
                    ))
                except Exception as e:
                    print(f"⚠️ Failed to load preset {file_path}: {e}")

        # Sort by modified date (newest first)
        presets.sort(key=lambda p: p.modified_at, reverse=True)
        return presets

    def delete_preset(self, name: str, preset_type: str) -> bool:
        """
        Delete preset from storage.

        Args:
            name: Preset name
            preset_type: 'klwp', 'klck', or 'kwgt'

        Returns:
            True if deleted, False if not found
        """
        type_dir = getattr(self, f'{preset_type}_dir')
        file_path = type_dir / f"{name}.json"
        thumbnail_path = self.thumbnails_dir / f"{name}.png"

        deleted = False

        if file_path.exists():
            file_path.unlink()
            deleted = True

        if thumbnail_path.exists():
            thumbnail_path.unlink()

        return deleted

    def export_preset(self, name: str, preset_type: str, export_path: str) -> str:
        """
        Export preset to external location (for sharing).

        Args:
            name: Preset name
            preset_type: 'klwp', 'klck', or 'kwgt'
            export_path: Destination file path

        Returns:
            Path to exported file
        """
        preset_data = self.load_preset(name, preset_type)

        # Remove internal metadata for clean export
        if 'metadata' in preset_data:
            preset_data = {k: v for k, v in preset_data.items() if k != 'metadata'}

        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, indent=2)

        return export_path

    def _sanitize_name(self, name: str) -> str:
        """Sanitize preset name for filesystem."""
        # Remove extension if present
        if name.endswith(('.klwp', '.klck', '.kwgt', '.json')):
            name = name.rsplit('.', 1)[0]

        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')

        # Limit length
        return name[:100]

    def _extract_colors(self, preset_data: Dict[str, Any]) -> List[str]:
        """Extract color palette from preset."""
        colors = set()

        def traverse(obj):
            if isinstance(obj, dict):
                for key in ['color', 'bgcolor', 'stroke_color']:
                    if key in obj and obj[key]:
                        colors.add(obj[key])
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        traverse(value)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)

        traverse(preset_data)
        return sorted(list(colors))[:10]  # Limit to 10 colors


# Test/Example usage
if __name__ == "__main__":
    print("🦎 PRESET STORAGE TEST\n")

    storage = PresetStorage()

    # Test save
    test_preset = {
        'version': 1,
        'width': 1080,
        'height': 1920,
        'items': [
            {
                'type': 'SHAPE',
                'id': 'background',
                'color': '#000000',
                'shape_type': 'rectangle',
                'width': 1080,
                'height': 1920,
                'position': {'x': 0, 'y': 0}
            },
            {
                'type': 'TEXT',
                'id': 'clock',
                'text': '$df(HH:mm)$',
                'color': '#00FFFF',
                'font_size': 96,
                'position': {'x': 'center', 'y': 800}
            }
        ]
    }

    print("1. SAVE PRESET:")
    meta = storage.save_preset('test_cyberpunk', test_preset, 'klwp')
    print(f"✅ Saved: {meta.name}")
    print(f"   Path: {meta.file_path}")
    print(f"   Colors: {meta.colors}")

    print("\n2. LIST PRESETS:")
    presets = storage.list_presets()
    for p in presets:
        print(f"   • {p.name} ({p.preset_type}) - {p.modified_at}")

    print("\n3. LOAD PRESET:")
    loaded = storage.load_preset('test_cyberpunk', 'klwp')
    print(f"✅ Loaded {len(loaded.get('items', []))} items")

    print(f"\n📁 Storage location: {storage.storage_dir}")
