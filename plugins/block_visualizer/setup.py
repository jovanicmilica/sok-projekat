from setuptools import setup, find_packages

setup(
    name="block_visualizer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.11",
    entry_points={
        "graph_platform.visualizers": [
            "block_visualizer = block_visualizer:BlockVisualizer",
        ],
    },
    package_data={
        "block_visualizer": ["templates/*", "static/*"],
    },
)