"""Base interface for customization app plugins."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class CustomizationPlugin(ABC):
    """
    Base class for all customization app plugins.

    Each plugin handles a specific Android customization app
    (KLWP, Total Launcher, Tasker, etc.)
    """

    @abstractmethod
    def get_plugin_name(self) -> str:
        """Return human-readable plugin name."""
        pass

    @abstractmethod
    def get_plugin_version(self) -> str:
        """Return plugin version string."""
        pass

    @abstractmethod
    def get_supported_app(self) -> str:
        """Return name of supported app (e.g., 'Total Launcher')."""
        pass

    @abstractmethod
    def get_app_package(self) -> str:
        """Return Android package name of supported app."""
        pass

    @abstractmethod
    def is_app_installed(self) -> bool:
        """Check if the target app is installed on the device."""
        pass

    @abstractmethod
    def get_config_directory(self) -> Path:
        """Return directory where app stores its configuration files."""
        pass

    @abstractmethod
    def list_configs(self) -> List[Dict[str, Any]]:
        """
        List all available configuration files.

        Returns:
            List of dicts with keys: name, path, size, type
        """
        pass

    @abstractmethod
    def read_config(self, config_name: str) -> Dict[str, Any]:
        """
        Read and parse a configuration file.

        Args:
            config_name: Name of configuration file

        Returns:
            Parsed configuration data
        """
        pass

    @abstractmethod
    def list_elements(self, config_name: str,
                     element_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all elements/items in a configuration.

        Args:
            config_name: Name of configuration file
            element_type: Optional filter by element type

        Returns:
            List of element info dicts
        """
        pass

    @abstractmethod
    def find_element(self, config_name: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for elements by term.

        Args:
            config_name: Name of configuration file
            search_term: Search term (case-insensitive)

        Returns:
            List of matching elements
        """
        pass

    @abstractmethod
    def modify_element(self, config_name: str, element_id: str,
                      properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify an element's properties.

        Args:
            config_name: Name of configuration file
            element_id: ID of element to modify
            properties: Properties to update

        Returns:
            Updated element info
        """
        pass

    @abstractmethod
    def save_config(self, config_name: str, data: Dict[str, Any],
                   backup: bool = True) -> str:
        """
        Save modified configuration back to file.

        Args:
            config_name: Name of configuration file
            data: Modified configuration data
            backup: Whether to create backup first

        Returns:
            Path to saved file
        """
        pass

    @abstractmethod
    def reload_app(self) -> bool:
        """
        Trigger the app to reload its configuration.

        Returns:
            True if reload signal sent successfully
        """
        pass

    # Optional methods with default implementations

    def get_element_types(self) -> List[str]:
        """
        Get list of supported element types for this app.

        Returns:
            List of element type names
        """
        return []

    def validate_config(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate configuration data.

        Args:
            data: Configuration data to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        return True, None

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default/empty configuration structure.

        Returns:
            Default configuration dict
        """
        return {}

    def export_config(self, config_name: str, export_path: Path) -> str:
        """
        Export configuration to a different location.

        Args:
            config_name: Name of configuration to export
            export_path: Path to export to

        Returns:
            Path to exported file
        """
        import shutil
        config_path = self.get_config_directory() / config_name
        shutil.copy2(config_path, export_path)
        return str(export_path)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.get_plugin_name()} v{self.get_plugin_version()} ({self.get_supported_app()})"
