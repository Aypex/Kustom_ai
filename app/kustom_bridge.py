"""
Kustom Bridge - Python interface to Kustom apps

Provides Python functions to apply presets to KLWP/KLCK/KWGT via Android intents.
"""

from typing import Optional
import os


class KustomBridge:
    """Bridge to Kustom apps via Android intents."""

    def __init__(self):
        """Initialize Kustom bridge."""
        self._android_available = False
        self._context = None

        # Try to import Android components
        try:
            from jnius import autoclass
            self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.KustomBridge = autoclass('com.chameleon.KustomBridge')
            self._android_available = True
            self._context = self.PythonActivity.mActivity
        except ImportError:
            print("⚠️ Android not available - running in development mode")

    def is_available(self) -> bool:
        """Check if Android bridge is available."""
        return self._android_available

    def check_installed(self, preset_type: str) -> bool:
        """
        Check if required Kustom app is installed.

        Args:
            preset_type: 'klwp', 'klck', or 'kwgt'

        Returns:
            True if installed, False otherwise
        """
        if not self._android_available:
            print(f"[DEV MODE] Would check if {preset_type.upper()} is installed")
            return False

        result = self.KustomBridge.checkInstalled(self._context, preset_type)
        return result == "installed"

    def apply_preset(self, preset_path: str, preset_type: str) -> tuple[bool, str]:
        """
        Apply preset to Kustom app.

        Args:
            preset_path: Absolute path to preset JSON file
            preset_type: 'klwp', 'klck', or 'kwgt'

        Returns:
            (success, message) tuple
        """
        # Validate file exists
        if not os.path.exists(preset_path):
            return False, f"Preset file not found: {preset_path}"

        if not self._android_available:
            print(f"[DEV MODE] Would apply preset:")
            print(f"  File: {preset_path}")
            print(f"  Type: {preset_type.upper()}")
            return True, f"[DEV] Simulated apply to {preset_type.upper()}"

        # Check if app is installed
        if not self.check_installed(preset_type):
            return False, f"{preset_type.upper()} not installed"

        # Send to Kustom app
        result = self.KustomBridge.applyPreset(self._context, preset_path, preset_type)

        if result.startswith("Success"):
            return True, result
        else:
            return False, result

    def open_kustom_app(self, preset_type: str):
        """
        Open Kustom app (or Play Store if not installed).

        Args:
            preset_type: 'klwp', 'klck', or 'kwgt'
        """
        if not self._android_available:
            print(f"[DEV MODE] Would open {preset_type.upper()} app")
            return

        self.KustomBridge.openKustomApp(self._context, preset_type)

    def get_install_status(self) -> dict[str, bool]:
        """
        Get installation status of all Kustom apps.

        Returns:
            Dict with 'klwp', 'klck', 'kwgt' keys and boolean values
        """
        return {
            'klwp': self.check_installed('klwp'),
            'klck': self.check_installed('klck'),
            'kwgt': self.check_installed('kwgt')
        }


# Global bridge instance
_bridge = None


def get_kustom_bridge() -> KustomBridge:
    """
    Get global KustomBridge instance.

    Returns:
        KustomBridge singleton
    """
    global _bridge
    if _bridge is None:
        _bridge = KustomBridge()
    return _bridge


def apply_preset_to_kustom(preset_path: str, preset_type: str) -> tuple[bool, str]:
    """
    Apply preset to Kustom app (convenience function).

    Args:
        preset_path: Path to preset JSON file
        preset_type: 'klwp', 'klck', or 'kwgt'

    Returns:
        (success, message) tuple
    """
    bridge = get_kustom_bridge()
    return bridge.apply_preset(preset_path, preset_type)


def check_kustom_installed(preset_type: str) -> bool:
    """
    Check if Kustom app is installed (convenience function).

    Args:
        preset_type: 'klwp', 'klck', or 'kwgt'

    Returns:
        True if installed
    """
    bridge = get_kustom_bridge()
    return bridge.check_installed(preset_type)


# Test/Example usage
if __name__ == "__main__":
    print("🦎 KUSTOM BRIDGE TEST\n")

    bridge = get_kustom_bridge()

    if bridge.is_available():
        print("✅ Android bridge available")
    else:
        print("⚠️ Running in development mode")

    # Check installation status
    print("\nKUSTOM APP STATUS:")
    status = bridge.get_install_status()
    for app, installed in status.items():
        status_icon = "✅" if installed else "❌"
        print(f"  {status_icon} {app.upper()}: {'Installed' if installed else 'Not installed'}")

    # Test apply (dev mode will just print)
    print("\nTEST APPLY:")
    success, message = bridge.apply_preset("/tmp/test.json", "klwp")
    print(f"  Result: {message}")
