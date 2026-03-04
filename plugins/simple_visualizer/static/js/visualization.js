class GraphVisualizer {
    constructor(data) {
        this.data = data;
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.nodeRadius = 25;

        this.linkEdgesToNodes();

        this.init();
    }

    linkEdgesToNodes() {
        // Create map
        const nodeMap = new Map();
        this.data.nodes.forEach(node => {
            nodeMap.set(node.id, node);
        });

        // Connect nodes
        this.data.edges = this.data.edges.map(edge => ({
            ...edge,
            source: nodeMap.get(edge.source),
            target: nodeMap.get(edge.target)
        })).filter(edge => edge.source && edge.target);
    }

    init() {
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        const radius = Math.min(this.width, this.height) * 0.3;

        this.data.nodes.forEach((node, i) => {
            const angle = (i / this.data.nodes.length) * 2 * Math.PI;
            node.x = centerX + radius * Math.cos(angle);
            node.y = centerY + radius * Math.sin(angle);
            node.fx = null;
            node.fy = null;
        });

        // Create SVG
        this.svg = d3.select("#graph")
            .append("svg")
            .attr("width", this.width)
            .attr("height", this.height)
            .call(d3.zoom()
                .scaleExtent([0.2, 3])
                .on("zoom", (e) => this.zoomed(e))
            )
            .append("g");

        // Force simulation
        this.simulation = d3.forceSimulation(this.data.nodes)
            .force("link", d3.forceLink(this.data.edges)
                .id(d => d.id)
                .distance(150)
                .strength(0.3)
            )
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .force("collision", d3.forceCollide().radius(this.nodeRadius + 10).strength(0.5))
            .alphaDecay(0.02)
            .velocityDecay(0.4);
        
        // Draw
        this.draw();
        
        // Start simulation
        this.simulation.on("tick", () => this.tick());
        
        // Update counter
        document.getElementById('nodeCount').textContent = this.data.nodes.length;
        document.getElementById('edgeCount').textContent = this.data.edges.length;

        window.viz = this;
    }
    
    draw() {
        // Edges
        this.edges = this.svg.append("g")
            .selectAll("line")
            .data(this.data.edges)
            .enter()
            .append("line")
            .attr("class", "edge")
            .attr("data-id", d => d.id)
            .on("mouseover", (e, d) => this.showTooltip(e, d, 'edge'))
            .on("mouseout", () => this.hideTooltip());
        
        // Nodes
        this.nodes = this.svg.append("g")
            .selectAll("g")
            .data(this.data.nodes)
            .enter()
            .append("g")
            .attr("class", "node")
            .attr("data-id", d => d.id)
            .call(d3.drag()
                .on("start", (e, d) => this.dragStart(e, d))
                .on("drag", (e, d) => this.drag(e, d))
                .on("end", (e, d) => this.dragEnd(e, d))
            )
            .on("mouseover", (e, d) => this.showTooltip(e, d, 'node'))
            .on("mouseout", () => this.hideTooltip());
        
        // Add circles
        this.nodes.append("circle")
            .attr("r", this.nodeRadius);
        
        // Add text
        this.nodes.append("text")
            .text(d => this.shortenLabel(d.name));
    }
    
    tick() {
        // Update positions
        this.edges
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
        this.nodes
            .attr("transform", d => `translate(${d.x},${d.y})`);
    }
    
    zoomed(e) {
        this.svg.attr("transform", e.transform);
    }
    
    dragStart(e, d) {
        if (!e.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
        d3.select(e.sourceEvent.target.parentNode).raise();
    }
    
    drag(e, d) {
        d.fx = e.x;
        d.fy = e.y;
    }
    
    dragEnd(e, d) {
        if (!e.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    showTooltip(e, d, type) {
        const tooltip = document.getElementById('tooltip');
        
        let html = '';
        if (type === 'node') {
            html = `<div class="title">🔵 ${d.name || d.id}</div>`;
            html += `<table>`;
            for (let [key, value] of Object.entries(d.attributes || {})) {
                if (key !== 'name') {
                    html += `<tr><td>${key}:</td><td>${value}</td></tr>`;
                }
            }
            html += `</table>`;
        } else {
            html = `<div class="title">🔗 ${d.type || 'edge'}</div>`;
            html += `<table>`;
            html += `<tr><td>from:</td><td>${d.source.id || d.source}</td></tr>`;
            html += `<tr><td>to:</td><td>${d.target.id || d.target}</td></tr>`;
            for (let [key, value] of Object.entries(d.attributes || {})) {
                if (key !== 'type') {
                    html += `<tr><td>${key}:</td><td>${value}</td></tr>`;
                }
            }
            html += `</table>`;
        }
        
        tooltip.innerHTML = html;
        tooltip.classList.remove('hidden');
        tooltip.style.left = (e.pageX + 15) + 'px';
        tooltip.style.top = (e.pageY - 10) + 'px';
    }
    
    hideTooltip() {
        document.getElementById('tooltip').classList.add('hidden');
    }
    
    shortenLabel(text, maxLen = 15) {
        if (!text) return '';
        if (text.length <= maxLen) return text;
        return text.slice(0, maxLen-3) + '...';
    }
    
    zoomIn() {
        this.zoomBy(1.2);
    }
    
    zoomOut() {
        this.zoomBy(0.8);
    }
    
    zoomBy(factor) {
        d3.select("svg")
            .transition()
            .duration(300)
            .call(d3.zoom().scaleBy, factor);
    }
    
    reset() {
        // Reset zoom
        d3.select("svg")
            .transition()
            .duration(300)
            .call(d3.zoom().transform, d3.zoomIdentity);

        const centerX = this.width / 2;
        const centerY = this.height / 2;
        const radius = Math.min(this.width, this.height) * 0.3;
        
        this.data.nodes.forEach((node, i) => {
            const angle = (i / this.data.nodes.length) * 2 * Math.PI;
            node.x = centerX + radius * Math.cos(angle);
            node.y = centerY + radius * Math.sin(angle);
        });
        
        this.simulation.alpha(0.3).restart();
    }
}

// Starting
document.addEventListener('DOMContentLoaded', () => {
    new GraphVisualizer(graphData);
});