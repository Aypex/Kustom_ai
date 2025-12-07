"""Easter Egg Manager - Handles hidden features and first-time experiences."""

from .secure_storage import SecureStorage


class EasterEggManager:
    """Manage easter eggs and hidden feature unlocks."""

    def __init__(self):
        """Initialize easter egg manager."""
        self.storage = SecureStorage()

    def check_theme_matching_trigger(self) -> bool:
        """
        Check if user should see the theme matching easter egg.

        Returns:
            True if this is their first preset creation (trigger easter egg)
        """
        return not self.storage.get('theme_easter_egg_shown', False)

    def activate_theme_matching(self) -> None:
        """Mark theme matching easter egg as activated."""
        self.storage.set('theme_easter_egg_shown', True)
        self.storage.set('theme_matching_unlocked', True)

    def is_theme_matching_unlocked(self) -> bool:
        """
        Check if theme matching feature is unlocked.

        Returns:
            True if user has discovered the easter egg
        """
        return self.storage.get('theme_matching_unlocked', False)

    def get_presets_created_count(self) -> int:
        """
        Get number of presets user has created.

        Returns:
            Count of presets created
        """
        return self.storage.get('presets_created_count', 0)

    def increment_presets_created(self) -> int:
        """
        Increment presets created counter.

        Returns:
            New count
        """
        count = self.get_presets_created_count() + 1
        self.storage.set('presets_created_count', count)
        return count

    def get_last_created_preset(self) -> str:
        """
        Get name of last created preset.

        Returns:
            Preset name or empty string
        """
        return self.storage.get('last_created_preset', '')

    def set_last_created_preset(self, preset_name: str) -> None:
        """
        Store name of last created preset.

        Args:
            preset_name: Name of the preset
        """
        self.storage.set('last_created_preset', preset_name)

    def check_and_trigger_easter_egg(self, preset_name: str) -> bool:
        """
        Check if easter egg should trigger and handle state.

        Call this after successfully saving a preset.

        Args:
            preset_name: Name of saved preset

        Returns:
            True if easter egg should be shown
        """
        # Increment counter
        count = self.increment_presets_created()

        # Store last preset
        self.set_last_created_preset(preset_name)

        # Check if this is first preset AND easter egg not shown yet
        if count == 1 and self.check_theme_matching_trigger():
            return True

        return False

    def unlock_hidden_feature(self, feature_name: str) -> None:
        """
        Unlock a hidden feature.

        Args:
            feature_name: Name of feature to unlock
        """
        self.storage.set(f'feature_unlocked_{feature_name}', True)

    def is_feature_unlocked(self, feature_name: str) -> bool:
        """
        Check if a feature is unlocked.

        Args:
            feature_name: Name of feature

        Returns:
            True if unlocked
        """
        return self.storage.get(f'feature_unlocked_{feature_name}', False)

    def get_easter_egg_stats(self) -> dict:
        """
        Get statistics about easter eggs and achievements.

        Returns:
            Dict with stats
        """
        return {
            'presets_created': self.get_presets_created_count(),
            'theme_matching_discovered': self.is_theme_matching_unlocked(),
            'last_preset': self.get_last_created_preset(),
            'unlocked_features': [
                feature for feature in ['theme_matching', 'preset_sync', 'auto_backup']
                if self.is_feature_unlocked(feature)
            ]
        }

    def reset_easter_eggs(self) -> None:
        """Reset all easter egg state (for testing)."""
        self.storage.set('theme_easter_egg_shown', False)
        self.storage.set('theme_matching_unlocked', False)
        self.storage.set('presets_created_count', 0)
        self.storage.set('last_created_preset', '')
