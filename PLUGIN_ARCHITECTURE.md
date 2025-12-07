# KLWP AI Assistant - Plugin Architecture

## Vision
Core app handles Kustom (KLWP/KLCK/KWGT), with a plugin system for community-contributed support for other customization apps.

## Architecture Overview

```
KLWP AI Assistant (Core App)
├── Built-in: Kustom Support (KLWP/KLCK/KWGT)
├── Plugin Manager
└── Plugin Interface

Plugins (Separate APKs or JARs):
├── Total Launcher Plugin
├── Tasker Plugin
├── Nova Launcher Plugin
└── ... (community-created)
```

## Core App Responsibilities

1. **UI Framework** - Main app screens, AI backend selection
2. **AI Integration** - Local/SSH/API model connections
3. **Plugin Management** - Discovery, loading, lifecycle
4. **Kustom Handler** - Built-in KLWP/KLCK/KWGT support
5. **Plugin API** - Interface for plugins to implement

## Plugin Responsibilities

1. **App Detection** - Check if target app is installed
2. **File Handling** - Parse/modify target app's files
3. **Operations** - Implement read/list/find/modify/save
4. **UI Integration** - Provide plugin settings screen (optional)
5. **Broadcast Intents** - Trigger target app reload

## Plugin Interface

### Method 1: Intent-Based Plugins (Simplest)

Plugins are separate apps that respond to intents from the main app.

```java
// Plugin declares intent filters in AndroidManifest.xml
<intent-filter>
    <action android:name="com.klwpai.PLUGIN_ACTION" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="application/json" />
</intent-filter>
```

**Main App → Plugin Communication:**
```java
// Main app sends command to plugin
Intent intent = new Intent("com.klwpai.PLUGIN_ACTION");
intent.setPackage("com.totallauncher.plugin"); // Plugin package name
intent.putExtra("command", "list_items");
intent.putExtra("layout_name", "home.tl");
startActivityForResult(intent, REQUEST_PLUGIN_ACTION);

// Plugin responds via result
@Override
protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    if (requestCode == REQUEST_PLUGIN_ACTION && resultCode == RESULT_OK) {
        String result = data.getStringExtra("result");
        // Process plugin response
    }
}
```

**Pros:**
- ✅ Completely separate apps
- ✅ No code dependencies
- ✅ Easy to install/uninstall plugins
- ✅ Sandbox security

**Cons:**
- ❌ Slower (IPC overhead)
- ❌ Less flexible API

### Method 2: Library-Based Plugins (More Flexible)

Plugins are JAR/AAR libraries that implement a common interface.

```kotlin
// Plugin Interface (in core app)
interface CustomizationPlugin {
    // Metadata
    fun getPluginName(): String
    fun getPluginVersion(): String
    fun getSupportedApp(): String  // "Total Launcher", "Tasker", etc.
    fun isAppInstalled(): Boolean

    // Core Operations
    fun listConfigs(): List<ConfigInfo>
    fun readConfig(configName: String): ConfigData
    fun listElements(configName: String, elementType: String?): List<ElementInfo>
    fun findElement(configName: String, searchTerm: String): List<ElementInfo>
    fun modifyElement(configName: String, elementId: String, properties: Map<String, Any>): ElementInfo
    fun saveConfig(configName: String, backup: Boolean): String
    fun reloadApp(): Boolean

    // Optional: Custom UI
    fun hasSettingsScreen(): Boolean
    fun getSettingsFragment(): Fragment?
}

// Data classes
data class ConfigInfo(val name: String, val path: String, val lastModified: Long)
data class ElementInfo(val id: String, val type: String, val properties: Map<String, Any>)
data class ConfigData(val raw: Any, val elements: List<ElementInfo>)
```

**Plugin Implementation Example:**
```kotlin
// Total Launcher Plugin (separate module/library)
class TotalLauncherPlugin : CustomizationPlugin {
    override fun getPluginName() = "Total Launcher Support"
    override fun getPluginVersion() = "1.0.0"
    override fun getSupportedApp() = "Total Launcher"

    override fun isAppInstalled(): Boolean {
        return try {
            context.packageManager.getPackageInfo("com.fs.tbrowser", 0)
            true
        } catch (e: PackageManager.NameNotFoundException) {
            false
        }
    }

    override fun listConfigs(): List<ConfigInfo> {
        val layoutsDir = File("/sdcard/TotalLauncher")
        return layoutsDir.listFiles { file -> file.extension == "tl" }
            ?.map { ConfigInfo(it.name, it.path, it.lastModified()) }
            ?: emptyList()
    }

    override fun readConfig(configName: String): ConfigData {
        // Parse .tl file (ZIP with XML)
        val layoutFile = File("/sdcard/TotalLauncher/$configName")
        val xml = extractXmlFromZip(layoutFile)
        val elements = parseLayoutElements(xml)
        return ConfigData(xml, elements)
    }

    override fun modifyElement(configName: String, elementId: String, properties: Map<String, Any>): ElementInfo {
        // Modify XML element
        // Return updated element info
    }

    // ... implement other methods
}
```

