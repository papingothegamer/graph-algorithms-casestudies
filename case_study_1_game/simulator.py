"""
Case Study 1: Open-World Game AI Pathfinding Simulator
=======================================================
Run from repo root: python -m case_study_1_game.simulator

Thesis reference: Chapter 10
Algorithms: BFS, DFS, Dijkstra, Bellman-Ford, A* (all via core.algorithms)
Graph model: 30x30 weighted grid, 4-directional movement
Terrain costs: Plain=1, Forest=3, Swamp=8, Wall=None (impassable)
"""

import tkinter as tk
from tkinter import ttk
from core.algorithms import bfs, dfs, dijkstra, bellman_ford, astar
from core.utils import build_grid, manhattan, timed

# -- Constants -----------------------------------------------------------------
ROWS, COLS  = 30, 30
CELL_SIZE   = 22

TERRAIN_COSTS = {
    'Plain':  1,
    'Forest': 3,
    'Swamp':  8,
    'Wall':   None,
    'Start':  1,
    'Goal':   1,
}

TERRAIN_COLORS = {
    'Plain':  '#c8e6c9',
    'Forest': '#2e7d32',
    'Swamp':  '#795548',
    'Wall':   '#263238',
    'Start':  '#1565c0',
    'Goal':   '#b71c1c',
}

C_PATH     = '#f9a825'
C_EXPANDED = '#b3e5fc'
C_PANEL    = '#263238'

# -- App -----------------------------------------------------------------------

