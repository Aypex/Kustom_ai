"""Total Launcher plugin for layout manipulation."""

import os
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .plugin_interface import CustomizationPlugin


class TotalLauncherPlugin(CustomizationPlugin):
    """Plugin for Total Launcher app."""

    def __init__(self):
        """Initialize Total Launcher plugin."""
        self.layouts_dir = Path("/storage/emulated/0/TotalLauncher")
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_plugin_name(self) -> str:
        """Return plugin name."""
        return "Total Launcher Support"

    def get_plugin_version(self) -> str:
        """Return plugin version."""
        return "1.0.0"

    def get_supported_app(self) -> str:
        """Return supported app name."""
        return "Total Launcher"

    def get_app_package(self) -> str:
        """Return Android package name."""
        return "com.fs.tbrowser"

    def is_app_installed(self) -> bool:
        """Check if Total Launcher is installed."""
        # Check if layout directory exists
        if self.layouts_dir.exists():
            return True

        # On Android, could also check package manager
        try:
            import subprocess
            result = subprocess.run(
                ['pm', 'list', 'packages', self.get_app_package()],
                capture_output=True,
                text=True,
                timeout=2
            )
            return self.get_app_package() in result.stdout
        except Exception:
            return False

    def get_config_directory(self) -> Path:
        """Return Total Launcher layouts directory."""
        return self.layouts_dir

    def list_configs(self) -> List[Dict[str, Any]]:
        """
        List all Total Launcher layouts.

        Returns:
            List of layout info dicts
        """
        if not self.layouts_dir.exists():
            return []

        layouts = []
        for layout_file in self.layouts_dir.glob('*.tl'):
            layouts.append({
                'name': layout_file.stem,
                'filename': layout_file.name,
                'path': str(layout_file),
                'size': layout_file.stat().st_size,
                'type': 'total_launcher'
            })

        return sorted(layouts, key=lambda x: x['name'].lower())

    def read_config(self, config_name: str) -> Dict[str, Any]:
        """
        Read Total Launcher layout file.

        Args:
            config_name: Layout filename (.tl file)

        Returns:
            Parsed layout data
        """
        if not config_name.endswith('.tl'):
            config_name += '.tl'

        layout_path = self.layouts_dir / config_name

        if not layout_path.exists():
            raise FileNotFoundError(f"Layout not found: {layout_path}")

        # .tl files are ZIP archives containing XML
        with zipfile.ZipFile(layout_path, 'r') as zf:
            # Find the main layout XML (usually layout.xml or similar)
            xml_files = [name for name in zf.namelist() if name.endswith('.xml')]

            if not xml_files:
                raise ValueError(f"No XML files found in {config_name}")

            # Use the first XML file (main layout)
            main_xml = xml_files[0]

            with zf.open(main_xml) as f:
                tree = ET.parse(f)
                root = tree.getroot()

        # Convert XML to dict structure
        data = self._xml_to_dict(root)

        # Cache the layout
        self._cache[config_name] = {
            'data': data,
            'root': root,
            'modified': False
        }

        return data

    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {
            'tag': element.tag,
            'attributes': dict(element.attrib),
            'text': element.text.strip() if element.text else None,
            'children': []
        }

        for child in element:
            result['children'].append(self._xml_to_dict(child))

        return result

    def _dict_to_xml(self, data: Dict[str, Any], parent: Optional[ET.Element] = None) -> ET.Element:
        """Convert dictionary back to XML element."""
        element = ET.Element(data['tag'], attrib=data.get('attributes', {}))

        if data.get('text'):
            element.text = data['text']

        for child_data in data.get('children', []):
            child = self._dict_to_xml(child_data)
            element.append(child)

        return element

    def list_elements(self, config_name: str,
                     element_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List items in Total Launcher layout.

        Args:
            config_name: Layout filename
            element_type: Optional filter (e.g., 'app', 'widget', 'folder')

        Returns:
            List of item info dicts
        """
        data = self._cache.get(config_name, {}).get('data')
        if data is None:
            data = self.read_config(config_name)

        elements = self._find_items_recursive(data, element_type)
        return elements

    def _find_items_recursive(self, node: Dict[str, Any],
                             item_type: Optional[str] = None,
                             path: str = "") -> List[Dict[str, Any]]:
        """Recursively find launcher items in layout."""
        items = []

        # Common Total Launcher tags
        item_tags = ['app', 'widget', 'folder', 'shortcut', 'icon', 'panel']

        if node['tag'] in item_tags:
            attrs = node['attributes']
            node_type = node['tag']

            if item_type is None or node_type == item_type:
                item_info = {
                    'id': attrs.get('id', attrs.get('name', f'item_{len(items)}')),
                    'type': node_type,
                    'path': path,
                    'label': attrs.get('label', attrs.get('title', '')),
                    'x': attrs.get('x', 0),
                    'y': attrs.get('y', 0),
                    'data': node
                }

                # Add type-specific properties
                if node_type == 'app':
                    item_info['package'] = attrs.get('package', '')
                elif node_type == 'folder':
                    item_info['items_count'] = len(node.get('children', []))

                items.append(item_info)

        # Recurse into children
        for i, child in enumerate(node.get('children', [])):
            new_path = f"{path}/{node['tag']}[{i}]" if path else f"{node['tag']}[{i}]"
            items.extend(self._find_items_recursive(child, item_type, new_path))

        return items

    def find_element(self, config_name: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for launcher items by term.

        Args:
            config_name: Layout filename
            search_term: Search term

        Returns:
            List of matching items
        """
        all_items = self.list_elements(config_name)
        search_lower = search_term.lower()

        matching = []
        for item in all_items:
            if (search_lower in str(item.get('id', '')).lower() or
                search_lower in str(item.get('label', '')).lower() or
                search_lower in str(item.get('package', '')).lower() or
                search_lower in str(item.get('type', '')).lower()):
                matching.append(item)

        return matching

    def modify_element(self, config_name: str, element_id: str,
                      properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify launcher item properties.

        Args:
            config_name: Layout filename
            element_id: Item ID
            properties: Properties to update

        Returns:
            Updated item info
        """
        data = self._cache.get(config_name, {}).get('data')
        if data is None:
            data = self.read_config(config_name)

        # Find and update item
        item = self._find_and_update_item(data, element_id, properties)

        if item is None:
            raise ValueError(f"Item '{element_id}' not found")

        # Mark as modified
        self._cache[config_name]['modified'] = True

        return item

    def _find_and_update_item(self, node: Dict[str, Any], item_id: str,
                             properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recursively find and update launcher item."""
        attrs = node.get('attributes', {})
        current_id = attrs.get('id', attrs.get('name', ''))

        if current_id == item_id:
            # Update attributes
            for key, value in properties.items():
                attrs[key] = str(value)
            return node

        # Recurse into children
        for child in node.get('children', []):
            result = self._find_and_update_item(child, item_id, properties)
            if result is not None:
                return result

        return None

    def save_config(self, config_name: str, data: Dict[str, Any],
                   backup: bool = True) -> str:
        """
        Save Total Launcher layout.

        Args:
            config_name: Layout filename
            data: Modified layout data
            backup: Create backup

        Returns:
            Path to saved file
        """
        if not config_name.endswith('.tl'):
            config_name += '.tl'

        layout_path = self.layouts_dir / config_name

        # Create backup
        if backup and layout_path.exists():
            import shutil
            backup_path = layout_path.with_suffix('.tl.backup')
            shutil.copy2(layout_path, backup_path)

        # Convert dict back to XML
        root = self._dict_to_xml(data)
        tree = ET.ElementTree(root)

        # Create temp ZIP
        temp_path = layout_path.with_suffix('.tmp')

        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Write XML to ZIP
            xml_str = ET.tostring(root, encoding='unicode', method='xml')
            zf.writestr('layout.xml', xml_str)

            # Copy other files from original if it exists
            if layout_path.exists():
                with zipfile.ZipFile(layout_path, 'r') as old_zf:
                    for item in old_zf.namelist():
                        if not item.endswith('.xml'):
                            zf.writestr(item, old_zf.read(item))

        # Replace original
        temp_path.replace(layout_path)

        # Clear cache
        if config_name in self._cache:
            del self._cache[config_name]

        return str(layout_path)

    def reload_app(self) -> bool:
        """
        Trigger Total Launcher to reload.

        Returns:
            True if signal sent successfully
        """
        try:
            import subprocess
            # Send broadcast to Total Launcher
            result = subprocess.run(
                [
                    'am', 'broadcast',
                    '-a', 'com.fs.tbrowser.ACTION_RELOAD',
                    '-n', f'{self.get_app_package()}/.Receiver'
                ],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_element_types(self) -> List[str]:
        """Get supported Total Launcher item types."""
        return ['app', 'widget', 'folder', 'shortcut', 'icon', 'panel']