**Plugin Loading in Main App:**
```kotlin
// PluginManager.kt in main app
class PluginManager(private val context: Context) {
    private val plugins = mutableListOf<CustomizationPlugin>()

    fun loadPlugins() {
        // Method 1: Load from assets (bundled plugins)
        loadBundledPlugins()

        // Method 2: Load from external directory (sideloaded)
        loadExternalPlugins()

        // Method 3: Discover via package manager (separate apps)
        discoverInstalledPlugins()
    }

    private fun loadBundledPlugins() {
        // Use reflection to load plugin classes
        try {
            val pluginClass = Class.forName("com.totallauncher.plugin.TotalLauncherPlugin")
            val plugin = pluginClass.newInstance() as CustomizationPlugin
            if (plugin.isAppInstalled()) {
                plugins.add(plugin)
            }
        } catch (e: Exception) {
            Log.w("PluginManager", "Plugin not available: ${e.message}")
        }
    }

    fun getAvailablePlugins(): List<CustomizationPlugin> = plugins

    fun getPluginFor(appName: String): CustomizationPlugin? {
        return plugins.find { it.getSupportedApp() == appName }
    }
}
```

**Pros:**
- ✅ Fast (no IPC)
- ✅ Rich API
- ✅ Easy to use in main app

**Cons:**
- ❌ Requires compilation with main app (if bundled)
- ❌ Or requires dynamic loading (complex)

### Method 3: Hybrid Approach (Recommended)

**Core plugins** (popular/stable): Bundled as libraries in main app
**Community plugins**: Separate APKs communicating via intents

This gives you:
- Fast, integrated experience for popular plugins
- Open ecosystem for experimentation
- Option to promote community plugins to core

## Recommended Implementation: Hybrid

### Phase 1: Core App (v1.0)
```
app/
├── plugins/
│   ├── PluginInterface.kt          # Interface definition
│   ├── PluginManager.kt            # Discovery and loading
│   └── builtin/
│       └── KustomPlugin.kt         # Built-in Kustom support
└── ui/
    ├── PluginListScreen.kt         # Show available plugins
    └── PluginSettingsScreen.kt     # Per-plugin settings
```

### Phase 2: Example External Plugin (v1.1)
```
plugins/
└── total-launcher-plugin/
    ├── build.gradle
    ├── AndroidManifest.xml         # Declares plugin metadata
    └── src/
        └── TotalLauncherPlugin.kt  # Implements interface
```

### Phase 3: Plugin SDK (v1.2)
```
klwp-ai-plugin-sdk/
├── plugin-api/                     # Interface definitions
├── plugin-template/                # Template for new plugins
├── docs/
│   ├── PLUGIN_DEVELOPMENT.md
│   └── examples/
└── build.gradle                    # Publish to Maven/JitPack
```

## Plugin Discovery

### 1. Built-in Plugins
Compiled into the main app, always available.

### 2. Installed Plugin Apps
Main app queries package manager for apps with plugin metadata:

```xml
<!-- Plugin app's AndroidManifest.xml -->
<application>
    <meta-data
        android:name="com.klwpai.plugin"
        android:value="true" />
    <meta-data
        android:name="com.klwpai.plugin.name"
        android:value="Total Launcher Support" />
    <meta-data
        android:name="com.klwpai.plugin.version"
        android:value="1.0.0" />
    <meta-data
        android:name="com.klwpai.plugin.target"
        android:value="com.fs.tbrowser" />
</application>
```

### 3. Plugin Repository (Future)
GitHub repo listing community plugins with install links.

## Plugin Communication Protocol (Intent-Based)

### Commands (Main App → Plugin)
```json
{
  "command": "list_configs",
  "params": {}
}

{
  "command": "read_config",
  "params": {
    "config_name": "home.tl"
  }
}

{
  "command": "modify_element",
  "params": {
    "config_name": "home.tl",
    "element_id": "app_icon_1",
    "properties": {
      "position_x": 100,
      "position_y": 200
    }
  }
}
```

### Responses (Plugin → Main App)
```json
{
  "status": "success",
  "data": {
    "configs": [
      {"name": "home.tl", "path": "/sdcard/TotalLauncher/home.tl"},
      {"name": "drawer.tl", "path": "/sdcard/TotalLauncher/drawer.tl"}
    ]
  }
}

{
  "status": "error",
  "error": "Config file not found",
  "code": 404
}
```

## Main App Changes Required

