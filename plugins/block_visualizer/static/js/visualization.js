(function() {
    // take data
    const nodes = window.__graphData.nodes;
    const edges = window.__graphData.edges;

    // setup
    const container = document.querySelector('.block-visualizer-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select(".block-visualizer-container svg");
    svg.selectAll("*").remove();

    // arrows for directed edges
    svg.append("defs").append("marker")
        .attr("id", "arrowhead-block")
        .attr("viewBox", "-0 -5 10 10")
        .attr("refX", 25)
        .attr("refY", 0)
        .attr("orient", "auto")
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("xoverflow", "visible")
        .append("svg:path")
        .attr("d", "M 0,-5 L 10 ,0 L 0,5")
        .attr("fill", "#999")
        .style("stroke", "none");

    // zoom and pan
    const g = svg.append("g").attr("class", "zoom-group");

    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoom);

    // force simulation
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(edges)
            .id(d => d.id)
            .distance(300)
        )
        .force("charge", d3.forceManyBody().strength(-500))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(d => d.height / 2 + 20))
        .force("x", d3.forceX(width / 2).strength(0.05))
        .force("y", d3.forceY(height / 2).strength(0.05));

    // edges - lines
    const link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(edges)
        .enter().append("line")
        .attr("class", d => d.directed ? "link-line directed" : "link-line")
        .attr("marker-end", d => d.directed ? "url(#arrowhead-block)" : null);

    // edges - labels (edge attributes)
    const linkText = g.append("g")
        .attr("class", "link-labels")
        .selectAll("text")
        .data(edges)
        .enter().append("text")
        .attr("class", "link-text")
        .attr("text-anchor", "middle")
        .attr("dy", -5)
        .attr("font-size", "9px")
        .attr("fill", "#333")
        .attr("stroke", "white")
        .attr("stroke-width", "0.5")
        .text(d => {
            // Show edge attributes
            if (d.attributes) {
                if (d.attributes.type) return d.attributes.type;
                if (d.attributes.odnos) return d.attributes.odnos;
                // Show first attribute if exists
                const firstKey = Object.keys(d.attributes)[0];
                if (firstKey) return d.attributes[firstKey];
            }
            return "";
        });

    // nodes
    const node = g.append("g")
        .attr("class", "nodes")
        .selectAll(".node-group")
        .data(nodes)
        .enter().append("g")
        .attr("class", "node-group")
        .attr("data-node-id", d => d.id)
        .call(d3.drag()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded));

    // rectangle for each node
    node.append("rect")
        .attr("class", "node-rect")
        .attr("width", d => 160)
        .attr("height", d => d.height)
        .attr("x", -80)
        .attr("y", d => -d.height / 2)
        .attr("rx", 8)
        .attr("ry", 8);

    // ID node
    node.append("text")
        .attr("class", "node-text node-id")
        .attr("x", 0)
        .attr("y", d => -d.height / 2 + 20)
        .text(d => d.id);

    // Attributes
    node.each(function(d) {
        const group = d3.select(this);
        const attrs = d.attributes;
        let yOffset = -d.height / 2 + 40;

        Object.entries(attrs).forEach(([key, value]) => {
            const displayValue = value.length > 15 ? value.substring(0, 12) + '...' : value;

            group.append("text")
                .attr("class", "node-text")
                .attr("x", 0)
                .attr("y", yOffset)
                .text(`${key}: ${displayValue}`);
            yOffset += 18;
        });
    });

    // interactions
    node.on("click", function(event, d) {
        event.stopPropagation();

        d3.selectAll(".node-rect").classed("selected", false);
        d3.select(this).select(".node-rect").classed("selected", true);

        window.dispatchEvent(new CustomEvent('nodeSelected', {
            detail: { nodeId: d.id }
        }));
    });

    // click on background to deselect
    svg.on("click", function() {
        d3.selectAll(".node-rect").classed("selected", false);
        window.dispatchEvent(new CustomEvent('nodeDeselected'));
    });

    // drag
    function dragStarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // tick - update positions for links, link labels and nodes
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        linkText
            .attr("x", d => (d.source.x + d.target.x) / 2)
            .attr("y", d => (d.source.y + d.target.y) / 2);

        node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // resize
    window.addEventListener('resize', () => {
        const newWidth = container.clientWidth;
        const newHeight = container.clientHeight;

        svg.attr("width", newWidth).attr("height", newHeight);
        simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));
        simulation.alpha(0.3).restart();
    });

    // initial zoom
    setTimeout(() => {
        svg.call(zoom.transform, d3.zoomIdentity.translate(50, 50).scale(0.8));
    }, 100);
})();