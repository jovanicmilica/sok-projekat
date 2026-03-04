document.addEventListener('DOMContentLoaded', function() {
    loadPlugins();
});

function loadPlugins() {
    const selectElement = document.getElementById('plugin-select');
    
    // send requst to backend to get list of plugins
    fetch('/api/plugins/')
        .then(response => response.json())
        .then(pluginNames => {
            console.log('Primljeni pluginovi:', pluginNames);
            
            // clear existing options
            selectElement.innerHTML = '<option value="none">Select datasource plugin...</option>';
            
            // populate select with plugin names
            pluginNames.forEach(pluginName => {
                const option = document.createElement('option');
                option.value = pluginName;
                option.textContent = pluginName;
                selectElement.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Greška:', error);
            selectElement.innerHTML = '<option value="none">Error loading plugins</option>';
        });
}

function handlePluginSelection() {
    const selectElement = document.getElementById('plugin-select');
    const selectedPlugin = selectElement.value;
    
    if (!selectedPlugin || selectedPlugin === 'none') {
        console.log('Nije izabran validan plugin');
        resetToDefaultInput();
        return;
    }
    
    console.log('Izabrani plugin:', selectedPlugin);
    
    // send request to backend to get parameters for selected plugin
    fetch(`/api/plugins/${selectedPlugin}/parameters/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(parameters => {
            console.log('📋 Parametri za plugin:', parameters);
            renderParameterInputs(selectedPlugin, parameters);
        })
        .catch(error => {
            console.error('Greška pri učitavanju parametara:', error);
            showError('Failed to load plugin parameters');
        });
}

function showLoadingIndicator() {
    const container = document.querySelector('.file-input-container');
    if (container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #8f9bb5;">
                <div class="loading-spinner" style="margin: 10px auto;"></div>
                <p>Loading plugin configuration...</p>
            </div>
        `;
    }
}

function showError(message) {
    const container = document.querySelector('.file-input-container');
    if (container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #ff7b89;">
                <p>${message}</p>
                <button class="text-btn" onclick="resetToDefaultInput()">Try Again</button>
            </div>
        `;
    }
}

function resetToDefaultInput() {
    const container = document.querySelector('.file-input-container');
    if (container) {
        container.innerHTML = `
            <input type="text" id="file-input" placeholder="Enter graph file path...">
            <button class="text-btn" onclick="loadGraph()">Enter</button>
        `;
    }
}

function renderParameterInputs(pluginName, parameters) {
    const container = document.querySelector('.file-input-container');
    
    let html = `<div class="plugin-params" data-plugin="${pluginName}">`;
    
    parameters.forEach(param => {
        const inputId = `param-${param.name}`;
        const required = param.required ? 'required' : '';
        const defaultValue = param.default !== undefined ? param.default : '';
        
        if (param.type === 'boolean') {
            html += `
                <div class="param-input" style="margin-bottom: 15px;">
                    <label style="display: flex; align-items: center; gap: 10px; color: #e3eaff;">
                        <input type="checkbox" id="${inputId}" name="${param.name}" 
                               ${defaultValue ? 'checked' : ''} style="width: 18px; height: 18px;">
                        <span>${param.name} ${param.required ? '*' : ''}</span>
                    </label>
                    ${param.description ? `<small style="color: #5f6f8c; display: block; margin-left: 28px;">${param.description}</small>` : ''}
                </div>
            `;
        } else {
            html += `
                <div class="param-input" style="margin-bottom: 15px;">
                    <label for="${inputId}" style="display: block; color: #8f9bb5; margin-bottom: 5px;">
                        ${param.name} ${param.required ? '*' : ''}
                    </label>
                    <input type="${param.type === 'number' ? 'number' : 'text'}" 
                           id="${inputId}" 
                           name="${param.name}"
                           placeholder="${param.placeholder || `Enter ${param.name}...`}"
                           value="${defaultValue}"
                           ${required}
                           style="width: 100%; background: #10161f; border: 1px solid #2b354a; 
                                  border-radius: 12px; padding: 12px 16px; color: #e3eaff;">
                    ${param.description ? `<small style="color: #5f6f8c; display: block; margin-top: 5px;">${param.description}</small>` : ''}
                </div>
            `;
        }
    });
    
    html += `
        <button class="text-btn" onclick="loadGraph()" style="width: 100%; margin-top: 15px;">
            Load Graph
        </button>
    </div>`;
    
    container.innerHTML = html;
}

// add event listener to plugin select dropdown
document.addEventListener('DOMContentLoaded', function() {
    const selectElement = document.getElementById('plugin-select');
    if (selectElement) {
        selectElement.addEventListener('change', handlePluginSelection);
    }
});