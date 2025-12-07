# KLWP MCP Server Setup

The KLWP MCP server is now installed! Here's how to configure it for Claude Desktop.

## Installation Complete ✅

- MCP server installed in: `/home/char/Downloads/Kustom_ai/.venv`
- Startup script created: `/home/char/Downloads/Kustom_ai/run_klwp_mcp.sh`

## Configuration for Claude Desktop

Add this entry to your Claude Desktop MCP configuration. Since you're on NixOS with home-manager, you'll need to add it to your home-manager configuration.

### Configuration to Add:

```json
"klwp": {
  "command": "bash",
  "args": ["/home/char/Downloads/Kustom_ai/run_klwp_mcp.sh"]
}
```

### Full Example (add to your existing servers):

```json
{
  "mcpServers": {
    "zen": {
      "command": "bash",
      "args": ["-c", "cd ~/.zen-mcp-server && source venv/bin/activate && python server.py"],
      "env": {
        "GOOGLE_API_KEY": "AIzaSyAbc123YourActualKeyHere456xyz"
      }
    },
    "ssh-forge": {
      "command": "node",
      "args": ["/home/char/mcp-servers/ssh-forge/index.js"],
      "env": {
        "SSH_PASSWORD": "0420"
      }
    },
    "bifrost": {
      "command": "node",
      "args": ["/home/char/mcp-servers/bifrost/index.js"]
    },
    "codeact": {
      "command": "node",
      "args": ["/home/char/codeact-mcp/index.js"]
    },
    "klwp": {
      "command": "bash",
      "args": ["/home/char/Downloads/Kustom_ai/run_klwp_mcp.sh"]
    }
  }
}
```

## For NixOS/Home-Manager Users

Since your `claude_desktop_config.json` is managed by home-manager (it's a symlink to `/nix/store/...`), you need to:

1. Find your home-manager configuration file (likely in `~/Documents/nixoscopy/` or `~/.config/home-manager/`)
2. Add the KLWP server entry to your Claude configuration
3. Rebuild with `home-manager switch`

OR use the temporary manual method:

```bash
# Temporarily edit the config directly (will be overwritten on next rebuild)
cp ~/.config/Claude/claude_desktop_config.json.backup ~/.config/Claude/claude_desktop_config.json.tmp
# Edit the tmp file to add the klwp entry
# Then replace the symlink:
rm ~/.config/Claude/claude_desktop_config.json
mv ~/.config/Claude/claude_desktop_config.json.tmp ~/.config/Claude/claude_desktop_config.json
# Restart Claude Desktop
```

## Testing the Server

Test if the server runs correctly:

```bash
/home/char/Downloads/Kustom_ai/run_klwp_mcp.sh
```

It should start without errors. Press Ctrl+C to stop.

## Available Tools

Once configured, you'll have access to these tools in Claude Desktop:

1. **read_klwp_preset** - Read and parse KLWP files
2. **list_elements** - List all elements (text, shapes, images)
3. **find_element** - Search for specific elements
4. **modify_element** - Change colors, text, positions, etc.
5. **save_preset** - Save changes with automatic backup
6. **reload_klwp** - Hot-reload KLWP (requires Android/Termux)
7. **list_presets** - Show all available presets

## Example Commands (once configured)

In Claude Desktop, you'll be able to say:

- "List all my KLWP presets"
- "Find all text elements in my wallpaper"
- "Change the clock color to #00FF00"
- "Make the weather widget bigger"
- "Show me all elements in preset.klwp"

## KLWP Preset Directories

The server searches these directories for presets:

- `/storage/emulated/0/Kustom/wallpapers` (Android)
- `/sdcard/Kustom/wallpapers` (Android)
- `/storage/emulated/0/Android/data/org.kustom.wallpaper/files`

If running on desktop for testing, you can place `.klwp` files in the project directory or modify `klwp_mcp_server/klwp_handler.py` to add your custom path.

## Notes

- This MCP server is designed primarily for Android/Termux environments
- On desktop, you can test the parsing/modification logic but won't be able to reload KLWP
- Always backs up presets before saving changes
