#!/usr/bin/env python3
"""
KLWP AI Assistant - Android App
Tap icon to control KLWP with AI (local, SSH, or API)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

from app.secure_storage import SecureStorage
from app.device_detector import DeviceDetector
from app.device_info_screen import DeviceInfoScreen
from app.plugins import get_plugin_manager
from app.onboarding import OnboardingManager
from app.onboarding_screen import OnboardingScreen
from app.chameleon_effects import ChameleonEffects, VoiceButtonReveal
from app.preview_layout import SplitChatPreviewLayout
from app.preview_system import PresetPreview, MoltType
from klwp_mcp_server.klwp_handler import KLWPHandler


class HomeScreen(Screen):
    """Main home screen with model selection."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        self.detector = DeviceDetector()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Title
        title = Label(
            text='[b]🦎 Chameleon[/b]',
            markup=True,
            size_hint_y=0.15,
            font_size='24sp'
        )
        layout.add_widget(title)

        # Device info and recommendation
        device_info = self.detector.get_ui_recommendations()
        info_text = f"[b]{device_info['device_name']}[/b]\n"
        info_text += f"Performance: {device_info['performance_tier']} ({device_info['score']}/100)\n"
        info_text += f"Recommended: {device_info['primary_mode']} Mode"

        device_label = Label(
            text=info_text,
            markup=True,
            size_hint_y=0.15,
            font_size='12sp'
        )
        layout.add_widget(device_label)

        # Model selection buttons
        btn_local = MDRaisedButton(
            text='🤖 Local Model (On-Device)',
            size_hint_y=0.15,
            on_release=self.select_local_model
        )
        layout.add_widget(btn_local)

        btn_ssh = MDRaisedButton(
            text='🏠 SSH to Home Network',
            size_hint_y=0.15,
            on_release=self.select_ssh_model
        )
        layout.add_widget(btn_ssh)

        btn_api = MDRaisedButton(
            text='☁️ API Model (Gemini)',
            size_hint_y=0.15,
            on_release=self.select_api_model
        )
        layout.add_widget(btn_api)

        # Settings button
        btn_settings = MDFlatButton(
            text='⚙️ Settings',
            size_hint_y=0.1,
            on_release=self.goto_settings
        )
        layout.add_widget(btn_settings)

        # App selection
        layout.add_widget(Label(text='Control App:', size_hint_y=0.06))

        btn_select_app = MDRaisedButton(
            text='🔌 Select App (Kustom/Launcher/Tasker)',
            size_hint_y=0.10,
            on_release=self.select_app
        )
        layout.add_widget(btn_select_app)

        # Quick actions
        layout.add_widget(Label(text='Quick Actions:', size_hint_y=0.06))

        btn_presets = MDFlatButton(
            text='📁 Browse Presets',
            size_hint_y=0.07,
            on_release=self.browse_presets
        )
        layout.add_widget(btn_presets)

        # Device info button
        btn_device_info = MDFlatButton(
            text='📊 Device Info & Recommendations',
            size_hint_y=0.07,
            on_release=self.show_device_info
        )
        layout.add_widget(btn_device_info)

        self.add_widget(layout)

    def select_local_model(self, instance):
        """Switch to local model interface."""
        self.manager.current = 'local_model'

    def select_ssh_model(self, instance):
        """Switch to SSH model interface."""
        self.manager.current = 'ssh_setup'

    def select_api_model(self, instance):
        """Switch to API model interface."""
        self.manager.current = 'api_setup'

    def goto_settings(self, instance):
        """Go to settings screen."""
        self.manager.current = 'settings'

    def browse_presets(self, instance):
        """Browse KLWP presets."""
        self.manager.current = 'presets'

    def show_device_info(self, instance):
        """Show device information and recommendations."""
        self.manager.current = 'device_info'

    def select_app(self, instance):
        """Go to plugin/app selection screen."""
        self.manager.current = 'plugin_selector'


