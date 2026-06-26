const cliState = {
    history: [],
    historyIndex: -1
};

function getCliOutputElement() {
    return document.getElementById('cli-output');
}

function getCliInputElement() {
    return document.getElementById('cli-command-input');
}

function appendCliLine(text, type = 'info') {
    const output = getCliOutputElement();
    if (!output) {
        return;
    }

    const line = document.createElement('div');
    line.className = 'cli-line cli-line-' + type;
    line.textContent = text;
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
}

function applyCliPayload(payload) {
    if (payload.visualizer_assets && typeof window.setVisualizerAssets === 'function') {
        window.setVisualizerAssets(payload.visualizer_assets);
    }
    if (payload.graph && typeof publishGraphData === 'function') {
        publishGraphData(payload.graph);
    }
    if (typeof window.setGraphOperationsFromServer === 'function') {
        window.setGraphOperationsFromServer(payload.operations || []);
    }
    if (typeof window.refreshWorkspacesFromPayload === 'function') {
        window.refreshWorkspacesFromPayload(payload);
    }
}

async function executeCliCommand(command) {
    appendCliLine('> ' + command, 'command');

    const response = await fetch('/api/cli/execute/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command })
    });

    const payload = await response.json();
    if (!response.ok || payload.error) {
        throw new Error(payload.error || 'CLI command failed');
    }

    appendCliLine(payload.message || 'OK', 'success');
    if (payload.graph) {
        applyCliPayload(payload);
    }
}

function submitCliCommand() {
    const input = getCliInputElement();
    if (!input) {
        return;
    }

    const command = input.value.trim();
    if (!command) {
        return;
    }

    cliState.history.push(command);
    cliState.historyIndex = cliState.history.length;
    input.value = '';

    executeCliCommand(command).catch(error => {
        appendCliLine(error.message, 'error');
    });
}

function browseCliHistory(direction) {
    const input = getCliInputElement();
    if (!input || cliState.history.length === 0) {
        return;
    }

    cliState.historyIndex = Math.max(0, Math.min(cliState.history.length, cliState.historyIndex + direction));
    input.value = cliState.history[cliState.historyIndex] || '';
}

function setupCliTerminal() {
    const input = getCliInputElement();
    const runButton = document.getElementById('cli-run-btn');
    if (!input || !runButton) {
        return;
    }

    input.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            submitCliCommand();
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            browseCliHistory(-1);
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            browseCliHistory(1);
        }
    });

    runButton.addEventListener('click', submitCliCommand);
    appendCliLine("Type 'help' for available commands.", 'info');
}

document.addEventListener('DOMContentLoaded', setupCliTerminal);
