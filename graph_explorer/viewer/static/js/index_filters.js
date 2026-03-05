let searches = [];
let filters = [];
window.APP_GRAPH_DATA = { nodes: {}, edges: [] };

function publishGraphData(graphData) {
    window.APP_GRAPH_DATA = graphData || { nodes: {}, edges: [] };
    window.dispatchEvent(new CustomEvent('graphDataLoaded', {
        detail: window.APP_GRAPH_DATA
    }));
}

async function loadGraphData() {
    try {
        const response = await fetch('/graph-data/');
        if (!response.ok) {
            throw new Error('Failed to load graph data');
        }

        const data = await response.json();
        publishGraphData(data);
    } catch (error) {
        publishGraphData(window.TEST_GRAPH_DATA || { nodes: {}, edges: [] });
    }
}

function getSearchText() {
    const searchInput = document.getElementById('word-search-input').value.trim();
    if (searchInput == "") {
        return null;
    } 
    else {
        return searchInput;
    }
}

function clearSearchInput() {
    document.getElementById('word-search-input').value = '';
}

function getFilterText() {
    const attributeName = document.getElementById('attribute-name-input').value.trim();
    const relation = document.getElementById('relation-input').value;
    const attributeValue = document.getElementById('attribute-value-input').value.trim();
    if (attributeName == "" || attributeValue == "") {
        return null; 
    }
    else {
        return `${attributeName} ${relation} ${attributeValue}`;
    }
}

function clearFilterInputs() {
    document.getElementById('attribute-name-input').value = '';
    document.getElementById('attribute-value-input').value = '';
    document.getElementById('relation-input').value = 'equals';
}

function addQuery(filterText, type) {
    // Create new filter element
    const appliedFiltersContainer = document.querySelector('.applied-filters-container');

    // Check weather the wrapper for filters already exists, if not create it
    let filtersWrapper = appliedFiltersContainer.querySelector('.applied-filters-wrapper');
    if (!filtersWrapper) {
        filtersWrapper = document.createElement('div');
        filtersWrapper.className = 'applied-filters-wrapper';
        appliedFiltersContainer.appendChild(filtersWrapper);
    }

    // Create the filter div and set its classes based on the type (search or filter)
    const filterDiv = document.createElement('div');
    filterDiv.classList.add('applied-filter');
    filterDiv.classList.add(type === 'search' ? 'search-filter' : 'attribute-filter');

    // Filter text part
    const textPart = document.createElement('div');
    textPart.className = 'text-part';
    textPart.textContent = filterText;

    // Remove button
    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-applied-filter-btn';
    removeBtn.textContent = 'x';
    
    // Add data attributes to identify the type and text of the filter for later removal
    filterDiv.dataset.type = type;
    filterDiv.dataset.filterText = filterText;
    
    removeBtn.onclick = function() {
        // Remove the filter element from the DOM
        filterDiv.remove();
        
        // Remove the filter from the corresponding array (searches or filters) based on its type
        const filterType = filterDiv.dataset.type;
        const filterText = filterDiv.dataset.filterText;
        
        if (filterType === 'search') {
            // Remove from searches array
            const index = searches.indexOf(filterText);
            if (index > -1) {
                searches.splice(index, 1);
            }
            console.log('Searches after removal:', searches);
        } else {
            // Remove from filters array
            const index = filters.indexOf(filterText);
            if (index > -1) {
                filters.splice(index, 1);
            }
            console.log('Filters after removal:', filters);
        }
        
        // Remove the wrapper if there are no more filters inside
        if (filtersWrapper.children.length === 0) {
            filtersWrapper.remove();
        }
    };

    // Add text and remove button to filter div
    filterDiv.appendChild(textPart);
    filterDiv.appendChild(removeBtn);

    // Add the new filter div to the wrapper
    filtersWrapper.appendChild(filterDiv);
}

function addFilter() {
    const filterText = getFilterText();
    if (filterText) {
        // Add to filters array before creating the element
        filters.push(filterText);
        console.log('Filters after add:', filters);
        
        // Pass the type 'filter' to the addQuery function
        addQuery(filterText, 'filter');
        clearFilterInputs();
    }
}

function addSearch() {
    const searchText = getSearchText(); 
    if (searchText) {
        // Add to searches array before creating the element
        searches.push(searchText);
        console.log('Searches after add:', searches);
        
        // Pass the type 'search' to the addQuery function
        addQuery(searchText, 'search');
        clearSearchInput();
    }  
}

// Setup event listeners for filter input fields to trigger addFilter on Enter key press
function setupFilterInputs() {
    const inputs = [
        document.getElementById('attribute-name-input'),
        document.getElementById('attribute-value-input')
    ];

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

// Setup event listener for when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', setupFilterInputs);
document.addEventListener('DOMContentLoaded', setupViewChooser);
document.addEventListener('DOMContentLoaded', loadGraphData);

function testFunction() {
    console.log('Test function called');
}

// Optional function to show current state of searches and filters in console
function showCurrentState() {
    console.log('Current searches:', searches);
    console.log('Current filters:', filters);
}
