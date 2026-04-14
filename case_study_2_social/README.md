# Case Study 2: Social Network Shortest Path Visualizer

**Thesis chapter:** 11
**Script:** `case_study_2_social/social_network.py`
**Run:** `python -m case_study_2_social.social_network`

---

## Overview

Models a 15-person social network as a weighted undirected graph. Demonstrates
the key distinction between BFS (fewest hops / degrees of separation) and
Dijkstra (strongest-tie path / minimum cumulative weight). Directly illustrates
the "six degrees of separation" concept with a visual node-link diagram.

---

## Graph Model

| Property | Value |
|---|---|
| Structure | Weighted undirected graph |
| Vertices | 15 people |
| Edges | 20 friendship connections |
| Edge weight | Tie strength: 1 (close friends) to 5 (acquaintances) |

BFS ignores weights -- finds the fewest hops between two people.
Dijkstra minimizes cumulative weight -- finds the strongest-tie chain.

---

## Algorithms Used

| Algorithm | Role | Metric |
|---|---|---|
| BFS | Degrees of separation | Hops (unweighted) |
| Dijkstra | Strongest relationship path | Cumulative tie score |

---

## Architecture and Core Integration

```python
from core.algorithms import bfs, dijkstra
from core.utils import build_undirected, timed

graph = build_undirected(PEOPLE, FRIENDSHIPS)
(path, hops, expanded), ms     = timed(bfs, graph, source, target)
(path, cost, expanded), ms     = timed(dijkstra, graph, source, target)
```

---

## How to Run

```bash
python -m case_study_2_social.social_network
```

---

## What to Observe

- **Find Path (BFS):** Highlights the fewest-hop route. Source=Alice,
  Target=Olivia should give Alice->Dave->Iris->Olivia (3 hops).
- **Find Path (Dijkstra):** Highlights the lowest cumulative tie-weight route.
  Same query should give Alice->Dave->Iris->Olivia (cost=6).
- **Compare Both:** Runs both algorithms and draws BFS path on canvas.
  Stats panel shows both results side by side.
- **Divergent paths:** Try Eve->Mia to see BFS and Dijkstra choose
  different routes, demonstrating the weighted vs unweighted distinction.

---

## Results to Record for Thesis

| Query | Algorithm | Path | Hops | Tie Score | Expanded | Time (ms) |
|---|---|---|---|---|---|---|
| Alice->Olivia | BFS | | 3 | -- | | |
| Alice->Olivia | Dijkstra | | -- | 6 | | |
| Eve->Mia | BFS | | | -- | | |
| Eve->Mia | Dijkstra | | | | | |

Screenshot the canvas for Alice->Olivia (both algorithms) and one
divergent-path query for the thesis figures.

---

## Connection to Thesis

Corresponds to **Chapter 11**. Provides a tangible application of unweighted
vs weighted shortest-path logic and connects to the social network analysis
section of Chapter 6 (Practical Applications).

---

## Key Implementation Decisions

- Node positions are hand-tuned to match the thesis diagram layout.
- Edge weights encode tie strength inversely: low cost = close relationship.
  This aligns sociological "strength" with Dijkstra's minimization objective.
- Compare Both always draws the BFS path on canvas after comparison so
  the visual state is not left blank.
