let workspaces = [];
let currentWorkspaceId = 'default';

function renderWorkspaceList() {
    const workspaceList = document.getElementById('workspace-list');
    if (!workspaceList) {
        return;
    }

    workspaceList.innerHTML = '';

    workspaces.forEach(workspace => {
        const badge = document.createElement('div');
        badge.className = 'workspace-badge ' + (workspace.id === currentWorkspaceId ? 'active' : '');
        badge.dataset.id = workspace.id;
        badge.title = getWorkspaceTitle(workspace);

        const nameSpan = document.createElement('span');
        nameSpan.className = 'workspace-name';
        nameSpan.textContent = workspace.name;
        nameSpan.addEventListener('click', () => switchWorkspace(workspace.id));

        const metaSpan = document.createElement('span');
        metaSpan.className = 'workspace-meta';
        metaSpan.textContent = workspace.has_graph
            ? workspace.node_count + 'N/' + workspace.edge_count + 'E'
            : 'empty';
        metaSpan.addEventListener('click', () => switchWorkspace(workspace.id));

        badge.appendChild(nameSpan);
        badge.appendChild(metaSpan);

        if (workspace.id !== 'default') {
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-workspace';
            removeBtn.type = 'button';
            removeBtn.textContent = 'x';
            removeBtn.addEventListener('click', event => {
                event.stopPropagation();
                deleteWorkspace(workspace.id);
            });
            badge.appendChild(removeBtn);
        }

        workspaceList.appendChild(badge);
    });
}

function getWorkspaceTitle(workspace) {
    const parts = [workspace.name];
    if (workspace.data_source_plugin) {
        parts.push('source: ' + workspace.data_source_plugin);
    }
    if (workspace.visualizer_plugin) {
        parts.push('visualizer: ' + workspace.visualizer_plugin);
    }
    if (workspace.operations_count) {
        parts.push('operations: ' + workspace.operations_count);
    }
    return parts.join('\n');
}

function refreshWorkspacesFromPayload(payload) {
    if (!payload) {
        return;
    }

    if (Array.isArray(payload.workspaces)) {
        workspaces = payload.workspaces;
    }

    if (payload.workspace && payload.workspace.id) {
        currentWorkspaceId = payload.workspace.id;
    } else if (payload.active_workspace_id) {
        currentWorkspaceId = payload.active_workspace_id;
    } else {
        const active = workspaces.find(workspace => workspace.active);
        if (active) {
            currentWorkspaceId = active.id;
        }
    }

    renderWorkspaceList();
}

function applyWorkspacePayload(payload) {
    refreshWorkspacesFromPayload(payload);

    if (payload.workspace) {
        setWorkspaceSelectValues(payload.workspace);
    }

    if (typeof window.setGraphOperationsFromServer === 'function') {
        window.setGraphOperationsFromServer(payload.operations || []);
    }

    const nextAssets = payload.visualizer_assets || {
        name: null,
        css: '',
        nodes: {},
        defaults: { width: 96, height: 64 }
    };
    if (typeof window.setVisualizerAssets === 'function') {
        window.setVisualizerAssets(nextAssets);
    }

    const nextGraph = payload.graph || { nodes: {}, edges: [], directed: true };
    if (typeof publishGraphData === 'function') {
        publishGraphData(nextGraph);
    }

    if (payload.workspace && !payload.workspace.has_graph) {
        resetWorkspaceInputs();
    }
}

function setWorkspaceSelectValues(workspace) {
    const dataSourceSelect = document.getElementById('plugin-select');
    const visualizerSelect = document.getElementById('visualizer-plugin-select');

    if (dataSourceSelect) {
        dataSourceSelect.value = workspace.data_source_plugin || 'none';
    }
    if (visualizerSelect) {
        visualizerSelect.value = workspace.visualizer_plugin || 'none';
    }
}

function resetWorkspaceInputs() {
    if (typeof resetToDefaultInput === 'function') {
        resetToDefaultInput();
    }

    const searchInput = document.getElementById('word-search-input');
    const attributeNameInput = document.getElementById('attribute-name-input');
    const attributeValueInput = document.getElementById('attribute-value-input');
    const relationInput = document.getElementById('relation-input');

    if (searchInput) {
        searchInput.value = '';
    }
    if (attributeNameInput) {
        attributeNameInput.value = '';
    }
    if (attributeValueInput) {
        attributeValueInput.value = '';
    }
    if (relationInput) {
        relationInput.value = '==';
    }
}

async function requestWorkspace(url, body) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body || {})
    });

    const data = await response.json();
    if (!response.ok || data.error) {
        throw new Error(data.error || 'Workspace request failed');
    }
    return data;
}

async function loadWorkspaces() {
    try {
        const response = await fetch('/api/workspaces/');
        const data = await response.json();
        if (!response.ok || data.error) {
            throw new Error(data.error || 'Failed to load workspaces');
        }
        applyWorkspacePayload(data);
    } catch (error) {
        console.error('Greska pri ucitavanju workspace-ova:', error);
    }
}

async function createNewWorkspace() {
    const name = prompt('Enter workspace name:', 'New Workspace');
    if (!name) {
        return;
    }

    try {
        const payload = await requestWorkspace('/api/workspaces/create/', { name });
        applyWorkspacePayload(payload);
    } catch (error) {
        alert(error.message);
    }
}

async function saveWorkspace() {
    const currentWorkspace = workspaces.find(workspace => workspace.id === currentWorkspaceId);
    if (!currentWorkspace) {
        return;
    }

    try {
        const payload = await requestWorkspace('/api/workspaces/save/', {
            workspace_id: currentWorkspaceId,
            name: currentWorkspace.name,
        });
        applyWorkspacePayload(payload);
        alert('Workspace "' + payload.workspace.name + '" saved.');
    } catch (error) {
        alert(error.message);
    }
}

async function switchWorkspace(workspaceId) {
    if (!workspaceId || workspaceId === currentWorkspaceId) {
        return;
    }

    try {
        const payload = await requestWorkspace('/api/workspaces/switch/', {
            workspace_id: workspaceId,
        });
        applyWorkspacePayload(payload);
    } catch (error) {
        alert(error.message);
    }
}

async function deleteWorkspace(workspaceId) {
    if (workspaceId === 'default') {
        alert('Cannot delete default workspace.');
        return;
    }

    if (!confirm('Are you sure you want to delete this workspace?')) {
        return;
    }

    try {
        const payload = await requestWorkspace('/api/workspaces/delete/', {
            workspace_id: workspaceId,
        });
        applyWorkspacePayload(payload);
    } catch (error) {
        alert(error.message);
    }
}

window.refreshWorkspacesFromPayload = refreshWorkspacesFromPayload;
window.applyWorkspacePayload = applyWorkspacePayload;
window.loadWorkspaces = loadWorkspaces;
window.createNewWorkspace = createNewWorkspace;
window.saveWorkspace = saveWorkspace;
window.switchWorkspace = switchWorkspace;
window.deleteWorkspace = deleteWorkspace;

document.addEventListener('DOMContentLoaded', loadWorkspaces);
