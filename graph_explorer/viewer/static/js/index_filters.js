let searches = [];
let filters = [];
let graphOperations = [];
window.APP_GRAPH_DATA = window.APP_GRAPH_DATA || { nodes: {}, edges: [] };

function publishGraphData(graphData) {
    if (window.graphSubject) {
        window.graphSubject.setGraphData(graphData);
        return;
    }

    window.APP_GRAPH_DATA = graphData || { nodes: {}, edges: [] };
    window.dispatchEvent(new CustomEvent('graphDataLoaded', { detail: window.APP_GRAPH_DATA }));
}

async function loadGraphData() {
    try {
        const response = await fetch('/graph-data/');
        if (!response.ok) {
            throw new Error('Failed to load graph data');
        }

        const data = await response.json();
        publishGraphData(data);
        if (typeof window.loadVisualizerAssets === 'function') {
            window.loadVisualizerAssets();
        }
    } catch (error) {
        publishGraphData(window.TEST_GRAPH_DATA || { nodes: {}, edges: [] });
    }
}

function getSearchText() {
    const searchInput = document.getElementById('word-search-input').value.trim();
    return searchInput === '' ? null : searchInput;
}

function clearSearchInput() {
    document.getElementById('word-search-input').value = '';
}

function getFilterText() {
    const attributeName = document.getElementById('attribute-name-input').value.trim();
    const relation = document.getElementById('relation-input').value;
    const attributeValue = document.getElementById('attribute-value-input').value.trim();

    if (attributeName === '' || attributeValue === '') {
        return null;
    }

    return attributeName + ' ' + relation + ' ' + attributeValue;
}

function clearFilterInputs() {
    document.getElementById('attribute-name-input').value = '';
    document.getElementById('attribute-value-input').value = '';
    document.getElementById('relation-input').value = '==';
}

function syncOperationLists() {
    searches = graphOperations
        .filter(operation => operation.type === 'search')
        .map(operation => operation.query);
    filters = graphOperations
        .filter(operation => operation.type === 'filter')
        .map(operation => operation.query);
}

function getOperationLabel(operation) {
    return operation.type === 'search'
        ? 'Search: ' + operation.query
        : 'Filter: ' + operation.query;
}

function showFilterError(message) {
    const container = document.querySelector('.applied-filters-container');
    if (!container) {
        alert(message);
        return;
    }

    let error = container.querySelector('.filter-error-message');
    if (!error) {
        error = document.createElement('div');
        error.className = 'filter-error-message';
        container.appendChild(error);
    }

    error.textContent = message;
}

function clearFilterError() {
    const error = document.querySelector('.filter-error-message');
    if (error) {
        error.remove();
    }
}

function renderAppliedOperations() {
    const appliedFiltersContainer = document.querySelector('.applied-filters-container');
    if (!appliedFiltersContainer) {
        return;
    }

    let filtersWrapper = appliedFiltersContainer.querySelector('.applied-filters-wrapper');
    if (!filtersWrapper) {
        filtersWrapper = document.createElement('div');
        filtersWrapper.className = 'applied-filters-wrapper';
        appliedFiltersContainer.appendChild(filtersWrapper);
    }

    filtersWrapper.innerHTML = '';

    graphOperations.forEach((operation, index) => {
        const filterDiv = document.createElement('div');
        filterDiv.classList.add('applied-filter');
        filterDiv.classList.add(operation.type === 'search' ? 'search-filter' : 'attribute-filter');
        filterDiv.dataset.type = operation.type;
        filterDiv.dataset.filterText = operation.query;

        const textPart = document.createElement('div');
        textPart.className = 'text-part';
        textPart.textContent = getOperationLabel(operation);

        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-applied-filter-btn';
        removeBtn.type = 'button';
        removeBtn.textContent = 'x';
        removeBtn.addEventListener('click', () => removeOperation(index));

        filterDiv.appendChild(textPart);
        filterDiv.appendChild(removeBtn);
        filtersWrapper.appendChild(filterDiv);
    });

    filtersWrapper.hidden = graphOperations.length === 0;
}

