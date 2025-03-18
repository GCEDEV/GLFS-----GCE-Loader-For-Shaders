# GLFS - Minecraft Bedrock Shader Loader

GLFS (Graphics Loader For Shaders) is a Windows application that helps you manage and apply shaders for Minecraft Bedrock Edition using BetterRenderDragon and MaterialBin.

## Features

- Easy management of Minecraft Bedrock shaders
- Support for both MaterialBinLoader and direct material.bin replacement
- Simple UI for importing, selecting, and applying shaders
- Shader presets system to quickly switch between your favorite configurations
- One-click Minecraft launch with BetterRenderDragon
- Automatic detection of Minecraft Bedrock installation
- MaterialBinLoader installation and configuration management

## Requirements

- Windows 10/11
- Minecraft Bedrock Edition
- Python 3.7+ (if running from source)

## Setup

1. Download BetterRenderDragon from its [GitHub releases page](https://github.com/ddf8196/BetterRenderDragon/releases/latest)
2. Extract the BetterRenderDragon.zip to a location of your choice
3. Open GLFS and go to the Settings tab
4. Set the following paths:
   - Minecraft Installation Path: The path to your Minecraft Bedrock installation
   - BetterRenderDragon Path: The path where you extracted BetterRenderDragon
   - Shaders Directory: A folder where you want to store your shaders
5. Click "Save Settings"

## Usage

### Importing Shaders

1. Click "Import Shader" on the Home tab
2. Select a shader file (.mcpack or material.bin)
3. The shader will be copied to your Shaders Directory

### Applying Shaders

1. Select a shader from the list
2. Click "Apply Selected Shader"
3. For .mcpack shaders:
   - The shader will be copied to Minecraft's resource_packs folder
   - The application will attempt to automatically enable it in Minecraft's Global Resources
4. For material.bin shaders:
   - The shader will directly replace Minecraft's material.bin file
   - A backup of the original file will be created

### MaterialBinLoader Management

GLFS includes tools to help you properly install and configure MaterialBinLoader:

1. **Checking MaterialBinLoader Status**:
   - The application automatically checks if MaterialBinLoader is properly installed and configured
   - The status is displayed in the MaterialBinLoader section of the home tab

2. **Installing/Fixing MaterialBinLoader**:
   - Click "Install/Fix MaterialBinLoader" to automatically:
     - Create required directories
     - Enable MaterialBinLoader in BetterRenderDragon config
     - Install MaterialBinLoader.dll (if available in resources)
     - Configure proper settings for shader support

3. **Manual Installation**:
   - If MaterialBinLoader.dll is not found, the application will offer to open the download page
   - Download the latest version and place it in the `plugins` folder of your BetterRenderDragon installation

### Managing Shader Presets

GLFS allows you to save and manage shader presets for quick switching between your favorite configurations:

1. **Saving a Preset**:
   - Select a shader from the list
   - Click "Save Current as Preset"
   - Enter a name for the preset
   - The preset will be saved and selected in the dropdown

2. **Loading a Preset**:
   - Select a preset from the dropdown
   - Click "Load Preset"
   - The shader from the preset will be selected and applied automatically

3. **Deleting a Preset**:
   - Select a preset from the dropdown
   - Click "Delete Preset"
   - Confirm the deletion

### Launching Minecraft

1. Click "Launch Minecraft" to start Minecraft with BetterRenderDragon
2. When Minecraft is running, press F6 to open the BetterRenderDragon menu
3. Make sure MaterialBinLoader is enabled (this should be done automatically by GLFS)

## Troubleshooting

### Shaders Not Working

If shaders are not working properly:

1. **Check MaterialBinLoader Status**:
   - Look at the MaterialBinLoader status in the home tab
   - If it shows any issues, click "Install/Fix MaterialBinLoader"

2. **Verify BetterRenderDragon Configuration**:
   - Make sure both "MaterialBinLoader" and "DeferredRendering" are enabled
   - In Minecraft, press F6 and check that both options are enabled

3. **Check Resource Pack Activation**:
   - For .mcpack shaders, ensure the shader is enabled in Minecraft's Global Resources
   - Try reapplying the shader using the "Apply Selected Shader" button

4. **Restart Minecraft**:
   - Some changes require a full restart of Minecraft to take effect
   - Close Minecraft completely and relaunch using the "Launch Minecraft" button

5. **Check Compatibility**:
   - Not all shaders are compatible with all versions of Minecraft
   - Try using a different shader to see if the issue is specific to one shader

## Credits

- BetterRenderDragon by [ddf8196](https://github.com/ddf8196/BetterRenderDragon)
- MaterialBinLoader included in BetterRenderDragon
