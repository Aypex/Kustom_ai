"""Tasker plugin for task and profile manipulation."""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

from .plugin_interface import CustomizationPlugin


class TaskerPlugin(CustomizationPlugin):
    """Plugin for Tasker automation app."""

    def __init__(self):
        """Initialize Tasker plugin."""
        self.tasker_dir = Path("/storage/emulated/0/Tasker")
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_plugin_name(self) -> str:
        """Return plugin name."""
        return "Tasker Support"

    def get_plugin_version(self) -> str:
        """Return plugin version."""
        return "1.0.0"

    def get_supported_app(self) -> str:
        """Return supported app name."""
        return "Tasker"

    def get_app_package(self) -> str:
        """Return Android package name."""
        return "net.dinglisch.android.taskerm"

    def is_app_installed(self) -> bool:
        """Check if Tasker is installed."""
        # Check if Tasker directory exists
        if self.tasker_dir.exists():
            return True

        # On Android, check package manager
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
        """Return Tasker directory."""
        return self.tasker_dir

    def list_configs(self) -> List[Dict[str, Any]]:
        """
        List all Tasker projects, tasks, and profiles.

        Returns:
            List of Tasker file info dicts
        """
        if not self.tasker_dir.exists():
            return []

        configs = []

        # List projects
        for prj_file in self.tasker_dir.glob('*.prj.xml'):
            configs.append({
                'name': prj_file.stem.replace('.prj', ''),
                'filename': prj_file.name,
                'path': str(prj_file),
                'size': prj_file.stat().st_size,
                'type': 'project'
            })

        # List tasks
        for tsk_file in self.tasker_dir.glob('*.tsk.xml'):
            configs.append({
                'name': tsk_file.stem.replace('.tsk', ''),
                'filename': tsk_file.name,
                'path': str(tsk_file),
                'size': tsk_file.stat().st_size,
                'type': 'task'
            })

        # List profiles
        for prf_file in self.tasker_dir.glob('*.prf.xml'):
            configs.append({
                'name': prf_file.stem.replace('.prf', ''),
                'filename': prf_file.name,
                'path': str(prf_file),
                'size': prf_file.stat().st_size,
                'type': 'profile'
            })

        return sorted(configs, key=lambda x: (x['type'], x['name'].lower()))

    def read_config(self, config_name: str) -> Dict[str, Any]:
        """
        Read Tasker configuration file.

        Args:
            config_name: Tasker file name (.prj.xml, .tsk.xml, or .prf.xml)

        Returns:
            Parsed Tasker data
        """
        # Determine file type
        if '.prj.xml' not in config_name and '.tsk.xml' not in config_name and '.prf.xml' not in config_name:
            # Try to find the file
            for ext in ['.prj.xml', '.tsk.xml', '.prf.xml']:
                test_path = self.tasker_dir / (config_name + ext)
                if test_path.exists():
                    config_name = test_path.name
                    break

        config_path = self.tasker_dir / config_name

        if not config_path.exists():
            raise FileNotFoundError(f"Tasker config not found: {config_path}")

        # Parse XML
        tree = ET.parse(config_path)
        root = tree.getroot()

        # Convert to dict
        data = self._xml_to_dict(root)

        # Cache
        self._cache[config_name] = {
            'data': data,
            'root': root,
            'tree': tree,
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

    def _dict_to_xml(self, data: Dict[str, Any]) -> ET.Element:
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
        List tasks/profiles/actions in Tasker config.

        Args:
            config_name: Tasker file name
            element_type: Optional filter (e.g., 'Task', 'Profile', 'Action')

        Returns:
            List of element info dicts
        """
        data = self._cache.get(config_name, {}).get('data')
        if data is None:
            data = self.read_config(config_name)

        elements = self._find_tasker_elements(data, element_type)
        return elements

    def _find_tasker_elements(self, node: Dict[str, Any],
                             element_type: Optional[str] = None,
                             path: str = "") -> List[Dict[str, Any]]:
        """Recursively find Tasker elements."""
        elements = []

        tag = node['tag']
        attrs = node['attributes']

        # Common Tasker tags
        tasker_tags = ['Task', 'Profile', 'Action', 'Event', 'State', 'Condition']

        if tag in tasker_tags:
            if element_type is None or tag == element_type:
                elem_info = {
                    'id': attrs.get('sr', attrs.get('ve', f'{tag}_{len(elements)}')),
                    'type': tag,
                    'path': path,
                    'name': attrs.get('name', ''),
                    'data': node
                }

                # Add type-specific properties
                if tag == 'Task':
                    elem_info['actions_count'] = len([c for c in node.get('children', []) if c['tag'] == 'Action'])
                elif tag == 'Action':
                    elem_info['code'] = attrs.get('code', '')

                elements.append(elem_info)

        # Recurse into children
        for i, child in enumerate(node.get('children', [])):
            new_path = f"{path}/{tag}[{i}]" if path else f"{tag}[{i}]"
            elements.extend(self._find_tasker_elements(child, element_type, new_path))

        return elements

    def find_element(self, config_name: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for Tasker elements by term.

        Args:
            config_name: Tasker file name
            search_term: Search term

        Returns:
            List of matching elements
        """
        all_elements = self.list_elements(config_name)
        search_lower = search_term.lower()

        matching = []
        for elem in all_elements:
            if (search_lower in str(elem.get('id', '')).lower() or
                search_lower in str(elem.get('name', '')).lower() or
                search_lower in str(elem.get('type', '')).lower() or
                search_lower in str(elem.get('code', '')).lower()):
                matching.append(elem)

        return matching

    def modify_element(self, config_name: str, element_id: str,
                      properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify Tasker element properties.

        Args:
            config_name: Tasker file name
            element_id: Element ID (sr attribute)
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

    def _find_and_update_element(self, node: Dict[str, Any], element_id: str,
                                properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recursively find and update Tasker element."""
        attrs = node.get('attributes', {})
        current_id = attrs.get('sr', attrs.get('ve', ''))

        if current_id == element_id:
            # Update attributes
            for key, value in properties.items():
                if key == 'name':
                    attrs['name'] = str(value)
                else:
                    attrs[key] = str(value)
            return node

        # Recurse into children
        for child in node.get('children', []):
            result = self._find_and_update_element(child, element_id, properties)
            if result is not None:
                return result

        return None

    def save_config(self, config_name: str, data: Dict[str, Any],
                   backup: bool = True) -> str:
        """
        Save Tasker configuration.

        Args:
            config_name: Tasker file name
            data: Modified data
            backup: Create backup

        Returns:
            Path to saved file
        """
        config_path = self.tasker_dir / config_name

        # Create backup
        if backup and config_path.exists():
            import shutil
            backup_path = config_path.with_suffix('.backup')
            shutil.copy2(config_path, backup_path)

        # Convert dict back to XML
        root = self._dict_to_xml(data)
        tree = ET.ElementTree(root)

        # Write XML
        tree.write(config_path, encoding='utf-8', xml_declaration=True)

        # Clear cache
        if config_name in self._cache:
            del self._cache[config_name]

        return str(config_path)

    def reload_app(self) -> bool:
        """
        Trigger Tasker to reload.

        Returns:
            True if signal sent successfully
        """
        try:
            import subprocess
            # Send intent to Tasker to reload
            result = subprocess.run(
                [
                    'am', 'broadcast',
                    '-a', 'net.dinglisch.android.tasker.ACTION_RELOAD',
                    '-n', f'{self.get_app_package()}/.TaskerReceiver'
                ],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_element_types(self) -> List[str]:
        """Get supported Tasker element types."""
        return ['Task', 'Profile', 'Action', 'Event', 'State', 'Condition', 'Variable']

    def create_simple_task(self, task_name: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a simple Tasker task structure.

        Args:
            task_name: Name of the task
            actions: List of action dicts with 'code' and params

        Returns:
            Task structure dict
        """
        task = {
            'tag': 'TaskerData',
            'attributes': {'sr': '', 'dvi': '1', 'tv': '6.3.16'},
            'children': [
                {
                    'tag': 'Task',
                    'attributes': {'sr': 'task1', 'name': task_name},
                    'children': []
                }
            ]
        }

        # Add actions
        for i, action in enumerate(actions):
            action_elem = {
                'tag': 'Action',
                'attributes': {
                    'sr': f'act{i}',
                    'code': str(action.get('code', '1')),  # Default: Alert action
                },
                'children': []
            }
            task['children'][0]['children'].append(action_elem)

        return task