### 1. Add Plugin Manager
```kotlin
// app/plugins/PluginManager.kt
class PluginManager(context: Context) {
    fun discoverPlugins(): List<PluginInfo>
    fun loadPlugin(pluginId: String): CustomizationPlugin?
    fun executeCommand(pluginId: String, command: String, params: Map<String, Any>): Result
}
```

### 2. Update Home Screen
```kotlin
// app/ui/HomeScreen.kt
// Add "Plugins" section showing:
// - Built-in: Kustom (KLWP/KLCK/KWGT) ✅
// - Available: Total Launcher (if installed and plugin available)
// - Available: Tasker (if installed and plugin available)
// - Discover more plugins → (link to plugin repository)
```

### 3. Add Plugin Settings
```kotlin
// Per-plugin configuration
// - Enable/disable plugin
// - Plugin-specific settings
// - Check for updates
```

## Example: Total Launcher Plugin

### Standalone Plugin App Structure
```
TotalLauncherPlugin/
├── app/
│   ├── src/main/
│   │   ├── AndroidManifest.xml
│   │   ├── java/com/totallauncher/klwpai/
│   │   │   ├── PluginService.kt      # Receives intents from main app
│   │   │   ├── TotalLauncherHandler.kt  # Business logic
│   │   │   └── models/
│   │   │       ├── LayoutFile.kt
│   │   │       └── LauncherItem.kt
│   │   └── res/
│   │       └── values/
│   │           └── strings.xml
│   └── build.gradle
└── README.md
```

### PluginService.kt
```kotlin
class PluginService : IntentService("TotalLauncherPlugin") {
    private val handler = TotalLauncherHandler()

    override fun onHandleIntent(intent: Intent?) {
        val command = intent?.getStringExtra("command") ?: return
        val params = intent.getBundleExtra("params")

        val result = when (command) {
            "list_configs" -> handler.listLayouts()
            "read_config" -> handler.readLayout(params?.getString("config_name") ?: "")
            "modify_element" -> handler.modifyItem(
                params?.getString("config_name") ?: "",
                params?.getString("element_id") ?: "",
                params?.getBundle("properties")?.toMap() ?: emptyMap()
            )
            else -> Result.error("Unknown command: $command")
        }

        // Send result back to main app
        val resultIntent = Intent()
        resultIntent.putExtra("result", result.toJson())
        setResult(Activity.RESULT_OK, resultIntent)
    }
}
```

## Plugin Development Workflow

### 1. Developer Creates Plugin
```bash
git clone https://github.com/Aypex/klwp-ai-plugin-template
cd klwp-ai-plugin-template
./gradlew build
adb install app/build/outputs/apk/release/plugin.apk
```

### 2. User Installs Plugin
- Install plugin APK from GitHub release or Play Store
- Open KLWP AI Assistant
- App auto-discovers plugin via package manager
- User enables plugin in settings

### 3. User Uses Plugin
- Select "Total Launcher" mode in main app
- App delegates commands to Total Launcher plugin
- Plugin handles all Total Launcher-specific logic

## Benefits of Plugin Architecture

1. **Core App Stays Lean**
   - Small download size
   - Fast, focused on Kustom
   - Easy to maintain

2. **Community Innovation**
   - Anyone can add support for their favorite launcher
   - Experiment without affecting core app
   - Natural selection of best plugins

3. **User Choice**
   - Install only what you need
   - No bloat from unused features
   - Extend functionality on demand

4. **Future Expansion**
   - Nova Launcher plugin
   - Zooper Widget plugin
   - Smart Launcher plugin
   - Even non-launcher apps (AutoTools, MacroDroid, etc.)

5. **Monetization Options** (Optional)
   - Core app: Free
   - Premium plugins: Paid
   - Or all free with donations

## Next Steps

### v1.0 (Core App - Now)
- [x] Kustom (KLWP/KLCK/KWGT) built-in
- [ ] Define plugin interface
- [ ] Implement plugin manager (basic)
- [ ] Ship without external plugins

### v1.1 (Plugin System)
- [ ] Finalize plugin API
- [ ] Document plugin development
- [ ] Create plugin template
- [ ] Build example Total Launcher plugin

### v1.2 (Community)
- [ ] Publish plugin SDK
- [ ] Create plugin repository
- [ ] Community starts building plugins
- [ ] Promote popular plugins to core (optional)

## Questions

1. **Plugin Format**: Intent-based (separate APKs) or library-based (JAR/AAR)?
   - **Recommendation**: Intent-based for true plugin independence

2. **Built-in vs External**: Which plugins should be bundled?
   - **Recommendation**: Only Kustom built-in, everything else external

3. **Plugin Repository**: GitHub org with approved plugins?
   - **Recommendation**: Yes, curated list of working plugins

4. **Verification**: Should plugins be signed/verified?
   - **Recommendation**: Not initially, but consider for v2.0

Would you like me to start implementing the plugin interface in the core app?
