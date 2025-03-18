import os
import sys
import json
import shutil
import datetime
import subprocess
import webbrowser
from pathlib import Path
import winreg
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid

# Create Flask app with correct paths
template_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)
CORS(app)

# Get the base directory for the application
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (compiled with PyInstaller)
    base_dir = sys._MEIPASS
else:
    # If the application is run from a Python interpreter
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration file path
config_path = os.path.join(base_dir, 'config.json')

# Configuration
DEFAULT_CONFIG = {
    "minecraft_path": "",
    "shaders_path": "",
    "brd_path": "",
    "theme": "dark",
    "last_used_shader": "",
    "presets": {}
}

def load_config():
    """Load configuration from file"""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load configuration: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to save configuration: {e}")
        return False

def detect_minecraft_path():
    """Auto-detect Minecraft Bedrock installation path"""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft.MinecraftUWP_8wekyb3d8bbwe") as key:
            install_location = winreg.QueryValueEx(key, "InstallLocation")[0]
            return install_location
    except:
        # Try common installation paths
        paths = [
            os.path.expandvars(r"%LocalAppData%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang"),
            r"C:\Program Files\WindowsApps\Microsoft.MinecraftUWP_8wekyb3d8bbwe\data"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    return None

def set_default_shaders_path(minecraft_path):
    """Set default shaders path inside Minecraft directory"""
    shaders_path = os.path.join(minecraft_path, "renderer", "materials")
    os.makedirs(shaders_path, exist_ok=True)
    return shaders_path

def check_material_bin_loader(brd_path):
    """Check if MaterialBinLoader is installed and working."""
    try:
        config = load_config()
        mc_path = config.get('minecraft_path')
        if not mc_path:
            return {"status": "error", "message": "Minecraft path not set"}

        # Check for MaterialBinLoader in the right directory
        mbl_path = os.path.join(mc_path, "data", "renderer", "materials", "MaterialBinLoader.js")
        if not os.path.exists(mbl_path):
            return {"status": "missing", "message": "MaterialBinLoader not installed"}

        return {"status": "ok", "message": "MaterialBinLoader is installed"}
        
    except Exception as e:
        return {"status": "error", "message": f"Error checking MaterialBinLoader status: {str(e)}"}

def install_material_bin_loader(brd_path):
    """Install or fix MaterialBinLoader"""
    if not brd_path:
        return {"status": "error", "message": "BetterRenderDragon path not set"}
    
    brd_exe = os.path.join(brd_path, "BetterRenderDragon.exe")
    if not os.path.exists(brd_exe):
        return {"status": "error", "message": "BetterRenderDragon.exe not found"}

    try:
        result = subprocess.run([brd_exe, "--install"], capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "ok", "message": "MaterialBinLoader installed successfully"}
        else:
            return {"status": "error", "message": f"Installation failed: {result.stderr}"}
    except Exception as e:
        return {"status": "error", "message": f"Error installing MaterialBinLoader: {str(e)}"}

def get_shaders(shaders_path):
    """Get list of available shaders"""
    if not shaders_path or not os.path.exists(shaders_path):
        return []
    
    shaders = []
    for file in os.listdir(shaders_path):
        if file.endswith(('.glsl', '.hlsl', '.shader', '.mcpack', '.bin')):
            shader_path = os.path.join(shaders_path, file)
            shaders.append({
                "name": file,
                "path": shader_path,
                "size": os.path.getsize(shader_path),
                "modified": datetime.datetime.fromtimestamp(os.path.getmtime(shader_path)).strftime("%Y-%m-%d %H:%M:%S")
            })
    return shaders

def ensure_shader_directories():
    """Create necessary shader directories if they don't exist."""
    try:
        # Create GLFS resource pack directory
        mc_local = os.path.expandvars(r'%LOCALAPPDATA%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang')
        resource_pack_dir = os.path.join(mc_local, 'resource_packs', 'glfs_shaders')
        
        if not os.path.exists(resource_pack_dir):
            os.makedirs(resource_pack_dir)
            
            # Create manifest.json for the resource pack
            manifest = {
                "format_version": 2,
                "header": {
                    "description": "GLFS Shaders Resource Pack",
                    "name": "GLFS Shaders",
                    "uuid": "3fb8bf01-0f1d-4876-bff7-" + str(uuid.uuid4())[:12],
                    "version": [1, 0, 0],
                    "min_engine_version": [1, 19, 0]
                },
                "modules": [
                    {
                        "description": "GLFS Shaders Resources",
                        "type": "resources",
                        "uuid": "5fb8bf02-0f1d-4876-bff7-" + str(uuid.uuid4())[:12],
                        "version": [1, 0, 0]
                    }
                ]
            }
            
            with open(os.path.join(resource_pack_dir, 'manifest.json'), 'w') as f:
                json.dump(manifest, f, indent=4)
                
        return {"status": "ok", "message": "Shader directories created"}
    except Exception as e:
        return {"status": "error", "message": f"Error creating shader directories: {str(e)}"}

def apply_shader(shader_path):
    """Apply a shader by copying it to the resource pack directory."""
    try:
        if not os.path.exists(shader_path):
            return {"status": "error", "message": "Shader file not found"}
            
        # Get resource pack directory
        mc_local = os.path.expandvars(r'%LOCALAPPDATA%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang')
        resource_pack_dir = os.path.join(mc_local, 'resource_packs', 'glfs_shaders')
        
        # Create materials directory if it doesn't exist
        materials_dir = os.path.join(resource_pack_dir, 'materials')
        if not os.path.exists(materials_dir):
            os.makedirs(materials_dir)
            
        # Copy shader to resource pack
        shader_name = os.path.basename(shader_path)
        dest_path = os.path.join(materials_dir, shader_name)
        shutil.copy2(shader_path, dest_path)
        
        config = load_config()
        config["last_used_shader"] = shader_path
        save_config(config)
        
        return {"status": "ok", "message": f"Shader {shader_name} applied successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error applying shader: {str(e)}"}

def launch_minecraft():
    """Launch Minecraft using the launchminecraft.bat file."""
    try:
        config = load_config()
        brd_path = config.get('brd_path')
        if not brd_path:
            return {'status': 'error', 'message': 'BetterRenderDragon path not set'}
        
        launch_script = os.path.join(brd_path, 'launchminecraft.bat')
        if not os.path.exists(launch_script):
            return {'status': 'error', 'message': 'launchminecraft.bat not found in BRD directory'}

        # Launch using subprocess
        subprocess.Popen(launch_script, cwd=brd_path, shell=True)
        return {'status': 'ok', 'message': 'Minecraft is launching...'}
        
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to launch Minecraft: {str(e)}'}

# Routes
@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/init', methods=['GET'])
def init_app():
    """Initialize the application."""
    try:
        # Load config
        config = load_config()
        
        # Ensure shader directories exist
        ensure_shader_directories()
        
        return {"status": "ok", "message": "App initialized"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/static/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(app.static_folder, path)
    except Exception as e:
        print(f"Error serving static file {path}: {e}")
        return f"Error: {str(e)}", 404

@app.route('/api/config', methods=['GET'])
def get_config():
    config = load_config()
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    config = load_config()
    new_config = request.json
    config.update(new_config)
    if save_config(config):
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": "Failed to save configuration"})

@app.route('/api/shaders', methods=['GET'])
def list_shaders():
    config = load_config()
    shaders = get_shaders(config["shaders_path"])
    return jsonify(shaders)

@app.route('/api/shaders/apply', methods=['POST'])
def api_apply_shader():
    """API endpoint to apply a shader."""
    try:
        data = request.get_json()
        shader_path = data.get('path')
        if not shader_path:
            return jsonify({"status": "error", "message": "No shader path provided"})
            
        result = apply_shader(shader_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/mbl/status', methods=['GET'])
def mbl_status():
    config = load_config()
    return jsonify(check_material_bin_loader(config["brd_path"]))

@app.route('/api/mbl/install', methods=['POST'])
def mbl_install():
    config = load_config()
    return jsonify(install_material_bin_loader(config["brd_path"]))

@app.route('/api/minecraft/launch', methods=['POST'])
def minecraft_launch():
    return jsonify(launch_minecraft())

@app.route('/api/dialog/open_folder', methods=['POST'])
def open_folder_dialog():
    from tkinter import filedialog, Tk
    root = Tk()
    root.withdraw()
    
    initial_dir = request.json.get('initial_dir', os.path.expanduser('~'))
    folder = filedialog.askdirectory(initialdir=initial_dir)
    root.destroy()
    
    if folder:
        return jsonify({"status": "ok", "path": folder})
    return jsonify({"status": "cancelled"})

@app.route('/api/dialog/open_file', methods=['POST'])
def open_file_dialog():
    from tkinter import filedialog, Tk
    root = Tk()
    root.withdraw()
    
    initial_dir = request.json.get('initial_dir', os.path.expanduser('~'))
    file_types = request.json.get('file_types', [('All Files', '*.*')])
    
    file = filedialog.askopenfilename(
        initialdir=initial_dir,
        filetypes=file_types
    )
    root.destroy()
    
    if file:
        return jsonify({"status": "ok", "path": file})
    return jsonify({"status": "cancelled"})

@app.route('/api/shaders/import', methods=['POST'])
def import_shader():
    config = load_config()
    shader_path = request.json.get('path')
    
    if not shader_path:
        return jsonify({"status": "error", "message": "No shader path provided"})
    
    if not config["shaders_path"]:
        return jsonify({"status": "error", "message": "Shaders path not set"})
    
    try:
        # Copy shader to shaders directory
        shader_name = os.path.basename(shader_path)
        dest_path = os.path.join(config["shaders_path"], shader_name)
        shutil.copy2(shader_path, dest_path)
        return jsonify({
            "status": "ok",
            "message": f"Shader {shader_name} imported successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error importing shader: {str(e)}"
        })

# Main function to run the app
def main():
    # For development, run Flask directly
    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        app.run(debug=True, port=5000)
    else:
        # For production, use pywebview
        window = webview.create_window(
            "GLFS - Minecraft Bedrock Shader Loader", 
            app, 
            width=900, 
            height=650, 
            min_size=(900, 650),
            text_select=True
        )
        webview.start(debug=True)

if __name__ == "__main__":
    main()
