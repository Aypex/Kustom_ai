#!/usr/bin/env python3
"""
Model manager - handles local, SSH, and API models.
"""

import json
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

from app.ssh_tunnel import SSHTunnel
from app.secure_storage import SecureStorage


class ModelManager:
    """Manages different AI model backends."""

    def __init__(self):
        self.storage = SecureStorage()
        self.current_model = None
        self.ssh_tunnel = None

    def use_local_model(self, model_name="llama3.2:1b"):
        """Use local Ollama model.

        Args:
            model_name: Name of the Ollama model

        Returns:
            True if successful
        """
        try:
            # Check if ollama is available
            result = subprocess.run(
                ["proot-distro", "login", "ubuntu", "--", "ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.current_model = ("local", model_name)
                return True
            else:
                return False

        except Exception as e:
            print(f"Local model error: {e}")
            return False

    def use_ssh_model(self):
        """Connect to model via SSH tunnel.

        Returns:
            True if successful
        """
        # Get SSH credentials
        ssh_host = self.storage.get('ssh_host')
        ssh_user = self.storage.get('ssh_user')
        ssh_password = self.storage.get('ssh_password')
        ssh_key_path = self.storage.get('ssh_key_path')
        ssh_port = int(self.storage.get('ssh_port', 22))

        if not ssh_host or not ssh_user:
            return False

        try:
            self.ssh_tunnel = SSHTunnel(
                ssh_host, ssh_user, ssh_password, ssh_key_path, ssh_port
            )

            if self.ssh_tunnel.connect():
                # Create tunnel to remote Ollama (usually port 11434)
                local_port = self.ssh_tunnel.create_tunnel('localhost', 11434)
                if local_port:
                    self.current_model = ("ssh", f"http://localhost:{local_port}")
                    return True

            return False

        except Exception as e:
            print(f"SSH model error: {e}")
            return False

    def use_api_model(self):
        """Use Gemini API model.

        Returns:
            True if API key is set
        """
        api_key = self.storage.get('gemini_api_key')
        if api_key:
            self.current_model = ("api", api_key)
            return True
        return False

    def query(self, prompt):
        """Send query to current model.

        Args:
            prompt: Prompt to send

        Returns:
            Model response
        """
        if not self.current_model:
            return "Error: No model selected"

        model_type, model_data = self.current_model

        if model_type == "local":
            return self._query_local(prompt, model_data)
        elif model_type == "ssh":
            return self._query_ssh(prompt, model_data)
        elif model_type == "api":
            return self._query_api(prompt, model_data)
        else:
            return "Error: Unknown model type"

    def _query_local(self, prompt, model_name):
        """Query local Ollama model."""
        try:
            result = subprocess.run(
                ["proot-distro", "login", "ubuntu", "--", "ollama", "run", model_name, prompt],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"

        except Exception as e:
            return f"Error: {e}"

    def _query_ssh(self, prompt, endpoint):
        """Query model via SSH tunnel."""
        try:
            # Use Ollama API format
            url = f"{endpoint}/api/generate"
            data = {
                "model": "llama3.2:1b",  # TODO: Make configurable
                "prompt": prompt,
                "stream": False
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', 'No response')

        except Exception as e:
            return f"Error: {e}"

    def _query_api(self, prompt, api_key):
        """Query Gemini API."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                text = result['candidates'][0]['content']['parts'][0]['text']
                return text

        except Exception as e:
            return f"Error calling Gemini: {e}"

    def disconnect(self):
        """Disconnect from current model."""
        if self.ssh_tunnel:
            self.ssh_tunnel.disconnect()

        self.current_model = None


# Singleton instance
_model_manager = None


def get_model_manager():
    """Get global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
