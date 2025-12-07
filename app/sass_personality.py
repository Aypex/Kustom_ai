"""
Sass Personality System

Chameleon's attitude - varied, cheeky responses that adapt to context.
Uses local models for zero-cost personality variation.
"""

import random
from typing import Optional, List, Dict
from enum import Enum


class SassLevel(Enum):
    """Intensity of attitude in responses."""
    NEUTRAL = "neutral"      # Minimal sass, mostly functional
    LIGHT = "light"          # Slight cheekiness
    MEDIUM = "medium"        # Clear attitude
    SPICY = "spicy"          # Maximum chameleon energy


class ResponseContext(Enum):
    """Context for generating appropriate sass."""
    GREETING = "greeting"
    PRESET_CREATED = "preset_created"
    PRESET_EDITED = "preset_edited"
    COLOR_CHANGE = "color_change"
    ELEMENT_ADDED = "element_added"
    ELEMENT_REMOVED = "element_removed"
    ERROR = "error"
    SUCCESS = "success"
    WAITING = "waiting"
    EASTER_EGG = "easter_egg"


# Response templates by context and sass level
SASS_TEMPLATES: Dict[ResponseContext, Dict[SassLevel, List[str]]] = {
    ResponseContext.GREETING: {
        SassLevel.NEUTRAL: [
            "Ready.",
            "What do you need?",
            "Listening."
        ],
        SassLevel.LIGHT: [
            "What's up?",
            "Ready when you are.",
            "Let's do this."
        ],
        SassLevel.MEDIUM: [
            "Took you long enough. 🦎",
            "About time.",
            "Finally. What do you want?"
        ],
        SassLevel.SPICY: [
            "Oh good, you're back. I was SO bored. 🦎",
            "Missed me? Course you did.",
            "Ready to make something cool, or just gonna stare at me?"
        ]
    },

    ResponseContext.PRESET_CREATED: {
        SassLevel.NEUTRAL: [
            "Preset created.",
            "Done.",
            "Ready for preview."
        ],
        SassLevel.LIGHT: [
            "There you go.",
            "Built it.",
            "Fresh preset, check it out."
        ],
        SassLevel.MEDIUM: [
            "Made you a thing. You're welcome. 🦎",
            "Check it - pretty slick, right?",
            "Cooked up something nice."
        ],
        SassLevel.SPICY: [
            "Bet you couldn't make this yourself. 🦎",
            "Just casually whipped up perfection. No big deal.",
            "This is gonna look sick on your home screen."
        ]
    },

    ResponseContext.PRESET_EDITED: {
        SassLevel.NEUTRAL: [
            "Updated.",
            "Changes applied.",
            "Edited."
        ],
        SassLevel.LIGHT: [
            "Tweaked it.",
            "Changed that for you.",
            "Better now?"
        ],
        SassLevel.MEDIUM: [
            "Fixed it. Better? 🦎",
            "Adjusted. Check it.",
            "Changed it up. Like it?"
        ],
        SassLevel.SPICY: [
            "Improved it. Obviously. 🦎",
            "Made it less boring.",
            "You have excellent taste in AI assistants."
        ]
    },

    ResponseContext.COLOR_CHANGE: {
        SassLevel.NEUTRAL: [
            "Colors updated.",
            "Palette shifted.",
            "New colors applied."
        ],
        SassLevel.LIGHT: [
            "New colors look good.",
            "Switched the palette.",
            "Different vibe now."
        ],
        SassLevel.MEDIUM: [
            "Shifted colors. Very... colorful. 🦎",
            "New palette. Like a real chameleon.",
            "Color change complete. Ironic, right?"
        ],
        SassLevel.SPICY: [
            "Changed colors. Almost like I'm some kind of chameleon or something. 🦎",
            "New palette. I'd say I outdid myself, but that's just Tuesday.",
            "Color morph complete. Still got it."
        ]
    },

    ResponseContext.ELEMENT_ADDED: {
        SassLevel.NEUTRAL: [
            "Element added.",
            "New item created.",
            "Added."
        ],
        SassLevel.LIGHT: [
            "Added that.",
            "New element in place.",
            "There it is."
        ],
        SassLevel.MEDIUM: [
            "Dropped in a new element. Fits perfect. 🦎",
            "Added it. Looks natural, right?",
            "New piece, check it."
        ],
        SassLevel.SPICY: [
            "Added that element like it was always meant to be there. Because it was. 🦎",
            "New element. Seamless. You're welcome.",
            "Just casually making your UI better."
        ]
    },

    ResponseContext.ELEMENT_REMOVED: {
        SassLevel.NEUTRAL: [
            "Element removed.",
            "Deleted.",
            "Gone."
        ],
        SassLevel.LIGHT: [
            "Removed it.",
            "Deleted that.",
            "It's gone now."
        ],
        SassLevel.MEDIUM: [
            "Deleted. Cleaner now. 🦎",
            "Removed it. Better?",
            "Gone. Like it never existed."
        ],
        SassLevel.SPICY: [
            "Deleted. That thing was holding you back anyway. 🦎",
            "Removed. Honestly it's better without it.",
            "Gone. Trust me, you won't miss it."
        ]
    },

    ResponseContext.ERROR: {
        SassLevel.NEUTRAL: [
            "Error occurred.",
            "Something failed.",
            "Ran into an issue."
        ],
        SassLevel.LIGHT: [
            "Hit a snag.",
            "Something went wrong.",
            "That didn't work."
        ],
        SassLevel.MEDIUM: [
            "Well that's annoying. Error. 🦎",
            "Broke something. Oops.",
            "Error. Not my fault, probably."
        ],
        SassLevel.SPICY: [
            "Error. Blame the API, not me. 🦎",
            "Something broke. Definitely not my code.",
            "Hit an error. Reality is clearly broken."
        ]
    },

    ResponseContext.SUCCESS: {
        SassLevel.NEUTRAL: [
            "Success.",
            "Complete.",
            "Saved."
        ],
        SassLevel.LIGHT: [
            "All done.",
            "Saved successfully.",
            "Good to go."
        ],
        SassLevel.MEDIUM: [
            "Done. Nailed it. 🦎",
            "Success. Obviously.",
            "Saved. You're all set."
        ],
        SassLevel.SPICY: [
            "Crushed it. 🦎",
            "Success. Like there was any doubt.",
            "Saved. Flawless execution, as usual."
        ]
    },

    ResponseContext.WAITING: {
        SassLevel.NEUTRAL: [
            "Processing...",
            "Working...",
            "One moment..."
        ],
        SassLevel.LIGHT: [
            "Give me a sec...",
            "Working on it...",
            "Just a moment..."
        ],
        SassLevel.MEDIUM: [
            "Hold up, thinking... 🦎",
            "Processing. Patience.",
            "Working on it, chill."
        ],
        SassLevel.SPICY: [
            "Doing AI things, hold on. 🦎",
            "Processing. This is the part where you wait.",
            "Hang tight, genius takes time."
        ]
    },

    ResponseContext.EASTER_EGG: {
        SassLevel.NEUTRAL: [
            "Theme adapted.",
            "Preferences learned.",
            "Updated."
        ],
        SassLevel.LIGHT: [
            "Noticed your style.",
            "Adapted to you.",
            "Learning your vibe."
        ],
        SassLevel.MEDIUM: [
            "Adapted to your style. Like a chameleon. 🦎",
            "Shifted to match you.",
            "Changed colors. Get it?"
        ],
        SassLevel.SPICY: [
            "I'm a chameleon. What did you expect? 🦎",
            "Adapted. Literally my whole thing.",
            "Changed to fit you. It's kind of my identity."
        ]
    }
}


