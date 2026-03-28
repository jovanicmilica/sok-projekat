class GraphSubject {
    constructor(graph) {
        this.originalGraph = graph; // real state of the graph
        this.presentedGraph = JSON.parse(JSON.stringify(graph)); // state of the graph that is currently presented to the user
        this.filters = []; // list of applied filters
        this.queries = []; // list of applied queries

        // may need more variables
        this.viewState = {
            zoom: 1,
            pan: { x: 0, y: 0 },
            selectedElement: null
        };
        
        this.observers = [];
    }

    attach(observer) {
        this.observers.push(observer);
        observer.update(this.presentedGraph); // send the current graph state to the newly attached observer
    }

    detach(observer) {
        this.observers = this.observers.filter(obs => obs !== observer);
    }

    _notify() {
        this.observers.forEach(observer => {
            try {
                observer.update(this.presentedGraph);
            } catch (error) {
                console.error('Error notifying observer:', error);
            }
        });
    }

    // this should use the function already implemented in the backend to apply filters and queries, not do it in the frontend
    async updatePresentedGraph() {
        //TODO: send request to backend to get the updated graph based on applied filters and queries, 
        //then update this.presentedGraph with the response and call this._notify() to update the visualization
    }

    // 
    async applyFilter(filter) {
        this.filters.push(filter);
        this.updatePresentedGraph();
    }

    async removeFilter(filter) {
        this.filters = this.filters.filter(f => f !== filter);
        await this.updatePresentedGraph();
    }
}