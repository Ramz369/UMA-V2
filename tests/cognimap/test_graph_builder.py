"""Tests for GraphBuilder."""

from cognimap.graph.graph_builder import GraphBuilder


def test_graph_builder_node_count() -> None:
    builder = GraphBuilder()
    graph = builder.build()
    assert len(graph["nodes"]) > 60


def test_graph_builder_relationships() -> None:
    builder = GraphBuilder()
    graph = builder.build()
    assert len(graph["edges"]) > 100


def test_graph_builder_scope_cognimap() -> None:
    full = GraphBuilder()
    subset = GraphBuilder(scope="cognimap")
    graph_full = full.build()
    graph_subset = subset.build()
    assert len(graph_subset["nodes"]) <= len(graph_full["nodes"])
    assert all(n["filepath"].startswith("cognimap/") for n in graph_subset["nodes"])