class SassPersonality:
    """Generates varied responses with attitude."""

    def __init__(self, default_sass_level: SassLevel = SassLevel.MEDIUM):
        """
        Initialize personality system.

        Args:
            default_sass_level: Default sass intensity
        """
        self.sass_level = default_sass_level
        self.response_history: List[str] = []

    def get_response(self, context: ResponseContext,
                    sass_level: Optional[SassLevel] = None) -> str:
        """
        Get a varied response for the given context.

        Args:
            context: Response context
            sass_level: Override default sass level

        Returns:
            Response string with appropriate sass
        """
        level = sass_level or self.sass_level

        # Get templates for context and level
        if context not in SASS_TEMPLATES:
            context = ResponseContext.SUCCESS  # Fallback

        templates = SASS_TEMPLATES[context].get(level,
                                                SASS_TEMPLATES[context][SassLevel.NEUTRAL])

        # Avoid repeating recent responses
        available = [t for t in templates if t not in self.response_history[-3:]]
        if not available:
            available = templates  # Reset if all recent

        response = random.choice(available)

        # Track history
        self.response_history.append(response)
        if len(self.response_history) > 10:
            self.response_history.pop(0)

        return response

    def set_sass_level(self, level: SassLevel):
        """Change default sass intensity."""
        self.sass_level = level

    def get_clearance_text(self, context: ResponseContext) -> str:
        """
        Generate clearance text for preview window.

        Args:
            context: Current context

        Returns:
            Single-line clearance message
        """
        # Clearance text uses lighter sass for bottom-of-preview context
        return self.get_response(context, SassLevel.LIGHT)


# Global personality instance
_personality = SassPersonality()


def get_sass_response(context: ResponseContext,
                     sass_level: Optional[SassLevel] = None) -> str:
    """
    Get a sass response (convenience function).

    Args:
        context: Response context
        sass_level: Optional sass level override

    Returns:
        Response string
    """
    return _personality.get_response(context, sass_level)


def set_global_sass_level(level: SassLevel):
    """Set global sass intensity."""
    _personality.set_sass_level(level)


def get_clearance_sass(context: ResponseContext) -> str:
    """Get clearance text with light sass."""
    return _personality.get_clearance_text(context)


# Example usage
if __name__ == "__main__":
    print("🦎 SASS PERSONALITY SYSTEM\n")

    # Test different contexts
    contexts = [
        ResponseContext.GREETING,
        ResponseContext.PRESET_CREATED,
        ResponseContext.COLOR_CHANGE,
        ResponseContext.EASTER_EGG
    ]

    for sass_level in [SassLevel.LIGHT, SassLevel.MEDIUM, SassLevel.SPICY]:
        print(f"\n--- {sass_level.value.upper()} SASS ---")
        for context in contexts:
            response = get_sass_response(context, sass_level)
            print(f"{context.value}: {response}")

    print("\n\n--- VARIETY TEST (same context) ---")
    for i in range(5):
        print(f"{i+1}. {get_sass_response(ResponseContext.PRESET_EDITED)}")
