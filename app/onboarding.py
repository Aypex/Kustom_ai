"""
Onboarding Flow Manager

Handles first-time user experience:
1. AI backend selection (local/SSH/API)
2. Model loading/connection
3. KLWP directory configuration
4. Preset workflow selection
5. Voice chat feature reveal (chameleon camo drop)
"""

from pathlib import Path
from typing import Optional, Dict, Any
from app.secure_storage import SecureStorage


class OnboardingManager:
    """Manage first-time user onboarding flow."""

    def __init__(self):
        """Initialize onboarding manager."""
        self.storage = SecureStorage()

    def is_onboarding_complete(self) -> bool:
        """
        Check if user has completed onboarding.

        Returns:
            True if onboarding is complete
        """
        return self.storage.get('onboarding_complete', False)

    def get_current_step(self) -> str:
        """
        Get current onboarding step.

        Returns:
            Step name: 'backend', 'model', 'directory', 'workflow', 'complete'
        """
        if self.is_onboarding_complete():
            return 'complete'

        # Check what's been configured
        if not self.storage.get('backend_selected', False):
            return 'backend'

        if not self.storage.get('model_loaded', False):
            return 'model'

        if not self.storage.get('klwp_directory', None):
            return 'directory'

        if not self.storage.get('workflow_shown', False):
            return 'workflow'

        return 'complete'

    def complete_backend_selection(self, backend: str, config: Dict[str, Any]) -> None:
        """
        Mark backend selection complete.

        Args:
            backend: 'local', 'ssh', or 'api'
            config: Backend-specific configuration
        """
        self.storage.set('backend_selected', backend)
        self.storage.set('backend_config', config)

    def complete_model_setup(self, model_info: Dict[str, Any]) -> None:
        """
        Mark model setup complete.

        Args:
            model_info: Model metadata
        """
        self.storage.set('model_loaded', True)
        self.storage.set('model_info', model_info)

    def set_klwp_directory(self, directory: str) -> None:
        """
        Set KLWP presets directory.

        Args:
            directory: Path to KLWP directory
        """
        self.storage.set('klwp_directory', directory)

    def get_klwp_directory(self) -> Optional[str]:
        """
        Get configured KLWP directory.

        Returns:
            Directory path or None
        """
        return self.storage.get('klwp_directory', None)

    def complete_workflow_intro(self) -> None:
        """Mark workflow introduction as shown."""
        self.storage.set('workflow_shown', True)

    def complete_onboarding(self) -> None:
        """Mark entire onboarding flow as complete."""
        self.storage.set('onboarding_complete', True)

    def should_show_voice_button(self) -> bool:
        """
        Check if voice chat button should be revealed.

        Voice button appears after workflow is shown (chameleon camo drop).

        Returns:
            True if voice button should be visible
        """
        return self.storage.get('workflow_shown', False)

    def has_voice_opt_in(self) -> bool:
        """
        Check if user has opted into voice features.

        Returns:
            True if voice is enabled
        """
        return self.storage.get('voice_enabled', False)

    def enable_voice(self) -> None:
        """Enable voice chat features."""
        self.storage.set('voice_enabled', True)

    def disable_voice(self) -> None:
        """Disable voice chat features."""
        self.storage.set('voice_enabled', False)

    def get_onboarding_progress(self) -> Dict[str, Any]:
        """
        Get onboarding progress summary.

        Returns:
            Dict with progress info
        """
        return {
            'complete': self.is_onboarding_complete(),
            'current_step': self.get_current_step(),
            'backend': self.storage.get('backend_selected', None),
            'model_loaded': self.storage.get('model_loaded', False),
            'directory': self.get_klwp_directory(),
            'workflow_shown': self.storage.get('workflow_shown', False),
            'voice_enabled': self.has_voice_opt_in()
        }

    def reset_onboarding(self) -> None:
        """Reset onboarding state (for testing)."""
        self.storage.set('onboarding_complete', False)
        self.storage.set('backend_selected', False)
        self.storage.set('model_loaded', False)
        self.storage.set('klwp_directory', None)
        self.storage.set('workflow_shown', False)
        self.storage.set('voice_enabled', False)


class OnboardingMessages:
    """Onboarding message templates."""

    @staticmethod
    def backend_selection() -> str:
        """Backend selection message."""
        return """
🦎 Welcome to Chameleon!

Let's get you set up. First, choose how you want me to run:

**Local** - On-device AI (private, offline)
  ↳ Best for: Privacy, no internet needed
  ↳ Requires: ~2GB storage

**SSH** - Your home server (Ollama, LM Studio)
  ↳ Best for: Power + privacy
  ↳ Requires: Home server running

**API** - Cloud AI (Gemini, Claude)
  ↳ Best for: Maximum capability
  ↳ Requires: API key (some free tiers available)

Note: API models tend to work best for complex preset generation, but local models work well too!
"""

    @staticmethod
    def model_loading(backend: str) -> str:
        """Model loading message."""
        if backend == 'local':
            return "Loading on-device model... This may take a moment on first run."
        elif backend == 'ssh':
            return "Connecting to your home server..."
        elif backend == 'api':
            return "Connecting to cloud API..."
        return "Setting up AI backend..."

    @staticmethod
    def directory_prompt() -> str:
        """KLWP directory selection prompt."""
        return """
Perfect! Now, where does KLWP store your presets?

This is usually set during KLWP installation. Common locations:

📁 /sdcard/Kustom/wallpapers/
📁 /storage/emulated/0/Kustom/wallpapers/
📁 Custom location (you chose during install)

I'll look here for existing presets to edit.
"""

    @staticmethod
    def workflow_intro() -> str:
        """Workflow introduction message."""
        return """
Great! You're all set up. Here's what I can do:

**Create from Scratch**
  "Create a cyberpunk wallpaper with neon blues"
  "Make a minimal lock screen with clock and battery"

**Edit Existing**
  "Change all text to #00FF00"
  "Make the clock bigger"
  "Add shadows to the weather widget"

**Cross-Format**
  "Create a matching KLCK from this KLWP"
  "Make a KWGT widget version"

Just describe what you want in natural language. I'll show you a preview before saving anything.

Ready to create something? 🦎
"""

    @staticmethod
    def voice_reveal() -> str:
        """Voice feature reveal (after button appears)."""
        return """
🎤 Voice chat is now available!

Tap the microphone icon to talk instead of type.

Want to enable voice features?
"""

    @staticmethod
    def get_default_directories() -> list:
        """Get common KLWP directory locations."""
        return [
            "/sdcard/Kustom/wallpapers",
            "/storage/emulated/0/Kustom/wallpapers",
            "/sdcard/Kustom/lockscreens",
            "/storage/emulated/0/Kustom/lockscreens",
            "/sdcard/Kustom/widgets",
            "/storage/emulated/0/Kustom/widgets"
        ]

    @staticmethod
    def validate_directory(path: str) -> bool:
        """
        Validate if directory exists and is accessible.

        Args:
            path: Directory path

        Returns:
            True if valid
        """
        try:
            p = Path(path)
            return p.exists() and p.is_dir()
        except Exception:
            return False
