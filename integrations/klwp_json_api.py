#!/usr/bin/env python3
"""
JSON API wrapper for KLWP CLI - works with any AI model.
Input: JSON command via stdin or argument
Output: JSON result

Examples:
  echo '{"action": "list"}' | python klwp_json_api.py
  python klwp_json_api.py '{"action": "elements", "preset": "my.klwp"}'
"""

import sys
import json
import subprocess
from pathlib import Path

KLWP_CLI = Path(__file__).parent.parent / 'klwp_cli.py'


def execute_klwp(command_dict):
    """Execute KLWP command from JSON and return JSON result."""
    action = command_dict.get('action')
    preset = command_dict.get('preset')

    cmd = ['python', str(KLWP_CLI)]

    if action == 'list':
        cmd.append('list')

    elif action == 'read':
        cmd.extend(['read', preset])

    elif action == 'elements':
        cmd.extend(['elements', preset])
        if 'type' in command_dict:
            cmd.extend(['--type', command_dict['type']])
        cmd.append('--json')

    elif action == 'find':
        cmd.extend(['find', preset, command_dict['search']])
        cmd.append('--json')

    elif action == 'modify':
        cmd.extend(['modify', preset, command_dict['element_id']])

        # Add properties
        properties = command_dict.get('properties', {})
        if 'text' in properties:
            cmd.extend(['--text', properties['text']])
        if 'x' in properties:
            cmd.extend(['--x', str(properties['x'])])
        if 'y' in properties:
            cmd.extend(['--y', str(properties['y'])])
        if 'color' in properties:
            cmd.extend(['--color', properties['color']])

        if command_dict.get('save', False):
            cmd.append('--save')

    elif action == 'save':
        cmd.extend(['save', preset])
        if command_dict.get('no_backup'):
            cmd.append('--no-backup')

    elif action == 'reload':
        cmd.append('reload')

    else:
        return {
            "success": False,
            "error": f"Unknown action: {action}",
            "available_actions": ["list", "read", "elements", "find", "modify", "save", "reload"]
        }

    # Execute command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Try to parse as JSON, otherwise return raw output
    try:
        output = json.loads(result.stdout)
        return {
            "success": result.returncode == 0,
            "data": output,
            "error": result.stderr if result.stderr else None
        }
    except json.JSONDecodeError:
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }


def main():
    # Read JSON from stdin or argument
    if len(sys.argv) > 1:
        try:
            command = json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            print(json.dumps({
                "success": False,
                "error": f"Invalid JSON: {e}"
            }))
            return 1
    else:
        try:
            command = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "success": False,
                "error": f"Invalid JSON: {e}"
            }))
            return 1

    result = execute_klwp(command)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get('success') else 1


if __name__ == '__main__':
    sys.exit(main())
