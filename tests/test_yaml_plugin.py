import pytest
import yaml

from api.models.graph import GraphBuilder, Graph
from plugins.yaml_data_source_plugin import YAMLSource


class TestYAMLSource:
    """
    Tests for YAMLSource class.
    """

    @pytest.fixture
    def yaml_source(self):
        """Fixture that creates a YAMLSource instance with a mock GraphBuilder"""
        return YAMLSource(GraphBuilder)

    @pytest.fixture
    def valid_yaml_content(self):
        """Fixture with valid YAML content"""
        return """
            nodes:
              - id: node1
                label: Node 1
                weight: 10
              - id: node2
                label: Node 2
                weight: 20
            edges:
              - id: edge1
                source: node1
                target: node2
                weight: 5
                label: Connection
            """

    def test_get_name(self, yaml_source):
        """Test: Check if plugin returns correct plugin name"""
        assert yaml_source.get_name() == "yaml_source"

    def test_file_not_found(self, yaml_source):
        """Test: File not found"""
        # Expect raises FileNotFoundError
        with pytest.raises(FileNotFoundError):
            yaml_source.parse('nonexistent_file.yaml')

    def test_invalid_yaml(self, yaml_source, tmp_path):
        """Test: Invalid YAML content"""
        # Setup malformed data
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("nodes: [unclosed list")

        # Expect raises yaml.YAMLError
        with pytest.raises(yaml.YAMLError):
            yaml_source.parse(str(yaml_file))

    def test_parse_valid_yaml(self, yaml_source, valid_yaml_content, tmp_path):
        """Test: Parse a valid YAML file"""
        # Create temporary YAML file
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(valid_yaml_content)

        # Parse the file
        graph = yaml_source.parse(str(yaml_file))

        # Expect graph to be a Graph instance
        assert isinstance(graph, Graph)
        # Expect 2 nodes and 1 edge
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1

        # Verify properties
        node1 = graph.get_node('node1')
        assert node1.id == 'node1'
        assert node1.attributes['label'] == 'Node 1'
        assert node1.attributes['weight'] == 10

        node2 = graph.get_node('node2')
        assert node2.id == 'node2'
        assert node2.attributes['label'] == 'Node 2'
        assert node2.attributes['weight'] == 20

        edge = list(graph.edges.values())[0]
        assert edge.id == 'edge1'
        assert edge.source == 'node1'
        assert edge.target == 'node2'
        assert edge.attributes['weight'] == 5
        assert edge.attributes['label'] == 'Connection'
