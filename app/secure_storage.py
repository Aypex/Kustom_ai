#!/usr/bin/env python3
"""
Secure storage for API keys and credentials.
Uses AES encryption with device-specific key.
"""

import os
import json
import hashlib
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64


class SecureStorage:
    """Encrypted storage for sensitive credentials."""

    def __init__(self, storage_dir=None):
        """Initialize secure storage.

        Args:
            storage_dir: Directory to store encrypted data (default: ~/.klwp_credentials)
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".klwp_credentials"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(mode=0o700, exist_ok=True)

        self.credentials_file = self.storage_dir / "credentials.enc"
        self.key_file = self.storage_dir / "key.dat"

        # Initialize encryption key
        self._init_key()

    def _init_key(self):
        """Initialize or load encryption key."""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            # Generate new key from device ID + random salt
            device_id = self._get_device_id()
            salt = get_random_bytes(32)

            # Derive key using PBKDF2
            self.key = hashlib.pbkdf2_hmac(
                'sha256',
                device_id.encode('utf-8'),
                salt,
                100000,
                dklen=32
            )

            # Store key securely
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
            os.chmod(self.key_file, 0o600)

    def _get_device_id(self):
        """Get device-specific identifier."""
        # Try Android ID first
        try:
            with open('/sys/class/android_usb/android0/iSerial', 'r') as f:
                return f.read().strip()
        except:
            pass

        # Fallback to hostname + user
        import socket
        return f"{socket.gethostname()}-{os.getuid()}"

    def _encrypt(self, data):
        """Encrypt data using AES-256-CBC.

        Args:
            data: String to encrypt

        Returns:
            Base64-encoded encrypted data
        """
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return json.dumps({'iv': iv, 'ciphertext': ct})

    def _decrypt(self, encrypted_data):
        """Decrypt data.

        Args:
            encrypted_data: Encrypted JSON string

        Returns:
            Decrypted string
        """
        try:
            data = json.loads(encrypted_data)
            iv = base64.b64decode(data['iv'])
            ct = base64.b64decode(data['ciphertext'])

            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def save(self, credentials):
        """Save credentials securely.

        Args:
            credentials: Dictionary of credentials to save
        """
        encrypted = self._encrypt(json.dumps(credentials))

        with open(self.credentials_file, 'w') as f:
            f.write(encrypted)

        os.chmod(self.credentials_file, 0o600)

    def load(self):
        """Load credentials.

        Returns:
            Dictionary of credentials, or empty dict if none exist
        """
        if not self.credentials_file.exists():
            return {}

        try:
            with open(self.credentials_file, 'r') as f:
                encrypted = f.read()

            decrypted = self._decrypt(encrypted)
            return json.loads(decrypted)
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return {}

    def set(self, key, value):
        """Set a credential value.

        Args:
            key: Credential key
            value: Credential value
        """
        creds = self.load()
        creds[key] = value
        self.save(creds)

    def get(self, key, default=None):
        """Get a credential value.

        Args:
            key: Credential key
            default: Default value if key doesn't exist

        Returns:
            Credential value or default
        """
        creds = self.load()
        return creds.get(key, default)

    def delete(self, key):
        """Delete a credential.

        Args:
            key: Credential key to delete
        """
        creds = self.load()
        if key in creds:
            del creds[key]
            self.save(creds)

    def clear(self):
        """Clear all credentials."""
        self.save({})

    def has(self, key):
        """Check if a credential exists.

        Args:
            key: Credential key

        Returns:
            True if exists, False otherwise
        """
        return key in self.load()


# Convenience functions
_storage = None


def get_storage():
    """Get the global secure storage instance."""
    global _storage
    if _storage is None:
        _storage = SecureStorage()
    return _storage


def save_credential(key, value):
    """Save a credential."""
    get_storage().set(key, value)


def get_credential(key, default=None):
    """Get a credential."""
    return get_storage().get(key, default)


def delete_credential(key):
    """Delete a credential."""
    get_storage().delete(key)


if __name__ == '__main__':
    # Test
    storage = SecureStorage()

    # Save test data
    storage.set('test_api_key', 'sk-1234567890')
    storage.set('ssh_host', '192.168.1.100')

    # Load and verify
    print(f"API Key: {storage.get('test_api_key')}")
    print(f"SSH Host: {storage.get('ssh_host')}")

    # Clear test data
    storage.clear()
    print("Cleared!")
