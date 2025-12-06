#!/usr/bin/env python3
"""
Gemini integration for KLWP manipulation.
Use Google's Gemini AI to control KLWP presets via natural language.

Setup:
  pip install google-generativeai
  export GEMINI_API_KEY="your-api-key"

Usage:
  python gemini_klwp.py

Then chat:
  You: List my KLWP presets
  You: Show me text elements in my_preset.klwp
  You: Change element text_1 to say "Hello World"
"""

import os
import sys
import subprocess
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai not installed")
    print("Install with: pip install google-generativeai")
    sys.exit(1)

KLWP_CLI = Path(__file__).parent.parent / 'klwp_cli.py'


# Function implementations that Gemini can call
def klwp_list():
    """List all KLWP presets."""
    result = subprocess.run(
        ['python', str(KLWP_CLI), 'list'],
        capture_output=True,
        text=True
    )
    return result.stdout


def klwp_elements(preset, element_type=None):
    """List elements in a KLWP preset."""
    cmd = ['python', str(KLWP_CLI), 'elements', preset, '--json']
    if element_type:
        cmd.extend(['--type', element_type])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def klwp_find(preset, search_term):
    """Find elements in a preset by search term."""
    result = subprocess.run(
        ['python', str(KLWP_CLI), 'find', preset, search_term, '--json'],
        capture_output=True,
        text=True
    )
    return result.stdout


def klwp_modify(preset, element_id, text=None, x=None, y=None, color=None, save=True):
    """Modify a KLWP element's properties."""
    cmd = ['python', str(KLWP_CLI), 'modify', preset, element_id]

    if text is not None:
        cmd.extend(['--text', text])
    if x is not None:
        cmd.extend(['--x', str(x)])
    if y is not None:
        cmd.extend(['--y', str(y)])
    if color is not None:
        cmd.extend(['--color', color])
    if save:
        cmd.append('--save')

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def klwp_reload():
    """Reload KLWP to apply changes."""
    result = subprocess.run(
        ['python', str(KLWP_CLI), 'reload'],
        capture_output=True,
        text=True
    )
    return result.stdout


# Function declarations for Gemini
FUNCTION_DECLARATIONS = [
    {
        'name': 'klwp_list',
        'description': 'List all available KLWP preset files in the wallpapers directory',
        'parameters': {
            'type': 'object',
            'properties': {}
        }
    },
    {
        'name': 'klwp_elements',
        'description': 'List all elements in a KLWP preset, optionally filtered by type (TEXT, SHAPE, IMAGE, etc.)',
        'parameters': {
            'type': 'object',
            'properties': {
                'preset': {
                    'type': 'string',
                    'description': 'Name of the preset file (e.g., "my_preset.klwp")'
                },
                'element_type': {
                    'type': 'string',
                    'description': 'Optional filter by element type (TEXT, SHAPE, IMAGE, OVERLAP, KOMPONENT)'
                }
            },
            'required': ['preset']
        }
    },
    {
        'name': 'klwp_find',
        'description': 'Find elements in a preset by searching for text in element names, IDs, or content',
        'parameters': {
            'type': 'object',
            'properties': {
                'preset': {
                    'type': 'string',
                    'description': 'Name of the preset file'
                },
                'search_term': {
                    'type': 'string',
                    'description': 'Term to search for (case-insensitive)'
                }
            },
            'required': ['preset', 'search_term']
        }
    },
    {
        'name': 'klwp_modify',
        'description': 'Modify properties of a KLWP element (text, position, color, etc.)',
        'parameters': {
            'type': 'object',
            'properties': {
                'preset': {
                    'type': 'string',
                    'description': 'Name of the preset file'
                },
                'element_id': {
                    'type': 'string',
                    'description': 'ID of the element to modify'
                },
                'text': {
                    'type': 'string',
                    'description': 'New text content (for TEXT elements)'
                },
                'x': {
                    'type': 'integer',
                    'description': 'New X position in pixels'
                },
                'y': {
                    'type': 'integer',
                    'description': 'New Y position in pixels'
                },
                'color': {
                    'type': 'string',
                    'description': 'New color in hex format (e.g., "#FF0000")'
                },
                'save': {
                    'type': 'boolean',
                    'description': 'Whether to save the preset after modifying (default: true)'
                }
            },
            'required': ['preset', 'element_id']
        }
    },
    {
        'name': 'klwp_reload',
        'description': 'Send a broadcast to KLWP to reload and apply changes',
        'parameters': {
            'type': 'object',
            'properties': {}
        }
    }
]

# Map function names to implementations
FUNCTION_MAP = {
    'klwp_list': klwp_list,
    'klwp_elements': klwp_elements,
    'klwp_find': klwp_find,
    'klwp_modify': klwp_modify,
    'klwp_reload': klwp_reload
}


def main():
    # Get API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        print("\nGet an API key at: https://makersuite.google.com/app/apikey")
        sys.exit(1)

    # Configure Gemini
    genai.configure(api_key=api_key)

    # Create model with function calling
    model = genai.GenerativeModel(
        'gemini-pro',
        tools=[{'function_declarations': FUNCTION_DECLARATIONS}]
    )

    # Start chat
    chat = model.start_chat()

    print("🤖 Gemini KLWP Assistant")
    print("=" * 50)
    print("\nI can help you manage KLWP presets!")
    print("Try asking me to:")
    print("  - List your presets")
    print("  - Show elements in a preset")
    print("  - Find elements by name")
    print("  - Modify element properties")
    print("  - Reload KLWP")
    print("\nType 'exit' to quit\n")

    while True:
        try:
            user_input = input('\n💬 You: ').strip()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            # Send message to Gemini
            response = chat.send_message(user_input)

            # Check if Gemini wants to call a function
            function_calls = []
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls.append(part.function_call)

            if function_calls:
                # Execute function calls
                for function_call in function_calls:
                    function_name = function_call.name
                    args = dict(function_call.args)

                    print(f"\n🔧 Calling: {function_name}({args})")

                    # Execute the function
                    if function_name in FUNCTION_MAP:
                        result = FUNCTION_MAP[function_name](**args)
                        print(f"\n📊 Result:\n{result}")

                        # Send result back to Gemini
                        response = chat.send_message(
                            genai.protos.Content(parts=[
                                genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=function_name,
                                        response={'result': result}
                                    )
                                )
                            ])
                        )
                    else:
                        print(f"❌ Unknown function: {function_name}")

            # Display Gemini's response
            if response.text:
                print(f"\n🤖 Gemini: {response.text}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
