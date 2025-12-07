"""
Chameleon Visual Effects

Implements chameleon-themed transitions and animations:
- Camo drop (reveal elements like chameleon dropping camouflage)
- Color shift transitions (smooth color morphing)
- Adaptive animations
"""

from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from typing import Callable, Optional, Tuple
import random


class ChameleonEffects:
    """Chameleon-themed visual effects for UI transitions."""

    @staticmethod
    def camo_drop(widget: Widget, duration: float = 0.8,
                  callback: Optional[Callable] = None) -> None:
        """
        Reveal a widget like a chameleon dropping camouflage.

        Effect: Widget fades in with slight color shift.

        Args:
            widget: Widget to reveal
            duration: Animation duration in seconds
            callback: Optional callback when complete
        """
        # Start invisible
        widget.opacity = 0

        # Animate to visible
        anim = Animation(opacity=1, duration=duration, t='out_cubic')

        if callback:
            anim.bind(on_complete=lambda *args: callback())

        anim.start(widget)

    @staticmethod
    def color_morph(widget: Widget, from_color: Tuple[float, float, float, float],
                    to_color: Tuple[float, float, float, float],
                    duration: float = 0.5) -> None:
        """
        Smooth color transition like chameleon skin changing.

        Args:
            widget: Widget to color-morph
            from_color: Starting RGBA color (normalized 0-1)
            to_color: Target RGBA color (normalized 0-1)
            duration: Transition duration
        """
        # This would typically be applied to a Canvas instruction
        # For widgets with md_bg_color or similar
        if hasattr(widget, 'md_bg_color'):
            widget.md_bg_color = from_color
            anim = Animation(md_bg_color=to_color, duration=duration, t='in_out_cubic')
            anim.start(widget)

    @staticmethod
    def slide_with_morph(widget: Widget, direction: str = 'left',
                        color_from: Optional[Tuple] = None,
                        color_to: Optional[Tuple] = None,
                        duration: float = 0.6) -> None:
        """
        Slide transition with simultaneous color morphing.

        Perfect for menus sliding in with chameleon color shift.

        Args:
            widget: Widget to animate
            direction: 'left', 'right', 'up', 'down'
            color_from: Starting color (RGBA 0-1)
            color_to: Ending color (RGBA 0-1)
            duration: Animation duration
        """
        # Calculate slide distance based on direction
        start_pos = widget.pos[:]
        end_pos = widget.pos[:]

        if direction == 'left':
            widget.x = widget.x + widget.width
        elif direction == 'right':
            widget.x = widget.x - widget.width
        elif direction == 'up':
            widget.y = widget.y - widget.height
        elif direction == 'down':
            widget.y = widget.y + widget.height

        # Slide animation
        anim = Animation(pos=start_pos, duration=duration, t='out_expo')

        # Add color morph if colors provided
        if color_from and color_to and hasattr(widget, 'md_bg_color'):
            widget.md_bg_color = color_from
            color_anim = Animation(md_bg_color=color_to, duration=duration, t='in_out_cubic')
            anim &= color_anim  # Parallel animation

        anim.start(widget)

    @staticmethod
    def pulse_glow(widget: Widget, color: Tuple[float, float, float, float],
                   duration: float = 1.0, cycles: int = 1) -> None:
        """
        Subtle pulsing glow effect (chameleon eye focus).

        Args:
            widget: Widget to pulse
            color: Glow color (RGBA 0-1)
            duration: Duration per cycle
            cycles: Number of pulse cycles
        """
        if not hasattr(widget, 'md_bg_color'):
            return

        original_color = widget.md_bg_color[:]

        # Create pulse sequence
        pulse_out = Animation(md_bg_color=color, duration=duration/2, t='in_out_sine')
        pulse_in = Animation(md_bg_color=original_color, duration=duration/2, t='in_out_sine')

        sequence = pulse_out + pulse_in

        # Repeat for cycles
        for _ in range(cycles - 1):
            sequence += (pulse_out + pulse_in)

        sequence.start(widget)

    @staticmethod
    def ripple_reveal(widget: Widget, center: Tuple[float, float],
                     duration: float = 0.5) -> None:
        """
        Ripple reveal effect from a point (like chameleon color spreading).

        Args:
            widget: Widget to reveal
            center: (x, y) center point for ripple
            duration: Animation duration
        """
        # Start invisible
        widget.opacity = 0

        # Animate to visible with scale
        widget.scale = 0.5

        anim = Animation(opacity=1, scale=1, duration=duration, t='out_elastic')
        anim.start(widget)

    @staticmethod
    def get_chameleon_colors() -> list:
        """
        Get a set of chameleon-like colors for transitions.

        Returns:
            List of (R, G, B, A) tuples normalized to 0-1
        """
        # Chameleon skin tones (greens, browns, occasional blues/yellows)
        colors = [
            (0.2, 0.6, 0.2, 1.0),   # Forest green
            (0.4, 0.8, 0.3, 1.0),   # Bright green
            (0.3, 0.4, 0.2, 1.0),   # Olive
            (0.6, 0.5, 0.3, 1.0),   # Brown
            (0.2, 0.7, 0.6, 1.0),   # Teal
            (0.7, 0.8, 0.3, 1.0),   # Yellow-green
        ]
        return colors

    @staticmethod
    def random_chameleon_transition(widget: Widget, duration: float = 0.8) -> None:
        """
        Apply a random chameleon color transition.

        Args:
            widget: Widget to transition
            duration: Transition duration
        """
        colors = ChameleonEffects.get_chameleon_colors()
        target_color = random.choice(colors)

        if hasattr(widget, 'md_bg_color'):
            anim = Animation(md_bg_color=target_color, duration=duration, t='in_out_cubic')
            anim.start(widget)


