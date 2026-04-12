"""
core/utils.py
=============
Shared utility functions used across all four case studies.

Includes:
    - Graph builders (weighted undirected, directed, grid)
    - Timing wrapper
    - Result formatter
    - Manhattan and Euclidean heuristics for A*

Author: Toluwanimi Daramola
Thesis: Comparative Analysis of Graph Search and Pathfinding Algorithms
        with Practical Applications
"""

import time
import math


# -- Heuristics (for A*) -------------------------------------------------------

def manhattan(node, goal):
    """
    Manhattan distance heuristic.
    Used for grid graphs with 4-directional movement.

    Args:
        node : (row, col) tuple
        goal : (row, col) tuple

    Returns:
        int : Manhattan distance
    """
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])


def euclidean(node, goal):
    """
    Euclidean distance heuristic.
    Used for grid graphs with 8-directional movement.

    Args:
        node : (row, col) tuple
        goal : (row, col) tuple

    Returns:
        float : Euclidean distance
    """
    return math.sqrt((node[0] - goal[0])**2 + (node[1] - goal[1])**2)


def zero_heuristic(node, goal):
    """
    Zero heuristic. Reduces A* to Dijkstra's algorithm.
    Useful for testing and comparison.
    """
    return 0


# -- Graph builders ------------------------------------------------------------

def build_undirected(nodes, edges):
    """
    Build a weighted undirected adjacency list.

    Args:
        nodes : list of node identifiers
        edges : list of (node_a, node_b, weight) tuples

    Returns:
        dict : {node: [(neighbor, weight), ...]}
    """
    graph = {n: [] for n in nodes}
    for a, b, w in edges:
        graph[a].append((b, w))
        graph[b].append((a, w))
    return graph


def build_directed(nodes, edges):
    """
    Build a weighted directed adjacency list.

    Args:
        nodes : list of node identifiers
        edges : list of (from_node, to_node, weight) tuples

    Returns:
        dict : {node: [(neighbor, weight), ...]}
    """
    graph = {n: [] for n in nodes}
    for a, b, w in edges:
        graph[a].append((b, w))
    return graph


def build_dag(nodes, edges):
    """
    Build an unweighted directed adjacency list (DAG).
    Used for dependency graphs in Case Study 4.

    Args:
        nodes : list of node identifiers
        edges : list of (from_node, to_node) tuples

    Returns:
        dict : {node: [neighbor, ...]}
    """
    graph = {n: [] for n in nodes}
    for a, b in edges:
        graph[a].append(b)
    return graph


def build_grid(rows, cols, cost_fn):
    """
    Build a grid graph with 4-directional movement.
    Used for Case Study 1: Game AI simulator.

    Args:
        rows    : number of rows
        cols    : number of columns
        cost_fn : callable(row, col) -> int/float
                  returns movement cost into cell (row, col)
                  return None or float('inf') for impassable cells

    Returns:
        dict : {(row, col): [((nr, nc), cost), ...]}
    """
    graph = {}
    for r in range(rows):
        for c in range(cols):
            if cost_fn(r, c) is None:
                continue
            neighbors = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    cost = cost_fn(nr, nc)
                    if cost is not None:
                        neighbors.append(((nr, nc), cost))
            graph[(r, c)] = neighbors
    return graph


# -- Timing wrapper ------------------------------------------------------------

def timed(fn, *args, **kwargs):
    """
    Run a function and return its result alongside execution time in ms.

    Args:
        fn   : callable to time
        args : positional arguments for fn
        kwargs : keyword arguments for fn

    Returns:
        result  : return value of fn(*args, **kwargs)
        elapsed : execution time in milliseconds (float)
    """
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = (time.perf_counter() - t0) * 1000
    return result, elapsed


# -- Result formatter ----------------------------------------------------------

def format_result(algorithm, path, cost, expanded, elapsed_ms, extra=None):
    """
    Format algorithm results into a consistent display string.
    Used by the stats panels in all four case study GUIs.

    Args:
        algorithm  : str  name of the algorithm
        path       : list of nodes
        cost       : numeric cost or hop count
        expanded   : list of expanded nodes
        elapsed_ms : float execution time in ms
        extra      : optional dict of additional fields {label: value}

    Returns:
        str : formatted multi-line result string
    """
    lines = [
        f'Algorithm : {algorithm}',
        f'Path      : {" -> ".join(str(n) for n in path) if path else "No path found"}',
        f'Cost      : {cost}',
        f'Hops      : {len(path) - 1 if path else "-"}',
        f'Expanded  : {len(expanded)} nodes',
        f'Time      : {elapsed_ms:.3f} ms',
    ]
    if extra:
        for label, value in extra.items():
            lines.append(f'{label:<10}: {value}')
    return '\n'.join(lines)


# -- Path cost calculator ------------------------------------------------------

def path_cost(graph, path):
    """
    Calculate the total cost of a path through a weighted graph.

    Args:
        graph : dict {node: [(neighbor, weight), ...]}
        path  : list of nodes

    Returns:
        float : total edge weight along the path
                returns float('inf') if any edge is missing
    """
    if not path or len(path) < 2:
        return 0
    total = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge = next((w for nb, w in graph.get(u, []) if nb == v), None)
        if edge is None:
            return float('inf')
        total += edge
    return total
