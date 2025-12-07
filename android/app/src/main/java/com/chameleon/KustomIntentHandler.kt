package com.chameleon

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.core.content.FileProvider
import java.io.File

/**
 * Kustom Intent Handler
 *
 * Handles communication with KLWP/KLCK/KWGT via Android intents.
 * Applies generated presets to the Kustom apps.
 */
object KustomIntentHandler {

    /**
     * Check if KLWP is installed on device.
     *
     * @param context Application context
     * @return True if KLWP is installed
     */
    fun isKLWPInstalled(context: Context): Boolean {
        return isAppInstalled(context, "org.kustom.wallpaper")
    }

    /**
     * Check if KLCK is installed on device.
     *
     * @param context Application context
     * @return True if KLCK is installed
     */
    fun isKLCKInstalled(context: Context): Boolean {
        return isAppInstalled(context, "org.kustom.lockscreen")
    }

    /**
     * Check if KWGT is installed on device.
     *
     * @param context Application context
     * @return True if KWGT is installed
     */
    fun isKWGTInstalled(context: Context): Boolean {
        return isAppInstalled(context, "org.kustom.widget")
    }

    /**
     * Apply preset to KLWP.
     *
     * @param context Application context
     * @param presetFile File containing preset JSON
     * @return True if intent was successfully sent
     */
    fun applyToKLWP(context: Context, presetFile: File): Boolean {
        if (!isKLWPInstalled(context)) {
            showToast(context, "KLWP not installed. Install from Play Store.")
            return false
        }

        return sendKustomIntent(
            context,
            "org.kustom.wallpaper",
            "org.kustom.api.ACTION_EDIT_PRESET",
            presetFile
        )
    }

    /**
     * Apply preset to KLCK.
     *
     * @param context Application context
     * @param presetFile File containing preset JSON
     * @return True if intent was successfully sent
     */
    fun applyToKLCK(context: Context, presetFile: File): Boolean {
        if (!isKLCKInstalled(context)) {
            showToast(context, "KLCK not installed. Install from Play Store.")
            return false
        }

        return sendKustomIntent(
            context,
            "org.kustom.lockscreen",
            "org.kustom.api.ACTION_EDIT_PRESET",
            presetFile
        )
    }

    /**
     * Apply preset to KWGT.
     *
     * @param context Application context
     * @param presetFile File containing preset JSON
     * @return True if intent was successfully sent
     */
    fun applyToKWGT(context: Context, presetFile: File): Boolean {
        if (!isKWGTInstalled(context)) {
            showToast(context, "KWGT not installed. Install from Play Store.")
            return false
        }

        return sendKustomIntent(
            context,
            "org.kustom.widget",
            "org.kustom.api.ACTION_EDIT_PRESET",
            presetFile
        )
    }

    /**
     * Open preset in KLWP for editing.
     *
     * @param context Application context
     * @param presetFile File containing preset JSON
     * @return True if intent was successfully sent
     */
    fun editInKLWP(context: Context, presetFile: File): Boolean {
        if (!isKLWPInstalled(context)) {
            showToast(context, "KLWP not installed. Install from Play Store.")
            return false
        }

        return sendKustomIntent(
            context,
            "org.kustom.wallpaper",
            "org.kustom.api.ACTION_EDIT_PRESET",
            presetFile,
            edit = true
        )
    }

    /**
     * Open KLWP app (to Play Store if not installed).
     *
     * @param context Application context
     */
    fun openKLWP(context: Context) {
        if (isKLWPInstalled(context)) {
            // Open KLWP
            val intent = context.packageManager.getLaunchIntentForPackage("org.kustom.wallpaper")
            if (intent != null) {
                context.startActivity(intent)
            }
        } else {
            // Open Play Store
            openPlayStore(context, "org.kustom.wallpaper")
        }
    }

    /**
     * Open KLCK app (to Play Store if not installed).
     *
     * @param context Application context
     */
    fun openKLCK(context: Context) {
        if (isKLCKInstalled(context)) {
            val intent = context.packageManager.getLaunchIntentForPackage("org.kustom.lockscreen")
            if (intent != null) {
                context.startActivity(intent)
            }
        } else {
            openPlayStore(context, "org.kustom.lockscreen")
        }
    }

