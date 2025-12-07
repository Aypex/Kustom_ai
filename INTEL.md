# 🦎 CHAMELEON INTEL

**Live intelligence feed for AI backend recommendations.**

*Last Updated: December 7, 2024*

---

## 🎯 Quick Start

Chameleon supports three AI backends:
1. **Local Models** (Privacy, offline)
2. **SSH to Home Network** (Your hardware, your rules)
3. **Cloud APIs** (Maximum capability)

---

## ☁️ RECOMMENDED: Cloud API (Zero Cost Options)

### Option 1: Google Gemini 2.0 ⭐ BEST FOR MOST USERS

**Status:** ✅ **FREE TIER ACTIVE** (as of Dec 2024)

**Why Recommended:**
- Extremely capable for preset generation
- Free API tier with generous limits (15 RPM)
- Works great with complex natural language

**How to Get Started:**
1. Go to: https://aistudio.google.com/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key
5. Paste into Chameleon → Settings → API Key

**⚠️ PRIVACY NOTICE:**
- **Free Tier:** Google may use your interactions to train models
- **Paid Tier:** Your data is private
- For theme/color requests this is fine
- For sensitive content, use local models

**Rate Limits:**
- Free: 15 requests/minute (plenty for casual use)
- Paid: Higher limits available

---

### Option 2: Groq ⚡ FASTEST

**Status:** ✅ **FREE TIER ACTIVE**

**Why Recommended:**
- Insanely fast (generates text faster than you can read)
- Hosts open-source models (Llama 3, Mixtral)
- Free developer tier
- Feels futuristic

**How to Get Started:**
1. Go to: https://console.groq.com
2. Sign up
3. Create API key
4. Use in Chameleon

**Models Available:**
- `llama3-70b-8192` (Recommended)
- `mixtral-8x7b-32768`
- `gemma-7b-it`

---

## 🏠 SSH to Home Network

**For Power Users with existing AI servers**

**Supported Backends:**
- Ollama
- LM Studio
- Text Generation WebUI
- Any OpenAI-compatible API

**Setup:**
1. Install AI server on home PC/NAS
2. Note IP address and port
3. Configure SSH tunnel or expose API
4. Enter connection details in Chameleon

**Recommended Models:**
- Qwen 2.5 Coder 32B (best for code)
- Llama 3.1 70B (general purpose)
- Mixtral 8x7B (fast, capable)

---

## 🤖 Local On-Device Models

**For Maximum Privacy**

**Status:** ⚠️ Requires ~2GB+ storage, powerful device

**How It Works:**
- Chameleon can run small models directly on your phone
- No internet required
- 100% private

**Recommended:**
- Gemma 2 2B
- Phi-3 Mini 3.8B
- Llama 3.2 3B

**Note:** For complex preset generation, cloud APIs work better.
Local models are great for simple commands and privacy.

---

## 💰 Cost Comparison

| Backend | Monthly Cost | Privacy | Speed | Capability |
|---------|-------------|---------|-------|------------|
| Gemini Free | $0 | ⚠️ Training data | Fast | ⭐⭐⭐⭐⭐ |
| Groq Free | $0 | ⚠️ Training data | ⚡ Ultra | ⭐⭐⭐⭐ |
| Home SSH | Hardware only | ✅ Full | Medium | ⭐⭐⭐⭐⭐ |
| Local Phone | $0 | ✅ Full | Slow | ⭐⭐⭐ |

---

## 🔧 Troubleshooting

### "API Key Invalid"
- Double-check you copied the full key
- Gemini keys start with `AI...`
- No spaces before/after

### "Rate Limit Exceeded"
- Free tiers have limits
- Wait a minute, try again
- Consider paid tier for heavy use

### "Connection Failed" (SSH)
- Check IP address and port
- Ensure home server is running
- Test with curl first

---

## 📡 Status Updates

**Current Status (Dec 2024):**
- ✅ Gemini 2.0 Free Tier: **ACTIVE**
- ✅ Groq Free Tier: **ACTIVE**
- ✅ SSH/Local: **STABLE**

**Check for updates:** This document is updated when API status changes.

---

## 🦎 Philosophy

Chameleon is built on **Radical Sovereignty**:
- Your data stays yours (unless you choose cloud free tiers)
- No accounts, no login, no tracking
- Works offline (local/SSH modes)
- You choose the tradeoff: Cost vs Privacy vs Capability

**We recommend what works best, but you decide.**

---

## 🆘 Need Help?

- Issues: https://github.com/Aypex/Kustom_ai/issues
- This doc updates automatically, no app update needed

---

*"The more you control, the less you can be controlled."*