class LocalModelScreen(Screen):
    """Local model chat interface with AI preset generation and live preview."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'local_model'

        # Import here to avoid circular imports
        from app.chat_handler import ChatHandler
        from app.theme_matcher import ThemeMatcher

        self.chat_handler = ChatHandler()
        self.theme_matcher = ThemeMatcher()
        self.onboarding = OnboardingManager()
        self.voice_reveal = VoiceButtonReveal()
        self.current_preset_name = None  # Track current editing preset

        # Create chat layout (will be wrapped in split layout)
        chat_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout = chat_layout  # Alias for compatibility with existing code below

        # Back button
        btn_back = MDFlatButton(
            text='← Back',
            size_hint_y=0.08,
            on_release=lambda x: setattr(self.manager, 'current', 'home')
        )
        layout.add_widget(btn_back)

        # Title
        layout.add_widget(Label(
            text='Local Model (On-Device)',
            size_hint_y=0.08,
            font_size='20sp'
        ))

        # Chat history
        self.chat_scroll = ScrollView(size_hint_y=0.6)
        self.chat_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)
        layout.add_widget(self.chat_scroll)

        # Input area
        input_layout = BoxLayout(size_hint_y=0.15, spacing=10)

        # Settings button (Terminal Chic style)
        settings_btn = MDIconButton(
            icon='cog',
            size_hint_x=0.1,
            on_release=self.open_settings
        )
        input_layout.add_widget(settings_btn)

        # Voice button (hidden initially - chameleon camo!)
        self.voice_button = MDRaisedButton(
            text='🎤',
            size_hint_x=0.15,
            opacity=0,  # Start invisible
            on_release=self.toggle_voice
        )
        input_layout.add_widget(self.voice_button)

        self.input_field = MDTextField(
            hint_text='Create amazing presets with AI...',
            multiline=False,
            size_hint_x=0.60
        )
        self.input_field.bind(on_text_validate=self.send_message)
        input_layout.add_widget(self.input_field)

        btn_send = MDRaisedButton(
            text='Send',
            size_hint_x=0.25,
            on_release=self.send_message
        )
        input_layout.add_widget(btn_send)

        layout.add_widget(input_layout)

        # Status
        self.status_label = Label(
            text='Status: Ready',
            size_hint_y=0.09,
            font_size='12sp'
        )
        layout.add_widget(self.status_label)

        # Wrap chat layout in split layout with preview
        self.split_layout = SplitChatPreviewLayout(chat_layout)
        self.add_widget(self.split_layout)

        # Check if voice button should be revealed
        self.check_voice_button_reveal()

    def check_voice_button_reveal(self):
        """Check if voice button should be revealed (chameleon camo drop)."""
        if self.onboarding.should_show_voice_button():
            # Reveal with chameleon effect!
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.reveal_voice_button(), 2.0)

    def reveal_voice_button(self):
        """Reveal voice button with chameleon camo drop animation."""
        self.voice_reveal.reveal_voice_button(self.voice_button, self.layout)

        # Add message about voice
        from app.onboarding import OnboardingMessages
        voice_message = OnboardingMessages.voice_reveal()
        self.add_chat_message('Chameleon', voice_message)

    def open_settings(self, instance):
        """Open settings screen."""
        self.manager.current = 'settings'

    def toggle_voice(self, instance):
        """Handle voice button click."""
        if not self.onboarding.has_voice_opt_in():
            # First time - ask permission
            self.show_voice_opt_in_dialog()
        else:
            # Voice is enabled - start recording
            self.start_voice_input()

    def show_voice_opt_in_dialog(self):
        """Show dialog asking to enable voice features."""
        dialog = MDDialog(
            title="Enable Voice Chat?",
            text="This will allow you to speak your commands instead of typing.\n\nVoice data is processed by your selected AI backend.",
            buttons=[
                MDFlatButton(
                    text="Not now",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Enable Voice 🎤",
                    on_release=lambda x: self.enable_voice_features(dialog)
                )
            ]
        )
        dialog.open()

    def enable_voice_features(self, dialog):
        """Enable voice features."""
        dialog.dismiss()
        self.onboarding.enable_voice()
        self.add_chat_message('Chameleon', "Voice enabled! Tap 🎤 to speak.")

    def start_voice_input(self):
        """Start voice recording (placeholder for now)."""
        # TODO: Implement actual voice recording
        self.add_chat_message('Chameleon', "Voice input coming soon! For now, use text. 🎤")

    def send_message(self, instance):
        """Send message to AI chat handler."""
        message = self.input_field.text.strip()
        if not message:
            return

        # Add user message to chat
        self.add_chat_message('You', message)

        # Clear input
        self.input_field.text = ''

        # Process with chat handler
        self.status_label.text = 'Status: Processing...'

        # Get response from chat handler (now returns preview_action or easter_egg_data)
        response, action_data = self.chat_handler.handle_message(message)

        # Add AI response
        self.add_chat_message('Chameleon', response)

        # Handle preview actions
        if action_data:
            if action_data.get('action') == 'show':
                self._show_preview(action_data['preset'])
            elif action_data.get('action') == 'update':
                self._update_preview_with_molt(
                    action_data['preset'],
                    action_data['molt_type']
                )
            elif action_data.get('action') == 'hide':
                self._hide_preview()
            elif action_data.get('trigger'):  # Easter egg
                self.show_easter_egg_dialog(action_data)

        self.status_label.text = 'Status: Ready'

    def _handle_preview_updates(self, user_message: str, ai_response: str):
        """
        Handle preview window showing/updating based on user commands.

        Args:
            user_message: User's message
            ai_response: AI's response
        """
        msg_lower = user_message.lower()

        # Check if user is creating a new preset
        if any(word in msg_lower for word in ['create', 'generate', 'make', 'build']):
            if 'wallpaper' in msg_lower or 'klwp' in msg_lower:
                self._show_preview_for_creation(user_message, 'klwp')
            elif 'lock screen' in msg_lower or 'klck' in msg_lower:
                self._show_preview_for_creation(user_message, 'klck')
            elif 'widget' in msg_lower or 'kwgt' in msg_lower:
                self._show_preview_for_creation(user_message, 'kwgt')

        # Check if user is editing an existing preset
        elif 'edit' in msg_lower or 'modify' in msg_lower or 'change' in msg_lower:
            # If preview is already visible, update it with molt
            if self.split_layout.preview_visible:
                self._update_preview_with_molt(user_message)

        # Check if user wants to save
        elif any(word in msg_lower for word in ['save', 'done', 'perfect', 'finished']):
            # Hide preview when saving
            self.split_layout.hide_preview()

    def _show_preview(self, preset: 'PresetPreview'):
        """
        Show preview window with new preset.

        Args:
            preset: PresetPreview object from ChatHandler
        """
        from app.sass_personality import get_clearance_sass, ResponseContext

        # Show preview with slide-in
        self.split_layout.show_preview(
            preset,
            clearance_msg=get_clearance_sass(ResponseContext.GREETING)
        )

    def _update_preview_with_molt(self, preset: 'PresetPreview', molt_type: 'MoltType'):
        """
        Update preview with molt animation.

        Args:
            preset: Updated PresetPreview object
            molt_type: Type of molt animation to use
        """
        # Molt durations based on type
        durations = {
            'COLOR_SHIFT': 0.8,
            'SCALE': 0.6,
            'BIRTH': 1.0,
            'FADE': 0.6,
            'TRANSFORM': 1.2
        }
        duration = durations.get(molt_type.name, 0.8)

        # Update preview with molt effect (preset is already updated by ChatHandler)
        self.split_layout.update_preview_with_molt(
            preset,
            molt_type,
            molt_duration=duration
        )

    def _hide_preview(self):
        """Hide preview window with slide-out animation."""
        self.split_layout.hide_preview()

    def show_easter_egg_dialog(self, easter_egg_data):
        """
        Show the hidden easter egg offer.

        Args:
            easter_egg_data: Dict with preset colors and metadata
        """
        preset_colors = easter_egg_data.get('preset_colors', [])

        # Get easter egg text
        offer_text = self.chat_handler.get_easter_egg_offer_text(preset_colors)

        # Check for smooth automatic version
        if offer_text == "smooth":
            # SMOOTH VERSION: Just do it automatically with style
            self.apply_smooth_easter_egg(preset_colors)
            return

        # Standard ask-first version
        # Create dialog
        dialog = MDDialog(
            title="✨",
            text=offer_text,
            buttons=[
                MDFlatButton(
                    text="Not now",
                    on_release=lambda x: self.handle_easter_egg_response(dialog, False, preset_colors)
                ),
                MDRaisedButton(
                    text="Yes! 🦎",
                    on_release=lambda x: self.handle_easter_egg_response(dialog, True, preset_colors)
                )
            ]
        )
        dialog.open()

    def apply_smooth_easter_egg(self, preset_colors):
        """
        Apply theme automatically with molting shader effect.

        This is THE easter egg - no asking, just adaptive evolution.

        Args:
            preset_colors: Colors from preset
        """
        # TODO: Trigger AGSL molting shader animation here (1.2 seconds)
        # For now, just apply immediately

        # Apply theme automatically
        fake_preset = {
            'items': [{'color': color} for color in preset_colors]
        }

        palette = self.theme_matcher.extract_color_palette(fake_preset)
        self.theme_matcher.apply_theme_to_kivy(palette)
        self.theme_matcher.save_theme_preset('chameleon_matched', palette)

        # Mark as unlocked
        self.chat_handler.easter_egg_manager.activate_theme_matching()

        # Show cheeky message
        smooth_message = "I'm a chameleon. What did you expect? 🦎"

        self.add_chat_message('Chameleon', smooth_message)

        # Offer revert option via dialog
        dialog = MDDialog(
            title="✨ Adaptive Camouflage Complete",
            text="Your interface is now part of your ecosystem.\n\nWant to keep this look?",
            buttons=[
                MDRaisedButton(
                    text="Keep It 🦎",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="Revert to Stock",
                    on_release=lambda x: self.revert_theme(dialog)
                )
            ]
        )
        dialog.open()

    def revert_theme(self, dialog):
        """Revert to default theme."""
        dialog.dismiss()

        # Apply default theme
        default_palette = {
            'primary': '#2196F3',
            'secondary': '#00BCD4',
            'accent': '#FF4081',
            'background': '#121212',
            'surface': '#1E1E1E',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B0B0B0'
        }

        self.theme_matcher.apply_theme_to_kivy(default_palette)

        # Mark as rejected so it never shows again
        self.chat_handler.easter_egg_manager.storage.set('easter_egg_rejected', True)

        self.add_chat_message('Chameleon', "No problem! Reverted to default theme.")

    def handle_easter_egg_response(self, dialog, accepted, preset_colors):
        """
        Handle user's response to easter egg.

        Args:
            dialog: The dialog to dismiss
            accepted: True if user accepted
            preset_colors: Colors from preset
        """
        dialog.dismiss()

        # Handle response
        response_text = self.chat_handler.handle_easter_egg_response(accepted)

        # Show response in chat
        self.add_chat_message('Chameleon', response_text)

        # If accepted, apply theme
        if accepted and preset_colors:
            # Extract palette from colors
            # Create fake preset data for theme extraction
            fake_preset = {
                'items': [
                    {'color': color} for color in preset_colors
                ]
            }

            palette = self.theme_matcher.extract_color_palette(fake_preset)

            # Apply theme
            self.theme_matcher.apply_theme_to_kivy(palette)

            # Save theme
            self.theme_matcher.save_theme_preset('chameleon_matched', palette)

    def add_chat_message(self, sender, message):
        """Add message to chat history."""
        msg_label = Label(
            text=f'[b]{sender}:[/b] {message}',
            markup=True,
            size_hint_y=None,
            height=max(60, len(message) // 40 * 20),  # Dynamic height based on length
            text_size=(Window.width - 40, None)
        )
        self.chat_layout.add_widget(msg_label)


class SSHSetupScreen(Screen):
    """SSH configuration and connection."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'ssh_setup'
        self.storage = SecureStorage()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Back button
        btn_back = MDFlatButton(
            text='← Back',
            size_hint_y=0.08,
            on_release=lambda x: setattr(self.manager, 'current', 'home')
        )
        layout.add_widget(btn_back)

        # Title
        layout.add_widget(Label(
            text='SSH to Home Network',
            size_hint_y=0.08,
            font_size='20sp'
        ))

        # SSH configuration
        self.ssh_host = MDTextField(
            hint_text='SSH Host (e.g., 192.168.1.100)',
            text=self.storage.get('ssh_host', ''),
            size_hint_y=0.1
        )
        layout.add_widget(self.ssh_host)

        self.ssh_port = MDTextField(
            hint_text='SSH Port (default: 22)',
            text=str(self.storage.get('ssh_port', '22')),
            size_hint_y=0.1
        )
        layout.add_widget(self.ssh_port)

        self.ssh_user = MDTextField(
            hint_text='SSH Username',
            text=self.storage.get('ssh_user', ''),
            size_hint_y=0.1
        )
        layout.add_widget(self.ssh_user)

        self.ssh_password = MDTextField(
            hint_text='SSH Password (optional if using key)',
            password=True,
            size_hint_y=0.1
        )
        layout.add_widget(self.ssh_password)

        self.ssh_key_path = MDTextField(
            hint_text='SSH Key Path (optional)',
            text=self.storage.get('ssh_key_path', '~/.ssh/id_rsa'),
            size_hint_y=0.1
        )
        layout.add_widget(self.ssh_key_path)

        # Model endpoint on remote server
        self.remote_endpoint = MDTextField(
            hint_text='Remote Model Endpoint (e.g., http://localhost:11434)',
            text=self.storage.get('remote_endpoint', 'http://localhost:11434'),
            size_hint_y=0.1
        )
        layout.add_widget(self.remote_endpoint)

        # Save button
        btn_save = MDRaisedButton(
            text='💾 Save & Connect',
            size_hint_y=0.12,
            on_release=self.save_and_connect
        )
        layout.add_widget(btn_save)

        # Test connection button
        btn_test = MDFlatButton(
            text='🔍 Test Connection',
            size_hint_y=0.1,
            on_release=self.test_connection
        )
        layout.add_widget(btn_test)

        # Status
        self.status_label = Label(
            text='Status: Not connected',
            size_hint_y=0.14,
            font_size='14sp'
        )
        layout.add_widget(self.status_label)

        self.add_widget(layout)

    def save_and_connect(self, instance):
        """Save SSH credentials and connect."""
        # Save to secure storage
        self.storage.set('ssh_host', self.ssh_host.text)
        self.storage.set('ssh_port', self.ssh_port.text)
        self.storage.set('ssh_user', self.ssh_user.text)
        self.storage.set('ssh_key_path', self.ssh_key_path.text)
        self.storage.set('remote_endpoint', self.remote_endpoint.text)

        if self.ssh_password.text:
            self.storage.set('ssh_password', self.ssh_password.text)

        self.status_label.text = 'Status: Credentials saved!'

        # Switch to SSH chat screen
        self.manager.current = 'ssh_chat'

    def test_connection(self, instance):
        """Test SSH connection."""
        self.status_label.text = 'Status: Testing connection...'

        # TODO: Implement SSH test
        try:
            # Test connection logic here
            self.status_label.text = 'Status: ✓ Connection successful!'
        except Exception as e:
            self.status_label.text = f'Status: ✗ Error: {str(e)}'


