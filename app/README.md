# KLWP AI Assistant - Android App

A native Android app for controlling KLWP with AI! Tap an icon and choose between local models, SSH to your home network, or cloud APIs.

## ✨ Features

### 🤖 Three AI Model Options

1. **Local Model (On-Device)**
   - Runs entirely on your Pixel 10 Pro XL
   - Uses Tensor G5 NPU when available
   - No internet required
   - Best privacy & speed

2. **SSH to Home Network**
   - Access powerful models on your home PC
   - Secure encrypted tunnel
   - Use your desktop's GPU
   - Perfect for larger models

3. **API Models (Gemini)**
   - Cloud-based AI
   - Latest models
   - No local resources needed
   - Best for complex tasks

### 🔒 Secure Credential Storage

- **AES-256 encryption** for all credentials
- Device-specific encryption keys
- API keys never stored in plaintext
- SSH passwords encrypted
- Automatic secure deletion

### 📱 Native Android UI

- Material Design interface
- Dark mode support
- Smooth animations
- Optimized for Pixel

### 📁 KLWP Integration

- Browse KLWP presets
- View preset locations
- Quick access to elements
- Live modification

## 🚀 Installation

### Quick Install

```bash
cd ~/klwp-mcp/app
chmod +x install.sh
./install.sh
```

### Manual Install

```bash
# Install dependencies
pkg install python python-pip
pip install kivy kivymd pycryptodome paramiko

# Make executable
chmod +x app/main.py

# Run
python app/main.py
```

## 📱 Usage

### Launch the App

**Method 1: Command Line**
```bash
cd ~/klwp-mcp
python app/main.py
```

**Method 2: Termux Widget**
1. Long-press home screen
2. Add widget → Termux:Widget
3. Tap "KLWP AI"

**Method 3: Shortcut**
```bash
~/run_klwp_ai.sh
```

### Using Local Models

1. Tap "🤖 Local Model (On-Device)"
2. Type your request:
   - "List my KLWP presets"
   - "Show text elements in my preset"
   - "Change the clock to 24-hour format"
3. Model processes and executes

**Requirements:**
- Ollama installed in proot
- At least one model pulled (llama3.2:1b recommended)

### Using SSH Models

