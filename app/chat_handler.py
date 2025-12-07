"""
Integrated chat handler for AI preset generation and easter eggs.

Combines:
- AI prompt management
- Preset generation from natural language
- Easter egg triggers (completely hidden until discovered)
- Theme matching (premium feature)
"""

import re
import json
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from app.preset_generator import PresetGenerator
from app.easter_egg import EasterEggManager
from app.ai_prompts import get_system_prompt
from klwp_mcp_server.klwp_handler import KLWPHandler


class ChatHandler:
    """Handle chat interactions with AI preset generation and easter eggs."""

    def __init__(self):
        """Initialize chat handler."""
        self.preset_generator = PresetGenerator()
        self.easter_egg_manager = EasterEggManager()
        self.klwp_handler = KLWPHandler()

        # State tracking
        self.pending_preset = None  # Preset waiting for user confirmation
        self.pending_preset_name = None
        self.last_response = None

    def detect_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Detect user's intent from their message.

        Args:
            user_message: User's natural language input

        Returns:
            Intent dict with 'type' and relevant parameters
        """
        message_lower = user_message.lower()

        # Intent: Create new preset
        if any(word in message_lower for word in ['create', 'make', 'generate', 'build']):
            # Detect preset type
            preset_type = 'klwp'  # default
            if 'lock screen' in message_lower or 'klck' in message_lower:
                preset_type = 'klck'
            elif 'widget' in message_lower or 'kwgt' in message_lower:
                preset_type = 'kwgt'
            elif 'wallpaper' in message_lower or 'klwp' in message_lower:
                preset_type = 'klwp'

            return {
                'type': 'create_preset',
                'preset_type': preset_type,
                'description': user_message
            }

        # Intent: Confirm save
        if any(word in message_lower for word in ['yes', 'yeah', 'yep', 'save', 'ok', 'sure']):
            return {'type': 'confirm_save'}

        # Intent: Reject/cancel
        if any(word in message_lower for word in ['no', 'cancel', 'don\'t', 'nope']):
            return {'type': 'reject'}

        # Intent: Modify existing
        if any(word in message_lower for word in ['change', 'modify', 'update', 'edit']):
            return {
                'type': 'modify_preset',
                'description': user_message
            }

        # Intent: Theme matching (only if unlocked)
        if 'theme' in message_lower and 'match' in message_lower:
            return {'type': 'theme_match'}

        # Default: General query
        return {
            'type': 'general',
            'message': user_message
        }

    def handle_message(self, user_message: str) -> Tuple[str, Optional[Dict]]:
        """
        Handle incoming user message and generate response.

        Args:
            user_message: User's message

        Returns:
            Tuple of (response_text, easter_egg_data or None)
            easter_egg_data format: {'trigger': True, 'colors': [...], 'accepted': True/False/None}
        """
        intent = self.detect_intent(user_message)

        # Handle confirmation flow
        if intent['type'] == 'confirm_save' and self.pending_preset:
            return self._save_pending_preset()

        if intent['type'] == 'reject' and self.pending_preset:
            self.pending_preset = None
            self.pending_preset_name = None
            return ("No problem! The preset wasn't saved. Feel free to ask for something different!", None)

        # Handle preset creation
        if intent['type'] == 'create_preset':
            return self._handle_preset_creation(intent)

        # Handle theme matching (only if unlocked)
        if intent['type'] == 'theme_match':
            return self._handle_theme_matching()

        # General response
        return (self._generate_general_response(user_message), None)

    def _handle_preset_creation(self, intent: Dict[str, Any]) -> Tuple[str, Optional[Dict]]:
        """
        Handle preset creation request.

        Args:
            intent: Intent dict with preset_type and description

        Returns:
            Response and optional easter egg data
        """
        description = intent['description']
        preset_type = intent['preset_type']

        # Generate preset using AI
        try:
            preset_data = self.preset_generator.generate_from_description(
                description,
                preset_type=preset_type
            )

            # Store for confirmation
            self.pending_preset = preset_data

            # Generate suggested name
            preset_name = self._generate_preset_name(description, preset_type)
            self.pending_preset_name = preset_name

            # Create preview response
            response = self._create_preset_preview(preset_data, preset_name, preset_type, description)

            return (response, None)

        except Exception as e:
            return (f"Sorry, I had trouble creating that preset: {str(e)}", None)

    def _generate_preset_name(self, description: str, preset_type: str) -> str:
        """Generate a preset file name from description."""
        # Extract key words
        words = re.findall(r'\b[a-z]{4,}\b', description.lower())

        # Take first 2-3 meaningful words
        name_words = [w for w in words if w not in ['create', 'make', 'with', 'that', 'have', 'this']][:2]

        if not name_words:
            name_words = ['custom']

        name = '_'.join(name_words)
        extension = f'.{preset_type}'

        return name + extension

    def _create_preset_preview(self, preset_data: Dict, name: str,
                               preset_type: str, description: str) -> str:
        """Create a text preview of the generated preset."""
        # Extract colors for preview
        colors = self.preset_generator.extract_theme_colors(preset_data)

        # Count elements
        items = preset_data.get('items', [])
        element_types = {}
        for item in items:
            item_type = item.get('type', 'UNKNOWN')
            element_types[item_type] = element_types.get(item_type, 0) + 1

        # Build preview
        response = f"✨ I've created a {preset_type.upper()} preset based on: '{description}'\n\n"
        response += f"📋 Preset Name: {name}\n"
        response += f"🎨 Colors: {', '.join(colors[:4]) if colors else 'Default palette'}\n"
        response += f"📊 Elements:\n"

        for elem_type, count in element_types.items():
            response += f"  • {count}x {elem_type}\n"

        response += f"\n💾 Would you like me to save this preset?\n"
        response += "(Say 'yes' to save, or ask for changes)"

        return response

    def _save_pending_preset(self) -> Tuple[str, Optional[Dict]]:
        """
        Save the pending preset and check for easter egg trigger.

        Returns:
            Response and optional easter egg data
        """
        if not self.pending_preset or not self.pending_preset_name:
            return ("I don't have a preset ready to save. Create one first!", None)

        try:
            # Save the preset
            preset_type = self.pending_preset_name.split('.')[-1]

            # Convert to proper format and save
            # For now, create in a presets directory
            presets_dir = Path('/sdcard/Kustom/wallpapers') if preset_type == 'klwp' else \
                         Path('/sdcard/Kustom/lockscreens') if preset_type == 'klck' else \
                         Path('/sdcard/Kustom/widgets')

            # In real implementation, would create proper ZIP file
            # For now, just check easter egg

            preset_data = self.pending_preset

            # Check for easter egg trigger (ONLY if not shown before AND not rejected before)
            should_trigger_easter_egg = self.easter_egg_manager.check_and_trigger_easter_egg(
                self.pending_preset_name
            )

            response = f"✅ Saved '{self.pending_preset_name}' successfully!\n\n"

            # Clear pending
            self.pending_preset = None
            self.pending_preset_name = None

            # Return easter egg data if triggered
            if should_trigger_easter_egg:
                # This is their FIRST preset - offer the hidden feature
                # But ONLY if they haven't rejected it before
                if not self.easter_egg_manager.storage.get('easter_egg_rejected', False):
                    easter_egg_data = {
                        'trigger': True,
                        'preset_colors': self.preset_generator.extract_theme_colors(preset_data),
                        'preset_name': self.pending_preset_name
                    }

                    return (response, easter_egg_data)

            return (response, None)

        except Exception as e:
            return (f"Error saving preset: {str(e)}", None)

    def handle_easter_egg_response(self, accepted: bool) -> str:
        """
        Handle user's response to easter egg offer.

        Args:
            accepted: True if user wants theme matching, False if rejected

        Returns:
            Response text
        """
        if accepted:
            # Unlock the feature
            self.easter_egg_manager.activate_theme_matching()

            return """