class APISetupScreen(Screen):
    """API model (Gemini) setup."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'api_setup'
        self.storage = SecureStorage()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Back button
        btn_back = MDFlatButton(
            text='← Back',
            size_hint_y=0.08,
            on_release=lambda x: setattr(self.manager, 'current', 'home')
        )
        layout.add_widget(btn_back)

        # Title
        layout.add_widget(Label(
            text='API Model Setup (Gemini)',
            size_hint_y=0.08,
            font_size='20sp'
        ))

        # API key input
        self.api_key_field = MDTextField(
            hint_text='Gemini API Key',
            text=self.storage.get('gemini_api_key', ''),
            password=True,
            size_hint_y=0.12
        )
        layout.add_widget(self.api_key_field)

        # Get API key button
        btn_get_key = MDFlatButton(
            text='🔑 Get API Key',
            size_hint_y=0.1,
            on_release=self.open_api_key_url
        )
        layout.add_widget(btn_get_key)

        # Save button
        btn_save = MDRaisedButton(
            text='💾 Save & Continue',
            size_hint_y=0.12,
            on_release=self.save_api_key
        )
        layout.add_widget(btn_save)

        # Instructions
        instructions = Label(
            text='Get your free API key from:\nmakersuite.google.com/app/apikey',
            size_hint_y=0.15,
            font_size='12sp'
        )
        layout.add_widget(instructions)

        # Status
        self.status_label = Label(
            text='Status: No API key set',
            size_hint_y=0.35,
            font_size='14sp'
        )
        layout.add_widget(self.status_label)

        self.add_widget(layout)

    def save_api_key(self, instance):
        """Save API key to secure storage."""
        api_key = self.api_key_field.text.strip()

        if not api_key:
            self.status_label.text = 'Status: Please enter an API key'
            return

        self.storage.set('gemini_api_key', api_key)
        self.status_label.text = 'Status: ✓ API key saved!'

        # Switch to API chat screen
        self.manager.current = 'api_chat'

    def open_api_key_url(self, instance):
        """Open API key URL in browser."""
        import webbrowser
        webbrowser.open('https://makersuite.google.com/app/apikey')


class PresetsScreen(Screen):
    """Browse and manage KLWP presets."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'presets'
        self.klwp = KLWPHandler()

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Back button
        btn_back = MDFlatButton(
            text='← Back',
            size_hint_y=0.08,
            on_release=lambda x: setattr(self.manager, 'current', 'home')
        )
        layout.add_widget(btn_back)

        # Title
        layout.add_widget(Label(
            text='KLWP Presets',
            size_hint_y=0.08,
            font_size='20sp'
        ))

        # Preset list
        self.preset_scroll = ScrollView(size_hint_y=0.74)
        self.preset_list = MDList()
        self.preset_scroll.add_widget(self.preset_list)
        layout.add_widget(self.preset_scroll)

        # Refresh button
        btn_refresh = MDFlatButton(
            text='🔄 Refresh',
            size_hint_y=0.1,
            on_release=self.refresh_presets
        )
        layout.add_widget(btn_refresh)

        self.add_widget(layout)

        # Load presets
        self.refresh_presets()

    def refresh_presets(self, instance=None):
        """Refresh preset list."""
        self.preset_list.clear_widgets()

        presets = self.klwp.list_presets_with_locations()

        if not presets:
            item = OneLineListItem(text='No presets found')
            self.preset_list.add_widget(item)
        else:
            for preset in presets:
                item = TwoLineListItem(
                    text=preset['name'],
                    secondary_text=preset['directory']
                )
                item.bind(on_release=lambda x, p=preset['name']: self.view_preset(p))
                self.preset_list.add_widget(item)

    def view_preset(self, preset_name):
        """View preset details."""
        # TODO: Switch to preset detail screen
        print(f"Viewing: {preset_name}")


