class Edge:
    def __init__(self, edge_id: str, source_id: str, target_id: str, attributes: dict[str, any]):
        self.id = edge_id
        self.source = source_id
        self.target = target_id
        self.attributes = attributes

    def __repr__(self):
        return f"Edge(id={self.id}, {self.source}->{self.target}\nattributes={self.attributes})"