let GRAPH_DATA = { nodes: {}, edges: [] };
let ADJACENCY_MAP = {};
let GRAPH_LAYOUT = { nodes: [], edges: [], width: 1000, height: 700 };
let selectedNodeId = null;
let suppressViewportPublish = false;

const treeState = {
    selectedView: 'simple-view',
    expandedNodes: new Set()
};

const mainViewState = {
    svg: null,
    graphLayer: null,
    scaleX: null,
    scaleY: null,
    zoomBehavior: null,
    simulation: null,
    linkSelection: null,
    nodeSelection: null,
    width: 0,
    height: 0
};

const birdViewState = {
    svg: null,
    viewportRect: null,
    linkSelection: null,
    nodeSelection: null,
    graphToBird: null,
    birdToGraph: null,
    width: 0,
    height: 0
};

let VISUALIZER_ASSETS = {
    name: null,
    css: '',
    nodes: {},
    defaults: { width: 96, height: 64 }
};

function getNodeName(nodeId) {
    const node = GRAPH_DATA.nodes[nodeId];
    return node?.attributes?.name || nodeId;
}

function getAdjacencyMap() {
    const adjacency = {};

    Object.keys(GRAPH_DATA.nodes).forEach(nodeId => {
        adjacency[nodeId] = [];
    });

    GRAPH_DATA.edges.forEach(edge => {
        if (adjacency[edge.source]) {
            adjacency[edge.source].push(edge.target);
        }
    });

    Object.keys(adjacency).forEach(nodeId => {
        adjacency[nodeId].sort((left, right) => getNodeName(left).localeCompare(getNodeName(right)));
    });

    return adjacency;
}

function getRootNodeIds() {
    const inDegree = {};
    Object.keys(GRAPH_DATA.nodes).forEach(nodeId => {
        inDegree[nodeId] = 0;
    });

    GRAPH_DATA.edges.forEach(edge => {
        if (inDegree[edge.target] !== undefined) {
            inDegree[edge.target] += 1;
        }
    });

    const roots = Object.keys(inDegree).filter(nodeId => inDegree[nodeId] === 0);
    const allNodes = Object.keys(GRAPH_DATA.nodes);
    const treeRoots = roots.length > 0 ? roots : allNodes;

    treeRoots.sort((left, right) => getNodeName(left).localeCompare(getNodeName(right)));
    return treeRoots;
}

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function getVisualizerNodeAsset(nodeId) {
    const defaults = VISUALIZER_ASSETS.defaults || { width: 96, height: 64 };
    const asset = VISUALIZER_ASSETS.nodes?.[nodeId] || {};
    return {
        html: asset.html || '',
        width: Number(asset.width || defaults.width || 96),
        height: Number(asset.height || defaults.height || 64)
    };
}

function createFallbackNodeHtml(nodeId, node) {
    return '<div class="default-visualizer-node"><span>' + escapeHtml(node.name || nodeId) + '</span></div>';
}

function getNodeHtml(nodeId, node) {
    const asset = getVisualizerNodeAsset(nodeId);
    return asset.html || createFallbackNodeHtml(nodeId, node);
}

function applyVisualizerStyles(css) {
    let styleElement = document.getElementById('visualizer-plugin-styles');
    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'visualizer-plugin-styles';
        document.head.appendChild(styleElement);
    }
    styleElement.textContent = css || '';
}

function setVisualizerAssets(assets) {
    VISUALIZER_ASSETS = {
        name: assets?.name || null,
        css: assets?.css || '',
        nodes: assets?.nodes || {},
        defaults: assets?.defaults || { width: 96, height: 64 }
    };

    applyVisualizerStyles(VISUALIZER_ASSETS.css);

    if (GRAPH_DATA && Object.keys(GRAPH_DATA.nodes || {}).length > 0) {
        GRAPH_LAYOUT = createGraphLayout();
        renderTreeView();
        renderMainView();
        renderBirdView();
    }
}

async function loadVisualizerAssets() {
    try {
        const response = await fetch('/api/visualizer-assets/');
        if (!response.ok) {
            return;
        }
        setVisualizerAssets(await response.json());
    } catch (error) {
        console.warn('Visualizer assets could not be loaded', error);
    }
}

