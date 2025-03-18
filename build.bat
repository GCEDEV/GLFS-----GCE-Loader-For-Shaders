@echo off
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install pyinstaller flask flask-cors pyqt5 pyqtwebengine

echo Building GLFS executable...
python -m PyInstaller --noconfirm ^
    --name="GLFS" ^
    --onefile ^
    --noconsole ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "config.json;." ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --hidden-import=werkzeug.utils ^
    --hidden-import=werkzeug.debug ^
    --hidden-import=werkzeug.middleware ^
    --hidden-import=PyQt5 ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=PyQt5.QtWidgets ^
    --hidden-import=PyQt5.QtWebEngineWidgets ^
    src/main.py

echo Build complete! The executable is in the dist folder.
pause