class GameSimulatorApp:
    def __init__(self, root):
        self.root  = root
        self.root.title('Case Study 1: Game AI Pathfinding Simulator')
        self.root.resizable(False, False)

        self.grid_data   = {(r, c): 'Plain' for r in range(ROWS) for c in range(COLS)}
        self.start_node  = (2, 2)
        self.goal_node   = (27, 27)
        self.current_tool  = tk.StringVar(value='Wall')
        self.selected_algo = tk.StringVar(value='A*')
        self.path_nodes    = []
        self.expanded_nodes = []

        self._build_ui()
        self._draw_grid()

    def _build_ui(self):
        panel = tk.Frame(self.root, bg=C_PANEL, width=260)
        panel.pack(side=tk.LEFT, fill=tk.Y)
        panel.pack_propagate(False)

        def lbl(text):
            tk.Label(panel, text=text, bg=C_PANEL, fg='white',
                     font=('Arial', 9, 'bold')).pack(anchor='w', padx=12, pady=(10, 2))

        lbl('Draw Tool')
        for tool in ['Start', 'Goal', 'Plain', 'Forest', 'Swamp', 'Wall']:
            tk.Radiobutton(
                panel, text=tool, variable=self.current_tool, value=tool,
                bg=C_PANEL, fg='white', selectcolor='#37474f',
                activebackground=C_PANEL, font=('Arial', 9)
            ).pack(anchor='w', padx=20)

        lbl('Algorithm')
        ttk.Combobox(
            panel, textvariable=self.selected_algo,
            values=['BFS', 'DFS', 'Dijkstra', 'Bellman-Ford', 'A*'],
            state='readonly', width=20
        ).pack(padx=12, pady=2)

        for text, cmd in [
            ('Run Selected',  self._run),
            ('Compare All',   self._compare_all),
            ('Clear Path',    self._clear_path),
            ('Reset Map',     self._reset_map),
        ]:
            tk.Button(
                panel, text=text, command=cmd,
                bg='#37474f', fg='white', width=22,
                font=('Arial', 9)
            ).pack(pady=3, padx=12)

        lbl('Statistics')
        self.stats_text = tk.Text(
            panel, height=16, width=30,
            bg='#1e272e', fg='#00e676',
            font=('Courier', 8), relief='flat'
        )
        self.stats_text.pack(padx=10, pady=4)

        lbl('Legend')
        for label, color in [
            ('Plain (cost 1)',  '#c8e6c9'),
            ('Forest (cost 3)', '#2e7d32'),
            ('Swamp (cost 8)',  '#795548'),
            ('Wall (blocked)',  '#263238'),
            ('Path',            C_PATH),
            ('Explored',        C_EXPANDED),
        ]:
            row = tk.Frame(panel, bg=C_PANEL)
            row.pack(anchor='w', padx=12)
            tk.Label(row, bg=color, width=2, relief='solid').pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=label, bg=C_PANEL, fg='white', font=('Arial', 8)).pack(side=tk.LEFT)

        self.canvas = tk.Canvas(
            self.root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE, bg='#37474f'
        )
        self.canvas.pack(side=tk.LEFT, padx=6, pady=6)
        self.canvas.bind('<Button-1>',  self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)

    def _cell_color(self, r, c):
        node = (r, c)
        if node == self.start_node:   return TERRAIN_COLORS['Start']
        if node == self.goal_node:    return TERRAIN_COLORS['Goal']
        if node in self.path_nodes:   return C_PATH
        if node in self.expanded_nodes: return C_EXPANDED
        return TERRAIN_COLORS[self.grid_data[node]]

    def _draw_grid(self):
        self.canvas.delete('all')
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                self.canvas.create_rectangle(
                    x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                    fill=self._cell_color(r, c), outline='#455a64', width=1
                )

    def _paint_cell(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return
        tool = self.current_tool.get()
        node = (r, c)
        if tool == 'Start':
            self.start_node = node
        elif tool == 'Goal':
            self.goal_node = node
        else:
            if node not in (self.start_node, self.goal_node):
                self.grid_data[node] = tool
        self._draw_grid()

    def _on_click(self, event): self._paint_cell(event)
    def _on_drag(self, event):  self._paint_cell(event)

    def _cost_fn(self, r, c):
        if (r, c) in (self.start_node, self.goal_node):
            return 1
        return TERRAIN_COSTS[self.grid_data.get((r, c), 'Wall')]

    def _run_algo(self, algo_name):
        graph = build_grid(ROWS, COLS, self._cost_fn)
        start = self.start_node
        goal  = self.goal_node

        if algo_name == 'BFS':
            (path, hops, expanded), ms = timed(bfs, graph, start, goal)
            cost = hops
            exp_count = len(expanded)
            extra = {'Hops': hops}

        elif algo_name == 'DFS':
            (path, cost, expanded), ms = timed(dfs, graph, start, goal)
            exp_count = len(expanded)
            extra = {}

        elif algo_name == 'Dijkstra':
            (path, cost, expanded), ms = timed(dijkstra, graph, start, goal)
            exp_count = len(expanded)
            extra = {}

        elif algo_name == 'Bellman-Ford':
            (path, cost, iterations, neg_cycle), ms = timed(
                bellman_ford, graph, start, goal,
                nodes=list(graph.keys())
            )
            expanded  = path
            exp_count = iterations
            extra     = {'Iterations': iterations, 'Neg cycle': neg_cycle}

        elif algo_name == 'A*':
            (path, cost, expanded), ms = timed(
                astar, graph, start, goal, heuristic=manhattan
            )
            exp_count = len(expanded)
            extra = {}

        else:
            return 'Unknown algorithm.', [], []

        lines = [
            f'Algorithm : {algo_name}',
            f'Path cost : {cost}',
            f'Path len  : {len(path) - 1 if path else "-"} hops',
            f'Expanded  : {exp_count}',
            f'Time      : {ms:.3f} ms',
        ]
        for k, v in extra.items():
            lines.append(f'{k:<10}: {v}')
        if not path:
            lines.append('Result    : NO PATH FOUND')

        return '\n'.join(lines), path, expanded if isinstance(expanded, list) else []

    def _run(self):
        algo = self.selected_algo.get()
        stats, path, expanded = self._run_algo(algo)
        self.path_nodes     = path
        self.expanded_nodes = expanded
        self._draw_grid()
        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert(tk.END, stats)

    def _compare_all(self):
        self._clear_path()
        results = []
        for algo in ['BFS', 'DFS', 'Dijkstra', 'Bellman-Ford', 'A*']:
            stats, _, _ = self._run_algo(algo)
            results.append(stats)
        self.stats_text.delete('1.0', tk.END)
        sep = '\n' + '-' * 28 + '\n'
        self.stats_text.insert(tk.END, sep.join(results))

    def _clear_path(self):
        self.path_nodes     = []
        self.expanded_nodes = []
        self._draw_grid()

    def _reset_map(self):
        self.grid_data  = {(r, c): 'Plain' for r in range(ROWS) for c in range(COLS)}
        self.start_node = (2, 2)
        self.goal_node  = (27, 27)
        self._clear_path()


if __name__ == '__main__':
    root = tk.Tk()
    GameSimulatorApp(root)
    root.mainloop()