function getGraphNodeList() {
    return Object.keys(GRAPH_DATA.nodes).map(nodeId => {
        const node = {
            id: nodeId,
            name: getNodeName(nodeId),
            attributes: GRAPH_DATA.nodes[nodeId].attributes || {}
        };
        const visual = getVisualizerNodeAsset(nodeId);

        return {
            ...node,
            visualWidth: visual.width,
            visualHeight: visual.height,
            html: getNodeHtml(nodeId, node)
        };
    });
}

function publishNodeSelection(nodeId, source) {
    if (window.graphSubject) {
        window.graphSubject.selectNode(nodeId, source);
    } else {
        setSelectedNode(nodeId);
    }
}

function publishViewport(viewport, source) {
    if (window.graphSubject) {
        window.graphSubject.setViewport(viewport, source);
    }
}

function toggleNode(nodeKey) {
    if (treeState.expandedNodes.has(nodeKey)) {
        treeState.expandedNodes.delete(nodeKey);
    } else {
        treeState.expandedNodes.add(nodeKey);
    }

    renderTreeView();
}

function createAttributesElement(attributes) {
    const attributesContainer = document.createElement('div');
    attributesContainer.className = 'tree-attributes';

    Object.entries(attributes).forEach(([key, value]) => {
        const item = document.createElement('div');
        item.className = 'tree-attribute-item';
        item.textContent = `${key}: ${value}`;
        attributesContainer.appendChild(item);
    });

    return attributesContainer;
}

function createTreeNodeElement(nodeId, depth, ancestorPath, lineage) {
    const node = GRAPH_DATA.nodes[nodeId];
    const children = (ADJACENCY_MAP[nodeId] || []).filter(childId => !ancestorPath.has(childId));
    const nodeKey = lineage.join('>');
    const isExpanded = treeState.expandedNodes.has(nodeKey);

    const wrapper = document.createElement('div');
    wrapper.className = 'tree-node';
    wrapper.dataset.nodeId = nodeId;

    const row = document.createElement('div');
    row.className = 'tree-node-row';
    row.style.paddingLeft = `${depth * 18}px`;
    row.addEventListener('click', () => publishNodeSelection(nodeId, 'tree'));
    row.addEventListener('mouseover', event => showGraphTooltip(event, { id: nodeId, name: getNodeName(nodeId), attributes: node.attributes || {} }, 'node'));
    row.addEventListener('mousemove', moveGraphTooltip);
    row.addEventListener('mouseout', hideGraphTooltip);

    const toggleButton = document.createElement('button');
    toggleButton.className = 'tree-toggle-btn';
    toggleButton.type = 'button';
    toggleButton.textContent = isExpanded ? '-' : '+';
    toggleButton.addEventListener('click', event => {
        event.stopPropagation();
        toggleNode(nodeKey);
    });

    const visual = getVisualizerNodeAsset(nodeId);
    const label = document.createElement('div');
    label.className = 'tree-node-visual graph-node-render';
    label.style.width = `${Math.min(visual.width, 220)}px`;
    label.style.minHeight = `${Math.min(visual.height, 120)}px`;
    label.innerHTML = getNodeHtml(nodeId, {
        id: nodeId,
        name: getNodeName(nodeId),
        attributes: node.attributes || {}
    });

    row.appendChild(toggleButton);
    row.appendChild(label);
    wrapper.appendChild(row);

    if (isExpanded && treeState.selectedView === 'block-view' && Object.keys(node.attributes).length > 0) {
        const attrs = createAttributesElement(node.attributes);
        attrs.style.marginLeft = `${depth * 18 + 36}px`;
        wrapper.appendChild(attrs);
    }

    if (isExpanded && children.length > 0) {
        const childrenContainer = document.createElement('div');
        childrenContainer.className = 'tree-children';

        children.forEach(childId => {
            const nextPath = new Set(ancestorPath);
            nextPath.add(childId);
            const nextLineage = [...lineage, childId];
            childrenContainer.appendChild(createTreeNodeElement(childId, depth + 1, nextPath, nextLineage));
        });

        wrapper.appendChild(childrenContainer);
    }

    return wrapper;
}

