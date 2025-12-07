"""
Preview Window System with Molting Effects

Architecture for split-screen chat + live preview with chameleon molting.

Components:
1. SplitLayout - Elastic chat/preview columns
2. PreviewRenderer - KLWP JSON → Visual preview
3. MoltingPreview - Localized shader effects on preview only
4. ClearanceText - Context-aware AI messaging at preview bottom
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class PreviewState(Enum):
    """Preview window states."""
    HIDDEN = "hidden"           # Preview not visible (100% chat)
    SLIDING_IN = "sliding_in"   # Preview entering from right
    VISIBLE = "visible"         # Preview stable (70/30 split)
    MOLTING = "molting"         # Molt animation active
    SLIDING_OUT = "sliding_out" # Preview exiting to right


class MoltType(Enum):
    """Types of molt animations based on edit type."""
    COLOR_SHIFT = "color"       # Color change (strong RGB split)
    SCALE = "scale"             # Size change (ripple + scale distortion)
    BIRTH = "birth"             # New element (ripple from element position)
    FADE = "fade"               # Remove element (reverse ripple)
    TRANSFORM = "transform"     # Complex change (multi-wave ripple)


@dataclass
class PresetPreview:
    """Data for rendering a KLWP preset preview."""
    preset_name: str
    preset_type: str  # 'klwp', 'klck', 'kwgt'
    preset_data: Dict[str, Any]  # Parsed JSON
    thumbnail_path: Optional[str] = None  # Cached preview image
    colors: List[str] = None  # Extracted color palette

    def __post_init__(self):
        if self.colors is None:
            self.colors = []


@dataclass
class MoltTransition:
    """Configuration for a molt animation."""
    molt_type: MoltType
    duration_ms: int
    current_preset: PresetPreview
    target_preset: PresetPreview
    origin_point: Optional[tuple] = None  # (x, y) for birth/fade effects

    def get_duration(self) -> float:
        """Get duration in seconds."""
        return self.duration_ms / 1000.0

    @staticmethod
    def from_edit_type(edit_description: str, current: PresetPreview,
                       target: PresetPreview) -> 'MoltTransition':
        """
        Detect molt type from edit description.

        Args:
            edit_description: Natural language edit (e.g., "make it blue")
            current: Current preset state
            target: Target preset state

        Returns:
            MoltTransition configured for the edit type
        """
        desc_lower = edit_description.lower()

        # Color change
        if any(word in desc_lower for word in ['color', 'blue', 'red', 'green',
                                                 'darker', 'lighter', 'theme']):
            return MoltTransition(
                molt_type=MoltType.COLOR_SHIFT,
                duration_ms=800,
                current_preset=current,
                target_preset=target
            )

        # Size change
        if any(word in desc_lower for word in ['bigger', 'smaller', 'larger',
                                                 'size', 'scale', 'grow', 'shrink']):
            return MoltTransition(
                molt_type=MoltType.SCALE,
                duration_ms=600,
                current_preset=current,
                target_preset=target
            )

        # Add element
        if any(word in desc_lower for word in ['add', 'create', 'new', 'insert']):
            return MoltTransition(
                molt_type=MoltType.BIRTH,
                duration_ms=1000,
                current_preset=current,
                target_preset=target
            )

        # Remove element
        if any(word in desc_lower for word in ['remove', 'delete', 'hide']):
            return MoltTransition(
                molt_type=MoltType.FADE,
                duration_ms=600,
                current_preset=current,
                target_preset=target
            )

        # Default: Complex transformation
        return MoltTransition(
            molt_type=MoltType.TRANSFORM,
            duration_ms=1200,
            current_preset=current,
            target_preset=target
        )


class PreviewManager:
    """
    Manages preview window state and transitions.

    Coordinates:
    - Preview visibility (show/hide)
    - Molt animations
    - Preset updates
    - Clearance text
    """

    def __init__(self):
        self.state = PreviewState.HIDDEN
        self.current_preview: Optional[PresetPreview] = None
        self.pending_molt: Optional[MoltTransition] = None
        self.clearance_text = ""

    def show_preview(self, preset: PresetPreview, clearance_msg: str = "") -> None:
        """
        Show preview window with slide-in animation.

        Args:
            preset: Preset to display
            clearance_msg: Message to show at bottom of preview
        """
        self.current_preview = preset
        self.clearance_text = clearance_msg or self._generate_clearance_text(preset)
        self.state = PreviewState.SLIDING_IN

        # After slide completes (400ms), set to VISIBLE
        # (In real implementation, triggered by animation completion callback)

    def hide_preview(self) -> None:
        """Hide preview window with slide-out animation."""
        self.state = PreviewState.SLIDING_OUT

        # After slide completes (300ms), set to HIDDEN
        # Clear current_preview

    def update_preview(self, new_preset: PresetPreview,
                      edit_description: str = "") -> None:
        """
        Update preview with molt animation.

        Args:
            new_preset: Updated preset to display
            edit_description: Description of the edit (for molt type detection)
        """
        if not self.current_preview:
            # No current preview, just show it
            self.show_preview(new_preset)
            return

        # Create molt transition
        molt = MoltTransition.from_edit_type(
            edit_description,
            self.current_preview,
            new_preset
        )

        self.pending_molt = molt
        self.state = PreviewState.MOLTING

        # Start molt animation
        # When complete, update current_preview and set state to VISIBLE

    def _generate_clearance_text(self, preset: PresetPreview) -> str:
        """
        Generate context-aware clearance text.

        Args:
            preset: Current preset

        Returns:
            Single line message for preview clearance
        """
        if preset.preset_type == 'klwp':
            return f"Editing '{preset.preset_name}'. Continue? 🦎"
        elif preset.preset_type == 'klck':
            return f"Lock screen preview. What next? 🦎"
        elif preset.preset_type == 'kwgt':
            return f"Widget preview loaded. Adjust? 🦎"

        return "Working with this? 🦎"

    def is_preview_active(self) -> bool:
        """Check if preview is currently visible (any state except HIDDEN)."""
        return self.state != PreviewState.HIDDEN

    def get_chat_width_fraction(self) -> float:
        """
        Get chat column width fraction based on preview state.

        Returns:
            Float 0.0-1.0 for chat width percentage
        """
        if self.state == PreviewState.HIDDEN:
            return 1.0  # 100% chat
        elif self.state in [PreviewState.VISIBLE, PreviewState.MOLTING]:
            return 0.3  # 30% chat, 70% preview
        elif self.state == PreviewState.SLIDING_IN:
            # Animated: 1.0 → 0.3 during slide
            return 0.3  # Target value
        elif self.state == PreviewState.SLIDING_OUT:
            # Animated: 0.3 → 1.0 during slide
            return 1.0  # Target value

        return 1.0  # Default


class KLWPPreviewRenderer:
    """
    Renders KLWP preset JSON to visual preview.

    This is a simplified renderer for preview purposes.
    Full KLWP rendering is complex - this creates a representative preview.
    """

    def __init__(self):
        self.cache = {}

    def render_preset(self, preset_data: Dict[str, Any],
                     width: int = 360, height: int = 640) -> Any:
        """
        Render KLWP preset JSON to preview image.

        Args:
            preset_data: Parsed KLWP JSON
            width: Preview width in pixels
            height: Preview height in pixels

        Returns:
            Preview image/drawable (implementation-specific)
        """
        # Extract layout
        items = preset_data.get('items', [])

        # Build visual representation
        # For Python: Would use PIL/Pillow
        # For Android: Would use Canvas API

        # This is a placeholder - actual implementation would:
        # 1. Parse KLWP elements (TEXT, SHAPE, IMAGE, etc.)
        # 2. Render each element to canvas
        # 3. Apply positions, colors, fonts
        # 4. Return rendered image

        return self._create_placeholder_preview(preset_data, width, height)

    def _create_placeholder_preview(self, preset_data: Dict,
                                    width: int, height: int) -> Dict:
        """
        Create a simple placeholder preview representation.

        Returns:
            Dict with preview metadata for rendering
        """
        items = preset_data.get('items', [])

        # Extract key visual elements
        background_color = '#000000'
        text_elements = []
        shapes = []

        for item in items:
            item_type = item.get('type', '')

            if item_type == 'SHAPE' and item.get('id') == 'background':
                background_color = item.get('color', '#000000')

            elif item_type == 'TEXT':
                text_elements.append({
                    'text': item.get('text', ''),
                    'color': item.get('color', '#FFFFFF'),
                    'size': item.get('font_size', 24),
                    'position': item.get('position', {})
                })

            elif item_type == 'SHAPE':
                shapes.append({
                    'shape_type': item.get('shape_type', 'rectangle'),
                    'color': item.get('color', '#FFFFFF'),
                    'position': item.get('position', {})
                })

        return {
            'width': width,
            'height': height,
            'background_color': background_color,
            'text_elements': text_elements,
            'shapes': shapes
        }


# Clearance text templates
CLEARANCE_TEMPLATES = {
    'initial_load': [
        "Working with this? 🦎",
        "Is this the one? 🦎",
        "Editing this preset? 🦎"
    ],
    'after_edit': [
        "Better? 🦎",
        "How's this look? 🦎",
        "Keep going? 🦎"
    ],
    'color_change': [
        "New colors applied. Continue? 🦎",
        "Shifted palette. Better? 🦎"
    ],
    'size_change': [
        "Resized. Good? 🦎",
        "Scale adjusted. More? 🦎"
    ],
    'element_added': [
        "Element added. What next? 🦎",
        "New addition. Continue? 🦎"
    ],
    'element_removed': [
        "Removed. Anything else? 🦎",
        "Deleted. Better? 🦎"
    ]
}


def get_clearance_text(context: str, molt_type: Optional[MoltType] = None) -> str:
    """
    Get appropriate clearance text based on context.

    Args:
        context: 'initial_load', 'after_edit', or molt type
        molt_type: Type of molt that just completed

    Returns:
        Clearance text string
    """
    from app.sass_personality import get_clearance_sass, ResponseContext

    # Map molt types to sass contexts
    if molt_type == MoltType.COLOR_SHIFT:
        return get_clearance_sass(ResponseContext.COLOR_CHANGE)
    elif molt_type == MoltType.SCALE:
        return get_clearance_sass(ResponseContext.PRESET_EDITED)
    elif molt_type == MoltType.BIRTH:
        return get_clearance_sass(ResponseContext.ELEMENT_ADDED)
    elif molt_type == MoltType.FADE:
        return get_clearance_sass(ResponseContext.ELEMENT_REMOVED)

    # Default contexts
    if context == 'initial_load':
        return get_clearance_sass(ResponseContext.GREETING)
    elif context == 'after_edit':
        return get_clearance_sass(ResponseContext.PRESET_EDITED)

    return "Working with this? 🦎"


# Usage example
if __name__ == "__main__":
    print("🦎 PREVIEW SYSTEM ARCHITECTURE\n")

    # Example flow
    print("FLOW EXAMPLE:")
    print("1. User: 'Edit my cyberpunk theme'")
    print("   → PreviewManager.show_preview()")
    print("   → Preview slides in from right (400ms)")
    print("   → State: SLIDING_IN → VISIBLE")
    print()

    print("2. User: 'Make the clock bigger'")
    print("   → PreviewManager.update_preview(new_preset, 'make clock bigger')")
    print("   → Detects SCALE molt type")
    print("   → State: MOLTING")
    print("   → RGB ripple effect on preview (600ms)")
    print("   → Clock grows during molt")
    print("   → State: VISIBLE")
    print("   → Clearance: 'Resized. Good? 🦎'")
    print()

    print("3. User: 'Perfect, save it'")
    print("   → PreviewManager.hide_preview()")
    print("   → Preview slides out to right (300ms)")
    print("   → State: SLIDING_OUT → HIDDEN")
    print("   → Chat returns to 100% width")
