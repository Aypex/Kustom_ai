#!/usr/bin/env python3
"""
Simple Gemini integration using REST API (no SDK needed).
Works immediately without waiting for package compilation!

Setup:
  export GEMINI_API_KEY="your-key"

Usage:
  python gemini_simple.py "List my KLWP presets"
  python gemini_simple.py "Show text elements in my_preset.klwp"
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

KLWP_CLI = Path(__file__).parent.parent / 'klwp_cli.py'

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"


def call_gemini(prompt, api_key):
    """Call Gemini API directly via HTTP."""
    url = f"{GEMINI_API_URL}?key={api_key}"

    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            # Extract text from response
            text = result['candidates'][0]['content']['parts'][0]['text']
            return text
    except Exception as e:
        return f"Error calling Gemini: {e}"


def execute_klwp_command(command_args):
    """Execute KLWP CLI command."""
    cmd = ['python', str(KLWP_CLI)] + command_args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def parse_intent_and_execute(user_message, api_key):
    """Use Gemini to understand user intent and suggest KLWP command."""

    # First, ask Gemini to interpret the user's request
    analysis_prompt = f"""
You are helping to control KLWP (Kustom Live Wallpaper) presets.
The user said: "{user_message}"

Available KLWP CLI commands:
- list: List all presets
- elements <preset_name>: List elements in a preset
- elements <preset_name> --type TEXT: List only TEXT elements
- find <preset_name> <search_term>: Find elements
- modify <preset_name> <element_id> --text "value" --save: Modify element

Based on the user's message, suggest the appropriate command.
Reply ONLY with the command, nothing else. If you're not sure what they want, say "unclear".

Examples:
User: "List my presets" -> list
User: "Show text elements in my.klwp" -> elements my.klwp --type TEXT
User: "Find clock" -> unclear (need preset name)
"""

    gemini_response = call_gemini(analysis_prompt, api_key)

    print(f"🤖 Gemini suggests: {gemini_response.strip()}")

    # Check if it's a valid command
    if "unclear" in gemini_response.lower():
        return f"Could you be more specific? Available commands:\n  - list\n  - elements <preset>\n  - find <preset> <term>"

    # Try to execute the command
    command_parts = gemini_response.strip().split()

    if command_parts:
        print(f"\n🔧 Executing: {' '.join(command_parts)}")
        result = execute_klwp_command(command_parts)
        print(f"\n📊 Result:\n{result}")

        # Ask Gemini to format the result nicely
        summary_prompt = f"""
The user asked: "{user_message}"
We ran this command: {' '.join(command_parts)}
Here's the result:

{result}

Please give a brief, friendly summary of the results.
"""

        summary = call_gemini(summary_prompt, api_key)
        return summary
    else:
        return "I couldn't determine what KLWP command to run."


def interactive_mode(api_key):
    """Interactive chat mode."""
    print("🤖 Simple Gemini KLWP Assistant")
    print("=" * 50)
    print("\nNo SDK needed - using REST API directly!")
    print("\nAsk me to:")
    print("  - List your presets")
    print("  - Show elements in a preset")
    print("  - Find elements")
    print("  - Modify elements")
    print("\nType 'exit' to quit\n")

    while True:
        try:
            user_input = input('\n💬 You: ').strip()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            response = parse_intent_and_execute(user_input, api_key)
            print(f"\n🤖 Assistant: {response}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    # Get API key
    api_key = os.environ.get('GEMINI_API_KEY')

    if not api_key:
        print("❌ Error: GEMINI_API_KEY not set")
        print("\nSet it with:")
        print("  export GEMINI_API_KEY='your-key-here'")
        print("\nGet an API key at: https://makersuite.google.com/app/apikey")
        sys.exit(1)

    # Check if prompt provided as argument
    if len(sys.argv) > 1:
        # Single command mode
        user_message = ' '.join(sys.argv[1:])
        response = parse_intent_and_execute(user_message, api_key)
        print(response)
    else:
        # Interactive mode
        interactive_mode(api_key)


if __name__ == '__main__':
    main()
