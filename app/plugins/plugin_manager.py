"""Plugin manager for discovering and loading customization plugins."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from .plugin_interface import CustomizationPlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages discovery, loading, and access to customization plugins."""

    def __init__(self):
        """Initialize plugin manager."""
        self.plugins: Dict[str, CustomizationPlugin] = {}
        self._loaded = False

    def load_plugins(self) -> None:
        """Discover and load all available plugins."""
        if self._loaded:
            return

        logger.info("Loading plugins...")

        # Import and register built-in plugins
        self._load_kustom_plugin()
        self._load_total_launcher_plugin()
        self._load_tasker_plugin()

        self._loaded = True
        logger.info(f"Loaded {len(self.plugins)} plugins")

    def _load_kustom_plugin(self) -> None:
        """Load Kustom plugin (KLWP/KLCK/KWGT)."""
        try:
            from .kustom_plugin import KustomPlugin
            plugin = KustomPlugin()
            self.plugins['kustom'] = plugin
            logger.info(f"Loaded: {plugin}")
        except Exception as e:
            logger.error(f"Failed to load Kustom plugin: {e}")

    def _load_total_launcher_plugin(self) -> None:
        """Load Total Launcher plugin."""
        try:
            from .total_launcher_plugin import TotalLauncherPlugin
            plugin = TotalLauncherPlugin()
            if plugin.is_app_installed():
                self.plugins['total_launcher'] = plugin
                logger.info(f"Loaded: {plugin}")
            else:
                logger.info(f"Total Launcher not installed, plugin not loaded")
        except Exception as e:
            logger.error(f"Failed to load Total Launcher plugin: {e}")

    def _load_tasker_plugin(self) -> None:
        """Load Tasker plugin."""
        try:
            from .tasker_plugin import TaskerPlugin
            plugin = TaskerPlugin()
            if plugin.is_app_installed():
                self.plugins['tasker'] = plugin
                logger.info(f"Loaded: {plugin}")
            else:
                logger.info(f"Tasker not installed, plugin not loaded")
        except Exception as e:
            logger.error(f"Failed to load Tasker plugin: {e}")

    def get_plugins(self) -> List[CustomizationPlugin]:
        """
        Get list of all loaded plugins.

        Returns:
            List of plugin instances
        """
        if not self._loaded:
            self.load_plugins()
        return list(self.plugins.values())

    def get_plugin(self, plugin_id: str) -> Optional[CustomizationPlugin]:
        """
        Get plugin by ID.

        Args:
            plugin_id: Plugin identifier (e.g., 'kustom', 'total_launcher')

        Returns:
            Plugin instance or None
        """
        if not self._loaded:
            self.load_plugins()
        return self.plugins.get(plugin_id)

    def get_plugin_by_app_name(self, app_name: str) -> Optional[CustomizationPlugin]:
        """
        Get plugin by supported app name.

        Args:
            app_name: App name (e.g., 'Total Launcher', 'Tasker')

        Returns:
            Plugin instance or None
        """
        if not self._loaded:
            self.load_plugins()

        for plugin in self.plugins.values():
            if plugin.get_supported_app().lower() == app_name.lower():
                return plugin
        return None

    def get_installed_plugins(self) -> List[CustomizationPlugin]:
        """
        Get list of plugins whose target apps are installed.

        Returns:
            List of plugin instances for installed apps
        """
        if not self._loaded:
            self.load_plugins()
        return [p for p in self.plugins.values() if p.is_app_installed()]

    def get_plugin_info(self) -> List[Dict[str, str]]:
        """
        Get information about all loaded plugins.

        Returns:
            List of dicts with plugin metadata
        """
        if not self._loaded:
            self.load_plugins()

        info = []
        for plugin_id, plugin in self.plugins.items():
            info.append({
                'id': plugin_id,
                'name': plugin.get_plugin_name(),
                'version': plugin.get_plugin_version(),
                'app': plugin.get_supported_app(),
                'package': plugin.get_app_package(),
                'installed': plugin.is_app_installed()
            })
        return info

    def reload_plugins(self) -> None:
        """Reload all plugins (useful after app installation)."""
        self._loaded = False
        self.plugins.clear()
        self.load_plugins()


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """
    Get global plugin manager instance.

    Returns:
        PluginManager singleton
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