class VoiceButtonReveal:
    """Special animation for voice button chameleon reveal."""

    @staticmethod
    def reveal_voice_button(button: Widget, chat_container: Widget,
                           duration: float = 1.2) -> None:
        """
        Reveal voice button with chameleon camo drop effect.

        Button starts invisible, then:
        1. Subtle pulse/glow
        2. Fade in
        3. Slight scale bounce

        Args:
            button: Voice button widget
            chat_container: Parent container
            duration: Total reveal duration
        """
        # Start invisible and small
        button.opacity = 0
        button.scale = 0.8

        # Stage 1: Subtle pre-reveal glow (0.3s)
        # Add a slight background glow effect
        if hasattr(button, 'md_bg_color'):
            glow_color = (0.3, 0.8, 0.3, 0.3)  # Subtle green glow
            pre_glow = Animation(md_bg_color=glow_color, duration=0.3, t='in_out_sine')
            pre_glow.start(button)

        # Stage 2: Fade in with scale (0.5s)
        reveal = Animation(
            opacity=1,
            scale=1.05,
            duration=0.5,
            t='out_cubic'
        )

        # Stage 3: Settle bounce (0.4s)
        settle = Animation(
            scale=1.0,
            duration=0.4,
            t='out_elastic'
        )

        # Chain animations
        sequence = reveal + settle
        sequence.start(button)


class TransitionHelpers:
    """Helper functions for chameleon transitions."""

    @staticmethod
    def hex_to_kivy_color(hex_color: str) -> Tuple[float, float, float, float]:
        """
        Convert hex color to Kivy RGBA (0-1).

        Args:
            hex_color: Hex color string (#RRGGBB or #AARRGGBB)

        Returns:
            (R, G, B, A) tuple normalized to 0-1
        """
        hex_color = hex_color.lstrip('#')

        # Handle ARGB
        if len(hex_color) == 8:
            a = int(hex_color[0:2], 16) / 255.0
            r = int(hex_color[2:4], 16) / 255.0
            g = int(hex_color[4:6], 16) / 255.0
            b = int(hex_color[6:8], 16) / 255.0
            return (r, g, b, a)

        # Handle RGB
        elif len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return (r, g, b, 1.0)

        # Fallback
        return (0.5, 0.5, 0.5, 1.0)

    @staticmethod
    def interpolate_colors(color1: Tuple, color2: Tuple, progress: float) -> Tuple:
        """
        Interpolate between two colors.

        Args:
            color1: Start color (RGBA 0-1)
            color2: End color (RGBA 0-1)
            progress: Interpolation progress (0-1)

        Returns:
            Interpolated color (RGBA 0-1)
        """
        return tuple(
            c1 + (c2 - c1) * progress
            for c1, c2 in zip(color1, color2)
        )

    @staticmethod
    def get_screen_transition_effect() -> str:
        """
        Get recommended screen transition effect for Kivy ScreenManager.

        Returns:
            Transition name
        """
        # Use 'swap' transition for chameleon-like instant adaptation
        # Or 'fade' for smooth color blending
        return 'fade'
