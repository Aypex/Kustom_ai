# 🎨 Flux UI Generation Prompts

**Terminal Chic / Industrial Brutalism Aesthetic for Chameleon**

Use these prompts with **Flux.1-dev** or **Flux.1-schnell** to generate UI mockups.

---

## 🖥️ Prompt 1: Main Command Deck (Home Screen)

The primary chat interface where users type natural language commands.

```
Mobile app UI design for Android, "Chameleon" app, dark mode, industrial cyberpunk aesthetic. Screen shows a command terminal interface. Top section: Data visualization widgets, minimalist line graphs in neon amber. Center: Large empty space with subtle grid pattern. Bottom: A prominent text input field labeled "NATURAL LANGUAGE INPUT" with a blinking cursor. Font is monospace / console style. High contrast, charcoal grey background, brutalist layout, sharp edges. 4k resolution, UI design, flat vector style.
```

**What to look for:**
- Input field should be prominent and inviting
- Grid pattern should be subtle (not loud retro)
- Monospace fonts throughout
- Sharp 90° angles, no rounded corners

---

## 💥 Prompt 2: Molting Effect (Theme Transition)

The chromatic aberration ripple - the visual centerpiece of the easter egg.

```
Mobile UI glitch effect, digital screen distortion. An Android app interface mid-transition. A ripple of chromatic aberration (RGB split) expanding from the center. The left side of the ripple is neon green (old theme), the right side of the ripple is deep crimson red (new theme). Text elements are slightly fragmented / tearing. "SYSTEM ADAPTATION IN PROGRESS" text visible. High tech, raw, aggressive visual style, data moshing.
```

**What to look for:**
- Clear RGB channel split (distinct red/blue edges)
- Digital artifacts (pixels, blocks) not blur
- "Tearing" effect, not smooth gradient
- Looks like software breaking/evolving

---

## 🦎 Prompt 3: Easter Egg Dialog

The popup where Chameleon reveals its adaptive nature.

```
Closeup of a mobile UI notification card. Dark brutalist style. A sharp rectangular dialog box with a thin neon red border. Inside the box, monospace text reads: "I'M A CHAMELEON. WHAT DID YOU EXPECT?". Two buttons below: "KEEP IT" (solid block) and "REVERT" (outline). Background is dimmed/blurred. The aesthetic is menacing but clean. Code editor vibe.
```

**What to look for:**
- Sharp 90° angles, NO rounded corners
- Thin border, not thick
- Monospace font
- Attitude conveyed through geometry

---

## 📡 Prompt 4: INTEL Screen (Settings)

Settings screen with the [ INTEL ] button and API configuration.

```
Settings menu UI for a hacker app. List of text-only options. Monospace font. Items: "API KEY [HIDDEN]", "LOCAL MODEL: OLLAMA", "CACHE STATUS: DIRTY". A distinct button at the top labeled "[ INTEL ]" with a small link icon. The design is strictly functional, like a BIOS screen or a bootloader. White text on pitch black. No images, just layout and typography.
```

**What to look for:**
- Minimal decoration
- Text alignment is precise
- OLED black background (#000000)
- Monospace everywhere
- Looks like a BIOS/bootloader

---

## 🎨 Color Palette Variations

If the default colors don't fit, try these variations:

**Neon Amber (Default):**
- Background: `#1A1A1A` (charcoal)
- Accent: `#FFB000` (amber)
- Text: `#FFFFFF` (white)

**Electric Blue (Cyberpunk):**
- Background: `#0A0A0A` (near black)
- Accent: `#00D9FF` (cyan)
- Text: `#E0E0E0` (light grey)

**Clinical White (Purist):**
- Background: `#000000` (pure OLED black)
- Accent: `#FFFFFF` (white)
- Text: `#FFFFFF` (white)

**Blood Red (Aggressive):**
- Background: `#0D0D0D` (dark charcoal)
- Accent: `#FF0033` (crimson)
- Text: `#F5F5F5` (off-white)

---

## 🚀 Generation Tips

### Running Locally (Flux.1-schnell):
```bash
# ComfyUI or Automatic1111
# Settings:
# - Steps: 4-8 (schnell is distilled, needs fewer)
# - Guidance: 1.0
# - Sampler: Euler
# - Resolution: 1080x1920 (mobile portrait)
```

### Using API (Replicate/Fal.ai):
```python
# Example with Replicate
import replicate

output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={
        "prompt": "YOUR PROMPT HERE",
        "aspect_ratio": "9:16",  # Mobile portrait
        "num_outputs": 4  # Generate 4 variants
    }
)
```

---

## 📐 Layout Guidelines

**Mobile Specs:**
- Canvas: 1080x1920px (standard Android)
- Safe area padding: 20px all sides
- Touch targets: Minimum 48x48dp
- Font sizes:
  - Headers: 24sp
  - Body: 16sp
  - Monospace: 14sp

**Brutalist Rules:**
- No gradients (solid colors only)
- No drop shadows (except for depth in modals)
- No rounded corners (0px radius)
- Grid lines: 1px, 50% opacity max
- Sharp, aggressive geometry

---

## 🎯 Next Steps

1. **Generate 4-5 variants** of each prompt
2. **Pick the sharpest** (not the prettiest)
3. **Feed to Claude Code:**
   - "Replicate this Jetpack Compose layout"
   - "Use Material3 but strip all rounded corners"
   - "Implement with brutalist aesthetic"

4. **Iterate:**
   - Claude generates code
   - You test in app
   - Refine based on feel

---

## 🦎 Philosophy

> "Function over form. Information over decoration."

The UI should feel like:
- A control deck, not an app
- A tool, not a toy
- Software with an attitude

If it looks friendly, it's wrong.
If it looks like it could hack the Pentagon, it's right.

---

*Generated for Chameleon - December 2024*
