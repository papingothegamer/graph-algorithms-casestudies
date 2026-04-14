# Case Study 4: Software Dependency Resolver

**Thesis chapter:** 13
**Script:** `case_study_4_deps/dependency_resolver.py`
**Run:** `python -m case_study_4_deps.dependency_resolver`

---

## Overview

Models a software package manager resolving an 18-package web application
ecosystem. Uses DFS-based topological sort to determine a valid installation
order, and BFS reachability to discover all transitive dependencies of a
selected package. Demonstrates cycle detection when a circular dependency
is injected.

This is the case study where DFS plays its most important role in the thesis.
While DFS is unsuitable for optimal pathfinding, it is the canonical algorithm
for topological ordering and the only algorithm that detects cycles efficiently
in O(|V|+|E|) time as a byproduct of the sort itself.

---

## Graph Model

| Property | Value |
|---|---|
| Structure | Directed Acyclic Graph (DAG) |
| Vertices | 18 software packages |
| Edges | 29 directed dependency edges |
| Weights | None -- structural ordering problem only |

Edge direction: A -> B means "A depends on B" (B must be installed first).

Layers:
| Layer | Packages | Color |
|---|---|---|
| Application | WebApp, APIServer, AdminPanel | Blue |
| Framework | Flask, Django, FastAPI | Teal |
| ORM / DB | SQLAlchemy, Psycopg2, Redis-py | Purple |
| Utility | JWT-lib, Bcrypt, Requests, Werkzeug, Jinja2, Pydantic | Orange |
| Low-level | OpenSSL, LibC, CFfi | Brown |

---

## Algorithms Used

| Algorithm | Role | Complexity |
|---|---|---|
| DFS topological sort | Valid installation order + cycle detection | O(V+E) |
| BFS reachability | Transitive dependency discovery by depth | O(V+E) |

### Three-color DFS cycle detection

| Color | Meaning |
|---|---|
| WHITE | Not yet visited |
| GRAY | Currently on the DFS stack (in progress) |
| BLACK | Fully processed (all descendants explored) |

A cycle is detected when DFS encounters a GRAY node -- a back-edge to a
node still on the active stack, indicating a circular dependency.

---

## Architecture and Core Integration

```python
from core.algorithms import topological_sort, bfs_reachability
from core.utils import build_dag, timed

graph = build_dag(PACKAGES, edges)
(order, log, has_cycle), ms  = timed(topological_sort, graph)
(order, levels), ms          = timed(bfs_reachability, graph, package)
```

---

## How to Run

```bash
python -m case_study_4_deps.dependency_resolver
```

---

## What to Observe

- **Topological Sort:** Click to see the numbered install order overlaid
  on each node. Low-level packages (LibC, CFfi, OpenSSL) appear first.
  Application layer (WebApp, APIServer, AdminPanel) appears last.
- **Transitive Deps (WebApp):** Should show 14 transitive dependencies
  across 3 depth levels:
  - Depth 1: Flask, SQLAlchemy, Redis-py, JWT-lib
  - Depth 2: Werkzeug, Jinja2, Psycopg2, Requests, Bcrypt, CFfi
  - Depth 3: OpenSSL, LibC
- **Inject Cycle:** Adds CFfi->WebApp edge (shown in red). Run Topological
  Sort -- should detect cycle and show error dialog.
- **Reset:** Removes injected cycle and restores clean DAG state.

---

## Results to Record for Thesis

Topological sort (clean DAG):

| Position | Package |
|---|---|
| 1 | LibC |
| 2 | CFfi |
| 3 | OpenSSL |
| ... | ... |
| 18 | (last app-layer package) |

Record full order from the stats panel.

BFS from WebApp:

| Depth | Packages |
|---|---|
| 1 | Flask, SQLAlchemy, Redis-py, JWT-lib |
| 2 | Werkzeug, Jinja2, Psycopg2, Requests, Bcrypt, CFfi |
| 3 | OpenSSL, LibC |

Screenshot: clean topo sort with numbered nodes, BFS highlight from WebApp,
and cycle detection error dialog after injection.

---

## Connection to Thesis

Corresponds to **Chapter 13**. Demonstrates that DFS is the algorithm of
choice for structural DAG analysis -- a domain where it excels and where
BFS and Dijkstra are not applicable. Connects to real package managers
(pip, npm, apt, cargo) that implement equivalent logic internally.

---

## Key Implementation Decisions

- `topological_sort` in `core/algorithms.py` returns the result in
  dependency-first order (LibC first, application layer last) via DFS
  finish-time reversal. The GUI displays this order directly.
- BFS reachability uses the unweighted DAG adjacency dict -- no weights
  needed since this is a structural, not optimization, problem.
- Cycle injection adds a single back-edge (CFfi->WebApp) which creates
  a cycle via the path CFfi->WebApp->Flask->Werkzeug->CFfi. The three-color
  DFS catches this on the next topological sort run.
