// Main application object
const App = {
    // State
    config: null,
    shaders: [],
    
    // Initialize the application
    init: async function() {
        try {
            // Initialize backend
            const initResponse = await fetch('/api/init');
            const initResult = await initResponse.json();
            if (initResult.status !== 'ok') {
                this.setStatus(initResult.message, 'error');
                return;
            }
            
            // Load config and setup UI
            await this.loadConfig();
            this.setupEventListeners();
            this.loadShaders();
            this.setupTheme();
            
            // Show home tab by default
            document.querySelector('.tab-btn[data-tab="home"]').click();
        } catch (error) {
            console.error('Error initializing app:', error);
            this.setStatus('Error initializing application', 'error');
        }
    },
    
    // Load configuration from server
    loadConfig: async function() {
        try {
            const response = await fetch('/api/config');
            this.config = await response.json();
            this.updateUI();
        } catch (error) {
            console.error('Error loading config:', error);
            this.setStatus('Error loading configuration', 'error');
        }
    },
    
    // Update UI with current config values
    updateUI: function() {
        if (this.config) {
            document.getElementById('minecraft-path').value = this.config.minecraft_path || '';
            document.getElementById('shaders-path').value = this.config.shaders_path || '';
            document.getElementById('brd-path').value = this.config.brd_path || '';
            
            // Set theme
            if (this.config.theme === 'light') {
                document.getElementById('theme-toggle-checkbox').checked = false;
                document.body.classList.add('light-theme');
            }
        }
    },
    
    // Save configuration to server
    saveConfig: async function() {
        const config = {
            minecraft_path: document.getElementById('minecraft-path').value,
            shaders_path: document.getElementById('shaders-path').value,
            brd_path: document.getElementById('brd-path').value,
            theme: document.getElementById('theme-toggle-checkbox').checked ? 'dark' : 'light'
        };
        
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            const result = await response.json();
            if (result.status === 'ok') {
                this.config = config;
                this.setStatus('Settings saved successfully', 'success');
            } else {
                this.setStatus('Error saving settings: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Error saving config:', error);
            this.setStatus('Error saving settings', 'error');
        }
    },
    
    // Load shaders from server
    loadShaders: async function() {
        try {
            const response = await fetch('/api/shaders');
            const shaders = await response.json();
            this.shaders = shaders;
            
            // Update shader list
            const shaderList = document.getElementById('shader-list');
            shaderList.innerHTML = '';
            
            shaders.forEach(shader => {
                const li = document.createElement('li');
                li.className = 'shader-item';
                li.innerHTML = `
                    <div class="shader-info">
                        <span class="shader-name">${shader.name}</span>
                        <span class="shader-details">
                            Size: ${this.formatSize(shader.size)} | 
                            Modified: ${shader.modified}
                        </span>
                    </div>
                    <div class="shader-actions">
                        <button class="btn btn-sm btn-primary apply-shader" data-path="${shader.path}">
                            Apply
                        </button>
                    </div>
                `;
                shaderList.appendChild(li);
                
                // Add click handler for apply button
                li.querySelector('.apply-shader').addEventListener('click', (e) => {
                    this.applyShader(e.target.dataset.path);
                });
            });
        } catch (error) {
            console.error('Error loading shaders:', error);
            this.setStatus('Error loading shaders', 'error');
        }
    },
    
    // Format file size
    formatSize: function(bytes) {
        const sizes = ['B', 'KB', 'MB', 'GB'];
        let i = 0;
        let size = bytes;
        while (size >= 1024 && i < sizes.length - 1) {
            size /= 1024;
            i++;
        }
        return size.toFixed(1) + ' ' + sizes[i];
    },
    
    // Apply a shader
    applyShader: async function(shaderPath) {
        try {
            const response = await fetch('/api/shaders/apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ path: shaderPath })
            });
            
            const result = await response.json();
            this.setStatus(result.message, result.status === 'ok' ? 'success' : 'error');
        } catch (error) {
            console.error('Error applying shader:', error);
            this.setStatus('Error applying shader', 'error');
        }
    },
    
    // Import a shader
    importShader: async function() {
        try {
            // Open file dialog
            const response = await fetch('/api/dialog/open_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    initial_dir: this.config.shaders_path || '',
                    file_types: [
                        ['Shader Files', '*.glsl;*.hlsl;*.shader;*.mcpack;*.bin'],
                        ['All Files', '*.*']
                    ]
                })
            });
            
            const result = await response.json();
            if (result.status === 'ok' && result.path) {
                // Import the selected shader
                const importResponse = await fetch('/api/shaders/import', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ path: result.path })
                });
                
                const importResult = await importResponse.json();
                this.setStatus(importResult.message, importResult.status === 'ok' ? 'success' : 'error');
                
                if (importResult.status === 'ok') {
                    this.loadShaders(); // Refresh shader list
                }
            }
        } catch (error) {
            console.error('Error importing shader:', error);
            this.setStatus('Error importing shader', 'error');
        }
    },
    
    // Browse for a path
    browsePath: async function(inputId) {
        try {
            const response = await fetch('/api/dialog/open_folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    initial_dir: document.getElementById(inputId).value || ''
                })
            });
            
            const result = await response.json();
            if (result.status === 'ok') {
                document.getElementById(inputId).value = result.path;
            }
        } catch (error) {
            console.error('Error opening folder dialog:', error);
            this.setStatus('Error selecting folder', 'error');
        }
    },
    
    // Check MaterialBinLoader status
    checkMBLStatus: async function() {
        try {
            const response = await fetch('/api/mbl/status');
            const result = await response.json();
            
            const statusElement = document.getElementById('mbl-status');
            statusElement.textContent = result.message;
            statusElement.className = 'status-message ' + result.status;
            
            return result.status === 'ok';
        } catch (error) {
            console.error('Error checking MBL status:', error);
            this.setStatus('Error checking MaterialBinLoader status', 'error');
            return false;
        }
    },
    
    // Install MaterialBinLoader
    installMBL: async function() {
        try {
            const response = await fetch('/api/mbl/install', {
                method: 'POST'
            });
            
            const result = await response.json();
            this.setStatus(result.message, result.status === 'ok' ? 'success' : 'error');
            
            if (result.status === 'ok') {
                await this.checkMBLStatus();
            }
        } catch (error) {
            console.error('Error installing MBL:', error);
            this.setStatus('Error installing MaterialBinLoader', 'error');
        }
    },
    
    // Launch Minecraft
    launchMinecraft: async function() {
        try {
            const response = await fetch('/api/minecraft/launch', {
                method: 'POST'
            });
            
            const result = await response.json();
            this.setStatus(result.message, result.status === 'ok' ? 'success' : 'error');
        } catch (error) {
            console.error('Error launching Minecraft:', error);
            this.setStatus('Error launching Minecraft', 'error');
        }
    },
    
    // Set status message
    setStatus: function(message, type = 'info') {
        const statusBar = document.getElementById('status-bar');
        statusBar.textContent = message;
        statusBar.className = 'status-bar ' + type;
    },
    
    // Setup theme
    setupTheme: function() {
        const themeToggle = document.getElementById('theme-toggle-checkbox');
        const themeLabel = document.getElementById('theme-label');
        
        themeToggle.addEventListener('change', () => {
            if (themeToggle.checked) {
                document.body.classList.remove('light-theme');
                themeLabel.textContent = 'Dark Mode';
            } else {
                document.body.classList.add('light-theme');
                themeLabel.textContent = 'Light Mode';
            }
        });
    },
    
    // Setup event listeners
    setupEventListeners: function() {
        // Refresh shaders button
        const refreshBtn = document.getElementById('refresh-shaders-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadShaders();
            });
        }
        
        // Import shader button
        const importBtn = document.getElementById('import-shader-btn');
        if (importBtn) {
            importBtn.addEventListener('click', () => {
                this.importShader();
            });
        }
        
        // Save settings button
        const saveSettingsBtn = document.getElementById('save-settings-btn');
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', () => {
                this.saveConfig();
            });
        }
        
        // Browse buttons for paths
        const browseMcBtn = document.getElementById('browse-minecraft-path-btn');
        if (browseMcBtn) {
            browseMcBtn.addEventListener('click', () => {
                this.browsePath('minecraft-path');
            });
        }
        
        const browseShadersBtn = document.getElementById('browse-shaders-path-btn');
        if (browseShadersBtn) {
            browseShadersBtn.addEventListener('click', () => {
                this.browsePath('shaders-path');
            });
        }
        
        const browseBrdBtn = document.getElementById('browse-brd-path-btn');
        if (browseBrdBtn) {
            browseBrdBtn.addEventListener('click', () => {
                this.browsePath('brd-path');
            });
        }
        
        // Launch Minecraft button
        const launchBtn = document.getElementById('launch-minecraft-btn');
        if (launchBtn) {
            launchBtn.addEventListener('click', () => {
                this.launchMinecraft();
            });
        }
        
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all tabs and content
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked tab and its content
                button.classList.add('active');
                document.getElementById(button.dataset.tab + '-tab').classList.add('active');
            });
        });
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
