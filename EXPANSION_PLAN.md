# Android Customization MCP Server - Expansion Plan

## Vision
Unified MCP server for controlling all major Android customization apps via AI.

## Currently Supported
- ✅ KLWP (Kustom Live Wallpaper)
- ✅ KLCK (Kustom Lock Screen) - via KLWP handler
- ✅ KWGT (Kustom Widget) - via KLWP handler

## Proposed Additions
- ❌ Total Launcher
- ❌ Tasker

## Architecture: Unified with Pluggable Handlers

### Phase 1: Refactor Current Code
1. Rename `klwp_mcp_server/` → `android_custom_mcp_server/`
2. Move `klwp_handler.py` → `handlers/kustom_handler.py`
3. Create `handlers/base_handler.py` with abstract interface
4. Update MCP server to route based on app type

### Phase 2: Add Total Launcher Support
**File Format**: `.tl` files (ZIP containing XML layouts)
**Location**: `/sdcard/TotalLauncher/`

#### New Tools:
- `read_total_launcher_layout` - Parse layout XML
- `list_launcher_items` - List icons, widgets, folders
- `find_launcher_item` - Search by label, type, position
- `modify_launcher_item` - Change icon, position, size, action
- `save_launcher_layout` - Save with backup
- `reload_launcher` - Trigger Total Launcher reload

#### Implementation:
```python
# handlers/total_launcher_handler.py
class TotalLauncherHandler(BaseHandler):
    def __init__(self):
        self.layouts_dir = Path("/sdcard/TotalLauncher")
        # Similar structure to KLWP handler but for XML

    def read_layout(self, layout_name): ...
    def list_items(self, layout_name, item_type=None): ...
    def modify_item(self, layout_name, item_id, properties): ...
```

### Phase 3: Add Tasker Support
**File Format**: `.xml` files (`.tsk.xml`, `.prf.xml`, `.prj.xml`)
**Location**: `/sdcard/Tasker/`

#### New Tools:
- `read_tasker_project` - Parse project XML
- `list_tasks` - List all tasks in project
- `list_profiles` - List all profiles
- `find_task` - Search tasks by name/action
- `modify_task` - Change task actions, variables
- `create_task` - Generate new task
- `save_tasker_project` - Save with backup
- `reload_tasker` - Trigger Tasker to reload

#### Implementation:
```python
# handlers/tasker_handler.py
class TaskerHandler(BaseHandler):
    def __init__(self):
        self.projects_dir = Path("/sdcard/Tasker")
        # XML parsing for Tasker format

    def read_project(self, project_name): ...
    def list_tasks(self, project_name): ...
    def modify_task(self, project_name, task_id, actions): ...
```

### Phase 4: Unified MCP Server Interface

```python
# server.py (updated)
@app.list_tools()
async def list_tools() -> list[Tool]:
    tools = []

    # Kustom tools (KLWP/KLCK/KWGT)
    tools.extend(kustom_handler.get_tools())

    # Total Launcher tools
    tools.extend(total_launcher_handler.get_tools())

    # Tasker tools
    tools.extend(tasker_handler.get_tools())

    return tools

@app.call_tool()
async def call_tool(name: str, arguments: Any):
    # Route to appropriate handler based on tool name prefix
    if name.startswith("kustom_"):
        return await kustom_handler.call(name, arguments)
    elif name.startswith("launcher_"):
        return await total_launcher_handler.call(name, arguments)
    elif name.startswith("tasker_"):
        return await tasker_handler.call(name, arguments)
```

## Base Handler Interface

```python
# handlers/base_handler.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

class BaseHandler(ABC):
    """Base class for all Android customization app handlers."""

    @abstractmethod
    def read_config(self, config_name: str) -> Dict[str, Any]:
        """Read and parse configuration file."""
        pass

    @abstractmethod
    def list_elements(self, config_name: str, element_type: Optional[str] = None) -> List[Dict]:
        """List all elements/items in the configuration."""
        pass

    @abstractmethod
    def find_element(self, config_name: str, search_term: str) -> List[Dict]:
        """Search for elements by term."""
        pass

    @abstractmethod
    def modify_element(self, config_name: str, element_id: str, properties: Dict) -> Dict:
        """Modify an element's properties."""
        pass

    @abstractmethod
    def save_config(self, config_name: str, backup: bool = True) -> str:
        """Save modified configuration."""
        pass

    @abstractmethod
    def reload_app(self) -> Dict:
        """Trigger app to reload configuration."""
        pass

    def get_tools(self) -> List[Tool]:
        """Return list of MCP tools this handler provides."""
        pass

    def call(self, tool_name: str, arguments: Any) -> List[TextContent]:
        """Handle a tool call for this handler."""
        pass
```

