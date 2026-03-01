class Node:
    def __init__(self, node_id: str, attributes: dict[str, any]):
        self.id = node_id
        self.attributes = attributes

    def __repr__(self):
        return f"Node(id={self.id}, attributes={self.attributes})"
