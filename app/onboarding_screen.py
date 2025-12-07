"""
Onboarding Screen with smooth flow.

Guides user through:
1. Backend selection (local/SSH/API)
2. Model setup
3. KLWP directory configuration
4. Workflow introduction
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineIconListItem

from app.onboarding import OnboardingManager, OnboardingMessages
from app.chameleon_effects import ChameleonEffects, TransitionHelpers
from app.secure_storage import SecureStorage


class OnboardingScreen(Screen):
    """
    Smooth onboarding flow screen.

    Dynamically adjusts based on onboarding progress.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'onboarding'

        self.onboarding = OnboardingManager()
        self.messages = OnboardingMessages()
        self.effects = ChameleonEffects()

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Header
        self.title = Label(
            text='🦎 Welcome to Chameleon',
            size_hint_y=0.1,
            font_size='24sp',
            markup=True
        )
        self.layout.add_widget(self.title)

        # Content area (dynamically populated)
        self.content_scroll = ScrollView(size_hint_y=0.7)
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.content_scroll.add_widget(self.content)
        self.layout.add_widget(self.content_scroll)

        # Action area (buttons)
        self.action_area = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=10)
        self.layout.add_widget(self.action_area)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        """Called before screen is shown - load current step."""
        self.load_current_step()

    def load_current_step(self):
        """Load the appropriate onboarding step."""
        step = self.onboarding.get_current_step()

        if step == 'backend':
            self.show_backend_selection()
        elif step == 'model':
            self.show_model_setup()
        elif step == 'directory':
            self.show_directory_selection()
        elif step == 'workflow':
            self.show_workflow_intro()
        elif step == 'complete':
            # Onboarding done, redirect to main
            self.manager.current = 'home'

    def clear_content(self):
        """Clear content area."""
        self.content.clear_widgets()
        self.action_area.clear_widgets()

    def show_backend_selection(self):
        """Show backend selection step."""
        self.clear_content()

        # Message
        message = Label(
            text=self.messages.backend_selection(),
            markup=True,
            size_hint_y=None,
            height=400,
            text_size=(self.width - 40, None)
        )
        self.content.add_widget(message)

        # Backend buttons
        btn_local = MDRaisedButton(
            text='🤖 Local (On-Device)',
            size_hint_y=None,
            height=60,
            on_release=lambda x: self.select_backend('local')
        )
        self.action_area.add_widget(btn_local)

        btn_ssh = MDRaisedButton(
            text='🏠 SSH (Home Server)',
            size_hint_y=None,
            height=60,
            on_release=lambda x: self.select_backend('ssh')
        )
        self.action_area.add_widget(btn_ssh)

        btn_api = MDRaisedButton(
            text='☁️ API (Cloud)',
            size_hint_y=None,
            height=60,
            on_release=lambda x: self.select_backend('api')
        )
        self.action_area.add_widget(btn_api)

    def select_backend(self, backend: str):
        """
        Handle backend selection.

        Args:
            backend: 'local', 'ssh', or 'api'
        """
        # Save selection
        self.onboarding.complete_backend_selection(backend, {})

        # Move to model setup
        self.show_model_setup_transition(backend)

    def show_model_setup_transition(self, backend: str):
        """Show loading/setup for model."""
        self.clear_content()

        # Loading message
        message = Label(
            text=self.messages.model_loading(backend),
            size_hint_y=None,
            height=100,
            font_size='16sp'
        )
        self.content.add_widget(message)

        # Simulate model loading (in real app, actually load/connect)
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.complete_model_setup(backend), 2.0)

    def complete_model_setup(self, backend: str):
        """
        Complete model setup and move to next step.

        Args:
            backend: Backend type
        """
        # Mark as loaded
        self.onboarding.complete_model_setup({'backend': backend, 'status': 'ready'})

        # Move to directory selection
        self.load_current_step()

    def show_model_setup(self):
        """Show model setup step (usually just loading)."""
        backend = self.onboarding.storage.get('backend_selected', 'api')
        self.show_model_setup_transition(backend)

    def show_directory_selection(self):
        """Show KLWP directory selection."""
        self.clear_content()

        # Message
        message = Label(
            text=self.messages.directory_prompt(),
            markup=True,
            size_hint_y=None,
            height=250,
            text_size=(self.width - 40, None)
        )
        self.content.add_widget(message)

        # Directory input
        self.directory_input = MDTextField(
            hint_text='KLWP Directory Path',
            text='/sdcard/Kustom/wallpapers',
            size_hint_y=None,
            height=50
        )
        self.content.add_widget(self.directory_input)

        # Common locations buttons
        for dir_path in self.messages.get_default_directories()[:3]:
            btn = MDFlatButton(
                text=f'📁 {dir_path}',
                size_hint_y=None,
                height=40,
                on_release=lambda x, p=dir_path: self.set_directory_quick(p)
            )
            self.content.add_widget(btn)

        # Continue button
        btn_continue = MDRaisedButton(
            text='Continue →',
            size_hint_y=None,
            height=60,
            on_release=lambda x: self.save_directory()
        )
        self.action_area.add_widget(btn_continue)

    def set_directory_quick(self, path: str):
        """Quickly set directory from button."""
        self.directory_input.text = path

    def save_directory(self):
        """Save KLWP directory and continue."""
        directory = self.directory_input.text.strip()

        if not directory:
            # Show error
            dialog = MDDialog(
                text="Please enter a directory path",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
            return

        # Save
        self.onboarding.set_klwp_directory(directory)

        # Move to workflow intro
        self.load_current_step()

    def show_workflow_intro(self):
        """Show workflow introduction."""
        self.clear_content()

        # Message
        message = Label(
            text=self.messages.workflow_intro(),
            markup=True,
            size_hint_y=None,
            height=400,
            text_size=(self.width - 40, None)
        )
        self.content.add_widget(message)

        # Start button
        btn_start = MDRaisedButton(
            text='Let\'s Go! 🦎',
            size_hint_y=None,
            height=70,
            on_release=lambda x: self.complete_onboarding_flow()
        )
        self.action_area.add_widget(btn_start)

    def complete_onboarding_flow(self):
        """Complete onboarding and transition to main app."""
        # Mark workflow as shown
        self.onboarding.complete_workflow_intro()

        # Mark onboarding complete
        self.onboarding.complete_onboarding()

        # Transition to home with chameleon effect
        self.manager.transition.direction = 'left'
        self.manager.current = 'home'
