#!/bin/bash
# Install KLWP AI Assistant App

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "KLWP AI Assistant - Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Check if in Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo "❌ Error: This must be run in Termux"
    exit 1
fi

echo "📦 Installing dependencies..."
echo

# Install system packages
pkg install -y python python-pip

# Install Python packages
pip install --upgrade pip
pip install kivy kivymd pycryptodome paramiko

echo
echo "✅ Dependencies installed!"
echo

# Make scripts executable
chmod +x app/main.py
chmod +x app/secure_storage.py
chmod +x app/ssh_tunnel.py
chmod +x app/model_manager.py

echo "✅ Scripts configured!"
echo

# Create desktop icon script
cat > ~/run_klwp_ai.sh << 'EOF'
#!/bin/bash
cd ~/klwp-mcp
python app/main.py
EOF

chmod +x ~/run_klwp_ai.sh

echo "✅ Launcher created!"
echo

# Create Termux widget shortcut
SHORTCUTS_DIR="~/.shortcuts"
mkdir -p "$SHORTCUTS_DIR"

cat > "$SHORTCUTS_DIR/KLWP AI" << 'EOF'
#!/bin/bash
cd ~/klwp-mcp
python app/main.py
EOF

chmod +x "$SHORTCUTS_DIR/KLWP AI"

echo "✅ Termux widget shortcut created!"
echo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Installation Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "🚀 To run the app:"
echo "   python app/main.py"
echo
echo "Or use Termux widget:"
echo "   1. Long-press home screen"
echo "   2. Add widget → Termux:Widget"
echo "   3. Tap 'KLWP AI'"
echo
echo "📱 Features:"
echo "   ✓ Local AI models (on-device)"
echo "   ✓ SSH to home network"
echo "   ✓ API models (Gemini)"
echo "   ✓ Secure credential storage"
echo "   ✓ KLWP preset browser"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
