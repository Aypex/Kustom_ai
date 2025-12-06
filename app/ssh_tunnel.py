#!/usr/bin/env python3
"""
SSH tunnel manager for accessing home network models.
"""

import paramiko
import socket
import threading
from contextlib import contextmanager


class SSHTunnel:
    """Manage SSH tunnel to remote model server."""

    def __init__(self, ssh_host, ssh_user, ssh_password=None, ssh_key_path=None, ssh_port=22):
        """Initialize SSH tunnel.

        Args:
            ssh_host: SSH server hostname/IP
            ssh_user: SSH username
            ssh_password: SSH password (optional if using key)
            ssh_key_path: Path to SSH private key
            ssh_port: SSH port (default: 22)
        """
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_key_path = ssh_key_path
        self.ssh_port = ssh_port

        self.client = None
        self.tunnel_thread = None
        self.is_connected = False

    def connect(self):
        """Establish SSH connection."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect with password or key
            if self.ssh_password:
                self.client.connect(
                    hostname=self.ssh_host,
                    port=self.ssh_port,
                    username=self.ssh_user,
                    password=self.ssh_password,
                    timeout=10
                )
            elif self.ssh_key_path:
                import os
                key_path = os.path.expanduser(self.ssh_key_path)
                self.client.connect(
                    hostname=self.ssh_host,
                    port=self.ssh_port,
                    username=self.ssh_user,
                    key_filename=key_path,
                    timeout=10
                )
            else:
                raise ValueError("Must provide either password or key path")

            self.is_connected = True
            return True

        except Exception as e:
            print(f"SSH connection failed: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Close SSH connection."""
        if self.client:
            self.client.close()
            self.is_connected = False

    def create_tunnel(self, remote_host, remote_port, local_port=None):
        """Create SSH tunnel for port forwarding.

        Args:
            remote_host: Remote host to forward to (e.g., 'localhost')
            remote_port: Remote port to forward (e.g., 11434 for Ollama)
            local_port: Local port to bind (default: same as remote_port)

        Returns:
            Local port number if successful, None otherwise
        """
        if not self.is_connected:
            if not self.connect():
                return None

        if local_port is None:
            local_port = remote_port

        try:
            # Create local listener
            transport = self.client.get_transport()
            transport.request_port_forward('', local_port)

            print(f"Tunnel created: localhost:{local_port} -> {remote_host}:{remote_port}")
            return local_port

        except Exception as e:
            print(f"Failed to create tunnel: {e}")
            return None

    def execute_command(self, command):
        """Execute command on remote server.

        Args:
            command: Command to execute

        Returns:
            (stdout, stderr, exit_status)
        """
        if not self.is_connected:
            if not self.connect():
                return (None, "Not connected", -1)

        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=30)
            exit_status = stdout.channel.recv_exit_status()

            return (
                stdout.read().decode('utf-8'),
                stderr.read().decode('utf-8'),
                exit_status
            )

        except Exception as e:
            return (None, str(e), -1)

    @contextmanager
    def tunnel_context(self, remote_host, remote_port, local_port=None):
        """Context manager for SSH tunnel.

        Example:
            with tunnel.tunnel_context('localhost', 11434) as local_port:
                # Use localhost:local_port to access remote service
                pass
        """
        port = self.create_tunnel(remote_host, remote_port, local_port)
        try:
            yield port
        finally:
            # Tunnel cleanup happens when connection closes
            pass


def test_ssh_connection(host, user, password=None, key_path=None, port=22):
    """Test SSH connection.

    Returns:
        (success, message)
    """
    try:
        tunnel = SSHTunnel(host, user, password, key_path, port)
        if tunnel.connect():
            tunnel.disconnect()
            return (True, "Connection successful!")
        else:
            return (False, "Connection failed")
    except Exception as e:
        return (False, str(e))


if __name__ == '__main__':
    # Test
    import sys

    if len(sys.argv) < 3:
        print("Usage: python ssh_tunnel.py <host> <user> [password]")
        sys.exit(1)

    host = sys.argv[1]
    user = sys.argv[2]
    password = sys.argv[3] if len(sys.argv) > 3 else None

    success, message = test_ssh_connection(host, user, password)
    print(f"Result: {message}")
