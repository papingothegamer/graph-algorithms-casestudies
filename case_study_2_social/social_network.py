"""
Case Study 2: Social Network Shortest Path Visualizer
======================================================
Run from repo root: python -m case_study_2_social.social_network

Thesis reference: Chapter 11
Algorithms: BFS (fewest hops / degrees of separation),
            Dijkstra (strongest-tie / minimum cumulative weight)
Graph model: 15-person weighted undirected graph, 20 edges
Edge weights: 1 (close friends) to 5 (distant acquaintances)

Thesis table (Alice -> Olivia):
  BFS:      Alice -> Dave -> Iris -> Olivia  hops=3  cost=6  expanded=7
  Dijkstra: Alice -> Dave -> Iris -> Olivia  hops=3  cost=6  expanded=9
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.algorithms import bfs, dijkstra
from core.utils import build_undirected, timed

# -- Network data (exact from thesis) -----------------------------------------

PEOPLE = [
    'Alice', 'Bob', 'Carol', 'Dave', 'Eve',
    'Frank', 'Grace', 'Hank', 'Iris', 'Jack',
    'Karen', 'Leo', 'Mia', 'Noah', 'Olivia'
]

FRIENDSHIPS = [
    ('Alice',  'Bob',    1),
    ('Alice',  'Carol',  2),
    ('Alice',  'Dave',   3),
    ('Bob',    'Eve',    1),
    ('Bob',    'Frank',  2),
    ('Bob',    'Grace',  5),
    ('Carol',  'Grace',  1),
    ('Carol',  'Hank',   4),
    ('Dave',   'Iris',   2),
    ('Dave',   'Noah',   3),
    ('Eve',    'Jack',   3),
    ('Frank',  'Karen',  1),
    ('Frank',  'Leo',    2),
    ('Grace',  'Mia',    1),
    ('Hank',   'Noah',   3),
    ('Iris',   'Olivia', 1),
    ('Jack',   'Karen',  2),
    ('Karen',  'Mia',    4),
    ('Leo',    'Mia',    3),
    ('Noah',   'Olivia', 2),
]

NODE_POS = {
    'Alice':  (300,  55),
    'Bob':    (155, 140),
    'Carol':  (445, 140),
    'Dave':   (290, 195),
    'Eve':    ( 75, 240),
    'Frank':  (175, 300),
    'Grace':  (465, 260),
    'Hank':   (535, 155),
    'Iris':   (355, 300),
    'Jack':   ( 85, 375),
    'Karen':  (218, 400),
    'Leo':    (315, 425),
    'Mia':    (445, 385),
    'Noah':   (545, 340),
    'Olivia': (475, 460),
}

# -- Colours ------------------------------------------------------------------

C_PANEL   = '#263238'
C_DEFAULT = '#546e7a'
C_SOURCE  = '#1565c0'
C_TARGET  = '#b71c1c'
C_PATH    = '#f9a825'
C_EXPAND  = '#b3e5fc'
C_EDGE    = '#b0bec5'
C_EDGE_P  = '#f9a825'
NODE_R    = 22
CW, CH    = 640, 520

# -- App ----------------------------------------------------------------------

class SocialNetworkApp:
    def __init__(self, root):
        self.root   = root
        self.root.title('Case Study 2: Social Network Shortest Path')
        self.root.resizable(False, False)

        self.graph  = build_undirected(PEOPLE, FRIENDSHIPS)
        self.source = tk.StringVar(value='Alice')
        self.target = tk.StringVar(value='Olivia')
        self.algo   = tk.StringVar(value='BFS')

        self._path     = []
        self._expanded = []

        self._build_ui()
        self._draw([], [])

    def _build_ui(self):
        panel = tk.Frame(self.root, bg=C_PANEL, width=220)
        panel.pack(side=tk.LEFT, fill=tk.Y)
        panel.pack_propagate(False)

        def lbl(text):
            tk.Label(panel, text=text, bg=C_PANEL, fg='white',
                     font=('Arial', 9, 'bold')).pack(anchor='w', padx=12, pady=(10, 2))

        lbl('Source Person')
        ttk.Combobox(panel, textvariable=self.source,
                     values=PEOPLE, state='readonly', width=18).pack(padx=12)

        lbl('Target Person')
        ttk.Combobox(panel, textvariable=self.target,
                     values=PEOPLE, state='readonly', width=18).pack(padx=12)

        lbl('Algorithm')
        for alg, label in [('BFS',      'BFS - fewest hops'),
                            ('Dijkstra', 'Dijkstra - strongest tie')]:
            tk.Radiobutton(
                panel, text=label, variable=self.algo, value=alg,
                bg=C_PANEL, fg='white', selectcolor='#37474f',
                activebackground=C_PANEL, font=('Arial', 9)
            ).pack(anchor='w', padx=16)

        for text, cmd in [
            ('Find Path',    self._run),
            ('Compare Both', self._compare),
            ('Reset',        self._reset),
        ]:
            tk.Button(
                panel, text=text, command=cmd,
                bg='#37474f', fg='white', width=20,
                font=('Arial', 9)
            ).pack(pady=3, padx=12)

        lbl('Statistics')
        self.stats = tk.StringVar(value='Select source and target,\nthen click Find Path.')
        tk.Label(
            panel, textvariable=self.stats,
            bg=C_PANEL, fg='#b2dfdb',
            font=('Courier', 8), justify=tk.LEFT,
            wraplength=200
        ).pack(anchor='w', padx=12, pady=4)

        lbl('Legend')
        for label, color in [
            ('Source',   C_SOURCE),
            ('Target',   C_TARGET),
            ('On path',  C_PATH),
            ('Explored', C_EXPAND),
            ('Default',  C_DEFAULT),
        ]:
            row = tk.Frame(panel, bg=C_PANEL)
            row.pack(anchor='w', padx=12)
            tk.Label(row, bg=color, width=2,
                     relief='solid').pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=label, bg=C_PANEL, fg='white',
                     font=('Arial', 8)).pack(side=tk.LEFT)

        tk.Label(panel,
                 text='\nWeight: 1=close friends\n5=acquaintances',
                 bg=C_PANEL, fg='#80cbc4',
                 font=('Arial', 8), justify=tk.LEFT
                 ).pack(anchor='w', padx=12)

        self.canvas = tk.Canvas(self.root, width=CW, height=CH, bg='#eceff1')
        self.canvas.pack(side=tk.LEFT, padx=4, pady=4)

    def _draw(self, path, expanded):
        self.canvas.delete('all')

        path_edges = set()
        if path:
            for i in range(len(path) - 1):
                path_edges.add((path[i], path[i+1]))
                path_edges.add((path[i+1], path[i]))

        drawn = set()
        for a, b, w in FRIENDSHIPS:
            if (a, b) in drawn:
                continue
            drawn.add((a, b)); drawn.add((b, a))
            x1, y1 = NODE_POS[a]
            x2, y2 = NODE_POS[b]
            on_p = (a, b) in path_edges
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=C_EDGE_P if on_p else C_EDGE,
                width=3 if on_p else 1)
            mx, my = (x1+x2)//2, (y1+y2)//2
            self.canvas.create_text(
                mx, my - 8, text=str(w),
                font=('Arial', 7), fill='#546e7a')

        src = self.source.get()
        tgt = self.target.get()
        for person, (x, y) in NODE_POS.items():
            if person == src:       c = C_SOURCE
            elif person == tgt:     c = C_TARGET
            elif person in path:    c = C_PATH
            elif person in expanded: c = C_EXPAND
            else:                   c = C_DEFAULT
            self.canvas.create_oval(
                x-NODE_R, y-NODE_R, x+NODE_R, y+NODE_R,
                fill=c, outline='white', width=2)
            self.canvas.create_text(
                x, y, text=person,
                font=('Arial', 7, 'bold'), fill='white')

    def _run(self, algo_override=None, draw=True):
        src = self.source.get()
        tgt = self.target.get()
        if src == tgt:
            messagebox.showwarning('Input error', 'Source and target must differ.')
            return None

        algo_name = algo_override or self.algo.get()

        if algo_name == 'BFS':
            (path, hops, expanded), ms = timed(bfs, self.graph, src, tgt)
            metric_label = f'Hops      : {hops}'
        else:
            (path, cost, expanded), ms = timed(dijkstra, self.graph, src, tgt)
            metric_label = f'Tie score : {cost}'

        if draw:
            self._path     = path
            self._expanded = expanded
            self._draw(path, expanded)

        stats = (
            f'Algorithm : {algo_name}\n'
            f'Path      : {" -> ".join(path) if path else "No path"}\n'
            f'{metric_label}\n'
            f'Degrees   : {len(path)-1 if path else "-"}\n'
            f'Expanded  : {len(expanded)} nodes\n'
            f'Time      : {ms:.3f} ms'
        )

        if draw:
            self.stats.set(stats)

        return stats

    def _compare(self):
        src = self.source.get()
        tgt = self.target.get()
        if src == tgt:
            messagebox.showwarning('Input error', 'Source and target must differ.')
            return

        r1 = self._run('BFS',      draw=False)
        r2 = self._run('Dijkstra', draw=False)

        (bfs_path, _, bfs_exp), _ = timed(bfs, self.graph, src, tgt)
        self._path     = bfs_path
        self._expanded = bfs_exp
        self._draw(bfs_path, bfs_exp)

        self.stats.set(f'{r1}\n{"-" * 24}\n{r2}')

    def _reset(self):
        self._path     = []
        self._expanded = []
        self._draw([], [])
        self.stats.set('Reset. Select source and target.')


if __name__ == '__main__':
    root = tk.Tk()
    SocialNetworkApp(root)
    root.mainloop()
