import os
import sys
import threading
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from src.app import app, load_config, save_config, detect_minecraft_path, set_default_shaders_path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLFS - Minecraft Bedrock Shader Loader")
        self.setGeometry(100, 100, 900, 650)
        self.setMinimumSize(900, 650)
        
        # Create web view
        self.web = QWebEngineView()
        self.web.setUrl(QUrl("http://127.0.0.1:5000"))
        self.setCentralWidget(self.web)

def run_flask():
    app.run(port=5000)

def main():
    print("Starting GLFS application...")
    
    # Load configuration
    config = load_config()
    
    # Auto-detect Minecraft Bedrock path if not set
    if not config["minecraft_path"]:
        minecraft_path = detect_minecraft_path()
        if minecraft_path:
            config["minecraft_path"] = minecraft_path
            save_config(config)
            
    # Auto-set shaders path to be inside Minecraft directory
    if config["minecraft_path"] and not config["shaders_path"]:
        shaders_path = set_default_shaders_path(config["minecraft_path"])
        if shaders_path:
            config["shaders_path"] = shaders_path
            save_config(config)
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Qt application
    qt_app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Start Qt event loop
    sys.exit(qt_app.exec_())

if __name__ == "__main__":
    main()
