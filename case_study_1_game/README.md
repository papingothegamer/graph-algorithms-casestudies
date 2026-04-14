# Case Study 1: Open-World Game AI Pathfinding Simulator

**Thesis chapter:** 10
**Script:** `case_study_1_game/simulator.py`
**Run:** `python -m case_study_1_game.simulator`

---

## Overview

Models an open-world game environment where an AI character must navigate
from a start position to a goal across terrain with varying movement costs
and impassable walls. All five algorithms are compared side-by-side on the
same grid, making behavioral differences directly observable.

---

## Graph Model

| Property | Value |
|---|---|
| Structure | 30x30 grid, 4-directional movement |
| Vertices | 900 cells (r, c) |
| Edges | Up to 4 per cell (cardinal neighbors) |
| Edge weight | Cost of entering the destination cell |

| Terrain | Color | Cost | Analogy |
|---|---|---|---|
| Plain | Light green | 1 | Open road |
| Forest | Dark green | 3 | Dense woodland |
| Swamp | Brown | 8 | Boggy terrain |
| Wall | Dark gray | None | Impassable cliff |

---

## Algorithms Used

| Algorithm | Role | Notes |
|---|---|---|
| A* | Primary -- optimal + fast | Manhattan heuristic, admissible on 4-dir grid |
| Dijkstra | Optimal baseline | No heuristic, expands radially |
| BFS | Unweighted baseline | Ignores terrain costs, finds fewest hops |
| DFS | Structural demo | Not optimal, shown for contrast |
| Bellman-Ford | Correctness check | Correct but slow; shows iteration count |

---

## Architecture and Core Integration

```python
from core.algorithms import bfs, dfs, dijkstra, bellman_ford, astar
from core.utils import build_grid, manhattan, timed

graph = build_grid(ROWS, COLS, cost_fn)
(path, cost, expanded), ms = timed(astar, graph, start, goal, heuristic=manhattan)
(path, cost, iterations, neg_cycle), ms = timed(bellman_ford, graph, start, goal, nodes=list(graph.keys()))
```

Note: `bellman_ford` returns 4 values. Iterations are displayed in the
stats panel instead of an expanded node count.

---

## How to Run

```bash
python -m case_study_1_game.simulator
```

---

## What to Observe

- **Terrain routing:** A* and Dijkstra route around swamps via plains.
  BFS cuts straight through (ignores weights).
- **Expansion pattern:** Dijkstra expands in all directions (radial).
  A* expands directionally toward the goal.
- **Compare All:** Shows side-by-side stats for all five algorithms on
  the same map. Record path cost, cells expanded, and time for each.
- **Bellman-Ford:** Noticeably slower on large maps. Iteration count
  visible in stats panel.

---

## Results to Record for Thesis

Run Compare All on the default 30x30 plain grid (start (2,2), goal (27,27)):

| Algorithm | Path Cost | Cells Expanded | Time (ms) | Optimal |
|---|---|---|---|---|
| BFS | | | | No |
| DFS | | | | No |
| Dijkstra | | | | Yes |
| Bellman-Ford | | | | Yes |
| A* | | | | Yes |

Then add a mixed terrain map (walls + swamp patches) and repeat.
Screenshot both states for the thesis figures.

---

## Connection to Thesis

Corresponds to **Chapter 10**. Substantiates the theoretical claims from
Chapters 2-5 regarding A* efficiency with admissible heuristics, and
Bellman-Ford's correctness vs speed tradeoff.

---

## Key Implementation Decisions

- `build_grid()` from `core.utils` constructs the adjacency dict dynamically
  from the live grid state on each algorithm run.
- Manhattan distance is used (not Euclidean) because movement is 4-directional.
  Euclidean would underestimate on this grid and reduce pruning effectiveness.
- `bellman_ford` receives `nodes=list(graph.keys())` explicitly to ensure
  correct iteration count (|V|-1 passes).
