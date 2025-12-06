# AI Model Integrations for KLWP CLI

This directory contains integrations that let **any AI model** (Gemini, local models, etc.) control KLWP.

## Available Integrations

### 1. JSON API (`klwp_json_api.py`)

**Best for**: Any AI that can pass JSON

```bash
# Input JSON via stdin
echo '{"action": "list"}' | python klwp_json_api.py

# Or as argument
python klwp_json_api.py '{"action": "elements", "preset": "my.klwp"}'
```

**Available actions**:
```json
{"action": "list"}
{"action": "elements", "preset": "my.klwp", "type": "TEXT"}
{"action": "find", "preset": "my.klwp", "search": "clock"}
{"action": "modify", "preset": "my.klwp", "element_id": "text_1", "properties": {"text": "Hello"}, "save": true}
{"action": "reload"}
```

### 2. HTTP Server (`klwp_http_server.py`)

**Best for**: Network-accessible AI, web interfaces, remote models

```bash
# Start server
python klwp_http_server.py --port 8080

# Use from any AI
curl http://localhost:8080/list
curl 'http://localhost:8080/elements?preset=my.klwp&type=TEXT'
curl -X POST http://localhost:8080/modify -d '{"preset":"my.klwp","element_id":"text_1","properties":{"text":"Hi"},"save":true}'
```

### 3. Gemini Integration (`gemini_klwp.py`)

**Best for**: Google Gemini users

```bash
# Setup
pip install google-generativeai
export GEMINI_API_KEY="your-key"

# Run
python gemini_klwp.py

# Chat naturally
You: List my KLWP presets
You: Show text elements in my_preset.klwp
You: Change element text_1 to say "Good Morning"
```

## Usage Examples

### With Gemini (via JSON API)

```python
import subprocess
import json

def ask_gemini_to_modify_klwp(prompt):
    # Your Gemini code here determines what to do
    # Then execute:
    command = {
        "action": "modify",
        "preset": "my_preset.klwp",
        "element_id": "text_1",
        "properties": {"text": "New text"},
        "save": True
    }

    result = subprocess.run(
        ['python', 'integrations/klwp_json_api.py', json.dumps(command)],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)
```

### With Local Models (Ollama)

```bash
# Start HTTP server
python integrations/klwp_http_server.py &

# Use with Ollama
ollama run llama3.2 "List my KLWP presets: $(curl -s http://localhost:8080/list)"
```

### With Termux:API

```bash
# Voice command
termux-speech-to-text > /tmp/cmd.txt
COMMAND=$(cat /tmp/cmd.txt)

# Process with local model or simple logic
if [[ "$COMMAND" == *"list presets"* ]]; then
    python integrations/klwp_json_api.py '{"action":"list"}' | termux-tts-speak
fi
```

### With LMStudio

```python
# In LMStudio, create a function/tool:
{
  "name": "klwp_command",
  "description": "Execute KLWP commands",
  "parameters": {
    "command": "JSON command string"
  }
}

# Implementation:
def klwp_command(command):
    import subprocess, json
    result = subprocess.run(
        ['python', 'integrations/klwp_json_api.py', command],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)
```

## Integration Checklist

✅ **Works with**:
- Google Gemini (function calling)
- Ollama (local models)
- LMStudio
- llama.cpp
- Any model with shell access
- Any model with HTTP capabilities
- Custom AI applications

✅ **Requires**:
- Python 3.10+
- KLWP installed on Android
- Termux (for local execution)

## Examples by Model Type

### Gemini Pro

Use the dedicated `gemini_klwp.py` script with function calling support.

### Llama 3.2 (Ollama)

```bash
# Via HTTP
python integrations/klwp_http_server.py &
ollama run llama3.2

>>> Use the KLWP API at localhost:8080 to list presets
```

### GPT-4 (with Code Interpreter)

```python
# In ChatGPT Code Interpreter
import subprocess, json

result = subprocess.run([
    'python', '/path/to/klwp_json_api.py',
    json.dumps({"action": "list"})
], capture_output=True, text=True)

print(result.stdout)
```

### Local Model (Any)

```bash
# Simplest: pipe commands
echo "List KLWP presets" > prompt.txt
cat prompt.txt | your-local-model

# Then execute based on output
python integrations/klwp_json_api.py '{"action":"list"}'
```

## Advanced: Create Your Own Integration

```python
#!/usr/bin/env python3
# your_ai_integration.py

from integrations.klwp_json_api import execute_klwp

# Your AI model
def your_ai_function(user_prompt):
    # AI determines what to do
    # Returns a KLWP command
    return {
        "action": "modify",
        "preset": "my.klwp",
        "element_id": "text_1",
        "properties": {"text": "AI generated text"}
    }

# Execute
user_input = "Change my wallpaper text"
command = your_ai_function(user_input)
result = execute_klwp(command)
print(result)
```

## Performance Notes

- **JSON API**: Fastest, direct execution
- **HTTP Server**: Small overhead, but works over network
- **Gemini Integration**: Requires API calls, depends on network

## Security

⚠️ The HTTP server binds to `localhost` by default. To expose externally:

```bash
# Only do this on trusted networks!
python klwp_http_server.py --host 0.0.0.0 --port 8080
```

## Troubleshooting

**JSON API not working**:
- Check Python path
- Verify klwp_cli.py exists
- Test with: `python klwp_json_api.py '{"action":"list"}'`

**HTTP Server connection refused**:
- Check port: `netstat -an | grep 8080`
- Try different port: `--port 8081`
- Check firewall settings

**Gemini integration fails**:
- Verify API key: `echo $GEMINI_API_KEY`
- Install package: `pip install google-generativeai`
- Check quota: https://makersuite.google.com/

## Contributing

Want to add integration for another AI model? Follow this pattern:

1. Create wrapper that calls KLWP CLI
2. Map AI's function/tool format to KLWP commands
3. Handle JSON parsing
4. Add error handling
5. Document usage

See existing integrations for examples!
