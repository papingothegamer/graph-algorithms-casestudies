"""
core/algorithms.py
==================
Shared algorithm implementations for all four case studies.
All five algorithms are implemented from scratch with consistent
interfaces: each returns (path, cost_or_metric, expanded_nodes).

Algorithms:
    - BFS   (Breadth-First Search)
    - DFS   (Depth-First Search)
    - Dijkstra
    - Bellman-Ford
    - A*    (A-star)

Author: Toluwanimi Daramola
Thesis: Comparative Analysis of Graph Search and Pathfinding Algorithms
        with Practical Applications
"""

import heapq
from collections import deque


# -- Shared path reconstruction ------------------------------------------------

def reconstruct(pred, start, goal):
    """
    Reconstruct a path from start to goal using a predecessor dictionary.
    Returns an empty list if no path exists.
    """
    if goal not in pred:
        return []
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = pred.get(node)
    path.reverse()
    return path if path and path[0] == start else []


# -- BFS -----------------------------------------------------------------------

def bfs(graph, start, goal):
    """
    Breadth-First Search.
    Finds the shortest path by fewest hops (ignores edge weights).

    Args:
        graph : dict  {node: [(neighbor, weight), ...]}
        start : starting node
        goal  : target node

    Returns:
        path     : list of nodes from start to goal
        hops     : number of edges on the path (int)
        expanded : list of nodes in order of expansion
    """
    pred    = {start: None}
    visited = {start}
    queue   = deque([start])
    expanded = []

    while queue:
        u = queue.popleft()
        expanded.append(u)
        if u == goal:
            break
        for v, _ in graph.get(u, []):
            if v not in visited:
                visited.add(v)
                pred[v] = u
                queue.append(v)

    path = reconstruct(pred, start, goal)
    return path, len(path) - 1 if path else -1, expanded


# -- DFS -----------------------------------------------------------------------

def dfs(graph, start, goal):
    """
    Depth-First Search.
    Finds A path (not necessarily shortest) from start to goal.

    Args:
        graph : dict  {node: [(neighbor, weight), ...]}
        start : starting node
        goal  : target node

    Returns:
        path     : list of nodes from start to goal
        cost     : total edge weight along the found path (int/float)
        expanded : list of nodes in order of visit
    """
    pred    = {start: None}
    visited = {start}
    stack   = [start]
    expanded = []
    edge_w  = {}

    while stack:
        u = stack.pop()
        expanded.append(u)
        if u == goal:
            break
        for v, w in graph.get(u, []):
            if v not in visited:
                visited.add(v)
                pred[v] = u
                edge_w[(u, v)] = w
                stack.append(v)

    path = reconstruct(pred, start, goal)
    cost = sum(edge_w.get((path[i], path[i+1]), 0)
               for i in range(len(path) - 1))
    return path, cost, expanded


# -- Dijkstra ------------------------------------------------------------------

def dijkstra(graph, start, goal):
    """
    Dijkstra's algorithm.
    Finds the minimum-cost path on a graph with non-negative weights.

    Args:
        graph : dict  {node: [(neighbor, weight), ...]}
        start : starting node
        goal  : target node

    Returns:
        path     : list of nodes from start to goal
        cost     : total minimum cost (int/float)
        expanded : list of nodes in settlement order
    """
    dist     = {start: 0}
    pred     = {start: None}
    visited  = set()
    heap     = [(0, start)]
    expanded = []

    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        expanded.append(u)
        if u == goal:
            break
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                pred[v] = u
                heapq.heappush(heap, (nd, v))

    path = reconstruct(pred, start, goal)
    return path, dist.get(goal, float('inf')), expanded


# -- Bellman-Ford --------------------------------------------------------------

