"""
Settings Screen - API Configuration and Preferences

Terminal Chic design for configuring AI models and API keys.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from app.terminal_theme import TerminalTheme, HEADER_STYLE, INPUT_STYLE, LABEL_STYLE
import os


class SettingsScreen(Screen):
    """Settings screen with API configuration."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'

        # Main layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding=TerminalTheme.SPACING_MEDIUM,
            spacing=TerminalTheme.SPACING_MEDIUM
        )
        main_layout.md_bg_color = TerminalTheme.BG_PRIMARY

        # Header
        header = Label(
            text='[ INTEL ]',
            size_hint=(1, None),
            height=48,
            **HEADER_STYLE
        )
        main_layout.add_widget(header)

        # Scrollable settings area
        scroll = ScrollView()
        settings_content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=TerminalTheme.SPACING_LARGE
        )
        settings_content.bind(minimum_height=settings_content.setter('height'))

        # API Provider Section
        settings_content.add_widget(self._create_section_header("AI MODEL PROVIDER"))
        settings_content.add_widget(self._create_provider_buttons())

        # API Key Section
        settings_content.add_widget(self._create_section_header("API KEY"))
        self.api_key_input = self._create_api_key_input()
        settings_content.add_widget(self.api_key_input)

        # Model Selection
        settings_content.add_widget(self._create_section_header("MODEL"))
        self.model_label = Label(
            text='gemini-2.0-flash-exp',
            size_hint=(1, None),
            height=48,
            **LABEL_STYLE
        )
        settings_content.add_widget(self.model_label)

        # Status Section
        settings_content.add_widget(self._create_section_header("STATUS"))
        self.status_label = Label(
            text='Not configured',
            size_hint=(1, None),
            height=48,
            color=TerminalTheme.TEXT_TERTIARY
        )
        settings_content.add_widget(self.status_label)

        # INTEL Button (link to GitHub docs)
        intel_btn = MDFlatButton(
            text='[ INTEL ] - Read API Setup Guide',
            size_hint=(1, None),
            height=48,
            on_release=self.open_intel
        )
        settings_content.add_widget(intel_btn)

        scroll.add_widget(settings_content)
        main_layout.add_widget(scroll)

        # Bottom buttons
        button_layout = BoxLayout(
            size_hint=(1, None),
            height=56,
            spacing=TerminalTheme.SPACING_SMALL
        )

        save_btn = MDRaisedButton(
            text='SAVE',
            size_hint=(0.5, 1),
            on_release=self.save_settings
        )
        button_layout.add_widget(save_btn)

        back_btn = MDFlatButton(
            text='BACK',
            size_hint=(0.5, 1),
            on_release=self.go_back
        )
        button_layout.add_widget(back_btn)

        main_layout.add_widget(button_layout)
        self.add_widget(main_layout)

        # Load current settings
        self.load_settings()

    def _create_section_header(self, text: str) -> Label:
        """Create a section header label."""
        return Label(
            text=f'> {text}',
            size_hint=(1, None),
            height=32,
            color=TerminalTheme.ACCENT_PRIMARY,
            font_name=TerminalTheme.FONT_MONO_BOLD,
            font_size=TerminalTheme.FONT_SMALL,
            halign='left',
            valign='middle'
        )

    def _create_provider_buttons(self) -> BoxLayout:
        """Create provider selection buttons."""
        layout = BoxLayout(
            size_hint=(1, None),
            height=48,
            spacing=TerminalTheme.SPACING_SMALL
        )

        providers = ['GEMINI', 'GROQ', 'OLLAMA']
        self.provider_buttons = {}

        for provider in providers:
            btn = Button(
                text=provider,
                size_hint=(1, 1),
                background_color=TerminalTheme.BG_SECONDARY,
                color=TerminalTheme.TEXT_PRIMARY,
                font_name=TerminalTheme.FONT_MONO
            )
            btn.bind(on_release=lambda b, p=provider: self.select_provider(p))
            self.provider_buttons[provider] = btn
            layout.add_widget(btn)

        return layout

    def _create_api_key_input(self) -> TextInput:
        """Create API key input field."""
        return TextInput(
            hint_text='Enter API key...',
            password=True,
            size_hint=(1, None),
            height=48,
            multiline=False,
            background_color=TerminalTheme.BG_INPUT,
            foreground_color=TerminalTheme.TEXT_PRIMARY,
            cursor_color=TerminalTheme.ACCENT_PRIMARY,
            font_name=TerminalTheme.FONT_MONO,
            font_size=TerminalTheme.FONT_SMALL
        )

    def select_provider(self, provider: str):
        """Handle provider selection."""
        self.current_provider = provider.lower()

        # Update button states
        for name, btn in self.provider_buttons.items():
            if name == provider:
                btn.background_color = TerminalTheme.ACCENT_PRIMARY
                btn.color = TerminalTheme.BG_PRIMARY
            else:
                btn.background_color = TerminalTheme.BG_SECONDARY
                btn.color = TerminalTheme.TEXT_PRIMARY

        # Update model based on provider
        models = {
            'gemini': 'gemini-2.0-flash-exp',
            'groq': 'llama-3.3-70b-versatile',
            'ollama': 'llama3.2'
        }
        self.model_label.text = models.get(self.current_provider, 'unknown')

        # Update status
        if self.current_provider == 'ollama':
            self.status_label.text = 'Local model (no API key needed)'
            self.api_key_input.disabled = True
        else:
            self.status_label.text = 'API key required'
            self.api_key_input.disabled = False

    def load_settings(self):
        """Load current settings from environment."""
        # Check for existing API keys
        gemini_key = os.getenv('GEMINI_API_KEY')
        groq_key = os.getenv('GROQ_API_KEY')

        if gemini_key:
            self.select_provider('GEMINI')
            self.api_key_input.text = gemini_key
            self.status_label.text = 'Configured ✓'
            self.status_label.color = TerminalTheme.SUCCESS
        elif groq_key:
            self.select_provider('GROQ')
            self.api_key_input.text = groq_key
            self.status_label.text = 'Configured ✓'
            self.status_label.color = TerminalTheme.SUCCESS
        else:
            self.select_provider('GEMINI')

    def save_settings(self, instance):
        """Save settings to environment."""
        api_key = self.api_key_input.text.strip()

        if self.current_provider == 'ollama':
            # No API key needed for local
            self.status_label.text = 'Saved (local model) ✓'
            self.status_label.color = TerminalTheme.SUCCESS
        elif api_key:
            # Set environment variable
            env_var = f'{self.current_provider.upper()}_API_KEY'
            os.environ[env_var] = api_key

            # Save to config file for persistence
            self._save_to_config(env_var, api_key)

            self.status_label.text = 'Saved ✓'
            self.status_label.color = TerminalTheme.SUCCESS
        else:
            self.status_label.text = 'Error: API key required'
            self.status_label.color = TerminalTheme.ERROR

    def _save_to_config(self, key: str, value: str):
        """Save API key to config file."""
        from pathlib import Path
        config_dir = Path.home() / '.chameleon'
        config_dir.mkdir(exist_ok=True)

        config_file = config_dir / 'config.env'

        # Read existing config
        existing = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        existing[k] = v

        # Update
        existing[key] = value

        # Write back
        with open(config_file, 'w') as f:
            for k, v in existing.items():
                f.write(f'{k}={v}\n')

    def open_intel(self, instance):
        """Open INTEL.md in browser."""
        import webbrowser
        webbrowser.open('https://github.com/Aypex/Kustom_ai/blob/main/INTEL.md')

    def go_back(self, instance):
        """Return to previous screen."""
        self.manager.current = 'local_model'
