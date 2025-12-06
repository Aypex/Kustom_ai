#!/usr/bin/env python3
"""
Example usage of the KLWP Handler directly (without MCP).
This demonstrates how to use the handler programmatically.
"""

from klwp_mcp_server.klwp_handler import KLWPHandler


def main():
    # Initialize handler
    klwp = KLWPHandler()

    # List all available presets
    print("Available presets:")
    presets = klwp.list_presets()
    for preset in presets:
        print(f"  - {preset}")

    if not presets:
        print("No presets found!")
        print(f"Place .klwp files in: {klwp.presets_dir}")
        return

    # Use the first preset for example
    preset_name = presets[0]
    print(f"\nWorking with preset: {preset_name}")

    # Read the preset
    print("\n1. Reading preset...")
    data = klwp.read_preset(preset_name)
    print(f"   Preset loaded successfully")

    # List all elements
    print("\n2. Listing all elements...")
    elements = klwp.list_elements(preset_name)
    print(f"   Found {len(elements)} elements")

    for elem in elements[:5]:  # Show first 5
        print(f"   - {elem['type']}: {elem['id']}")
        if 'text' in elem:
            print(f"     Text: {elem['text']}")

    # List only TEXT elements
    print("\n3. Listing TEXT elements...")
    text_elements = klwp.list_elements(preset_name, element_type="TEXT")
    print(f"   Found {len(text_elements)} text elements")

    # Find elements containing "clock"
    print("\n4. Searching for 'clock'...")
    clock_elements = klwp.find_element(preset_name, "clock")
    print(f"   Found {len(clock_elements)} matching elements")

    # Modify an element (if any exist)
    if elements:
        print("\n5. Modifying first element...")
        first_elem = elements[0]
        elem_id = first_elem['id']

        print(f"   Modifying element: {elem_id}")
        klwp.modify_element(
            preset_name,
            elem_id,
            {
                "text": "Modified by KLWP MCP!",
                # Add other properties as needed
            }
        )
        print("   Element modified (in memory)")

        # Save the preset
        print("\n6. Saving preset...")
        saved_path = klwp.save_preset(preset_name, backup=True)
        print(f"   Saved to: {saved_path}")
        print("   Backup created: Yes")

        print("\n7. To reload KLWP, run:")
        print("   am broadcast -a org.kustom.wallpaper.RELOAD")
    else:
        print("\nNo elements found to modify")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