def bellman_ford(graph, start, goal, nodes=None):
    """
    Bellman-Ford algorithm.
    Finds shortest path; handles negative edge weights.
    Detects negative cycles.

    Args:
        graph : dict  {node: [(neighbor, weight), ...]}
        start : starting node
        goal  : target node
        nodes : full list of nodes (required for correct iteration count)

    Returns:
        path          : list of nodes from start to goal
        cost          : total minimum cost (int/float)
        iterations    : number of relaxation passes performed (int)
        negative_cycle: True if a negative cycle was detected (bool)
    """
    if nodes is None:
        nodes = list(graph.keys())

    dist = {n: float('inf') for n in nodes}
    pred = {n: None for n in nodes}
    dist[start] = 0

    edges = [(u, v, w) for u in graph for v, w in graph.get(u, [])]

    iterations = 0
    for _ in range(len(nodes) - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] + w < dist.get(v, float('inf')):
                dist[v] = dist[u] + w
                pred[v] = u
                updated = True
        iterations += 1
        if not updated:
            break

    # Negative cycle check
    for u, v, w in edges:
        if dist[u] + w < dist.get(v, float('inf')):
            return [], float('inf'), iterations, True

    path = reconstruct(pred, start, goal)
    return path, dist.get(goal, float('inf')), iterations, False


# -- A* ------------------------------------------------------------------------

def astar(graph, start, goal, heuristic):
    """
    A* search algorithm.
    Finds the optimal path using a heuristic function to guide search.

    Args:
        graph     : dict  {node: [(neighbor, weight), ...]}
        start     : starting node
        goal      : target node
        heuristic : callable(node, goal) -> estimated cost to goal

    Returns:
        path     : list of nodes from start to goal
        cost     : total minimum cost (int/float)
        expanded : list of nodes in order of expansion
    """
    g_cost   = {start: 0}
    pred     = {start: None}
    visited  = set()
    heap     = [(heuristic(start, goal), 0, start)]
    expanded = []

    while heap:
        f, g, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        expanded.append(u)
        if u == goal:
            break
        for v, w in graph.get(u, []):
            ng = g + w
            if ng < g_cost.get(v, float('inf')):
                g_cost[v] = ng
                pred[v]   = u
                heapq.heappush(heap, (ng + heuristic(v, goal), ng, v))

    path = reconstruct(pred, start, goal)
    return path, g_cost.get(goal, float('inf')), expanded


# -- Topological Sort (DFS-based) ----------------------------------------------

def topological_sort(graph):
    """
    DFS-based topological sort for a Directed Acyclic Graph (DAG).
    Used by Case Study 4: Dependency Resolver.

    Args:
        graph : dict  {node: [dependency, ...]}  (unweighted directed edges)

    Returns:
        order     : list of nodes in valid topological order (install order)
        dfs_log   : list of (node, event) where event is 'discover' or 'finish'
        has_cycle : True if a cycle was detected (topological sort impossible)
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color   = {p: WHITE for p in graph}
    result  = []
    log     = []
    cycle   = [False]

    def visit(u):
        if cycle[0]:
            return
        color[u] = GRAY
        log.append((u, 'discover'))
        for v in graph.get(u, []):
            if v not in color:
                continue
            if color[v] == GRAY:
                cycle[0] = True
                log.append((v, 'cycle!'))
                return
            if color[v] == WHITE:
                visit(v)
        color[u] = BLACK
        log.append((u, 'finish'))
        result.append(u)

    for node in graph:
        if color[node] == WHITE and not cycle[0]:
            visit(node)

    if cycle[0]:
        return [], log, True

    result.reverse()
    return result, log, False


# -- BFS reachability (for dependency traversal) -------------------------------

def bfs_reachability(graph, start):
    """
    BFS from start node; returns all reachable nodes with their depth level.
    Used by Case Study 4 for transitive dependency discovery.

    Args:
        graph : dict  {node: [neighbor, ...]}  (unweighted directed edges)
        start : starting node

    Returns:
        order  : list of nodes in BFS order
        levels : dict {node: depth_from_start}
    """
    visited = {start}
    queue   = deque([(start, 0)])
    order   = []
    levels  = {start: 0}

    while queue:
        u, level = queue.popleft()
        order.append(u)
        for v in graph.get(u, []):
            if v not in visited:
                visited.add(v)
                levels[v] = level + 1
                queue.append((v, level + 1))

    return order, levels