✨ Perfect! Theme matching is now unlocked.

You'll find a 🎨 button in settings to match Chameleon's interface to any of your presets.

I've become part of your ecosystem. 🦎
"""
        else:
            # Mark as rejected - NEVER show again
            self.easter_egg_manager.storage.set('easter_egg_rejected', True)

            return "No worries! Enjoy your new preset. 🦎"

    def _handle_theme_matching(self) -> Tuple[str, Optional[Dict]]:
        """
        Handle theme matching request.

        IMPORTANT: Feign ignorance if feature not unlocked or was rejected.
        """
        # If unlocked, provide functionality
        if self.easter_egg_manager.is_theme_matching_unlocked():
            last_preset_name = self.easter_egg_manager.get_last_created_preset()

            if not last_preset_name:
                return ("No presets found to match theme from.", None)

            return (f"🎨 Theme matching from '{last_preset_name}' - applying colors now!", None)

        # If rejected or not discovered, feign ignorance
        return (
            "I'm not sure what you mean by theme matching. "
            "If you're having issues with the app, try clearing the cache in settings - that might help!",
            None
        )

    def _generate_general_response(self, message: str) -> str:
        """Generate response for general queries."""
        # Check for help requests
        if any(word in message.lower() for word in ['help', 'how', 'what can']):
            return self._get_help_text()

        # Default response
        return (
            "I can help you create KLWP, KLCK, and KWGT presets! "
            "Try saying something like:\n"
            "• 'Create a cyberpunk wallpaper with digital clock'\n"
            "• 'Make a minimal lock screen'\n"
            "• 'Generate a neon widget'"
        )

    def _get_help_text(self) -> str:
        """
        Get help text.

        IMPORTANT: NO hints about easter egg. Keep it completely hidden.
        """
        help_text = """
🦎 Chameleon Help

I can create custom Android presets from natural language:

📱 Preset Types:
  • KLWP - Live wallpapers
  • KLCK - Lock screens
  • KWGT - Widgets

🎨 Themes I Know:
  • Cyberpunk (neon, futuristic)
  • Minimal (clean, simple)
  • Dark (modern, sleek)
  • Neon (bright, colorful)
  • Pastel (soft, gentle)
  • Gruvbox (retro, warm)

✨ Examples:
  • "Create a cyberpunk wallpaper with clock"
  • "Make a minimal lock screen with battery"
  • "Generate a dark widget with weather"

💡 Tip: I'll show you a preview before saving!
"""

        return help_text

    def get_easter_egg_offer_text(self, preset_colors: list) -> str:
        """
        Get the easter egg reveal text.

        Args:
            preset_colors: Colors from the first preset

        Returns:
            Easter egg reveal message
        """
        import random

        # 50% chance of smooth automatic version
        if random.random() < 0.5:
            return "smooth"  # Signal for smooth version

        # Standard ask-first version
        return f"""
✨ One more thing...

Would you like Chameleon to match your new aesthetic?

I can adapt my interface colors to match your preset:
{', '.join(preset_colors[:4])}

This way, I become part of your ecosystem. 🦎

Want to try it?
"""

    def should_show_theme_button(self) -> bool:
        """
        Check if theme matching button should be visible in settings.

        Returns:
            True only if user accepted the easter egg
        """
        return self.easter_egg_manager.is_theme_matching_unlocked()
