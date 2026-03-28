/* This class represents an observer in the Observer pattern for the graph */
class MainViewObserver {
    constructor(graphSubject) {
        this.graphSubject = graphSubject;
        this.container = document.querySelector('.main-view-container');
    }

    // Add all necessary checks and error handling to make sure the graph data is valid before trying to render it

    update() {
        // this should be used via getter
        this.graph = this.graphSubject.presentedGraph;
        this._render();
    }

    _render() {
        this._clear();
        //TODO: render graph in the container using this.graph data
    }

    _clear() {
        this.container.innerHTML = '';
    }
}
