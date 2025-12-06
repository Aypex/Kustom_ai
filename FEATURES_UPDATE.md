# New Features Added

## 1. AI Context System (`app/ai_prompts.py`)

Every AI model (local, SSH, or API) now automatically receives specialized prompts that teach it how to:

### Understand Kustom Formats
- KLWP (Live Wallpaper) - Full-screen layouts
- KLCK (Lock Screen) - Lock screen designs  
- KWGT (Widget) - Home screen widgets

### Modify Presets Intelligently
- Change colors, fonts, sizes, positions
- Add shadows, effects, animations
- Preserve formulas and complex logic
- Create backups automatically

### Create Matching Presets
When you say "create a matching KLCK" it will:
- Extract your KLWP's color palette
- Match fonts and design style
- Adapt layout for lock screen format
- Maintain visual consistency

## 2. Universal Kustom Handler (`app/kustom_handler.py`)

Single unified code for all three Kustom apps:

### Features
- **Multi-format support**: Handles .klwp, .klck, and .kwgt files
- **Cross-preset creation**: Convert between formats while preserving style
- **Style extraction**: Automatically detect colors, fonts, and design patterns
- **Smart adaptation**: Adjusts layouts for each format's constraints

### Example Usage
```python
# Create KLCK from KLWP
handler = KustomHandler('klwp')
handler.create_matching_preset('MyWallpaper', 'klck', 'MyLockScreen')

# Create KWGT from either
handler.create_matching_preset('MyWallpaper', 'kwgt', 'MyClock')
```

## 3. How It Works

### When You Open a Preset
1. App detects preset type (.klwp, .klck, or .kwgt)
2. Loads appropriate system prompt for AI
3. Analyzes preset structure (colors, fonts, elements)
4. Prepends context to every AI message

### When You Ask to Modify
**You:** "Change all text to blue"

**AI receives:**
```
[SYSTEM PROMPT: Expert in KLWP/KLCK/KWGT, knows all element types...]
[CURRENT PRESET: MyWallpaper.klwp, 15 elements, colors: #FF0000, #00FF00...]
[USER]: Change all text to blue
```

**AI responds:** "I'll change all TEXT elements to #0000FF. Found 5 text elements..."

### When You Ask for Matching Preset
**You:** "Create a matching lock screen"

**AI receives:**
- Full system prompt with cross-preset instructions
- Current preset's extracted style data
- Specific guidance on KLCK layout requirements

**AI creates:**
- New .klck file with matching colors/fonts
- Lock screen appropriate layout (time, date, battery)
- Maintains your visual identity

## 4. Example Commands You Can Use

### Modifications
- "Change the clock font to Roboto Bold"
- "Make all backgrounds 50% transparent"
- "Add a blue glow to the battery indicator"
- "Set weather widget to use my accent color"

### Cross-Format Creation
- "Create a matching KLCK lock screen"
- "Make a 4x2 KWGT widget version"
- "Generate a KLWP wallpaper from this widget"
- "Create KLCK, KWGT, and KLWP versions with the same style"

### Style Analysis
- "What colors are used in this preset?"
- "List all fonts in use"
- "Show me all the text elements"
- "Analyze the design style"

## 5. Benefits

### For Users
- **Consistent theming** across wallpaper, lock screen, and widgets
- **Faster workflow** - AI understands Kustom automatically
- **Better results** - Context-aware suggestions
- **No manual conversion** between formats

### For Developers
- **Clean code** - Single handler for all formats
- **Extensible** - Easy to add new AI backends
- **Maintainable** - Centralized prompt management
- **Testable** - Isolated components

## 6. Technical Implementation

### Prompt Injection
```python
from app.ai_prompts import get_system_prompt, get_user_context

# When initializing AI
system_prompt = get_system_prompt('klwp', target_type='klck')

# Before each user message
context = get_user_context(preset_data, 'MyWallpaper.klwp')
full_message = context + "\n\n" + user_message
```

### Cross-Preset Workflow
```python
# 1. User selects KLWP preset
handler_klwp = KustomHandler('klwp')
data = handler_klwp.read_preset('MyWallpaper')

# 2. User asks "create matching KLCK"
# AI or user triggers:
handler_klck = KustomHandler('klck')
new_data = handler_klwp.create_matching_preset(
    'MyWallpaper',
    'klck',
    'MyLockScreen'
)

# 3. Save new preset
handler_klck.save_preset('MyLockScreen', new_data)
```

## 7. Future Enhancements

- Image-based style transfer (match wallpaper photo colors)
- Component library (reusable elements across presets)
- Batch operations (apply changes to multiple presets)
- Style presets (apply "Material", "iOS", "Minimal" themes)
- AI-generated formulas for dynamic content

---

This makes the KLWP AI Assistant the first tool to seamlessly work across all three Kustom apps with intelligent cross-format support!