function createGraphLayout() {
    const nodes = getGraphNodeList();
    const width = 1000;
    const height = 700;
    const radius = 260;
    const centerX = width / 2;
    const centerY = height / 2;
    const positionedNodes = nodes.map((node, index) => {
        if (nodes.length === 1) {
            return { ...node, x: centerX, y: centerY };
        }

        const angle = (2 * Math.PI * index) / nodes.length - Math.PI / 2;
        return {
            ...node,
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle)
        };
    });
    const nodePositions = Object.fromEntries(positionedNodes.map(node => [node.id, node]));
    const edges = (GRAPH_DATA.edges || []).filter(edge => nodePositions[edge.source] && nodePositions[edge.target]);

    return { nodes: positionedNodes, edges, nodePositions, width, height };
}

function getNodePosition(nodeId) {
    return GRAPH_LAYOUT.nodePositions?.[nodeId] || null;
}

function createTreeSelectionIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'tree-selection-indicator';

    if (!selectedNodeId || !GRAPH_DATA.nodes[selectedNodeId]) {
        indicator.classList.add('is-empty');
        indicator.textContent = 'No selected node';
        return indicator;
    }

    const label = document.createElement('span');
    label.className = 'tree-selection-label';
    label.textContent = 'Selected';

    const value = document.createElement('span');
    value.className = 'tree-selection-value';
    value.textContent = getNodeName(selectedNodeId);

    indicator.appendChild(label);
    indicator.appendChild(value);
    return indicator;
}

function updateTreeSelectionIndicator() {
    const indicator = document.querySelector('.tree-selection-indicator');
    if (!indicator) {
        return;
    }

    const nextIndicator = createTreeSelectionIndicator();
    indicator.replaceWith(nextIndicator);
}

function getTooltipElement() {
    let tooltip = document.getElementById('graph-tooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.id = 'graph-tooltip';
        tooltip.className = 'graph-tooltip hidden';
        document.body.appendChild(tooltip);
    }

    return tooltip;
}

function formatAttributesTable(attributes) {
    const entries = Object.entries(attributes || {});
    if (entries.length === 0) {
        return '<div class="tooltip-muted">No attributes</div>';
    }

    return '<table>' + entries.map(([key, value]) => {
        return `<tr><td>${key}</td><td>${value}</td></tr>`;
    }).join('') + '</table>';
}

function showGraphTooltip(event, item, type) {
    const tooltip = getTooltipElement();
    const title = type === 'node'
        ? (item.name || item.id)
        : `${item.source?.id || item.source} -> ${item.target?.id || item.target}`;
    const attributes = item.attributes || {};

    tooltip.innerHTML = `<div class="tooltip-title">${title}</div>${formatAttributesTable(attributes)}`;
    tooltip.classList.remove('hidden');
    moveGraphTooltip(event);
}

function moveGraphTooltip(event) {
    const tooltip = getTooltipElement();
    tooltip.style.left = `${event.clientX + 14}px`;
    tooltip.style.top = `${event.clientY + 14}px`;
}

function hideGraphTooltip() {
    getTooltipElement().classList.add('hidden');
}

function renderTreeView() {
    const treeContainer = document.querySelector('.tree-view-container');
    if (!treeContainer) {
        return;
    }

    let content = treeContainer.querySelector('.tree-content');
    if (!content) {
        content = document.createElement('div');
        content.className = 'tree-content';
        treeContainer.appendChild(content);
    }

    content.innerHTML = '';
    content.appendChild(createTreeSelectionIndicator());

    const rootNodeIds = getRootNodeIds();
    if (rootNodeIds.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'tree-empty';
        empty.textContent = 'No nodes loaded.';
        content.appendChild(empty);
        return;
    }

    rootNodeIds.forEach(rootId => {
        const path = new Set();
        path.add(rootId);
        content.appendChild(createTreeNodeElement(rootId, 0, path, [rootId]));
    });

    applySelectedNodeStyles();
}

