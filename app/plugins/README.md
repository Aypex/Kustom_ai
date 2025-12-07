# KLWP AI Assistant - Plugin System

This directory contains the plugin system for Android customization app support.

## Available Plugins

### 1. Kustom Plugin (`kustom_plugin.py`)
**Supports:** KLWP, KLCK, KWGT
**File Format:** `.klwp`, `.klck`, `.kwgt` (ZIP files containing `preset.json`)
**Location:** `/storage/emulated/0/Kustom/`

Features:
- Read/modify Kustom presets
- Cross-format preset generation
- Element searching and manipulation
- Style extraction and adaptation

### 2. Total Launcher Plugin (`total_launcher_plugin.py`)
**Supports:** Total Launcher
**File Format:** `.tl` (ZIP files containing XML layouts)
**Location:** `/storage/emulated/0/TotalLauncher/`

Features:
- Read/modify launcher layouts
- App icon manipulation
- Widget and folder management
- Position and appearance changes

### 3. Tasker Plugin (`tasker_plugin.py`)
**Supports:** Tasker
**File Format:** `.prj.xml`, `.tsk.xml`, `.prf.xml`
**Location:** `/storage/emulated/0/Tasker/`

Features:
- Read/modify tasks and profiles
- Action manipulation
- Task creation
- Profile triggering

## Plugin Interface

All plugins implement the `CustomizationPlugin` interface defined in `plugin_interface.py`.

### Required Methods

```python
def get_plugin_name() -> str
def get_plugin_version() -> str
def get_supported_app() -> str
def get_app_package() -> str
def is_app_installed() -> bool
def get_config_directory() -> Path
def list_configs() -> List[Dict]
def read_config(config_name: str) -> Dict
def list_elements(config_name: str, element_type: str = None) -> List[Dict]
def find_element(config_name: str, search_term: str) -> List[Dict]
def modify_element(config_name: str, element_id: str, properties: Dict) -> Dict
def save_config(config_name: str, data: Dict, backup: bool = True) -> str
def reload_app() -> bool
```

## Plugin Manager

The `PluginManager` class (`plugin_manager.py`) handles:
- Plugin discovery and loading
- Plugin lifecycle management
- Access to plugins by ID or app name
- Listing installed vs available plugins

### Usage

```python
from plugins import get_plugin_manager

# Get plugin manager
pm = get_plugin_manager()

# List all plugins
plugins = pm.get_plugins()

# Get specific plugin
kustom = pm.get_plugin('kustom')
launcher = pm.get_plugin('total_launcher')
tasker = pm.get_plugin('tasker')

# Check installed apps
installed = pm.get_installed_plugins()
```

## Adding New Plugins

To add support for a new customization app:

1. Create `your_app_plugin.py` implementing `CustomizationPlugin`
2. Add loading logic to `PluginManager._load_your_app_plugin()`
3. Update `PluginManager.load_plugins()` to call your loader
4. Test with real files from the app

### Plugin Template

```python
from .plugin_interface import CustomizationPlugin
from pathlib import Path
from typing import Any, Dict, List, Optional

class YourAppPlugin(CustomizationPlugin):
    def __init__(self):
        self.config_dir = Path("/storage/emulated/0/YourApp")
        self._cache = {}

    def get_plugin_name(self) -> str:
        return "Your App Support"

    def get_plugin_version(self) -> str:
        return "1.0.0"

    def get_supported_app(self) -> str:
        return "Your App Name"

    def get_app_package(self) -> str:
        return "com.yourapp.package"

    # ... implement other required methods
```

## Testing Plugins

Each plugin can be tested individually:

```python
from plugins.total_launcher_plugin import TotalLauncherPlugin

plugin = TotalLauncherPlugin()

# Check if app is installed
if plugin.is_app_installed():
    # List layouts
    layouts = plugin.list_configs()

    # Read a layout
    data = plugin.read_config('home.tl')

    # List items
    items = plugin.list_elements('home.tl')

    # Find specific item
    clock = plugin.find_element('home.tl', 'clock')

    # Modify item
    plugin.modify_element('home.tl', 'clock_widget', {
        'x': 100,
        'y': 200
    })

    # Save changes
    plugin.save_config('home.tl', data, backup=True)

    # Reload app
    plugin.reload_app()
```

## Error Handling

Plugins should raise appropriate exceptions:
- `FileNotFoundError` - Config file not found
- `ValueError` - Invalid data or element not found
- `PermissionError` - Insufficient permissions
- `Exception` - General errors with descriptive messages

## Future Plugins

Potential plugins to add:
- Nova Launcher
- Apex Launcher
- Smart Launcher
- Zooper Widget
- AutoTools
- MacroDroid
- IFTTT

## Architecture Notes

- Plugins are loaded lazily (only when first accessed)
- Plugins with uninstalled apps are not loaded (saves memory)
- All plugins use caching to avoid repeated file reads
- Modifications are cached until save is called
- Backups are created by default before saving