1. Tap "🏠 SSH to Home Network"
2. Enter connection details:
   - **SSH Host**: Your PC's IP (e.g., 192.168.1.100)
   - **Username**: Your PC username
   - **Password** or **SSH Key**: Authentication
   - **Remote Endpoint**: Model URL (e.g., http://localhost:11434)
3. Tap "Save & Connect"
4. Chat with your home model!

**Requirements:**
- SSH server running on home PC
- Ollama (or similar) running on home PC
- Port forwarding configured if accessing remotely

### Using API Models

1. Tap "☁️ API Model (Gemini)"
2. Enter your Gemini API key
   - Get one free at: https://makersuite.google.com/app/apikey
3. Tap "Save & Continue"
4. Start chatting!

**Requirements:**
- Internet connection
- Gemini API key

## 🔧 Architecture

```
app/
├── main.py              # Main app UI
├── secure_storage.py    # Encrypted credential storage
├── ssh_tunnel.py        # SSH tunneling
├── model_manager.py     # Model backend manager
├── requirements.txt     # Python dependencies
├── install.sh          # Installation script
└── README.md           # This file
```

### Screens

- **HomeScreen**: Model selection
- **LocalModelScreen**: Local AI chat
- **SSHSetupScreen**: SSH configuration
- **APISetupScreen**: API key setup
- **PresetsScreen**: Browse KLWP presets
- **SettingsScreen**: App settings

## 🔒 Security

### Credential Storage

All credentials are encrypted using:
- **Algorithm**: AES-256-CBC
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Device-Bound**: Keys tied to device ID
- **File Permissions**: 0600 (owner read/write only)

### What Gets Encrypted?

- ✅ Gemini API keys
- ✅ SSH passwords
- ✅ SSH private key paths
- ✅ Remote endpoints
- ✅ All user credentials

### Credential Location

```
~/.klwp_credentials/
├── credentials.enc  # Encrypted credentials
└── key.dat         # Encryption key (device-specific)
```

**Permissions**: `drwx------` (700) - Owner only

## 🎨 Customization

### Change Theme

Edit `app/main.py`:
```python
class KLWPAIApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Light'  # or 'Dark'
        self.theme_cls.primary_palette = 'Blue'  # or other
```

### Add New Model Backend

1. Edit `app/model_manager.py`
2. Add new method:
```python
def use_custom_model(self):
    # Your implementation
    self.current_model = ("custom", config)
    return True
```

3. Add query handler:
```python
def _query_custom(self, prompt, config):
    # Your query logic
    return response
```

### Add New Screen

1. Create screen class in `app/main.py`:
```python
class MyNewScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'my_screen'
        # Add widgets
```

2. Register in main app:
```python
sm.add_widget(MyNewScreen())
```

## 🐛 Troubleshooting

### App won't start

**Check Kivy installation:**
```bash
python -c "import kivy; print(kivy.__version__)"
```

**Reinstall dependencies:**
```bash
pip install --force-reinstall kivy kivymd
```

### SSH connection fails

**Test manually:**
```bash
python app/ssh_tunnel.py your-host your-user your-password
```

**Check firewall:**
- Ensure SSH port (22) is open
- Verify model port (11434) is accessible

### Local model not found

**Install Ollama:**
```bash
proot-distro install ubuntu
proot-distro login ubuntu
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:1b
```

### Credentials not saving

**Check permissions:**
```bash
ls -la ~/.klwp_credentials/
# Should show: drwx------
```

**Reset storage:**
```bash
python -c "from app.secure_storage import SecureStorage; SecureStorage().clear()"
```

### API key invalid

**Verify key:**
- Must start with correct prefix
- Check for typos
- Ensure key is active at makersuite.google.com

**Test manually:**
```bash
python integrations/gemini_simple.py "test"
```

## 📊 Performance

### Resource Usage

| Mode | RAM | CPU | Battery |
|------|-----|-----|---------|
| Local (1B) | ~2GB | Medium | Good |
| SSH | ~100MB | Low | Excellent |
| API | ~50MB | Minimal | Excellent |

### Speed Comparison

| Mode | Latency | Quality |
|------|---------|---------|
| Local | <1s | ⭐⭐⭐ |
| SSH | 1-3s | ⭐⭐⭐⭐ |
| API | 2-5s | ⭐⭐⭐⭐⭐ |

## 🔄 Updates

### Update App

```bash
cd ~/klwp-mcp
git pull  # if using git

# Or re-download
# Then reinstall:
cd app
./install.sh
```

### Update Dependencies

```bash
pip install --upgrade kivy kivymd pycryptodome paramiko
```

## 📝 Changelog

### v1.0.0 (2024-12-06)
- ✨ Initial release
- 🤖 Local model support
- 🏠 SSH tunnel integration
- ☁️ Gemini API support
- 🔒 Secure credential storage
- 📱 Material Design UI
- 📁 KLWP preset browser

## 🤝 Contributing

Want to add features? Ideas:

- [ ] Voice input integration
- [ ] Preset templates
- [ ] Batch operations
- [ ] Export/import settings
- [ ] Theme customization
- [ ] Notification integration

## 📄 License

MIT License - See main project LICENSE

## 🙏 Acknowledgments

- **Kivy** - Python UI framework
- **KivyMD** - Material Design
- **Paramiko** - SSH library
- **PyCryptodome** - Encryption

## 📞 Support

- Issues: File in main klwp-mcp repository
- Docs: See main README.md
- Security: Report privately

---

**Made with ❤️ for KLWP automation**