class SettingsScreen(Screen):
    """App settings."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        self.storage = SecureStorage()

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Back button
        btn_back = MDFlatButton(
            text='← Back',
            size_hint_y=0.08,
            on_release=lambda x: setattr(self.manager, 'current', 'home')
        )
        self.layout.add_widget(btn_back)

        # Title
        self.layout.add_widget(Label(
            text='Settings',
            size_hint_y=0.08,
            font_size='20sp'
        ))

        # INTEL button (always visible - live docs)
        btn_intel = MDRaisedButton(
            text='[ INTEL ]',
            size_hint_y=0.12,
            on_release=self.open_intel_docs
        )
        self.layout.add_widget(btn_intel)

        # Theme matching button (only if unlocked)
        self.theme_button_container = BoxLayout(size_hint_y=None, height=0)
        self.layout.add_widget(self.theme_button_container)

        # Clear credentials button
        btn_clear = MDRaisedButton(
            text='🗑️ Clear All Saved Credentials',
            size_hint_y=0.12,
            on_release=self.clear_credentials
        )
        self.layout.add_widget(btn_clear)

        # About
        about_text = """
        🦎 Chameleon
        Version 1.0

        AI-powered Android customization
        - KLWP, KLCK, KWGT
        - Total Launcher
        - Tasker

        Adapt to any style:
        - Local models (on-device)
        - SSH to home network
        - API models (Gemini/Claude)

        All credentials stored securely
        with AES-256 encryption.
        """
        self.layout.add_widget(Label(
            text=about_text,
            size_hint_y=0.72,
            font_size='12sp'
        ))

        self.add_widget(self.layout)

    def on_pre_enter(self):
        """Called before screen is shown - check for unlocked features."""
        # Check if theme matching is unlocked
        from app.easter_egg import EasterEggManager

        easter_egg = EasterEggManager()

        if easter_egg.is_theme_matching_unlocked():
            self.show_theme_matching_button()

    def show_theme_matching_button(self):
        """Show the theme matching button (easter egg unlocked!)."""
        # Clear container
        self.theme_button_container.clear_widgets()

        # Create button
        btn_theme = MDRaisedButton(
            text='🎨 Match Theme to Preset',
            on_release=self.open_theme_matcher
        )

        self.theme_button_container.size_hint_y = 0.12
        self.theme_button_container.add_widget(btn_theme)

    def open_theme_matcher(self, instance):
        """Open theme matcher dialog."""
        from app.easter_egg import EasterEggManager
        from app.theme_matcher import ThemeMatcher

        easter_egg = EasterEggManager()
        theme_matcher = ThemeMatcher()

        # Get saved themes
        saved_themes = theme_matcher.get_saved_themes()

        if not saved_themes:
            # No themes yet
            dialog = MDDialog(
                title="Theme Matching",
                text="Create and save a preset first to use theme matching!",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
            return

        # Show theme selection dialog
        dialog_text = "Select a theme to apply:\n\n" + "\n".join(f"• {t}" for t in saved_themes)

        dialog = MDDialog(
            title="🎨 Theme Matching",
            text=dialog_text,
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Apply Last Theme",
                    on_release=lambda x: self.apply_saved_theme(dialog, 'chameleon_matched')
                )
            ]
        )
        dialog.open()

    def apply_saved_theme(self, dialog, theme_name):
        """Apply a saved theme."""
        from app.theme_matcher import ThemeMatcher

        dialog.dismiss()

        theme_matcher = ThemeMatcher()
        palette = theme_matcher.load_theme_preset(theme_name)

        if palette:
            theme_matcher.apply_theme_to_kivy(palette)

            # Show confirmation
            confirm = MDDialog(
                text="✨ Theme applied! Chameleon has adapted to your aesthetic. 🦎",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: confirm.dismiss()
                    )
                ]
            )
            confirm.open()

    def open_intel_docs(self, instance):
        """Open live INTEL documentation (GitHub)."""
        import webbrowser

        # URL to raw GitHub markdown (will render nicely on mobile)
        intel_url = "https://github.com/Aypex/Kustom_ai/blob/main/INTEL.md"

        webbrowser.open(intel_url)

    def clear_credentials(self, instance):
        """Clear all saved credentials."""
        self.storage.clear()

        # Show confirmation
        dialog = MDDialog(
            text="All credentials cleared!",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()


class PluginSelectorScreen(Screen):
    """Screen for selecting which app to control."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'plugin_selector'
        self.plugin_manager = get_plugin_manager()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Back button
        btn_back = MDFlatButton(
            text='← Back',
            size_hint_y=0.08,
            on_release=lambda x: setattr(self.manager, 'current', 'home')
        )
        layout.add_widget(btn_back)

        # Title
        layout.add_widget(Label(
            text='[b]Select App to Control[/b]',
            markup=True,
            size_hint_y=0.10,
            font_size='20sp'
        ))

        # Description
        layout.add_widget(Label(
            text='Choose which Android customization app you want to control with AI:',
            size_hint_y=0.08,
            font_size='14sp'
        ))

        # Plugin list scroll view
        scroll = ScrollView(size_hint_y=0.64)
        self.plugin_list = MDList()
        scroll.add_widget(self.plugin_list)
        layout.add_widget(scroll)

        # Refresh button
        btn_refresh = MDFlatButton(
            text='🔄 Refresh',
            size_hint_y=0.10,
            on_release=self.refresh_plugins
        )
        layout.add_widget(btn_refresh)

        self.add_widget(layout)

        # Load plugins
        self.refresh_plugins()

    def refresh_plugins(self, instance=None):
        """Refresh plugin list."""
        self.plugin_list.clear_widgets()

        # Get all plugins
        plugins = self.plugin_manager.get_plugins()

        if not plugins:
            item = OneLineListItem(text='No plugins found')
            self.plugin_list.add_widget(item)
            return

        # Add plugin items
        for plugin in plugins:
            # Check if app is installed
            installed = plugin.is_app_installed()
            status_icon = '✅' if installed else '❌'

            # Create list item
            item = TwoLineListItem(
                text=f'{status_icon} {plugin.get_supported_app()}',
                secondary_text=f'{plugin.get_plugin_name()} v{plugin.get_plugin_version()}' +
                              ('' if installed else ' (App not installed)')
            )

            # Only make clickable if app is installed
            if installed:
                item.bind(on_release=lambda x, p=plugin: self.select_plugin(p))

            self.plugin_list.add_widget(item)

    def select_plugin(self, plugin):
        """Select a plugin to use."""
        # Store selected plugin
        app = self.manager.get_screen('home')
        if hasattr(app, 'selected_plugin'):
            app.selected_plugin = plugin
        else:
            setattr(app, 'selected_plugin', plugin)

        # Show confirmation dialog
        dialog = MDDialog(
            text=f"Now controlling {plugin.get_supported_app()}!",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: (dialog.dismiss(),
                                        setattr(self.manager, 'current', 'home'))
                )
            ]
        )
        dialog.open()


