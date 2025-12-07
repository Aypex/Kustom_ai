package com.chameleon

import android.graphics.RenderEffect
import android.graphics.RuntimeShader
import android.os.Build
import androidx.annotation.RequiresApi

/**
 * Molting Effect Shader - Chromatic Aberration Ripple
 *
 * AGSL shader for chameleon skin-change animation.
 * Creates RGB channel split ripple effect for preview window transitions.
 */
@RequiresApi(Build.VERSION_CODES.TIRAMISU)
object MoltingShader {

    /**
     * AGSL shader source for chromatic aberration molt effect.
     *
     * Uniforms:
     * - time: Animation progress (0.0 to 1.2)
     * - resolution: Canvas size (vec2)
     * - center: Ripple origin point (vec2)
     * - intensity: RGB split strength (float)
     */
    private const val SHADER_SOURCE = """
        uniform shader composable;
        uniform float time;
        uniform vec2 resolution;
        uniform vec2 center;
        uniform float intensity;

        vec4 main(vec2 fragCoord) {
            vec2 uv = fragCoord / resolution;
            vec2 centerUV = center / resolution;

            // Distance from ripple center
            float dist = distance(uv, centerUV);

            // Ripple wave (moves outward over time)
            float ripple = smoothstep(time - 0.1, time, dist) -
                          smoothstep(time, time + 0.1, dist);

            // Chromatic aberration offset
            float aberration = ripple * intensity * 0.02;

            // Sample RGB channels with offset
            vec2 rOffset = vec2(aberration, 0.0);
            vec2 gOffset = vec2(0.0, 0.0);
            vec2 bOffset = vec2(-aberration, 0.0);

            float r = composable.eval(fragCoord + rOffset * resolution).r;
            float g = composable.eval(fragCoord + gOffset * resolution).g;
            float b = composable.eval(fragCoord + bOffset * resolution).b;

            // Combine channels
            vec4 color = vec4(r, g, b, 1.0);

            // Add digital artifacts on ripple edge
            if (ripple > 0.5) {
                float noise = fract(sin(dot(fragCoord, vec2(12.9898, 78.233))) * 43758.5453);
                color += vec4(noise * 0.05);
            }

            return color;
        }
    """

    /**
     * Create molt effect shader for preview transition.
     *
     * @param width Preview width in pixels
     * @param height Preview height in pixels
     * @param centerX Ripple origin X (default: center)
     * @param centerY Ripple origin Y (default: center)
     * @param intensity RGB split strength (0.0-2.0, default 1.0)
     * @return RuntimeShader ready for animation
     */
    fun createShader(
        width: Float,
        height: Float,
        centerX: Float = width / 2f,
        centerY: Float = height / 2f,
        intensity: Float = 1.0f
    ): RuntimeShader {
        return RuntimeShader(SHADER_SOURCE).apply {
            setFloatUniform("resolution", width, height)
            setFloatUniform("center", centerX, centerY)
            setFloatUniform("intensity", intensity)
            setFloatUniform("time", 0.0f)  // Will be animated
        }
    }

    /**
     * Create RenderEffect for applying to View.
     *
     * @param shader RuntimeShader with molt effect
     * @return RenderEffect for setRenderEffect()
     */
    fun createRenderEffect(shader: RuntimeShader): RenderEffect {
        return RenderEffect.createRuntimeShaderEffect(shader, "composable")
    }

    /**
     * Intensity presets for different molt types.
     */
    object Intensity {
        const val COLOR_SHIFT = 1.5f   // Strong RGB split for color changes
        const val SCALE = 0.8f         // Moderate for size changes
        const val BIRTH = 1.2f         // Medium-strong for new elements
        const val FADE = 0.6f          // Subtle for removals
        const val TRANSFORM = 1.0f     // Standard for complex edits
    }
}

/**
 * Example usage in Compose:
 *
 * ```kotlin
 * var moltProgress by remember { mutableFloatStateOf(0f) }
 * val shader = remember {
 *     MoltingShader.createShader(
 *         width = 1080f,
 *         height = 1920f,
 *         intensity = MoltingShader.Intensity.COLOR_SHIFT
 *     )
 * }
 *
 * LaunchedEffect(Unit) {
 *     animate(
 *         initialValue = 0f,
 *         targetValue = 1.2f,
 *         animationSpec = tween(800, easing = EaseOutCubic)
 *     ) { value, _ ->
 *         shader.setFloatUniform("time", value)
 *         moltProgress = value
 *     }
 * }
 *
 * Box(
 *     modifier = Modifier
 *         .graphicsLayer {
 *             if (moltProgress > 0f && moltProgress < 1.2f) {
 *                 renderEffect = MoltingShader.createRenderEffect(shader)
 *             }
 *         }
 * ) {
 *     // Preview content here
 * }
 * ```
 */