    /**
     * Open KWGT app (to Play Store if not installed).
     *
     * @param context Application context
     */
    fun openKWGT(context: Context) {
        if (isKWGTInstalled(context)) {
            val intent = context.packageManager.getLaunchIntentForPackage("org.kustom.widget")
            if (intent != null) {
                context.startActivity(intent)
            }
        } else {
            openPlayStore(context, "org.kustom.widget")
        }
    }

    // Private helper methods

    private fun isAppInstalled(context: Context, packageName: String): Boolean {
        return try {
            context.packageManager.getPackageInfo(packageName, 0)
            true
        } catch (e: Exception) {
            false
        }
    }

    private fun sendKustomIntent(
        context: Context,
        targetPackage: String,
        action: String,
        presetFile: File,
        edit: Boolean = false
    ): Boolean {
        return try {
            // Get content URI for file (required for Android 7+)
            val fileUri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                presetFile
            )

            val intent = Intent(action).apply {
                setPackage(targetPackage)
                data = fileUri
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

                // Extra flags for edit mode
                if (edit) {
                    putExtra("EDIT_MODE", true)
                }
            }

            context.startActivity(intent)
            showToast(context, "Opening in ${getAppName(targetPackage)}...")
            true

        } catch (e: Exception) {
            showToast(context, "Failed to open preset: ${e.message}")
            false
        }
    }

    private fun openPlayStore(context: Context, packageName: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW).apply {
                data = Uri.parse("market://details?id=$packageName")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            // Fallback to web browser
            val intent = Intent(Intent.ACTION_VIEW).apply {
                data = Uri.parse("https://play.google.com/store/apps/details?id=$packageName")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
        }
    }

    private fun getAppName(packageName: String): String {
        return when (packageName) {
            "org.kustom.wallpaper" -> "KLWP"
            "org.kustom.lockscreen" -> "KLCK"
            "org.kustom.widget" -> "KWGT"
            else -> "Kustom"
        }
    }

    private fun showToast(context: Context, message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }
}

/**
 * Python/Kivy bridge functions for calling from Python layer.
 */
object KustomBridge {
    /**
     * Apply preset file to appropriate Kustom app.
     *
     * @param context Application context
     * @param presetPath Absolute path to preset JSON file
     * @param presetType Type: "klwp", "klck", or "kwgt"
     * @return Success message or error
     */
    @JvmStatic
    fun applyPreset(context: Context, presetPath: String, presetType: String): String {
        val file = File(presetPath)
        if (!file.exists()) {
            return "Error: Preset file not found"
        }

        val success = when (presetType.lowercase()) {
            "klwp" -> KustomIntentHandler.applyToKLWP(context, file)
            "klck" -> KustomIntentHandler.applyToKLCK(context, file)
            "kwgt" -> KustomIntentHandler.applyToKWGT(context, file)
            else -> {
                return "Error: Unknown preset type '$presetType'"
            }
        }

        return if (success) {
            "Success: Preset sent to ${presetType.uppercase()}"
        } else {
            "Error: Failed to send preset"
        }
    }

    /**
     * Check if required Kustom app is installed.
     *
     * @param context Application context
     * @param presetType Type: "klwp", "klck", or "kwgt"
     * @return "installed" or "not_installed"
     */
    @JvmStatic
    fun checkInstalled(context: Context, presetType: String): String {
        val installed = when (presetType.lowercase()) {
            "klwp" -> KustomIntentHandler.isKLWPInstalled(context)
            "klck" -> KustomIntentHandler.isKLCKInstalled(context)
            "kwgt" -> KustomIntentHandler.isKWGTInstalled(context)
            else -> false
        }

        return if (installed) "installed" else "not_installed"
    }

    /**
     * Open Kustom app or Play Store.
     *
     * @param context Application context
     * @param presetType Type: "klwp", "klck", or "kwgt"
     */
    @JvmStatic
    fun openKustomApp(context: Context, presetType: String) {
        when (presetType.lowercase()) {
            "klwp" -> KustomIntentHandler.openKLWP(context)
            "klck" -> KustomIntentHandler.openKLCK(context)
            "kwgt" -> KustomIntentHandler.openKWGT(context)
        }
    }
}
