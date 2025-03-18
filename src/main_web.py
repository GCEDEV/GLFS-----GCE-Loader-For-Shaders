import os
import sys
import webview
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app

def main():
    # Check if we're running in development mode
    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        # Run Flask directly for development
        app.run(debug=True, port=5000)
    else:
        # For production, use pywebview
        window = webview.create_window(
            "GLFS - Minecraft Bedrock Shader Loader", 
            app, 
            width=1000, 
            height=700, 
            min_size=(800, 600),
            text_select=True
        )
        webview.start(debug=True)

if __name__ == "__main__":
    main()
