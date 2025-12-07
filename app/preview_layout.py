"""
Preview Layout - Kivy/KivyMD Implementation

Split-screen chat + preview with slide animations and molting effects.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.properties import NumericProperty, BooleanProperty, StringProperty, ObjectProperty
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock

from app.preview_system import (
    PreviewManager, PreviewState, PresetPreview,
    MoltType, get_clearance_text
)
from app.klwp_renderer import KLWPRenderer


class PreviewWindow(FloatLayout):
    """
    Preview window that slides in/out from right side.

    Contains:
    - KLWP preview rendering
    - Clearance text at bottom
    - Molt animation overlay
    """

    clearance_text = StringProperty("Working with this? 🦎")
    is_molting = BooleanProperty(False)
    molt_progress = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Preview content container
        self.preview_content = BoxLayout(orientation='vertical')

        # KLWP preview image/render
        self.preview_image = Image(
            size_hint=(1, 0.9),
            allow_stretch=True,
            keep_ratio=True
        )
        self.preview_content.add_widget(self.preview_image)

        # Clearance text at bottom
        self.clearance_label = Label(
            text=self.clearance_text,
            size_hint=(1, 0.1),
            font_name='RobotoMono-Regular',  # Monospace for Terminal Chic
            font_size='14sp',
            markup=True
        )
        self.preview_content.add_widget(self.clearance_label)

        self.add_widget(self.preview_content)

        # Bind property updates
        self.bind(clearance_text=self._update_clearance)

    def _update_clearance(self, instance, value):
        """Update clearance label text."""
        self.clearance_label.text = value

    def trigger_molt(self, molt_type: MoltType, duration: float = 0.8):
        """
        Trigger molt animation on preview.

        Args:
            molt_type: Type of molt effect
            duration: Animation duration in seconds
        """
        self.is_molting = True

        # Animate molt_progress from 0 → 1.2
        anim = Animation(
            molt_progress=1.2,
            duration=duration,
            t='out_cubic'
        )

        def molt_complete(animation, widget):
            self.is_molting = False
            self.molt_progress = 0.0

        anim.bind(on_complete=molt_complete)
        anim.start(self)

    def update_preview_image(self, image_path: str):
        """
        Update the preview image.

        Args:
            image_path: Path to preview image file
        """
        self.preview_image.source = image_path
        self.preview_image.reload()


class SplitChatPreviewLayout(BoxLayout):
    """
    Elastic split layout for chat + preview.

    Layout:
    - Chat: Left side (elastic width 0.3-1.0)
    - Preview: Right side (slides in/out, 0.7 width when visible)
    """

    preview_visible = BooleanProperty(False)
    chat_width_fraction = NumericProperty(1.0)  # 1.0 = 100% chat, 0.3 = 30% chat

    def __init__(self, chat_widget, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)

        self.chat_widget = chat_widget
        self.preview_window = PreviewWindow(size_hint_x=0)

        # Initialize KLWP renderer
        self.renderer = KLWPRenderer()

        # Add chat (elastic width)
        self.add_widget(self.chat_widget)

        # Add preview (initially hidden)
        self.add_widget(self.preview_window)

        # Bind property changes
        self.bind(preview_visible=self._on_preview_visibility_change)

    def show_preview(self, preset: PresetPreview, clearance_msg: str = ""):
        """
        Show preview with slide-in animation.

        Args:
            preset: Preset to display
            clearance_msg: Clearance text to display
        """
        if self.preview_visible:
            return  # Already visible

        self.preview_visible = True

        # Update clearance text
        self.preview_window.clearance_text = clearance_msg or \
            get_clearance_text('initial_load')

        # Render preview image if we have preset data
        if preset.preset_data:
            try:
                preview_path = self.renderer.render_preset(preset.preset_data)
                self.preview_window.update_preview_image(preview_path)
            except Exception as e:
                print(f"⚠️ Preview render failed: {e}")
                # Continue with animation even if render fails

        # Animate: Chat 100% → 30%, Preview 0% → 70%
        self._animate_split(
            chat_target=0.3,
            preview_target=0.7,
            duration=0.4
        )

    def hide_preview(self):
        """Hide preview with slide-out animation."""
        if not self.preview_visible:
            return

        self.preview_visible = False

        # Animate: Chat 30% → 100%, Preview 70% → 0%
        self._animate_split(
            chat_target=1.0,
            preview_target=0.0,
            duration=0.3
        )

    def update_preview_with_molt(self, new_preset: PresetPreview,
                                 molt_type: MoltType,
                                 molt_duration: float = 0.8):
        """
        Update preview with molt animation.

        Args:
            new_preset: Updated preset
            molt_type: Type of molt effect
            molt_duration: Molt animation duration
        """
        if not self.preview_visible:
            self.show_preview(new_preset)
            return

        # Trigger molt effect
        self.preview_window.trigger_molt(molt_type, molt_duration)

        # Update preview image after molt starts (0.5s delay for visual continuity)
        def update_after_delay(dt):
            if new_preset.preset_data:
                try:
                    preview_path = self.renderer.render_preset(new_preset.preset_data)
                    self.preview_window.update_preview_image(preview_path)
                except Exception as e:
                    print(f"⚠️ Preview update failed: {e}")

        Clock.schedule_once(update_after_delay, molt_duration * 0.5)

        # Update clearance text based on molt type
        clearance = get_clearance_text('after_edit', molt_type)
        self.preview_window.clearance_text = clearance

    def _animate_split(self, chat_target: float, preview_target: float,
                      duration: float):
        """
        Animate the split layout transition.

        Args:
            chat_target: Target width fraction for chat (0.0-1.0)
            preview_target: Target width fraction for preview (0.0-1.0)
            duration: Animation duration in seconds
        """
        # Animate chat width
        chat_anim = Animation(
            size_hint_x=chat_target,
            duration=duration,
            t='out_expo'
        )
        chat_anim.start(self.chat_widget)

        # Animate preview width
        preview_anim = Animation(
            size_hint_x=preview_target,
            duration=duration,
            t='out_expo'
        )
        preview_anim.start(self.preview_window)

        # Update width fraction property
        self.chat_width_fraction = chat_target

    def _on_preview_visibility_change(self, instance, value):
        """Handle preview visibility state changes."""
        if value:
            # Preview becoming visible
            self.preview_window.opacity = 1.0
        else:
            # Preview hiding
            def hide_after_animation(dt):
                self.preview_window.opacity = 0.0

            Clock.schedule_once(hide_after_animation, 0.3)


# Integration example
INTEGRATION_EXAMPLE = """
# How to integrate into LocalModelScreen:

from app.preview_layout import SplitChatPreviewLayout
from app.preview_system import PresetPreview, MoltType

class LocalModelScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create chat layout (existing code)
        chat_layout = BoxLayout(orientation='vertical')
        # ... add chat history, input field, etc.

        # Wrap chat in split layout
        self.split_layout = SplitChatPreviewLayout(chat_layout)
        self.add_widget(self.split_layout)

    def on_preset_edit_request(self, preset_name):
        '''User wants to edit a preset'''
        # Load preset data
        preset = PresetPreview(
            preset_name=preset_name,
            preset_type='klwp',
            preset_data=self.load_preset_json(preset_name)
        )

        # Show preview
        self.split_layout.show_preview(
            preset,
            clearance_msg=f"Editing '{preset_name}'. Continue? 🦎"
        )

    def on_ai_edit_response(self, user_command, new_preset_data):
        '''AI has generated updated preset'''
        # Create new preset object
        new_preset = PresetPreview(
            preset_name=self.current_preset_name,
            preset_type='klwp',
            preset_data=new_preset_data
        )

        # Determine molt type from command
        if 'color' in user_command.lower():
            molt_type = MoltType.COLOR_SHIFT
        elif 'bigger' in user_command.lower():
            molt_type = MoltType.SCALE
        else:
            molt_type = MoltType.TRANSFORM

        # Update with molt
        self.split_layout.update_preview_with_molt(
            new_preset,
            molt_type,
            molt_duration=0.8
        )

    def on_save_complete(self):
        '''User saved the preset'''
        # Hide preview
        self.split_layout.hide_preview()
"""


if __name__ == "__main__":
    print("🦎 PREVIEW LAYOUT SYSTEM\n")
    print("Kivy/KivyMD implementation for split-screen chat + preview\n")
    print(INTEGRATION_EXAMPLE)
