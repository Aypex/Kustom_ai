"""
AGSL Molting Shader - Chromatic Aberration Ripple Effect

This is the visual effect for the easter egg theme transition.
Creates a "digital molting" effect where RGB channels split during transition.

NOTE: This is Python documentation for the Kotlin implementation.
The actual AGSL shader code below needs to be added to the Android app
in a Kotlin file (see instructions at bottom).
"""

# AGSL Shader Source Code (Copy this to Kotlin)
MOLTING_SHADER_AGSL = """
uniform shader composable;   // The UI content
uniform float time;          // 0.0 to 1.0 (transition progress)
uniform float2 resolution;   // Screen size

// Pseudo-random noise function
float random(float2 st) {
    return fract(sin(dot(st.xy, float2(12.9898, 78.233))) * 43758.5453123);
}

half4 main(float2 fragCoord) {
    // Normalize coordinates (0-1)
    float2 uv = fragCoord.xy / resolution.xy;

    // Calculate distance from center
    float dist = distance(uv, float2(0.5, 0.5));

    // Create expanding ripple wave
    // The wave is a thin ring that expands outward
    float wave = smoothstep(time - 0.1, time, dist) -
                 smoothstep(time, time + 0.1, dist);

    // Add glitchy noise to the wave (digital artifacts)
    float glitch = (random(uv * time) - 0.5) * 0.05 * wave;

    // Chromatic aberration offsets (RGB channel split)
    float2 redOffset = float2(glitch, 0.0);
    float2 blueOffset = float2(-glitch, 0.0);

    // Sample the UI with channel offsets
    half4 normalColor = composable.eval(fragCoord);
    half4 redChannel = composable.eval(fragCoord + redOffset * resolution.xy);
    half4 blueChannel = composable.eval(fragCoord + blueOffset * resolution.xy);

    // Mix channels - creates the "tearing" effect
    // Wave intensity determines how much chromatic aberration shows
    half4 glitchColor = half4(
        redChannel.r,     // Red channel shifted right
        normalColor.g,    // Green channel normal
        blueChannel.b,    // Blue channel shifted left
        1.0
    );

    // Blend normal and glitch based on wave
    return mix(normalColor, glitchColor, wave * 2.0);
}
"""


# Kotlin Implementation Template
KOTLIN_IMPLEMENTATION = """
// File: app/src/main/kotlin/com/chameleonai/chameleon/MoltingShader.kt

package com.chameleonai.chameleon

import android.graphics.RuntimeShader
import androidx.compose.ui.graphics.ShaderBrush
import org.intellij.lang.annotations.Language

// The AGSL shader source
@Language("AGSL")
private const val MOLTING_SHADER_SRC = '''
    uniform shader composable;
    uniform float time;
    uniform float2 resolution;

    float random(float2 st) {
        return fract(sin(dot(st.xy, float2(12.9898, 78.233))) * 43758.5453123);
    }

    half4 main(float2 fragCoord) {
        float2 uv = fragCoord.xy / resolution.xy;
        float dist = distance(uv, float2(0.5, 0.5));

        float wave = smoothstep(time - 0.1, time, dist) -
                     smoothstep(time, time + 0.1, dist);

        float glitch = (random(uv * time) - 0.5) * 0.05 * wave;

        float2 redOffset = float2(glitch, 0.0);
        float2 blueOffset = float2(-glitch, 0.0);

        half4 normalColor = composable.eval(fragCoord);
        half4 redChannel = composable.eval(fragCoord + redOffset * resolution.xy);
        half4 blueChannel = composable.eval(fragCoord + blueOffset * resolution.xy);

        half4 glitchColor = half4(redChannel.r, normalColor.g, blueChannel.b, 1.0);

        return mix(normalColor, glitchColor, wave * 2.0);
    }
'''

/**
 * Create a molting shader brush for Compose.
 *
 * @param progress Transition progress (0.0 to 1.5 recommended)
 * @param width Screen width in pixels
 * @param height Screen height in pixels
 * @return ShaderBrush ready to use in Compose Modifier
 */
fun createMoltingBrush(progress: Float, width: Float, height: Float): ShaderBrush {
    val shader = RuntimeShader(MOLTING_SHADER_SRC)
    shader.setFloatUniform("time", progress)
    shader.setFloatUniform("resolution", width, height)
    return ShaderBrush(shader)
}

/**
 * Composable modifier to apply molting effect.
 *
 * Usage in Compose:
 * ```kotlin
 * Box(
 *     modifier = Modifier
 *         .fillMaxSize()
 *         .drawWithCache {
 *             val brush = createMoltingBrush(animatedProgress, size.width, size.height)
 *             onDrawBehind {
 *                 drawRect(brush)
 *             }
 *         }
 * )
 * ```
 */
"""


