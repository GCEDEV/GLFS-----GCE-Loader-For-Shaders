import os
import sys
import json
import shutil
import datetime
import subprocess
import webbrowser
from pathlib import Path
import webview
import threading
import tkinter as tk
from tkinter import filedialog

# Configuration
CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    "minecraft_path": "",
    "shaders_path": "",
    "brd_path": "",
    "theme": "dark",
    "last_used_shader": "",
    "presets": {}
}

class GLFSApp:
    def __init__(self):
        self.config = self.load_config()
        self.window = None
        
    def load_config(self):
        """Load configuration from config file"""
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    loaded_config = json.load(f)
                    config = DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
            except Exception as e:
                print(f"Failed to load configuration: {e}")
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save configuration to config file"""
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            return False
    
    # API exposed to JavaScript
    def get_config(self):
        """Get configuration for JavaScript"""
        # Auto-detect Minecraft path if not set
        if not self.config["minecraft_path"]:
            minecraft_path = self.detect_minecraft_path()
            if minecraft_path:
                self.config["minecraft_path"] = minecraft_path
                self.save_config()
        
        # Set default shaders path if Minecraft path is set but shaders path is not
        if self.config["minecraft_path"] and not self.config["shaders_path"]:
            shaders_path = self.set_default_shaders_path()
            if shaders_path:
                self.config["shaders_path"] = shaders_path
                self.save_config()
        
        return self.config
    
    def update_config(self, new_config):
        """Update configuration from JavaScript"""
        # Update only valid keys
        for key in DEFAULT_CONFIG.keys():
            if key in new_config:
                self.config[key] = new_config[key]
        
        self.save_config()
        return {"status": "ok", "message": "Configuration updated"}
    
    def get_shaders(self):
        """Get available shaders for JavaScript"""
        shaders = []
        shaders_path = self.config["shaders_path"]
        
        if shaders_path and os.path.exists(shaders_path):
            try:
                for item in os.listdir(shaders_path):
                    item_path = os.path.join(shaders_path, item)
                    if os.path.isfile(item_path) and item.endswith((".glsl", ".hlsl", ".shader")):
                        shaders.append(item)
            except Exception as e:
                print(f"Error listing shaders: {e}")
        
        return {"shaders": shaders}
    
    def apply_shader(self, shader_name):
        """Apply shader for JavaScript"""
        if not shader_name:
            return {"status": "error", "message": "No shader specified"}
        
        if not self.config["shaders_path"] or not os.path.exists(self.config["shaders_path"]):
            return {"status": "error", "message": "Shaders path not set or invalid"}
        
        shader_path = os.path.join(self.config["shaders_path"], shader_name)
        if not os.path.exists(shader_path):
            return {"status": "error", "message": f"Shader {shader_name} not found"}
        
        if not self.config["brd_path"] or not os.path.exists(self.config["brd_path"]):
            return {"status": "error", "message": "BetterRenderDragon path not set or invalid"}
        
        # Copy shader to BetterRenderDragon shaders directory
        try:
            brd_shaders_dir = os.path.join(self.config["brd_path"], "shaders")
            if not os.path.exists(brd_shaders_dir):
                os.makedirs(brd_shaders_dir)
            
            # Copy the shader
            shutil.copy2(shader_path, os.path.join(brd_shaders_dir, "shader.hlsl"))
            
            # Update last used shader
            self.config["last_used_shader"] = shader_name
            self.save_config()
            
            return {"status": "ok", "message": f"Shader {shader_name} applied successfully"}
        except Exception as e:
            return {"status": "error", "message": f"Error applying shader: {e}"}
    
    def get_presets(self):
        """Get presets for JavaScript"""
        return {"presets": list(self.config.get("presets", {}).keys())}
    
    def save_preset(self, preset_name, shader_name):
        """Save preset for JavaScript"""
        if not preset_name or not shader_name:
            return {"status": "error", "message": "Preset name and shader name are required"}
        
        if "presets" not in self.config:
            self.config["presets"] = {}
        
        self.config["presets"][preset_name] = shader_name
        self.save_config()
        
        return {"status": "ok", "message": f"Preset {preset_name} saved"}
    
    def load_preset(self, preset_name):
        """Load preset for JavaScript"""
        if not preset_name:
            return {"status": "error", "message": "Preset name is required"}
        
        if "presets" not in self.config or preset_name not in self.config["presets"]:
            return {"status": "error", "message": f"Preset {preset_name} not found"}
        
        shader_name = self.config["presets"][preset_name]
        
        # Apply the shader
        return self.apply_shader(shader_name)
    
    def delete_preset(self, preset_name):
        """Delete preset for JavaScript"""
        if not preset_name:
            return {"status": "error", "message": "Preset name is required"}
        
        if "presets" not in self.config or preset_name not in self.config["presets"]:
            return {"status": "error", "message": f"Preset {preset_name} not found"}
        
        del self.config["presets"][preset_name]
        self.save_config()
        
        return {"status": "ok", "message": f"Preset {preset_name} deleted"}
    
    def check_mbl_status(self):
        """Check MaterialBinLoader status for JavaScript"""
        brd_path = self.config["brd_path"]
        
        if not brd_path or not os.path.exists(brd_path):
            return {"status": "error", "message": "BetterRenderDragon path not set or invalid"}
        
        # Check for config.json
        brd_config_path = os.path.join(brd_path, "config.json")
        if not os.path.exists(brd_config_path):
            return {"status": "error", "message": "BetterRenderDragon config.json not found"}
        
        # Check for MaterialBinLoader.js
        mbl_path = os.path.join(brd_path, "plugins", "MaterialBinLoader.js")
        if not os.path.exists(mbl_path):
            return {"status": "missing", "message": "MaterialBinLoader not installed"}
        
        # Check if it's properly configured
        try:
            with open(brd_config_path, "r") as f:
                brd_config = json.load(f)
                
            # Check if the plugin is enabled
            plugins = brd_config.get("plugins", [])
            if "MaterialBinLoader" not in plugins:
                return {"status": "disabled", "message": "MaterialBinLoader is installed but not enabled"}
                
            # Check if the plugin is properly configured
            plugin_config = brd_config.get("MaterialBinLoader", {})
            if not plugin_config.get("enabled", False):
                return {"status": "disabled", "message": "MaterialBinLoader is installed but disabled"}
                
        except Exception as e:
            return {"status": "error", "message": f"Error checking MaterialBinLoader configuration: {e}"}
        
        # All checks passed
        return {"status": "ok", "message": "MaterialBinLoader is properly installed"}
    
    def install_mbl(self):
        """Install MaterialBinLoader for JavaScript"""
        brd_path = self.config["brd_path"]
        
        if not brd_path or not os.path.exists(brd_path):
            return {"status": "error", "message": "BetterRenderDragon path not set or invalid"}
        
        try:
            # Create plugins directory if it doesn't exist
            plugins_dir = os.path.join(brd_path, "plugins")
            if not os.path.exists(plugins_dir):
                os.makedirs(plugins_dir)
            
            # Copy MaterialBinLoader.js from resources
            mbl_source = os.path.join("resources", "MaterialBinLoader.js")
            mbl_dest = os.path.join(plugins_dir, "MaterialBinLoader.js")
            
            if not os.path.exists(mbl_source):
                return {"status": "error", "message": "MaterialBinLoader.js source file not found"}
            
            shutil.copy2(mbl_source, mbl_dest)
            
            # Update BetterRenderDragon config
            brd_config_path = os.path.join(brd_path, "config.json")
            if os.path.exists(brd_config_path):
                try:
                    with open(brd_config_path, "r") as f:
                        brd_config = json.load(f)
                    
                    # Add MaterialBinLoader to plugins list if not already there
                    if "plugins" not in brd_config:
                        brd_config["plugins"] = []
                    
                    if "MaterialBinLoader" not in brd_config["plugins"]:
                        brd_config["plugins"].append("MaterialBinLoader")
                    
                    # Add or update MaterialBinLoader configuration
                    brd_config["MaterialBinLoader"] = {
                        "enabled": True,
                        "priority": 0
                    }
                    
                    # Save updated config
                    with open(brd_config_path, "w") as f:
                        json.dump(brd_config, f, indent=4)
                    
                    return {"status": "ok", "message": "MaterialBinLoader installed and configured successfully"}
                except Exception as e:
                    return {"status": "error", "message": f"Error updating BetterRenderDragon configuration: {e}"}
            else:
                return {"status": "error", "message": "BetterRenderDragon config.json not found"}
        except Exception as e:
            return {"status": "error", "message": f"Error installing MaterialBinLoader: {e}"}
    
    def launch_minecraft(self):
        """Launch Minecraft for JavaScript"""
        try:
            # Try to launch Minecraft via the Microsoft Store protocol
            subprocess.Popen(["start", "minecraft://"], shell=True)
            return {"status": "ok", "message": "Launching Minecraft..."}
        except Exception as e:
            return {"status": "error", "message": f"Error launching Minecraft: {e}"}
    
    def browse_directory(self, title="Select Directory"):
        """Open a directory browser dialog"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        directory = filedialog.askdirectory(title=title)
        root.destroy()
        
        if directory:
            return directory
        return ""
    
    def browse_minecraft_path(self):
        """Browse for Minecraft path"""
        path = self.browse_directory("Select Minecraft Bedrock Directory")
        if path:
            self.config["minecraft_path"] = path
            self.save_config()
            return {"status": "ok", "path": path}
        return {"status": "cancelled"}
    
    def browse_shaders_path(self):
        """Browse for shaders path"""
        path = self.browse_directory("Select Shaders Directory")
        if path:
            self.config["shaders_path"] = path
            self.save_config()
            return {"status": "ok", "path": path}
        return {"status": "cancelled"}
    
    def browse_brd_path(self):
        """Browse for BetterRenderDragon path"""
        path = self.browse_directory("Select BetterRenderDragon Directory")
        if path:
            self.config["brd_path"] = path
            self.save_config()
            return {"status": "ok", "path": path}
        return {"status": "cancelled"}
    
    def import_shader(self):
        """Import a shader file"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        file_path = filedialog.askopenfilename(
            title="Select Shader File",
            filetypes=[("Shader Files", "*.glsl;*.hlsl;*.shader"), ("All Files", "*.*")]
        )
        root.destroy()
        
        if not file_path:
            return {"status": "cancelled"}
        
        if not self.config["shaders_path"] or not os.path.exists(self.config["shaders_path"]):
            return {"status": "error", "message": "Shaders path not set or invalid"}
        
        try:
            # Copy the shader to the shaders directory
            shader_name = os.path.basename(file_path)
            dest_path = os.path.join(self.config["shaders_path"], shader_name)
            
            shutil.copy2(file_path, dest_path)
            
            return {"status": "ok", "message": f"Shader {shader_name} imported successfully", "shader": shader_name}
        except Exception as e:
            return {"status": "error", "message": f"Error importing shader: {e}"}
    
    def detect_minecraft_path(self):
        """Auto-detect Minecraft Bedrock installation path"""
        try:
            import winreg
            # Method 1: Try to find via Windows Registry
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                    local_app_data = winreg.QueryValueEx(key, "Local AppData")[0]
                    
                # Check for Minecraft UWP app
                mc_path = os.path.join(os.path.expandvars(local_app_data), "Packages")
                if os.path.exists(mc_path):
                    for folder in os.listdir(mc_path):
                        if folder.startswith("Microsoft.MinecraftUWP"):
                            mc_uwp_path = os.path.join(mc_path, folder, "LocalState", "games", "com.mojang")
                            if os.path.exists(mc_uwp_path):
                                return mc_uwp_path
            except Exception as e:
                print(f"Registry detection failed: {e}")
                
            # Method 2: Try common installation paths
            common_paths = [
                os.path.expandvars("%LOCALAPPDATA%\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang"),
                os.path.expanduser("~\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang")
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
                    
            return ""
        except Exception as e:
            print(f"Error detecting Minecraft path: {e}")
            return ""
    
    def set_default_shaders_path(self):
        """Set default shaders path inside Minecraft directory"""
        if self.config["minecraft_path"]:
            # Create a 'shaders' directory inside the resource_packs directory
            resource_packs_dir = os.path.join(self.config["minecraft_path"], "resource_packs")
            shaders_dir = os.path.join(resource_packs_dir, "glfs_shaders")
            
            # Create the directory if it doesn't exist
            try:
                if not os.path.exists(resource_packs_dir):
                    os.makedirs(resource_packs_dir)
                    
                if not os.path.exists(shaders_dir):
                    os.makedirs(shaders_dir)
                
                return shaders_dir
            except Exception as e:
                print(f"Error creating shaders directory: {e}")
        return ""
    
    def start(self):
        """Start the application"""
        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates', 'standalone.html'))
        
        # Create window
        self.window = webview.create_window(
            'GLFS - Minecraft Bedrock Shader Loader',
            html_path,
            js_api=self,
            width=1000,
            height=700,
            min_size=(800, 600)
        )
        
        # Start webview
        webview.start(debug=True)

def main():
    app = GLFSApp()
    app.start()

if __name__ == "__main__":
    main()
