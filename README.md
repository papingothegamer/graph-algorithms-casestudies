# Graph Search and Pathfinding Algorithms: Practical Case Studies

This repository contains the four interactive case study applications developed
for the Master's thesis:

> **Comparative Analysis of Graph Search and Pathfinding Algorithms
> with Practical Applications**

**Author:** Toluwanimi Daramola
**Institution:** University of Lodz, Faculty of Mathematics and Computer Science
**Supervisor:** dr hab. Liudmyla Koliechkina, prof. UL
**Exam Topic:** 27 -- Graph pathfinding algorithms

---

## Thesis Context

This repository maps directly to **Chapters 9-13** of the thesis (Phase 2 and
Phase 3). All five algorithms studied in the thesis are implemented from scratch
in pure Python (standard library only) inside the shared `core/` module, then
applied across four distinct real-world domains.

---

## Repository Structure

| Path | Description |
|---|---|
| `core/algorithms.py` | BFS, DFS, Dijkstra, Bellman-Ford, A*, topological sort, BFS reachability |
| `core/utils.py` | Graph builders, heuristics, timing wrapper, result formatter |
| `case_study_1_game/` | Open-world game AI pathfinding simulator |
| `case_study_2_social/` | Social network shortest path visualizer |
| `case_study_3_routing/` | Network routing protocol simulator (OSPF vs RIP) |
| `case_study_4_deps/` | Software dependency resolver |

---

## Algorithm to Case Study Mapping

| Case Study | Domain | Algorithms | Thesis Chapter |
|---|---|---|---|
| 1: Game AI | 2D weighted grid | BFS, DFS, Dijkstra, Bellman-Ford, A* | Chapter 10 |
| 2: Social Network | Weighted undirected graph | BFS, Dijkstra | Chapter 11 |
| 3: Network Routing | ISP topology | Dijkstra (OSPF), Bellman-Ford (RIP) | Chapter 12 |
| 4: Dependency Resolver | DAG | DFS topological sort, BFS reachability | Chapter 13 |

---

## How to Run

Requires Python 3.8+. No pip installs needed -- all dependencies are stdlib.

Run each script as a module from the repo root:

```bash
python -m case_study_1_game.simulator
python -m case_study_2_social.social_network
python -m case_study_3_routing.network_routing
python -m case_study_4_deps.dependency_resolver
```

Verify core imports first:

```bash
python -c "from core import algorithms, utils; print('core OK')"
```

---

## Core Module

All case studies import exclusively from `core/`. No algorithm logic is
duplicated across scripts.

`core/algorithms.py` exposes consistent interfaces:
- `bfs(graph, start, goal)` -> `(path, hops, expanded)`
- `dfs(graph, start, goal)` -> `(path, cost, expanded)`
- `dijkstra(graph, start, goal)` -> `(path, cost, expanded)`
- `bellman_ford(graph, start, goal, nodes)` -> `(path, cost, iterations, negative_cycle)`
- `astar(graph, start, goal, heuristic)` -> `(path, cost, expanded)`
- `topological_sort(graph)` -> `(order, log, has_cycle)`
- `bfs_reachability(graph, start)` -> `(order, levels)`

`core/utils.py` exposes:
- `build_undirected(nodes, edges)`
- `build_dag(nodes, edges)`
- `build_grid(rows, cols, cost_fn)`
- `manhattan(node, goal)` / `euclidean(node, goal)`
- `timed(fn, *args, **kwargs)` -> `(result, elapsed_ms)`
