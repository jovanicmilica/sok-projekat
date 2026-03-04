class BlockVisualizer {
    constructor(data) {
        this.data = data;
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.nodeWidth = 160;
        this.tooltip = null;

        this.init();
    }

    init() {
        this.linkEdges();
        this.setInitialPositions();
        this.createTooltip();

        this.svg = d3.select("#graph")
            .append("svg")
            .attr("width", this.width)
            .attr("height", this.height)
            .call(d3.zoom()
                .scaleExtent([0.2, 4])
                .on("zoom", (e) => this.zoomed(e))
            )
            .append("g");

        this.svg.append("defs").append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");

        this.simulation = d3.forceSimulation(this.data.nodes)
            .force("link", d3.forceLink(this.data.edges)
                .id(d => d.id)
                .distance(400)
                .strength(0.3)
            )
            .force("charge", d3.forceManyBody().strength(-400))
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .force("collision", d3.forceCollide().radius(90))
            .alphaDecay(0.02)
            .velocityDecay(0.4);

        this.draw();
        this.simulation.on("tick", () => this.tick());

        window.viz = this;
    }

    createTooltip() {
        d3.select("#edge-tooltip").remove();

        this.tooltip = d3.select("body")
            .append("div")
            .attr("id", "edge-tooltip")
            .style("position", "absolute")
            .style("background", "#fff")
            .style("color", "#333")
            .style("padding", "10px 14px")
            .style("border-radius", "6px")
            .style("font-size", "12px")
            .style("pointer-events", "none")
            .style("z-index", "1000")
            .style("border", "1px solid #ccc")
            .style("box-shadow", "0 2px 10px rgba(0,0,0,0.1)")
            .style("display", "none")
            .style("max-width", "300px")
            .style("line-height", "1.5");
    }

    showEdgeTooltip(event, d) {
        let html = `<strong style="font-size:13px;">Edge: ${d.id}</strong><br>`;
        html += `<span style="color:#666;">Directed: ${d.directed ? 'Yes' : 'No'}</span><br>`;
        html += `<span style="color:#666;">Source: ${d.source.id}</span><br>`;
        html += `<span style="color:#666;">Target: ${d.target.id}</span>`;

        if (d.attributes && Object.keys(d.attributes).length > 0) {
            html += `<br><hr style="margin:6px 0; border:1px solid #eee;">`;
            html += `<span style="font-weight:500;">Attributes:</span><br>`;
            for (let [key, value] of Object.entries(d.attributes)) {
                html += `<span style="color:#666;">${key}: ${value}</span><br>`;
            }
        }

        this.tooltip
            .style("display", "block")
            .style("left", (event.pageX + 15) + "px")
            .style("top", (event.pageY - 30) + "px")
            .html(html);
    }

    hideEdgeTooltip() {
        this.tooltip.style("display", "none");
    }

    linkEdges() {
        const nodeMap = new Map();
        this.data.nodes.forEach(node => nodeMap.set(node.id, node));

        this.data.edges = this.data.edges.map(edge => ({
            ...edge,
            source: nodeMap.get(edge.source),
            target: nodeMap.get(edge.target)
        })).filter(edge => edge.source && edge.target);
    }

    setInitialPositions() {
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        const radius = Math.min(this.width, this.height) * 0.3;

        this.data.nodes.forEach((node, i) => {
            const angle = (i / this.data.nodes.length) * 2 * Math.PI;
            node.x = centerX + radius * Math.cos(angle);
            node.y = centerY + radius * Math.sin(angle);
        });
    }

    draw() {
        this.edges = this.svg.append("g")
            .selectAll("line")
            .data(this.data.edges)
            .enter()
            .append("line")
            .attr("class", "edge-line")
            .attr("marker-end", d => d.directed ? "url(#arrow)" : null)
            .style("stroke", "#999")
            .style("stroke-width", "2")
            .style("stroke-opacity", "0.6")
            .on("mouseover", (event, d) => this.showEdgeTooltip(event, d))
            .on("mousemove", (event) => {
                this.tooltip
                    .style("left", (event.pageX + 15) + "px")
                    .style("top", (event.pageY - 30) + "px");
            })
            .on("mouseout", () => this.hideEdgeTooltip());

        this.edgeLabels = this.svg.append("g")
            .selectAll("text")
            .data(this.data.edges)
            .enter()
            .append("text")
            .style("font-size", "10px")
            .style("fill", "#333")
            .style("text-anchor", "middle")
            .style("paint-order", "stroke")
            .style("stroke", "white")
            .style("stroke-width", "2px")
            .text(d => d.attributes?.tip || d.attributes?.type || '');

        this.nodes = this.svg.append("g")
            .selectAll("g")
            .data(this.data.nodes)
            .enter()
            .append("g")
            .attr("class", "node-group")
            .call(d3.drag()
                .on("start", (e, d) => this.dragStart(e, d))
                .on("drag", (e, d) => this.drag(e, d))
                .on("end", (e, d) => this.dragEnd(e, d))
            );

        this.nodes.append("rect")
            .attr("width", this.nodeWidth)
            .attr("height", d => d.height)
            .attr("x", -this.nodeWidth/2)
            .attr("y", d => -d.height/2)
            .attr("rx", 4)
            .attr("ry", 4)
            .style("fill", "#4CAF50")
            .style("stroke", "#333")
            .style("stroke-width", "2");

        this.nodes.append("text")
            .attr("class", "node-id")
            .attr("x", 0)
            .attr("y", d => -d.height/2 + 18)
            .style("fill", "white")
            .style("font-size", "12px")
            .style("font-weight", "bold")
            .style("text-anchor", "middle")
            .text(d => d.id);

        this.nodes.each(function(d) {
            const group = d3.select(this);
            const attrs = d.attributes;
            let yPos = -d.height/2 + 38;

            Object.entries(attrs).forEach(([key, value]) => {
                const shortValue = String(value).length > 15
                    ? String(value).substring(0, 12) + '...'
                    : value;

                group.append("text")
                    .attr("x", 0)
                    .attr("y", yPos)
                    .style("fill", "white")
                    .style("font-size", "10px")
                    .style("text-anchor", "middle")
                    .text(`${key}: ${shortValue}`);

                yPos += 18;
            });
        });
    }

    tick() {
        this.edges
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        this.edgeLabels
            .attr("x", d => (d.source.x + d.target.x) / 2)
            .attr("y", d => (d.source.y + d.target.y) / 2);

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

    zoomIn() {
        d3.select("svg").transition().duration(300).call(d3.zoom().scaleBy, 1.2);
    }

    zoomOut() {
        d3.select("svg").transition().duration(300).call(d3.zoom().scaleBy, 0.8);
    }

    reset() {
        d3.select("svg").transition().duration(300).call(d3.zoom().transform, d3.zoomIdentity);
        this.setInitialPositions();
        this.simulation.alpha(0.3).restart();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (typeof graphData !== 'undefined') {
        new BlockVisualizer(graphData);
    }
});