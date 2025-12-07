"""
AI Client for Preset Generation

Handles API calls to AI models (Gemini, Groq, Ollama) for natural language → KLWP JSON.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AIConfig:
    """AI model configuration."""
    provider: str  # 'gemini', 'groq', 'ollama'
    api_key: Optional[str] = None
    model: str = 'gemini-2.0-flash-exp'
    base_url: Optional[str] = None  # For Ollama


class AIClient:
    """Client for AI model API calls."""

    def __init__(self, config: AIConfig):
        """
        Initialize AI client.

        Args:
            config: AI configuration
        """
        self.config = config
        self.session = requests.Session()

        # Set up headers
        if config.provider == 'gemini':
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.model}:generateContent"
        elif config.provider == 'groq':
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.session.headers['Authorization'] = f'Bearer {config.api_key}'
        elif config.provider == 'ollama':
            self.api_url = f"{config.base_url or 'http://localhost:11434'}/api/generate"

    def generate_preset(self, user_prompt: str, preset_type: str = 'klwp') -> Dict[str, Any]:
        """
        Generate KLWP preset from natural language.

        Args:
            user_prompt: User's description
            preset_type: 'klwp', 'klck', or 'kwgt'

        Returns:
            KLWP preset JSON dict

        Raises:
            Exception: If API call fails
        """
        system_prompt = self._build_system_prompt(preset_type)

        if self.config.provider == 'gemini':
            return self._call_gemini(system_prompt, user_prompt)
        elif self.config.provider == 'groq':
            return self._call_groq(system_prompt, user_prompt)
        elif self.config.provider == 'ollama':
            return self._call_ollama(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown provider: {self.config.provider}")

    def _build_system_prompt(self, preset_type: str) -> str:
        """Build system prompt for preset generation."""
        return f"""You are a KLWP preset generator. Convert natural language descriptions into valid KLWP JSON.

PRESET TYPE: {preset_type.upper()}

OUTPUT FORMAT (JSON only, no markdown):
{{
    "version": 1,
    "width": 1080,
    "height": 1920,
    "items": [
        {{
            "type": "SHAPE",
            "id": "background",
            "shape_type": "rectangle",
            "color": "#000000",
            "width": 1080,
            "height": 1920,
            "position": {{"x": 0, "y": 0}}
        }},
        {{
            "type": "TEXT",
            "id": "clock",
            "text": "$df(HH:mm)$",
            "font_size": 96,
            "color": "#FFFFFF",
            "font": "Roboto",
            "position": {{"x": "center", "y": 800}},
            "align": "center"
        }}
    ]
}}

KLWP FORMULAS:
- Time: $df(HH:mm)$ or $df(hh:mm a)$
- Date: $df(EEEE, MMMM d)$ or $df(MMM d)$
- Battery: $bi(level)$ (0-100)
- Weather temp: $wi(temp)$
- Weather condition: $wi(cond)$
- Music title: $mi(title)$

ELEMENT TYPES:
- SHAPE: rectangle, circle, arc (for battery/progress)
- TEXT: labels, time, date, info
- IMAGE: icons, backgrounds (use placeholder)

COLORS: Use hex format (#RRGGBB or #AARRGGBB)
POSITIONS: Can be numeric, "center", or percentage like "50%"

IMPORTANT: Return ONLY valid JSON. No explanations, no markdown code blocks."""

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Call Google Gemini API."""
        url = f"{self.api_url}?key={self.config.api_key}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{system_prompt}\n\nUSER REQUEST: {user_prompt}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json"
            }
        }

        response = self.session.post(url, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Extract JSON from response
        try:
            content = data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse Gemini response: {e}\nResponse: {data}")

    def _call_groq(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Call Groq API (OpenAI-compatible)."""
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "response_format": {"type": "json_object"}
        }

        response = self.session.post(self.api_url, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        try:
            content = data['choices'][0]['message']['content']
            return json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse Groq response: {e}\nResponse: {data}")

    def _call_ollama(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Call local Ollama API."""
        payload = {
            "model": self.config.model,
            "prompt": f"{system_prompt}\n\nUSER REQUEST: {user_prompt}",
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.7,
                "num_predict": 2048
            }
        }

        response = self.session.post(self.api_url, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()

        try:
            content = data['response']
            return json.loads(content)
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse Ollama response: {e}\nResponse: {data}")


def create_ai_client(provider: str = 'gemini', api_key: Optional[str] = None,
                    model: Optional[str] = None, base_url: Optional[str] = None) -> AIClient:
    """
    Create AI client from environment or parameters.

    Args:
        provider: 'gemini', 'groq', or 'ollama'
        api_key: API key (or None to read from env)
        model: Model name (or None for default)
        base_url: Ollama base URL

    Returns:
        Configured AIClient

    Environment variables:
        GEMINI_API_KEY, GROQ_API_KEY, OLLAMA_BASE_URL
    """
    # Default models
    default_models = {
        'gemini': 'gemini-2.0-flash-exp',
        'groq': 'llama-3.3-70b-versatile',
        'ollama': 'llama3.2'
    }

    # Get API key from env if not provided
    if api_key is None:
        if provider == 'gemini':
            api_key = os.getenv('GEMINI_API_KEY')
        elif provider == 'groq':
            api_key = os.getenv('GROQ_API_KEY')

    # Get base URL for Ollama
    if provider == 'ollama' and base_url is None:
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

    config = AIConfig(
        provider=provider,
        api_key=api_key,
        model=model or default_models.get(provider, 'gemini-2.0-flash-exp'),
        base_url=base_url
    )

    return AIClient(config)


# Test/Example usage
if __name__ == "__main__":
    print("🦎 AI CLIENT TEST\n")

    # Example: Create client (requires API key in env)
    try:
        client = create_ai_client(provider='gemini')

        print("Testing preset generation...")
        preset = client.generate_preset(
            "Create a cyberpunk wallpaper with a digital clock and battery indicator",
            preset_type='klwp'
        )

        print("\n✅ Generated preset:")
        print(json.dumps(preset, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure to set GEMINI_API_KEY environment variable.")
