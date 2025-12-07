"""Plugin system for Android customization apps."""

from .plugin_interface import CustomizationPlugin
from .plugin_manager import PluginManager

__all__ = ['CustomizationPlugin', 'PluginManager']