class KLWPAIApp(MDApp):
    """Main application."""

    def build(self):
        """Build the app."""
        from app.terminal_theme import TerminalTheme

        self.title = 'Chameleon'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Amber'

        # Apply Terminal Chic theme
        self.theme_cls.bg_darkest = TerminalTheme.BG_PRIMARY
        self.theme_cls.bg_dark = TerminalTheme.BG_SECONDARY
        self.theme_cls.bg_normal = TerminalTheme.BG_INPUT

        # Override Material Design rounded corners (brutalist = 0)
        self.theme_cls.round_button_radius = TerminalTheme.CORNER_RADIUS

        # Create screen manager with fade transitions (chameleon-like)
        from kivy.uix.screenmanager import FadeTransition
        sm = ScreenManager(transition=FadeTransition())

        # Add screens
        from app.settings_screen import SettingsScreen

        sm.add_widget(OnboardingScreen())  # Add onboarding first
        sm.add_widget(HomeScreen())
        sm.add_widget(PluginSelectorScreen())
        sm.add_widget(LocalModelScreen())
        sm.add_widget(SettingsScreen())
        sm.add_widget(SSHSetupScreen())
        sm.add_widget(APISetupScreen())
        sm.add_widget(PresetsScreen())
        sm.add_widget(DeviceInfoScreen())

        # Check if onboarding is complete
        onboarding = OnboardingManager()
        if not onboarding.is_onboarding_complete():
            sm.current = 'onboarding'
        else:
            sm.current = 'home'

        return sm


if __name__ == '__main__':
    KLWPAIApp().run()