function renderMainView() {
    const mainContainer = document.querySelector('.main-view-container');
    if (!mainContainer) {
        return;
    }

    mainContainer.innerHTML = '';

    if (GRAPH_LAYOUT.nodes.length === 0) {
        mainContainer.classList.remove('has-graph');
        const empty = document.createElement('div');
        empty.className = 'empty-graph-hint';
        empty.textContent = 'No nodes loaded.';
        mainContainer.appendChild(empty);
        return;
    }

    mainContainer.classList.add('has-graph');

    const stage = document.createElement('div');
    stage.className = 'embedded-graph-stage';
    mainContainer.appendChild(stage);

    const width = Math.max(mainContainer.clientWidth - 32, 360);
    const height = Math.max(mainContainer.clientHeight - 76, 260);
    mainViewState.width = width;
    mainViewState.height = height;

    const svg = d3.select(stage)
        .append('svg')
        .attr('class', 'main-graph-svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`);

    const viewportLayer = svg.append('g').attr('class', 'main-viewport-layer');
    const graphLayer = viewportLayer.append('g').attr('class', 'main-graph-layer');
    const scaleX = d3.scaleLinear().domain([0, GRAPH_LAYOUT.width]).range([0, width]);
    const scaleY = d3.scaleLinear().domain([0, GRAPH_LAYOUT.height]).range([0, height]);

    const linkSelection = graphLayer.selectAll('line')
        .data(GRAPH_LAYOUT.edges)
        .enter()
        .append('line')
        .attr('class', 'main-edge-line')
        .attr('x1', edge => scaleX(getNodePosition(edge.source).x))
        .attr('y1', edge => scaleY(getNodePosition(edge.source).y))
        .attr('x2', edge => scaleX(getNodePosition(edge.target).x))
        .attr('y2', edge => scaleY(getNodePosition(edge.target).y))
        .on('mouseover', (event, edge) => showGraphTooltip(event, edge, 'edge'))
        .on('mousemove', moveGraphTooltip)
        .on('mouseout', hideGraphTooltip);

    const nodeDragBehavior = d3.drag()
        .on('start', function (event, node) {
            event.sourceEvent.stopPropagation();
            d3.select(this).classed('is-dragging', true).raise();
            publishNodeSelection(node.id, 'main');
            if (!event.active && mainViewState.simulation) {
                mainViewState.simulation.alphaTarget(0.25).restart();
            }
            node.fx = node.x;
            node.fy = node.y;
        })
        .on('drag', function (event, node) {
            event.sourceEvent.stopPropagation();
            const [screenX, screenY] = d3.pointer(event.sourceEvent, mainViewState.svg.node());
            const [layerX, layerY] = d3.zoomTransform(mainViewState.svg.node()).invert([screenX, screenY]);
            node.fx = clamp(scaleX.invert(layerX), 0, GRAPH_LAYOUT.width);
            node.fy = clamp(scaleY.invert(layerY), 0, GRAPH_LAYOUT.height);
        })
        .on('end', function (event, node) {
            event.sourceEvent.stopPropagation();
            d3.select(this).classed('is-dragging', false);
            if (!event.active && mainViewState.simulation) {
                mainViewState.simulation.alphaTarget(0);
            }
            node.fx = null;
            node.fy = null;
        });

    const nodeGroups = graphLayer.selectAll('g.main-node')
        .data(GRAPH_LAYOUT.nodes)
        .enter()
        .append('g')
        .attr('class', 'main-node')
        .attr('data-node-id', node => node.id)
        .attr('transform', node => `translate(${scaleX(node.x)}, ${scaleY(node.y)})`)
        .on('click', function (event, node) {
            event.stopPropagation();
            publishNodeSelection(node.id, 'main');
        })
        .on('mouseover', (event, node) => showGraphTooltip(event, node, 'node'))
        .on('mousemove', moveGraphTooltip)
        .on('mouseout', hideGraphTooltip)
        .call(nodeDragBehavior);

    nodeGroups.append('foreignObject')
        .attr('class', 'main-node-foreign-object')
        .attr('x', node => -node.visualWidth / 2)
        .attr('y', node => -node.visualHeight / 2)
        .attr('width', node => node.visualWidth)
        .attr('height', node => node.visualHeight)
        .append('xhtml:div')
        .attr('class', 'main-node-html graph-node-render')
        .style('width', node => `${node.visualWidth}px`)
        .style('height', node => `${node.visualHeight}px`)
        .html(node => node.html);

    svg.on('click', () => publishNodeSelection(null, 'main'));

    const zoomBehavior = d3.zoom()
        .scaleExtent([0.5, 6])
        .on('zoom', event => {
            viewportLayer.attr('transform', event.transform);
            if (!suppressViewportPublish) {
                publishViewport({ x: event.transform.x, y: event.transform.y, k: event.transform.k }, 'main');
            }
            updateBirdViewportRect(event.transform);
        });

    svg.call(zoomBehavior);

    mainViewState.svg = svg;
    mainViewState.graphLayer = graphLayer;
    mainViewState.scaleX = scaleX;
    mainViewState.scaleY = scaleY;
    mainViewState.zoomBehavior = zoomBehavior;
    mainViewState.linkSelection = linkSelection;
    mainViewState.nodeSelection = nodeGroups;

    startForceSimulation();
    applySelectedNodeStyles();
    applyViewport(window.graphSubject?.viewport || { x: 0, y: 0, k: 1 }, 'render');
}

function renderBirdView() {
    const birdContainer = document.querySelector('.bird-view-container');
    if (!birdContainer) {
        return;
    }

    birdContainer.innerHTML = '';

    if (GRAPH_LAYOUT.nodes.length === 0) {
        birdContainer.classList.remove('has-graph');
        const empty = document.createElement('div');
        empty.className = 'empty-graph-hint';
        empty.textContent = 'No nodes loaded.';
        birdContainer.appendChild(empty);
        return;
    }

    birdContainer.classList.add('has-graph');

    const stage = document.createElement('div');
    stage.className = 'bird-graph-stage';
    birdContainer.appendChild(stage);

    const width = Math.max(birdContainer.clientWidth - 32, 220);
    const height = Math.max(birdContainer.clientHeight - 76, 160);
    birdViewState.width = width;
    birdViewState.height = height;

    const margin = 18;
    const scale = Math.min((width - margin * 2) / GRAPH_LAYOUT.width, (height - margin * 2) / GRAPH_LAYOUT.height);
    const offsetX = (width - GRAPH_LAYOUT.width * scale) / 2;
    const offsetY = (height - GRAPH_LAYOUT.height * scale) / 2;

    birdViewState.graphToBird = point => ({
        x: offsetX + point.x * scale,
        y: offsetY + point.y * scale
    });
    birdViewState.birdToGraph = point => ({
        x: (point.x - offsetX) / scale,
        y: (point.y - offsetY) / scale
    });

    const svg = d3.select(stage)
        .append('svg')
        .attr('class', 'bird-graph-svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`);

    const birdLinks = svg.selectAll('line')
        .data(GRAPH_LAYOUT.edges)
        .enter()
        .append('line')
        .attr('class', 'bird-edge-line')
        .attr('x1', edge => birdViewState.graphToBird(getNodePosition(edge.source)).x)
        .attr('y1', edge => birdViewState.graphToBird(getNodePosition(edge.source)).y)
        .attr('x2', edge => birdViewState.graphToBird(getNodePosition(edge.target)).x)
        .attr('y2', edge => birdViewState.graphToBird(getNodePosition(edge.target)).y)
        .on('mouseover', (event, edge) => showGraphTooltip(event, edge, 'edge'))
        .on('mousemove', moveGraphTooltip)
        .on('mouseout', hideGraphTooltip);

    const birdNodes = svg.selectAll('circle')
        .data(GRAPH_LAYOUT.nodes)
        .enter()
        .append('circle')
        .attr('class', 'bird-node-circle')
        .attr('data-node-id', node => node.id)
        .attr('cx', node => birdViewState.graphToBird(node).x)
        .attr('cy', node => birdViewState.graphToBird(node).y)
        .attr('r', Math.max(4, Math.min(8, 90 / GRAPH_LAYOUT.nodes.length)))
        .on('click', function (event, node) {
            event.stopPropagation();
            publishNodeSelection(node.id, 'bird');
        })
        .on('mouseover', (event, node) => showGraphTooltip(event, node, 'node'))
        .on('mousemove', moveGraphTooltip)
        .on('mouseout', hideGraphTooltip);

    const viewportRect = svg.append('rect')
        .attr('class', 'bird-viewport-rect')
        .attr('rx', 6)
        .call(d3.drag().on('drag', event => handleBirdViewportDrag(event)));

    svg.on('click', event => {
        if (event.target === svg.node()) {
            const [x, y] = d3.pointer(event, svg.node());
            centerMainViewportOnBirdPoint(x, y);
        }
    });

    birdViewState.svg = svg;
    birdViewState.linkSelection = birdLinks;
    birdViewState.nodeSelection = birdNodes;
    birdViewState.viewportRect = viewportRect;

    applySelectedNodeStyles();
    updateBirdViewportRect(window.graphSubject?.viewport || { x: 0, y: 0, k: 1 });
}

function screenViewportToGraphBounds(transform) {
    const scaleX = GRAPH_LAYOUT.width / Math.max(mainViewState.width, 1);
    const scaleY = GRAPH_LAYOUT.height / Math.max(mainViewState.height, 1);

    return {
        x: (-transform.x / transform.k) * scaleX,
        y: (-transform.y / transform.k) * scaleY,
        width: (mainViewState.width / transform.k) * scaleX,
        height: (mainViewState.height / transform.k) * scaleY
    };
}

function graphBoundsToMainTransform(bounds, k) {
    const scaleX = mainViewState.width / GRAPH_LAYOUT.width;
    const scaleY = mainViewState.height / GRAPH_LAYOUT.height;

    return {
        x: -bounds.x * scaleX * k,
        y: -bounds.y * scaleY * k,
        k
    };
}

function updateBirdViewportRect(viewport) {
    if (!birdViewState.viewportRect || !birdViewState.graphToBird || mainViewState.width === 0) {
        return;
    }

    const bounds = screenViewportToGraphBounds(viewport);
    const topLeft = birdViewState.graphToBird({ x: bounds.x, y: bounds.y });
    const bottomRight = birdViewState.graphToBird({ x: bounds.x + bounds.width, y: bounds.y + bounds.height });

    birdViewState.viewportRect
        .attr('x', topLeft.x)
        .attr('y', topLeft.y)
        .attr('width', Math.max(bottomRight.x - topLeft.x, 10))
        .attr('height', Math.max(bottomRight.y - topLeft.y, 10));
}

function handleBirdViewportDrag(event) {
    if (!birdViewState.viewportRect || !birdViewState.birdToGraph || mainViewState.width === 0) {
        return;
    }

    const currentViewport = window.graphSubject?.viewport || { x: 0, y: 0, k: 1 };
    const rectX = Number(birdViewState.viewportRect.attr('x')) + event.dx;
    const rectY = Number(birdViewState.viewportRect.attr('y')) + event.dy;
    const graphTopLeft = birdViewState.birdToGraph({ x: rectX, y: rectY });
    const graphBounds = {
        x: clamp(graphTopLeft.x, -GRAPH_LAYOUT.width, GRAPH_LAYOUT.width),
        y: clamp(graphTopLeft.y, -GRAPH_LAYOUT.height, GRAPH_LAYOUT.height)
    };

    publishViewport(graphBoundsToMainTransform(graphBounds, currentViewport.k), 'bird');
}

function centerMainViewportOnBirdPoint(birdX, birdY) {
    if (!birdViewState.birdToGraph || mainViewState.width === 0) {
        return;
    }

    const currentViewport = window.graphSubject?.viewport || { x: 0, y: 0, k: 1 };
    const graphPoint = birdViewState.birdToGraph({ x: birdX, y: birdY });
    const visible = screenViewportToGraphBounds(currentViewport);
    const nextBounds = {
        x: graphPoint.x - visible.width / 2,
        y: graphPoint.y - visible.height / 2
    };

    publishViewport(graphBoundsToMainTransform(nextBounds, currentViewport.k), 'bird');
}

function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

function startForceSimulation() {
    if (mainViewState.simulation) {
        mainViewState.simulation.stop();
    }

    const simulationLinks = GRAPH_LAYOUT.edges.map(edge => ({
        ...edge,
        source: edge.source,
        target: edge.target
    }));

    mainViewState.simulation = d3.forceSimulation(GRAPH_LAYOUT.nodes)
        .force('link', d3.forceLink(simulationLinks)
            .id(node => node.id)
            .distance(155)
            .strength(0.35))
        .force('charge', d3.forceManyBody().strength(-420))
        .force('center', d3.forceCenter(GRAPH_LAYOUT.width / 2, GRAPH_LAYOUT.height / 2))
        .force('collision', d3.forceCollide().radius(node => Math.max(node.visualWidth, node.visualHeight) / 2 + 18).strength(0.9))
        .alpha(0.9)
        .alphaDecay(0.025)
        .velocityDecay(0.38)
        .on('tick', updateGraphPositionsFromLayout);
}

function updateGraphPositionsFromLayout() {
    if (!mainViewState.graphLayer || !mainViewState.scaleX || !mainViewState.scaleY) {
        return;
    }

    GRAPH_LAYOUT.nodes.forEach(node => {
        node.x = clamp(node.x, 0, GRAPH_LAYOUT.width);
        node.y = clamp(node.y, 0, GRAPH_LAYOUT.height);
        GRAPH_LAYOUT.nodePositions[node.id] = node;
    });

    mainViewState.linkSelection
        .attr('x1', edge => mainViewState.scaleX(getNodePosition(edge.source).x))
        .attr('y1', edge => mainViewState.scaleY(getNodePosition(edge.source).y))
        .attr('x2', edge => mainViewState.scaleX(getNodePosition(edge.target).x))
        .attr('y2', edge => mainViewState.scaleY(getNodePosition(edge.target).y));

    mainViewState.nodeSelection
        .attr('transform', node => `translate(${mainViewState.scaleX(node.x)}, ${mainViewState.scaleY(node.y)})`);

    updateBirdGraphPositionsFromLayout();
}

function updateBirdGraphPositionsFromLayout() {
    if (!birdViewState.graphToBird || !birdViewState.linkSelection || !birdViewState.nodeSelection) {
        return;
    }

    birdViewState.linkSelection
        .attr('x1', edge => birdViewState.graphToBird(getNodePosition(edge.source)).x)
        .attr('y1', edge => birdViewState.graphToBird(getNodePosition(edge.source)).y)
        .attr('x2', edge => birdViewState.graphToBird(getNodePosition(edge.target)).x)
        .attr('y2', edge => birdViewState.graphToBird(getNodePosition(edge.target)).y);

    birdViewState.nodeSelection
        .attr('cx', node => birdViewState.graphToBird(node).x)
        .attr('cy', node => birdViewState.graphToBird(node).y);
}

function applyViewport(viewport, source) {
    if (!mainViewState.svg || !mainViewState.zoomBehavior) {
        updateBirdViewportRect(viewport);
        return;
    }

    const transform = d3.zoomIdentity.translate(viewport.x, viewport.y).scale(viewport.k);

    if (source === 'main') {
        updateBirdViewportRect(transform);
        return;
    }

    suppressViewportPublish = true;
    mainViewState.svg.call(mainViewState.zoomBehavior.transform, transform);
    suppressViewportPublish = false;
    updateBirdViewportRect(transform);
}

function setSelectedNode(nodeId) {
    selectedNodeId = nodeId;
    updateTreeSelectionIndicator();
    applySelectedNodeStyles();
}

function applySelectedNodeStyles() {
    document.querySelectorAll('[data-node-id]').forEach(element => {
        element.classList.toggle('is-selected', element.dataset.nodeId === selectedNodeId);
    });

    if (!selectedNodeId) {
        return;
    }

    const selectedTreeNode = document.querySelector(`.tree-node[data-node-id="${CSS.escape(selectedNodeId)}"]`);
    if (selectedTreeNode) {
        selectedTreeNode.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
}

function setGraphData(graphData) {
    GRAPH_DATA = graphData || { nodes: {}, edges: [] };
    ADJACENCY_MAP = getAdjacencyMap();
    GRAPH_LAYOUT = createGraphLayout();
    renderTreeView();
    renderMainView();
    renderBirdView();
}

window.addEventListener('graphDataLoaded', function (event) {
    if (!window.graphSubject) {
        setGraphData(event.detail);
    }
});

window.addEventListener('visualizerAssetsLoaded', function (event) {
    setVisualizerAssets(event.detail);
});

window.setVisualizerAssets = setVisualizerAssets;
window.loadVisualizerAssets = loadVisualizerAssets;

document.addEventListener('DOMContentLoaded', function () {
    if (window.graphSubject) {
        window.graphSubject.addGraphObserver(setGraphData);
        window.graphSubject.addSelectionObserver(setSelectedNode);
        window.graphSubject.addViewportObserver(applyViewport);
    } else if (window.APP_GRAPH_DATA && Object.keys(window.APP_GRAPH_DATA.nodes || {}).length > 0) {
        setGraphData(window.APP_GRAPH_DATA);
    } else {
        renderTreeView();
        renderMainView();
        renderBirdView();
    }
});