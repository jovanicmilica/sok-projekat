class GraphSubject {
    constructor() {
        this.graphObservers = [];
        this.selectionObservers = [];
        this.viewportObservers = [];
        this.graphData = { nodes: {}, edges: [] };
        this.selectedNodeId = null;
        this.viewport = { x: 0, y: 0, k: 1 };
    }

    addObserver(observer) {
        this.addGraphObserver(observer);
    }

    addGraphObserver(observer) {
        if (typeof observer === 'function' && !this.graphObservers.includes(observer)) {
            this.graphObservers.push(observer);
            observer(this.graphData);
        }
    }

    addSelectionObserver(observer) {
        if (typeof observer === 'function' && !this.selectionObservers.includes(observer)) {
            this.selectionObservers.push(observer);
            observer(this.selectedNodeId, 'init');
        }
    }

    addViewportObserver(observer) {
        if (typeof observer === 'function' && !this.viewportObservers.includes(observer)) {
            this.viewportObservers.push(observer);
            observer(this.viewport, 'init');
        }
    }

    removeObserver(observer) {
        this.graphObservers = this.graphObservers.filter(item => item !== observer);
        this.selectionObservers = this.selectionObservers.filter(item => item !== observer);
        this.viewportObservers = this.viewportObservers.filter(item => item !== observer);
    }

    setGraphData(graphData) {
        this.graphData = normalizeGraphData(graphData);
        this.selectedNodeId = null;
        this.viewport = { x: 0, y: 0, k: 1 };
        window.APP_GRAPH_DATA = this.graphData;
        this.notifyGraph();
        this.notifySelection('graph');
        this.notifyViewport('graph');
    }

    selectNode(nodeId, source = 'unknown') {
        const nextNodeId = nodeId ? String(nodeId) : null;
        if (this.selectedNodeId === nextNodeId) {
            return;
        }

        this.selectedNodeId = nextNodeId;
        this.notifySelection(source);
    }

    setViewport(viewport, source = 'unknown') {
        const nextViewport = {
            x: Number(viewport?.x) || 0,
            y: Number(viewport?.y) || 0,
            k: Math.max(Number(viewport?.k) || 1, 0.05)
        };

        if (
            Math.abs(this.viewport.x - nextViewport.x) < 0.01 &&
            Math.abs(this.viewport.y - nextViewport.y) < 0.01 &&
            Math.abs(this.viewport.k - nextViewport.k) < 0.001
        ) {
            return;
        }

        this.viewport = nextViewport;
        this.notifyViewport(source);
    }

    notifyGraph() {
        this.graphObservers.forEach(observer => observer(this.graphData));
        window.dispatchEvent(new CustomEvent('graphDataLoaded', {
            detail: this.graphData
        }));
    }

    notifySelection(source) {
        this.selectionObservers.forEach(observer => observer(this.selectedNodeId, source));
        window.dispatchEvent(new CustomEvent('graphNodeSelected', {
            detail: { nodeId: this.selectedNodeId, source }
        }));
    }

    notifyViewport(source) {
        this.viewportObservers.forEach(observer => observer(this.viewport, source));
        window.dispatchEvent(new CustomEvent('graphViewportChanged', {
            detail: { viewport: this.viewport, source }
        }));
    }
}

function getNodeAttributes(node) {
    if (!node || typeof node !== 'object') {
        return {};
    }

    if (node.attributes && typeof node.attributes === 'object') {
        return node.attributes;
    }

    const attributes = { ...node };
    delete attributes.id;
    return attributes;
}

function normalizeGraphData(graphData) {
    if (!graphData) {
        return { nodes: {}, edges: [] };
    }

    let data = graphData;
    if (typeof data === 'string') {
        try {
            data = JSON.parse(data);
        } catch (error) {
            return { nodes: {}, edges: [] };
        }
    }

    const rawNodes = data.nodes || {};
    const nodes = {};

    if (Array.isArray(rawNodes)) {
        rawNodes.forEach((node, index) => {
            const nodeId = String(node?.id ?? node?.name ?? index);
            nodes[nodeId] = {
                id: nodeId,
                attributes: getNodeAttributes(node)
            };
        });
    } else {
        Object.entries(rawNodes).forEach(([nodeId, node]) => {
            const id = String(node?.id ?? nodeId);
            nodes[id] = {
                id: id,
                attributes: getNodeAttributes(node)
            };
        });
    }

    const rawEdges = Array.isArray(data.edges) ? data.edges : Object.values(data.edges || {});
    const edges = rawEdges
        .map((edge, index) => {
            const source = edge?.source?.id ?? edge?.source;
            const target = edge?.target?.id ?? edge?.target;

            if (source === undefined || source === null || target === undefined || target === null) {
                return null;
            }

            return {
                id: edge.id ?? String(index),
                source: String(source),
                target: String(target),
                attributes: edge.attributes || {}
            };
        })
        .filter(Boolean);

    return {
        directed: data.directed !== undefined ? data.directed : true,
        nodes,
        edges
    };
}

window.GraphSubject = GraphSubject;
window.graphSubject = window.graphSubject || new GraphSubject();
window.APP_GRAPH_DATA = window.graphSubject.graphData;
