# Case Study 3: Network Routing Protocol Simulator

**Thesis chapter:** 12
**Script:** `case_study_3_routing/network_routing.py`
**Run:** `python -m case_study_3_routing.network_routing`

---

## Overview

Simulates packet routing across a 12-router ISP-style network topology.
Models two real-world routing protocols directly:

| Protocol | Algorithm | RFC |
|---|---|---|
| OSPF (Open Shortest Path First) | Dijkstra | RFC 2328 |
| RIP (Routing Information Protocol) | Bellman-Ford | RFC 2453 |

This is the most academically grounded case study in the thesis -- the
algorithms are not analogies for these protocols, they are the literal
algorithmic core as defined in the RFCs.

---

## Graph Model

| Property | Value |
|---|---|
| Structure | Weighted undirected graph |
| Vertices | 12 routers (R1-R12) |
| Edges | 18 bidirectional network links |
| Edge weight | OSPF cost = max(1, int(10^5 / bandwidth_Mbps)) |

| Bandwidth | OSPF Cost | Link Type |
|---|---|---|
| 1000 Mbps | 100 | Backbone |
| 100 Mbps | 1000 | Distribution |
| 10 Mbps | 10000 | Access/slow |

---

## Algorithms Used

| Algorithm | Protocol | Behavior |
|---|---|---|
| Dijkstra | OSPF | Full topology map, single-pass shortest path |
| Bellman-Ford | RIP | Distributed relaxation, returns iteration count |

Note: `bellman_ford` returns `(path, cost, iterations, negative_cycle)`.
Iterations are displayed in the stats panel (not expanded node count).

---

## Architecture and Core Integration

```python
from core.algorithms import dijkstra, bellman_ford
from core.utils import build_undirected, timed

graph = build_undirected(ROUTERS, active_links_with_costs)
(path, cost, expanded), ms          = timed(dijkstra, graph, src, dst)
(path, cost, iters, neg), ms        = timed(bellman_ford, graph, src, dst, nodes=ROUTERS)
```

---

## How to Run

```bash
python -m case_study_3_routing.network_routing
```

---

## What to Observe

- **Route Packet (Both):** R1->R12 should produce identical paths for OSPF
  and RIP: R1->R2->R4->R7->R11->R12, cost=500. OSPF will be significantly
  faster.
- **Routing Table:** Opens a window showing the full OSPF forwarding table
  for the selected source router. Record next-hop and cost for each destination.
- **Link Failure:** Toggle R7<->R11 as failed, then re-run routing. Both
  protocols should reroute. Record the new path and cost increase.
- **Protocol speed gap:** Compare OSPF vs RIP execution time. The ratio
  demonstrates Dijkstra's O((V+E)logV) vs Bellman-Ford's O(VE) at scale.

---

## Results to Record for Thesis

Static topology R1->R12:

| Protocol | Path | Hops | Cost | Time (ms) |
|---|---|---|---|---|
| OSPF (Dijkstra) | | 5 | 500 | |
| RIP (Bellman-Ford) | | 5 | 500 | |

After failing link R7<->R11:

| Protocol | New Path | New Cost | Time (ms) |
|---|---|---|---|
| OSPF (Dijkstra) | | | |
| RIP (Bellman-Ford) | | | |

Screenshot: normal routing, and post-failure rerouting.
Screenshot the Routing Table window for R1.

---

## Connection to Thesis

Corresponds to **Chapter 12**. Grounds graph algorithm theory in RFC-defined
networking protocols, directly satisfying the thesis requirement to connect
algorithmic analysis to production deployed systems.

---

## Key Implementation Decisions

- OSPF cost formula: `max(1, int(1e5 / bw_mbps))` -- bandwidth input is
  in Mbps, so the Cisco formula (10^8 / bps) simplifies to 10^5 / Mbps.
  This gives: 1000 Mbps=100, 100 Mbps=1000, 10 Mbps=10000.
- `bellman_ford` is called with `nodes=ROUTERS` explicitly to ensure
  the correct |V|-1 iteration bound.
- Failed links are excluded from the graph dict before passing to algorithms,
  keeping the routing logic clean and the failure simulation realistic.
