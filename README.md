# KLWP AI Assistant 🤖

AI-powered editor for Kustom Live Wallpaper (KLWP) files on Android. Modify your KLWP presets using natural language with local AI models, remote APIs, or SSH to your home server.

## Features

- 🤖 **Multiple AI Backends**
  - Local on-device AI models (lightweight, private)
  - SSH tunnel to home-hosted AI (Ollama, LM Studio, etc.)
  - Cloud API support (Gemini, Claude, etc.)

- 📱 **Smart Device Detection**
  - Automatically recommends best AI mode for your hardware
- 🎨 **Multi-Format Support**
  - Works with KLWP (wallpapers), KLCK (lock screens), and KWGT (widgets)
  - Create matching presets across formats
  - Automatic style extraction and adaptation
  - Maintain consistent theming
  - Performance scoring and optimization tips
  - Works on low-end to high-end devices

- 🎨 **KLWP Integration**
  - Browse and edit KLWP presets directly
  - Modify elements with natural language
  - Automatic preset backup before changes
  - Hot-reload KLWP after modifications

- 🔒 **Secure & Private**
  - Encrypted storage for API keys
  - SSH key management
  - Local processing options for privacy

## Download

**Latest Release:** [Download APK](https://github.com/YOUR_USERNAME/klwp-ai-assistant/releases/latest)

Or build from source (see below)

## Quick Start

1. Install the APK on your Android device
2. Grant storage permissions when prompted
3. Choose your AI backend:
   - **Local Model**: Best for privacy, works offline
   - **SSH Home Server**: Connect to your AI server at home
   - **Cloud API**: Use Gemini or other cloud services
4. Start editing KLWP with natural language!

## Example Commands

### Cross-Format Creation
- "Create a matching KLCK lock screen"
- "Make a 4x2 KWGT widget from this"
- "Generate KLWP wallpaper from my widget"
- "Create matching presets for all three apps"

- "Change all text colors to #00FF00"
- "Make the weather widget larger"
- "Set all fonts to Roboto"
- "Add a shadow to the clock"
- "List all text elements in the preset"

## Requirements

- Android 8.0 (API 26) or higher
- KLWP app installed
- Storage permissions
- (Optional) AI API key or home server for remote AI

## Building from Source

### Using GitHub Actions (Recommended)

1. Fork this repository
2. Push to `main` branch
3. GitHub Actions will automatically build the APK
4. Download from the Actions tab or Releases

### Local Build

```bash
# Install buildozer
pip install buildozer cython==0.29.36

# Build APK
buildozer android debug

# APK will be in bin/ folder
```

## Architecture

- **Frontend**: Kivy + KivyMD for native Android UI
- **Backend**: Python MCP server for KLWP file manipulation
- **AI Integration**: Pluggable backends (local/SSH/API)
- **Storage**: Secure encrypted storage for credentials

## Project Structure

```
.
├── app/                    # Main application code
│   ├── main.py            # App entry point & UI
│   ├── device_detector.py # Hardware detection
│   ├── secure_storage.py  # Encrypted key storage
│   └── ssh_tunnel.py      # SSH connection manager
├── klwp_mcp_server/       # KLWP file handler
│   ├── klwp_handler.py    # ZIP/JSON operations
│   └── server.py          # MCP protocol server
├── integrations/          # AI backend integrations
│   ├── gemini_klwp.py     # Gemini API
│   └── klwp_http_server.py # HTTP API for external AIs
└── buildozer.spec         # Android build configuration
```

## Development

### Prerequisites

- Python 3.11+
- Android SDK (for local builds)
- Git

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/klwp-ai-assistant.git
cd klwp-ai-assistant

# Install dependencies
pip install -r app/requirements.txt

# Test locally (will need Android emulator or device)
python app/main.py
```

## Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Credits

Built with:
- [Kivy](https://kivy.org/) - Cross-platform Python framework
- [KivyMD](https://kivymd.readthedocs.io/) - Material Design components
- [Buildozer](https://buildozer.readthedocs.io/) - Android packaging

## Support

- 🐛 [Report bugs](https://github.com/YOUR_USERNAME/klwp-ai-assistant/issues)
- 💡 [Request features](https://github.com/YOUR_USERNAME/klwp-ai-assistant/issues)
- 📖 [Documentation](https://github.com/YOUR_USERNAME/klwp-ai-assistant/wiki)

---

**Note:** This is an unofficial tool and is not affiliated with Kustom or its developers.
