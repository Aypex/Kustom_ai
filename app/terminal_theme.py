"""
Terminal Chic Theme - Brutalist Color Palette and Typography

Industrial aesthetic for Chameleon UI.
"""

from kivy.utils import get_color_from_hex


class TerminalTheme:
    """Terminal Chic color palette and design tokens."""

    # Core palette - Neon Amber (default)
    BG_PRIMARY = get_color_from_hex('#0D0D0D')      # Near-black background
    BG_SECONDARY = get_color_from_hex('#1A1A1A')    # Charcoal cards/sections
    BG_INPUT = get_color_from_hex('#000000')        # Pure black for inputs

    ACCENT_PRIMARY = get_color_from_hex('#FFB000')  # Amber highlight
    ACCENT_SECONDARY = get_color_from_hex('#FF6B00') # Orange accent

    TEXT_PRIMARY = get_color_from_hex('#FFFFFF')    # White text
    TEXT_SECONDARY = get_color_from_hex('#CCCCCC')  # Light grey
    TEXT_TERTIARY = get_color_from_hex('#888888')   # Dark grey
    TEXT_DISABLED = get_color_from_hex('#444444')   # Very dark grey

    BORDER = get_color_from_hex('#333333')          # Subtle borders
    BORDER_ACCENT = get_color_from_hex('#FFB000')   # Highlighted borders

    GRID_LINE = get_color_from_hex('#1A1A1A')       # Subtle grid overlay

    # Status colors
    SUCCESS = get_color_from_hex('#00FF00')         # Matrix green
    ERROR = get_color_from_hex('#FF0033')           # Crimson red
    WARNING = get_color_from_hex('#FFB000')         # Amber
    INFO = get_color_from_hex('#00D9FF')            # Cyan

    # Chameleon signature
    CHAMELEON_GREEN = get_color_from_hex('#00FF00') # 🦎 emoji color

    # Typography
    FONT_MONO = 'RobotoMono-Regular'                # Monospace for everything
    FONT_MONO_BOLD = 'RobotoMono-Bold'

    # Font sizes (sp)
    FONT_HEADER = 24
    FONT_BODY = 16
    FONT_SMALL = 14
    FONT_TINY = 12

    # Spacing (dp)
    SPACING_NONE = 0
    SPACING_TINY = 4
    SPACING_SMALL = 8
    SPACING_MEDIUM = 16
    SPACING_LARGE = 24
    SPACING_XLARGE = 32

    # Geometry
    CORNER_RADIUS = 0                               # NO ROUNDED CORNERS
    BORDER_WIDTH = 1
    BORDER_WIDTH_THICK = 2

    # Touch targets
    TOUCH_TARGET_MIN = 48


class AlternativeThemes:
    """Alternative color schemes for Terminal Chic."""

    @staticmethod
    def electric_blue():
        """Cyberpunk blue variant."""
        return {
            'bg_primary': get_color_from_hex('#0A0A0A'),
            'bg_secondary': get_color_from_hex('#0D1117'),
            'accent_primary': get_color_from_hex('#00D9FF'),
            'accent_secondary': get_color_from_hex('#0099FF'),
            'success': get_color_from_hex('#00FFFF'),
        }

    @staticmethod
    def clinical_white():
        """High-contrast white variant."""
        return {
            'bg_primary': get_color_from_hex('#000000'),
            'bg_secondary': get_color_from_hex('#0D0D0D'),
            'accent_primary': get_color_from_hex('#FFFFFF'),
            'accent_secondary': get_color_from_hex('#CCCCCC'),
            'text_primary': get_color_from_hex('#FFFFFF'),
            'border_accent': get_color_from_hex('#FFFFFF'),
        }

    @staticmethod
    def blood_red():
        """Aggressive red variant."""
        return {
            'bg_primary': get_color_from_hex('#0D0D0D'),
            'bg_secondary': get_color_from_hex('#1A0A0A'),
            'accent_primary': get_color_from_hex('#FF0033'),
            'accent_secondary': get_color_from_hex('#CC0000'),
            'success': get_color_from_hex('#FF3366'),
        }


def apply_brutalist_style(widget):
    """
    Apply brutalist design principles to a widget.

    Args:
        widget: Kivy widget to style
    """
    # Remove rounded corners
    if hasattr(widget, 'corner_radius'):
        widget.corner_radius = TerminalTheme.CORNER_RADIUS

    # Set monospace font
    if hasattr(widget, 'font_name'):
        widget.font_name = TerminalTheme.FONT_MONO

    # Ensure minimum touch target
    if hasattr(widget, 'size_hint') and widget.size_hint == (None, None):
        if widget.width < TerminalTheme.TOUCH_TARGET_MIN:
            widget.width = TerminalTheme.TOUCH_TARGET_MIN
        if widget.height < TerminalTheme.TOUCH_TARGET_MIN:
            widget.height = TerminalTheme.TOUCH_TARGET_MIN


# Example widget styles
BUTTON_STYLE = {
    'background_color': TerminalTheme.BG_SECONDARY,
    'color': TerminalTheme.TEXT_PRIMARY,
    'font_name': TerminalTheme.FONT_MONO,
    'font_size': TerminalTheme.FONT_BODY,
    'border': (TerminalTheme.BORDER_WIDTH, TerminalTheme.BORDER_ACCENT),
}

INPUT_STYLE = {
    'background_color': TerminalTheme.BG_INPUT,
    'foreground_color': TerminalTheme.TEXT_PRIMARY,
    'cursor_color': TerminalTheme.ACCENT_PRIMARY,
    'font_name': TerminalTheme.FONT_MONO,
    'font_size': TerminalTheme.FONT_BODY,
}

LABEL_STYLE = {
    'color': TerminalTheme.TEXT_PRIMARY,
    'font_name': TerminalTheme.FONT_MONO,
    'font_size': TerminalTheme.FONT_BODY,
}

HEADER_STYLE = {
    'color': TerminalTheme.ACCENT_PRIMARY,
    'font_name': TerminalTheme.FONT_MONO_BOLD,
    'font_size': TerminalTheme.FONT_HEADER,
}


if __name__ == "__main__":
    print("🦎 TERMINAL CHIC THEME\n")
    print("PRIMARY PALETTE:")
    print(f"  Background: {TerminalTheme.BG_PRIMARY}")
    print(f"  Accent: {TerminalTheme.ACCENT_PRIMARY}")
    print(f"  Text: {TerminalTheme.TEXT_PRIMARY}")
    print(f"\nFONT: {TerminalTheme.FONT_MONO}")
    print(f"CORNER RADIUS: {TerminalTheme.CORNER_RADIUS}px (BRUTALIST)")
