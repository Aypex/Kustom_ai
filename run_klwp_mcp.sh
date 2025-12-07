#!/bin/bash
# KLWP MCP Server startup script

cd /home/char/Downloads/Kustom_ai
source .venv/bin/activate
exec python -m klwp_mcp_server.server
