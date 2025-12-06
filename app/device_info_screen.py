"""Device information and recommendations screen."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivymd.uix.button import MDFlatButton

from app.device_detector import DeviceDetector


class DeviceInfoScreen(Screen):
    """Display device capabilities and AI hosting recommendations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'device_info'
        self.detector = DeviceDetector()

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Back button
        btn_back = MDFlatButton(
            text='← Back',
            size_hint_y=0.08,
            on_release=lambda x: setattr(self.manager, 'current', 'home')
        )
        layout.add_widget(btn_back)

        # Scrollable content
        scroll = ScrollView(size_hint_y=0.92)
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=10)
        content.bind(minimum_height=content.setter('height'))

        # Get device info
        info = self.detector.get_ui_recommendations()

        # Device Information
        device_text = f"""[b][size=18]Device Information[/size][/b]

[b]Device:[/b] {info['device_name']}
[b]SoC:[/b] {info['soc']}
[b]RAM:[/b] {info['ram_mb']}MB
[b]NPU:[/b] {'✓ Available' if info['has_npu'] else '✗ Not detected'}
[b]Performance:[/b] {info['performance_tier']} ({info['score']}/100)
"""

        device_label = Label(
            text=device_text,
            markup=True,
            size_hint_y=None,
            height=200,
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        content.add_widget(device_label)

        # Recommendations
        rec_text = f"""[b][size=18]Recommendations[/size][/b]

[b]Primary Mode:[/b] {info['primary_mode']}
[b]Can Use Local:[/b] {'✓ Yes' if info['can_use_local'] else '✗ Not Recommended'}
"""

        rec_label = Label(
            text=rec_text,
            markup=True,
            size_hint_y=None,
            height=120,
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        content.add_widget(rec_label)

        # Recommended models
        if info['recommended_models']:
            models_text = "[b][size=18]Recommended Local Models[/size][/b]\n\n"
            for model in info['recommended_models']:
                models_text += f"• [b]{model['name']}[/b] ({model['size']})\n"
                models_text += f"  Quality: {model['quality']} | Speed: {model['speed']}\n\n"

            models_label = Label(
                text=models_text,
                markup=True,
                size_hint_y=None,
                height=150,
                text_size=(None, None),
                halign='left',
                valign='top'
            )
            content.add_widget(models_label)

        # Warnings
        if info['warnings']:
            warn_text = "[b][size=18]⚠️ Warnings[/size][/b]\n\n"
            for warning in info['warnings']:
                warn_text += f"• {warning}\n"

            warn_label = Label(
                text=warn_text,
                markup=True,
                size_hint_y=None,
                height=100,
                text_size=(None, None),
                halign='left',
                valign='top',
                color=(1, 0.8, 0, 1)  # Orange
            )
            content.add_widget(warn_label)

        # Tips
        if info['tips']:
            tips_text = "[b][size=18]💡 Tips[/size][/b]\n\n"
            for tip in info['tips']:
                tips_text += f"• {tip}\n"

            tips_label = Label(
                text=tips_text,
                markup=True,
                size_hint_y=None,
                height=150,
                text_size=(None, None),
                halign='left',
                valign='top',
                color=(0, 1, 0.5, 1)  # Green
            )
            content.add_widget(tips_label)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        self.add_widget(layout)
