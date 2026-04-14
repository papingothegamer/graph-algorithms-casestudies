"""
Case Study 4: Software Dependency Resolver
==========================================
Run from repo root: python -m case_study_4_deps.dependency_resolver

Thesis reference: Chapter 13
Algorithms: DFS topological sort (installation ordering + cycle detection),
            BFS reachability (transitive dependency discovery)
Graph model: 18-package web-app ecosystem as a DAG
             A -> B means A depends on B (B installed first)

Thesis install order (first and last positions):
  First: LibC, CFfi, OpenSSL (low-level, no dependencies)
  Last:  WebApp, APIServer, AdminPanel (application layer)

Transitive deps of WebApp (BFS):
  Depth 1: Flask, SQLAlchemy, Redis-py, JWT-lib
  Depth 2: Werkzeug, Jinja2, Psycopg2, Requests, Bcrypt, CFfi
  Depth 3: OpenSSL, LibC

Cycle injection: CFfi -> WebApp (detected via GRAY back-edge in DFS)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.algorithms import topological_sort, bfs_reachability
from core.utils import build_dag, timed

# -- Package ecosystem (exact from thesis) ------------------------------------

PACKAGES = [
    'WebApp', 'APIServer', 'AdminPanel',
    'Flask', 'Django', 'FastAPI',
    'SQLAlchemy', 'Psycopg2', 'Redis-py',
    'JWT-lib', 'Bcrypt', 'Requests',
    'Werkzeug', 'Jinja2', 'Pydantic',
    'OpenSSL', 'LibC', 'CFfi',
]

BASE_DEPS = [
    ('WebApp',     'Flask'),
    ('WebApp',     'SQLAlchemy'),
    ('WebApp',     'Redis-py'),
    ('WebApp',     'JWT-lib'),
    ('APIServer',  'FastAPI'),
    ('APIServer',  'Pydantic'),
    ('APIServer',  'SQLAlchemy'),
    ('APIServer',  'JWT-lib'),
    ('AdminPanel', 'Django'),
    ('AdminPanel', 'SQLAlchemy'),
    ('AdminPanel', 'Bcrypt'),
    ('Flask',      'Werkzeug'),
    ('Flask',      'Jinja2'),
    ('Django',     'SQLAlchemy'),
    ('Django',     'Jinja2'),
    ('FastAPI',    'Pydantic'),
    ('FastAPI',    'Werkzeug'),
    ('SQLAlchemy', 'Psycopg2'),
    ('Psycopg2',   'LibC'),
    ('Psycopg2',   'OpenSSL'),
    ('Redis-py',   'Requests'),
    ('JWT-lib',    'Bcrypt'),
    ('JWT-lib',    'CFfi'),
    ('Bcrypt',     'CFfi'),
    ('Requests',   'OpenSSL'),
    ('Werkzeug',   'CFfi'),
    ('Pydantic',   'CFfi'),
    ('CFfi',       'LibC'),
    ('OpenSSL',    'LibC'),
]

PKG_POS = {
    'WebApp':     (120,  40, '#1565c0'),
    'APIServer':  (340,  40, '#1565c0'),
    'AdminPanel': (560,  40, '#1565c0'),
    'Flask':      ( 80, 130, '#00695c'),
    'Django':     (350, 130, '#00695c'),
    'FastAPI':    (560, 130, '#00695c'),
    'SQLAlchemy': (200, 230, '#6a1b9a'),
    'Psycopg2':   (100, 320, '#6a1b9a'),
    'Redis-py':   (480, 230, '#6a1b9a'),
    'JWT-lib':    (350, 230, '#e65100'),
    'Bcrypt':     (390, 320, '#e65100'),
    'Requests':   (560, 320, '#e65100'),
    'Werkzeug':   ( 80, 400, '#e65100'),
    'Jinja2':     (220, 400, '#e65100'),
    'Pydantic':   (490, 400, '#e65100'),
    'OpenSSL':    (180, 490, '#4e342e'),
    'LibC':       (380, 490, '#4e342e'),
    'CFfi':       (540, 490, '#4e342e'),
}

# -- Colours ------------------------------------------------------------------

C_PANEL  = '#263238'
C_TOPO   = '#f9a825'
C_BFS_HL = '#b3e5fc'
C_CYCLE  = '#b71c1c'
C_EDGE   = '#90a4ae'
NODE_W   = 82
NODE_H   = 24
CW, CH   = 680, 560

# -- App ----------------------------------------------------------------------

class DependencyResolverApp:
    def __init__(self, root):
        self.root  = root
        self.root.title('Case Study 4: Software Dependency Resolver')
        self.root.resizable(False, False)

        self.edges       = list(BASE_DEPS)
        self.query_pkg   = tk.StringVar(value='WebApp')
        self._topo_order = []
        self._bfs_nodes  = set()

        self._build_ui()
        self._draw()

    def _build_ui(self):
        panel = tk.Frame(self.root, bg=C_PANEL, width=220)
        panel.pack(side=tk.LEFT, fill=tk.Y)
        panel.pack_propagate(False)

        def lbl(text):
            tk.Label(panel, text=text, bg=C_PANEL, fg='white',
                     font=('Arial', 9, 'bold')).pack(anchor='w', padx=12, pady=(10, 2))

        lbl('Query Package')
        ttk.Combobox(panel, textvariable=self.query_pkg,
                     values=PACKAGES, state='readonly',
                     width=18).pack(padx=12)

        for text, cmd, bg in [
            ('Topological Sort (DFS)',     self._run_topo,  '#1565c0'),
            ('Transitive Deps (BFS)',       self._run_bfs,   '#006064'),
            ('Inject Cycle (CFfi->WebApp)', self._inject,    '#b71c1c'),
            ('Reset',                       self._reset,     '#37474f'),
        ]:
            tk.Button(
                panel, text=text, command=cmd,
                bg=bg, fg='white', width=22,
                font=('Arial', 9), wraplength=180
            ).pack(pady=4, padx=12)

        lbl('Statistics')
        self.stats = tk.StringVar(value='Click an action to begin.')
        tk.Label(
            panel, textvariable=self.stats,
            bg=C_PANEL, fg='#b2dfdb',
            font=('Courier', 8), justify=tk.LEFT,
            wraplength=200
        ).pack(anchor='w', padx=12, pady=4)

        lbl('Layer Legend')
        for label, color in [
            ('Application', '#1565c0'),
            ('Framework',   '#00695c'),
            ('ORM / DB',    '#6a1b9a'),
            ('Utility',     '#e65100'),
            ('Low-level',   '#4e342e'),
            ('Topo order',  C_TOPO),
            ('BFS deps',    C_BFS_HL),
        ]:
            row = tk.Frame(panel, bg=C_PANEL)
            row.pack(anchor='w', padx=12)
            tk.Label(row, bg=color, width=2,
                     relief='solid').pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=label, bg=C_PANEL, fg='white',
                     font=('Arial', 8)).pack(side=tk.LEFT)

        self.canvas = tk.Canvas(
            self.root, width=CW, height=CH, bg='#eceff1')
        self.canvas.pack(side=tk.LEFT, padx=4, pady=4)

    def _draw(self):
        self.canvas.delete('all')
        cycle_edge = ('CFfi', 'WebApp')

        for a, b in self.edges:
            if a not in PKG_POS or b not in PKG_POS:
                continue
            x1, y1, _ = PKG_POS[a]
            x2, y2, _ = PKG_POS[b]
            is_cycle   = (a, b) == cycle_edge
            self.canvas.create_line(
                x1, y1 + NODE_H//2,
                x2, y2 + NODE_H//2,
                fill=C_CYCLE if is_cycle else C_EDGE,
                width=2 if is_cycle else 1,
                arrow=tk.LAST,
                arrowshape=(8, 10, 4))

        for pkg, (x, y, layer_color) in PKG_POS.items():
            if pkg in self._topo_order:
                fill = C_TOPO
            elif pkg in self._bfs_nodes:
                fill = C_BFS_HL
            else:
                fill = layer_color

            self.canvas.create_rectangle(
                x - NODE_W//2, y,
                x + NODE_W//2, y + NODE_H,
                fill=fill, outline='white', width=2)

            label = pkg
            if pkg in self._topo_order:
                idx   = self._topo_order.index(pkg) + 1
                label = f'{idx}. {pkg}'

            text_color = '#263238' if fill in (C_TOPO, C_BFS_HL) else 'white'
            self.canvas.create_text(
                x, y + NODE_H//2,
                text=label,
                font=('Arial', 7, 'bold'),
                fill=text_color)

    def _run_topo(self):
        graph = build_dag(PACKAGES, self.edges)
        (result, log, has_cycle), ms = timed(topological_sort, graph)

        self._bfs_nodes = set()

        if has_cycle:
            self._topo_order = []
            self._draw()
            self.stats.set(
                f'CYCLE DETECTED!\n'
                f'Topological sort\nimpossible on a\ncyclic graph.\n'
                f'Time: {ms:.3f} ms')
            messagebox.showerror(
                'Cycle Detected',
                'A circular dependency exists.\n'
                'Topological sort requires a DAG.\n\n'
                'Remove the injected cycle and retry.')
            return

        self._topo_order = result
        lines = [
            f'Topo Sort (DFS)',
            f'Time     : {ms:.3f} ms',
            f'Packages : {len(result)}',
            f'DFS calls: {len(log)}',
            '',
            'Install order:',
        ]
        for i, pkg in enumerate(result, 1):
            lines.append(f'  {i:>2}. {pkg}')
        self.stats.set('\n'.join(lines))
        self._draw()

    def _run_bfs(self):
        pkg   = self.query_pkg.get()
        graph = build_dag(PACKAGES, self.edges)
        (order, levels), ms = timed(bfs_reachability, graph, pkg)

        self._topo_order = []
        self._bfs_nodes  = set(order)

        max_level = max(levels.values()) if levels else 0
        lines = [
            f'Transitive Deps (BFS)',
            f'Source   : {pkg}',
            f'Time     : {ms:.3f} ms',
            f'Total    : {len(order)-1} deps',
            '',
        ]
        for lvl in range(max_level + 1):
            pkgs   = [p for p, l in levels.items() if l == lvl]
            prefix = 'self' if lvl == 0 else f'depth {lvl}'
            lines.append(f'[{prefix}]')
            lines.append(f'  {", ".join(pkgs)}')
        self.stats.set('\n'.join(lines))
        self._draw()

    def _inject(self):
        cycle_edge = ('CFfi', 'WebApp')
        if cycle_edge in self.edges:
            messagebox.showinfo(
                'Already injected',
                'CFfi -> WebApp is already active.\n'
                'Click Reset to remove it.')
            return
        self.edges.append(cycle_edge)
        self._topo_order = []
        self._bfs_nodes  = set()
        self._draw()
        self.stats.set(
            'Cycle injected:\nCFfi -> WebApp\n\n'
            'Run Topological Sort\nto detect it.')

    def _reset(self):
        self.edges       = list(BASE_DEPS)
        self._topo_order = []
        self._bfs_nodes  = set()
        self._draw()
        self.stats.set('Reset. Click an action to begin.')


if __name__ == '__main__':
    root = tk.Tk()
    DependencyResolverApp(root)
    root.mainloop()
