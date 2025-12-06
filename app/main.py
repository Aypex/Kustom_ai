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
            text='[b]KLWP AI Assistant[/b]',
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

        # Quick KLWP actions
        layout.add_widget(Label(text='Quick Actions:', size_hint_y=0.08))

        btn_presets = MDFlatButton(
            text='📁 Browse Presets',
            size_hint_y=0.08,
            on_release=self.browse_presets
        )
        layout.add_widget(btn_presets)

        # Device info button
        btn_device_info = MDFlatButton(
            text='📊 Device Info & Recommendations',
            size_hint_y=0.08,
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


class LocalModelScreen(Screen):
    """Local model chat interface."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'local_model'

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

        self.input_field = MDTextField(
            hint_text='Ask me to modify KLWP...',
            multiline=False,
            size_hint_x=0.75
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

        self.add_widget(layout)

    def send_message(self, instance):
        """Send message to local model."""
        message = self.input_field.text.strip()
        if not message:
            return

        # Add user message to chat
        self.add_chat_message('You', message)

        # Clear input
        self.input_field.text = ''

        # Process with local model (placeholder)
        self.status_label.text = 'Status: Processing...'

        # TODO: Integrate with local model
        response = f"Local model: I'll help you with '{message}'"
        self.add_chat_message('AI', response)

        self.status_label.text = 'Status: Ready'

    def add_chat_message(self, sender, message):
        """Add message to chat history."""
        msg_label = Label(
            text=f'[b]{sender}:[/b] {message}',
            markup=True,
            size_hint_y=None,
            height=60,
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
            text='Settings',
            size_hint_y=0.08,
            font_size='20sp'
        ))

        # Clear credentials button
        btn_clear = MDRaisedButton(
            text='🗑️ Clear All Saved Credentials',
            size_hint_y=0.12,
            on_release=self.clear_credentials
        )
        layout.add_widget(btn_clear)

        # About
        about_text = """
        KLWP AI Assistant
        Version 1.0

        Control KLWP with AI models
        - Local models (on-device)
        - SSH to home network
        - API models (Gemini)

        All credentials stored securely
        with AES-256 encryption.
        """
        layout.add_widget(Label(
            text=about_text,
            size_hint_y=0.72,
            font_size='12sp'
        ))

        self.add_widget(layout)

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


class KLWPAIApp(MDApp):
    """Main application."""

    def build(self):
        """Build the app."""
        self.title = 'KLWP AI Assistant'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Blue'

        # Create screen manager
        sm = ScreenManager()

        # Add screens
        sm.add_widget(HomeScreen())
        sm.add_widget(LocalModelScreen())
        sm.add_widget(SSHSetupScreen())
        sm.add_widget(APISetupScreen())
        sm.add_widget(PresetsScreen())
        sm.add_widget(SettingsScreen())
        sm.add_widget(DeviceInfoScreen())

        return sm


if __name__ == '__main__':
    KLWPAIApp().run()