# Animation Timeline
ANIMATION_GUIDE = """
=== MOLTING SHADER ANIMATION TIMELINE ===

Total Duration: 1000ms (1 second)

PHASE 1: Pre-Ripple (0-200ms)
- time: 0.0 → 0.2
- Effect: Ripple starts at center, barely visible
- User sees: Subtle distortion building at center

PHASE 2: Main Ripple (200-700ms)
- time: 0.2 → 0.7
- Effect: RGB split wave expands across screen
- User sees: Chromatic aberration tearing outward
- Colors "molt" from old theme to new theme

PHASE 3: Settle (700-1000ms)
- time: 0.7 → 1.0
- Effect: Ripple completes, glitch fades
- User sees: New theme fully visible, clean

PHASE 4: Overshoot (1000-1200ms) [Optional]
- time: 1.0 → 1.2
- Effect: Slight reverse pulse for impact
- User sees: Final "snap" into place

Recommended Implementation:
```kotlin
val animatedProgress by animateFloatAsState(
    targetValue = if (triggered) 1.2f else 0f,
    animationSpec = tween(
        durationMillis = 1200,
        easing = FastOutSlowInEasing
    )
)
```
"""


# Usage Instructions
USAGE_INSTRUCTIONS = """
=== HOW TO USE THE MOLTING SHADER ===

1. CREATE THE KOTLIN FILE:
   - Copy the KOTLIN_IMPLEMENTATION code above
   - Save as: app/src/main/kotlin/.../MoltingShader.kt
   - Fix package name to match your project

2. ADD TO BUILD.GRADLE:
   ```gradle
   android {
       buildFeatures {
           compose = true
       }
       composeOptions {
           kotlinCompilerExtensionVersion = "1.5.3"
       }
   }
   ```

3. TRIGGER IN EASTER EGG:
   ```kotlin
   // When first preset saved:
   var showMolting by remember { mutableStateOf(false) }

   LaunchedEffect(easterEggTriggered) {
       if (easterEggTriggered) {
           // Apply new theme colors to state
           updateThemeColors(newColors)

           // Trigger shader animation
           showMolting = true

           // Wait for animation to complete
           delay(1200)

           // Show "I'm a chameleon" dialog
           showRevertDialog = true
       }
   }
   ```

4. RENDER THE EFFECT:
   ```kotlin
   Box(modifier = Modifier.fillMaxSize()) {
       // Your normal UI content
       YourMainContent()

       // Overlay shader during transition
       if (showMolting) {
           val progress by animateFloatAsState(
               targetValue = 1.2f,
               animationSpec = tween(1200)
           )

           Box(
               modifier = Modifier
                   .fillMaxSize()
                   .drawWithCache {
                       val brush = createMoltingBrush(
                           progress,
                           size.width,
                           size.height
                       )
                       onDrawBehind {
                           drawRect(brush)
                       }
                   }
           )
       }
   }
   ```

RESULT:
- Screen "tears" with RGB split
- Old colors → New colors in ripple wave
- Looks like digital skin molting
- Takes 1.2 seconds total
- Smooth, GPU-accelerated
"""


# Python Helper (for testing color extraction)
def extract_dominant_colors_for_shader(preset_colors: list) -> dict:
    """
    Helper to prepare color data for theme transition.

    Args:
        preset_colors: List of hex color codes from preset

    Returns:
        Dict with normalized RGBA values for shader
    """
    def hex_to_normalized_rgba(hex_color: str) -> tuple:
        """Convert hex to RGBA (0.0-1.0)"""
        hex_color = hex_color.lstrip('#')

        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return (r, g, b, 1.0)

        return (0.5, 0.5, 0.5, 1.0)

    # Convert all preset colors
    normalized = [hex_to_normalized_rgba(c) for c in preset_colors[:4]]

    return {
        'primary': normalized[0] if len(normalized) > 0 else (0.5, 0.5, 0.5, 1.0),
        'secondary': normalized[1] if len(normalized) > 1 else (0.5, 0.5, 0.5, 1.0),
        'accent': normalized[2] if len(normalized) > 2 else (0.5, 0.5, 0.5, 1.0),
        'background': normalized[3] if len(normalized) > 3 else (0.1, 0.1, 0.1, 1.0)
    }


if __name__ == "__main__":
    print("=== CHAMELEON MOLTING SHADER ===\n")
    print("This shader creates a chromatic aberration ripple effect")
    print("for the easter egg theme transition.\n")
    print(ANIMATION_GUIDE)
    print("\n")
    print(USAGE_INSTRUCTIONS)
