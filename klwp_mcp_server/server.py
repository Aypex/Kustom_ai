"""MCP Server for KLWP preset manipulation."""

import asyncio
import json
import logging
import subprocess
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .klwp_handler import KLWPHandler


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("klwp-mcp-server")


# Initialize KLWP handler
klwp = KLWPHandler()


# Create MCP server
app = Server("klwp-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for KLWP manipulation."""
    return [
        Tool(
            name="read_klwp_preset",
            description=(
                "Read and parse a KLWP preset file. "
                "Unzips the .klwp file and parses preset.json. "
                "Returns the complete preset structure."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "preset_name": {
                        "type": "string",
                        "description": "Name of the preset file (with or without .klwp extension)"
                    }
                },
                "required": ["preset_name"]
            }
        ),
        Tool(
            name="list_elements",
            description=(
                "List all elements in a KLWP preset, optionally filtered by type. "
                "Returns element ID, type, position, text, and other key properties. "
                "Common types: TEXT, SHAPE, IMAGE, OVERLAP, KOMPONENT"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "preset_name": {
                        "type": "string",
                        "description": "Name of the preset file"
                    },
                    "element_type": {
                        "type": "string",
                        "description": "Optional filter by element type (e.g., 'TEXT', 'SHAPE', 'IMAGE')"
                    }
                },
                "required": ["preset_name"]
            }
        ),
        Tool(
            name="find_element",
            description=(
                "Find elements by searching for a term in element name, text, ID, or type. "
                "Case-insensitive search. Returns matching elements with their properties."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "preset_name": {
                        "type": "string",
                        "description": "Name of the preset file"
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Term to search for in element properties"
                    }
                },
                "required": ["preset_name", "search_term"]
            }
        ),
        Tool(
            name="modify_element",
            description=(
                "Modify an element's properties such as position, color, text, etc. "
                "Provide the element ID and a dictionary of properties to update. "
                "Changes are cached until save_preset is called."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "preset_name": {
                        "type": "string",
                        "description": "Name of the preset file"
                    },
                    "element_id": {
                        "type": "string",
                        "description": "ID of the element to modify"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Dictionary of properties to update (e.g., {'text': 'New Text', 'position': {'x': 100, 'y': 200}})"
                    }
                },
                "required": ["preset_name", "element_id", "properties"]
            }
        ),
        Tool(
            name="save_preset",
            description=(
                "Save modified preset back to the .klwp ZIP file. "
                "Creates a backup (.klwp.bak) by default before overwriting. "
                "Only saves if modifications were made."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "preset_name": {
                        "type": "string",
                        "description": "Name of the preset file to save"
                    },
                    "backup": {
                        "type": "boolean",
                        "description": "Whether to create a backup (default: true)"
                    }
                },
                "required": ["preset_name"]
            }
        ),
        Tool(
            name="reload_klwp",
            description=(
                "Trigger KLWP to reload presets using Android broadcast intent. "
                "Requires Termux:API and appropriate permissions. "
                "Useful after saving changes to see them in KLWP immediately."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_presets",
            description=(
                "List all available KLWP preset files in the wallpapers directory. "
                "Returns a list of .klwp filenames."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for KLWP manipulation."""
    try:
        if name == "read_klwp_preset":
            preset_name = arguments["preset_name"]
            data = klwp.read_preset(preset_name)

            # Return formatted JSON
            return [
                TextContent(
                    type="text",
                    text=json.dumps(data, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "list_elements":
            preset_name = arguments["preset_name"]
            element_type = arguments.get("element_type")

            elements = klwp.list_elements(preset_name, element_type)

            # Format elements for readability
            result = {
                "preset": preset_name,
                "count": len(elements),
                "elements": [
                    {
                        "id": elem.get("id"),
                        "type": elem.get("type"),
                        "path": elem.get("path"),
                        "text": elem.get("text"),
                        "title": elem.get("title"),
                        "position": elem.get("position"),
                    }
                    for elem in elements
                ]
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "find_element":
            preset_name = arguments["preset_name"]
            search_term = arguments["search_term"]

            elements = klwp.find_element(preset_name, search_term)

            result = {
                "preset": preset_name,
                "search_term": search_term,
                "matches": len(elements),
                "elements": [
                    {
                        "id": elem.get("id"),
                        "type": elem.get("type"),
                        "path": elem.get("path"),
                        "text": elem.get("text"),
                        "title": elem.get("title"),
                        "position": elem.get("position"),
                    }
                    for elem in elements
                ]
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "modify_element":
            preset_name = arguments["preset_name"]
            element_id = arguments["element_id"]
            properties = arguments["properties"]

            updated_element = klwp.modify_element(preset_name, element_id, properties)

            result = {
                "preset": preset_name,
                "element_id": element_id,
                "status": "modified",
                "updated_properties": properties,
                "note": "Changes cached. Call save_preset to persist."
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "save_preset":
            preset_name = arguments["preset_name"]
            backup = arguments.get("backup", True)

            saved_path = klwp.save_preset(preset_name, backup)

            result = {
                "preset": preset_name,
                "status": "saved",
                "path": saved_path,
                "backup_created": backup
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "reload_klwp":
            # Use Android broadcast to reload KLWP
            # This requires termux-api package
            try:
                # KLWP typically listens to broadcasts for reload
                # Common broadcast: org.kustom.wallpaper.RELOAD
                result = subprocess.run(
                    [
                        "am", "broadcast",
                        "-a", "org.kustom.wallpaper.RELOAD",
                        "-n", "org.kustom.wallpaper/.Receiver"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    response = {
                        "status": "success",
                        "message": "KLWP reload broadcast sent",
                        "output": result.stdout.strip()
                    }
                else:
                    response = {
                        "status": "warning",
                        "message": "Broadcast command executed but may have failed",
                        "error": result.stderr.strip(),
                        "note": "Ensure Termux has permission to send broadcasts and KLWP is installed"
                    }

            except FileNotFoundError:
                response = {
                    "status": "error",
                    "message": "Android 'am' command not found",
                    "note": "This feature requires running on Android"
                }
            except subprocess.TimeoutExpired:
                response = {
                    "status": "error",
                    "message": "Broadcast command timed out"
                }
            except Exception as e:
                response = {
                    "status": "error",
                    "message": f"Failed to send broadcast: {str(e)}"
                }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "list_presets":
            presets = klwp.list_presets()

            result = {
                "directory": str(klwp.presets_dir),
                "count": len(presets),
                "presets": presets
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except FileNotFoundError as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": "FileNotFoundError",
                    "message": str(e),
                    "suggestion": "Check that the preset file exists and the path is correct"
                }, indent=2)
            )
        ]
    except ValueError as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": "ValueError",
                    "message": str(e)
                }, indent=2)
            )
        ]
    except Exception as e:
        logger.error(f"Error in {name}: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": type(e).__name__,
                    "message": str(e)
                }, indent=2)
            )
        ]


async def main():
    """Run the MCP server using stdio transport."""
    logger.info("Starting KLWP MCP Server")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