async function applyGraphOperations() {
    clearFilterError();

    const response = await fetch('/api/graph-operations/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ operations: graphOperations })
    });

    const data = await response.json();
    if (!response.ok || data.error) {
        throw new Error(data.error || 'Failed to apply graph operations');
    }

    graphOperations = data.operations || graphOperations;
    if (typeof window.refreshWorkspacesFromPayload === 'function') {
        window.refreshWorkspacesFromPayload(data);
    }
    syncOperationLists();
    renderAppliedOperations();

    if (data.visualizer_assets && typeof window.setVisualizerAssets === 'function') {
        window.setVisualizerAssets(data.visualizer_assets);
    }
    publishGraphData(data.graph);
}

async function addOperation(operation) {
    graphOperations.push(operation);

    try {
        await applyGraphOperations();
        return true;
    } catch (error) {
        graphOperations.pop();
        syncOperationLists();
        renderAppliedOperations();
        showFilterError(error.message);
        return false;
    }
}

async function removeOperation(index) {
    const removed = graphOperations.splice(index, 1)[0];

    try {
        await applyGraphOperations();
    } catch (error) {
        graphOperations.splice(index, 0, removed);
        syncOperationLists();
        renderAppliedOperations();
        showFilterError(error.message);
    }
}

function setGraphOperationsFromServer(operations) {
    graphOperations = Array.isArray(operations) ? operations.map(operation => ({
        type: operation.type,
        query: operation.query
    })) : [];
    syncOperationLists();
    clearFilterError();
    renderAppliedOperations();
}

function getGraphOperationsSnapshot() {
    return graphOperations.map(operation => ({
        type: operation.type,
        query: operation.query
    }));
}

function resetGraphOperations() {
    graphOperations = [];
    searches = [];
    filters = [];
    renderAppliedOperations();
    applyGraphOperations().catch(error => showFilterError(error.message));
}

function clearGraphOperationsForNewGraph() {
    graphOperations = [];
    searches = [];
    filters = [];
    clearFilterError();
    renderAppliedOperations();
}

async function addFilter() {
    const filterText = getFilterText();
    if (!filterText) {
        return;
    }

    if (await addOperation({ type: 'filter', query: filterText })) {
        clearFilterInputs();
    }
}

async function addSearch() {
    const searchText = getSearchText();
    if (!searchText) {
        return;
    }

    if (await addOperation({ type: 'search', query: searchText })) {
        clearSearchInput();
    }
}

function setupFilterInputs() {
    const inputs = [
        document.getElementById('attribute-name-input'),
        document.getElementById('attribute-value-input')
    ].filter(Boolean);

    inputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addFilter();
            }
        });
    });

    const searchInput = document.getElementById('word-search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addSearch();
            }
        });
    }
}

function setupViewChooser() {
    const simpleRadio = document.getElementById('simple-view-radio');
    const blockRadio = document.getElementById('block-view-radio');

    if (!simpleRadio || !blockRadio || typeof treeState === 'undefined') {
        return;
    }

    if (!simpleRadio.checked && !blockRadio.checked) {
        simpleRadio.checked = true;
    }

    treeState.selectedView = blockRadio.checked ? 'block-view' : 'simple-view';

    simpleRadio.addEventListener('change', function () {
        if (simpleRadio.checked) {
            treeState.selectedView = 'simple-view';
            if (typeof renderTreeView === 'function') {
                renderTreeView();
            }
        }
    });

    blockRadio.addEventListener('change', function () {
        if (blockRadio.checked) {
            treeState.selectedView = 'block-view';
            if (typeof renderTreeView === 'function') {
                renderTreeView();
            }
        }
    });
}

function testFunction() {
    console.log('Test function called');
}

function showCurrentState() {
    console.log('Current operations:', graphOperations);
    console.log('Current searches:', searches);
    console.log('Current filters:', filters);
}

window.resetGraphOperations = resetGraphOperations;
window.clearGraphOperationsForNewGraph = clearGraphOperationsForNewGraph;

document.addEventListener('DOMContentLoaded', setupFilterInputs);
document.addEventListener('DOMContentLoaded', setupViewChooser);
document.addEventListener('DOMContentLoaded', renderAppliedOperations);
document.addEventListener('DOMContentLoaded', loadGraphData);
