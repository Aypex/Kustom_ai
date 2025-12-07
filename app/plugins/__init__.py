"""Plugin system for Android customization apps."""

from .plugin_interface import CustomizationPlugin
from .plugin_manager import PluginManager, get_plugin_manager

__all__ = ['CustomizationPlugin', 'PluginManager', 'get_plugin_manager']