## Shared Utilities

```python
# utils/xml_utils.py
import xml.etree.ElementTree as ET

def parse_xml(xml_path: Path) -> ET.Element:
    """Parse XML file."""
    pass

def find_elements_by_tag(root: ET.Element, tag: str) -> List[ET.Element]:
    """Find all elements with specific tag."""
    pass

def update_element(element: ET.Element, properties: Dict) -> None:
    """Update element attributes."""
    pass

# utils/zip_utils.py
def extract_zip(zip_path: Path, target_dir: Path) -> None:
    """Extract ZIP archive."""
    pass

def create_zip(source_dir: Path, zip_path: Path) -> None:
    """Create ZIP archive."""
    pass
```

## MCP Tool Naming Convention

- **Kustom (KLWP/KLCK/KWGT)**: `kustom_*`
  - `kustom_read_preset`
  - `kustom_list_elements`
  - `kustom_modify_element`

- **Total Launcher**: `launcher_*`
  - `launcher_read_layout`
  - `launcher_list_items`
  - `launcher_modify_item`

- **Tasker**: `tasker_*`
  - `tasker_read_project`
  - `tasker_list_tasks`
  - `tasker_modify_task`

## Example Usage (Once Implemented)

```python
# In Claude Desktop with unified MCP server

# KLWP
"List all text elements in my wallpaper"
→ kustom_list_elements(preset="my.klwp", type="TEXT")

# Total Launcher
"Show all apps on my home screen"
→ launcher_list_items(layout="home.tl", type="APP")

# Tasker
"What tasks run when I connect to WiFi?"
→ tasker_list_tasks(project="my_project.prj.xml", filter="WiFi")

# Cross-app modification
"Make my wallpaper clock match my launcher theme"
→ kustom_read_preset("wallpaper.klwp")
→ launcher_read_layout("home.tl")
→ Extract colors from launcher
→ kustom_modify_element(... update clock colors ...)
```

## Implementation Timeline

### Immediate (v1.1)
- [x] KLWP working
- [ ] Refactor to handler architecture
- [ ] Create base handler class
- [ ] Move KLWP to kustom_handler.py

### Short-term (v1.2)
- [ ] Add Total Launcher handler
- [ ] XML parsing utilities
- [ ] Total Launcher reload broadcast
- [ ] Testing with real .tl files

### Medium-term (v1.3)
- [ ] Add Tasker handler
- [ ] Tasker XML parsing
- [ ] Task creation/modification
- [ ] Tasker reload integration

### Long-term (v2.0)
- [ ] Cross-app theme sync
- [ ] AI-powered preset generation
- [ ] Voice command interface
- [ ] Cloud backup integration

## Benefits of Unified Approach

1. **Single Configuration**: One MCP server entry in Claude Desktop
2. **Shared Logic**: Backup, file searching, error handling
3. **Cross-App Intelligence**: AI can coordinate changes across apps
4. **Consistent API**: Same patterns for all handlers
5. **Easy Expansion**: Add nova launcher, zooper, etc. easily

## Migration Path

For existing users:
1. Keep `klwp-mcp-server` name for compatibility
2. Add new tools without breaking existing ones
3. Deprecate old names gradually
4. Provide migration guide

OR rename completely:
1. `klwp-mcp-server` → `android-custom-mcp-server`
2. Update all tool names
3. Better reflects expanded scope
4. Clean break for v2.0

## Questions to Consider

1. **Naming**: Keep "klwp-mcp-server" or rename to "android-custom-mcp-server"?
2. **Versioning**: Major bump (2.0) for the refactor?
3. **Backward Compatibility**: Maintain old tool names with deprecation warnings?
4. **App Priority**: Implement Total Launcher or Tasker first?
5. **Testing**: Need real .tl and .xml files - do you have examples?

## Next Steps

If you want to proceed:
1. I can start the refactor to handler architecture
2. Create the base handler interface
3. Implement Total Launcher or Tasker handler (your choice!)
4. Update the Android app UI to show all supported apps

What do you think? Should we go unified or separate servers?
