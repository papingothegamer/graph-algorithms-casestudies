"""
Case Study 3: Network Routing Simulator
========================================
Run from repo root: python -m case_study_3_routing.network_routing

Thesis reference: Chapter 12
Algorithms: Dijkstra (models OSPF - RFC 2328),
            Bellman-Ford (models RIP - RFC 2453)
Graph model: 12-router ISP topology, 18 bidirectional links
OSPF cost: max(1, int(10^5 / bandwidth_Mbps))
  1000 Mbps -> cost 100  (backbone)
   100 Mbps -> cost 1000 (distribution)
    10 Mbps -> cost 10000 (access/slow)

Thesis table (R1 -> R12):
  OSPF: R1->R2->R4->R7->R11->R12  hops=5  cost=500
  RIP:  R1->R2->R4->R7->R11->R12  hops=5  cost=500
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.algorithms import dijkstra, bellman_ford
from core.utils import build_undirected, timed

# -- Topology (exact from thesis) ---------------------------------------------

ROUTERS = ['R1','R2','R3','R4','R5','R6',
           'R7','R8','R9','R10','R11','R12']

LINKS_RAW = [
    ('R1',  'R2',  1000),
    ('R1',  'R3',  100),
    ('R2',  'R4',  1000),
    ('R2',  'R5',  100),
    ('R3',  'R5',  10),
    ('R3',  'R6',  100),
    ('R4',  'R7',  1000),
    ('R4',  'R8',  100),
    ('R5',  'R8',  10),
    ('R5',  'R9',  100),
    ('R6',  'R9',  10),
    ('R6',  'R10', 100),
    ('R7',  'R11', 1000),
    ('R8',  'R11', 100),
    ('R9',  'R11', 10),
    ('R9',  'R12', 100),
    ('R10', 'R12', 100),
    ('R11', 'R12', 1000),
]

def ospf_cost(bw_mbps):
    """
    OSPF reference bandwidth formula.
    Cisco convention: cost = 10^8 / bandwidth_bps
    Since input is in Mbps: cost = 10^5 / bw_mbps
      1000 Mbps -> 100, 100 Mbps -> 1000, 10 Mbps -> 10000
    Path R1->R12 via 5 x 1000Mbps links = 5 x 100 = total cost 500
    """
    return max(1, int(1e5 / bw_mbps))

LINKS = [(a, b, ospf_cost(bw)) for a, b, bw in LINKS_RAW]

ROUTER_POS = {
    'R1':  ( 80,  80),
    'R2':  (240,  80),
    'R3':  ( 80, 220),
    'R4':  (380,  80),
    'R5':  (240, 220),
    'R6':  ( 80, 360),
    'R7':  (500,  80),
    'R8':  (380, 220),
    'R9':  (240, 360),
    'R10': ( 80, 480),
    'R11': (500, 220),
    'R12': (380, 480),
}

# -- Colours ------------------------------------------------------------------

C_PANEL  = '#263238'
C_NODE   = '#37474f'
C_EDGE   = '#90a4ae'
C_OSPF   = '#42a5f5'
C_RIP    = '#ef5350'
C_BOTH   = '#8e24aa'
C_FAIL   = '#ff8f00'
NODE_R   = 20
CW, CH   = 620, 580

# -- App ----------------------------------------------------------------------

class NetworkRoutingApp:
    def __init__(self, root):
        self.root  = root
        self.root.title('Case Study 3: Network Routing Simulator')
        self.root.resizable(False, False)

        self.failed_links = set()
        self.src          = tk.StringVar(value='R1')
        self.dst          = tk.StringVar(value='R12')
        self.proto        = tk.StringVar(value='Both')
        self._ospf_path   = []
        self._rip_path    = []

        self._build_ui()
        self._draw([], [])

    def _get_graph(self):
        active = [
            (a, b, c) for a, b, c in LINKS
            if (a, b) not in self.failed_links
            and (b, a) not in self.failed_links
        ]
        return build_undirected(ROUTERS, active)

    def _build_ui(self):
        panel = tk.Frame(self.root, bg=C_PANEL, width=220)
        panel.pack(side=tk.LEFT, fill=tk.Y)
        panel.pack_propagate(False)

        def lbl(text):
            tk.Label(panel, text=text, bg=C_PANEL, fg='white',
                     font=('Arial', 9, 'bold')).pack(anchor='w', padx=12, pady=(10, 2))

        lbl('Source Router')
        ttk.Combobox(panel, textvariable=self.src,
                     values=ROUTERS, state='readonly', width=18).pack(padx=12)

        lbl('Destination Router')
        ttk.Combobox(panel, textvariable=self.dst,
                     values=ROUTERS, state='readonly', width=18).pack(padx=12)

        lbl('Protocol')
        for p in ('OSPF (Dijkstra)', 'RIP (Bellman-Ford)', 'Both'):
            tk.Radiobutton(
                panel, text=p, variable=self.proto, value=p,
                bg=C_PANEL, fg='white', selectcolor='#37474f',
                activebackground=C_PANEL, font=('Arial', 9)
            ).pack(anchor='w', padx=16)

        for text, cmd in [
            ('Route Packet',        self._route),
            ('Routing Table',       self._show_table),
            ('Toggle Link Failure', self._pick_fail),
            ('Reset',               self._reset),
        ]:
            tk.Button(
                panel, text=text, command=cmd,
                bg='#37474f', fg='white', width=20,
                font=('Arial', 9)
            ).pack(pady=3, padx=12)

        lbl('Statistics')
        self.stats = tk.StringVar(
            value='Select source and destination,\nthen click Route Packet.')
        tk.Label(
            panel, textvariable=self.stats,
            bg=C_PANEL, fg='#b2dfdb',
            font=('Courier', 8), justify=tk.LEFT,
            wraplength=200
        ).pack(anchor='w', padx=12, pady=4)

        lbl('Legend')
        for label, color in [
            ('OSPF path',   C_OSPF),
            ('RIP path',    C_RIP),
            ('Both',        C_BOTH),
            ('Failed link', C_FAIL),
            ('Router',      C_NODE),
        ]:
            row = tk.Frame(panel, bg=C_PANEL)
            row.pack(anchor='w', padx=12)
            tk.Label(row, bg=color, width=2,
                     relief='solid').pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=label, bg=C_PANEL, fg='white',
                     font=('Arial', 8)).pack(side=tk.LEFT)

        tk.Label(panel,
                 text='\nCost = 10^5 / bandwidth\n(OSPF metric)',
                 bg=C_PANEL, fg='#80cbc4',
                 font=('Arial', 8), justify=tk.LEFT
                 ).pack(anchor='w', padx=12)

        self.canvas = tk.Canvas(self.root, width=CW, height=CH, bg='#eceff1')
        self.canvas.pack(side=tk.LEFT, padx=4, pady=4)

    def _draw(self, ospf_path, rip_path):
        self.canvas.delete('all')

        ospf_edges = set()
        for i in range(len(ospf_path) - 1):
            ospf_edges.add((ospf_path[i], ospf_path[i+1]))
            ospf_edges.add((ospf_path[i+1], ospf_path[i]))

        rip_edges = set()
        for i in range(len(rip_path) - 1):
            rip_edges.add((rip_path[i], rip_path[i+1]))
            rip_edges.add((rip_path[i+1], rip_path[i]))

        drawn = set()
        for a, b, cost in LINKS:
            if (a, b) in drawn:
                continue
            drawn.add((a, b)); drawn.add((b, a))
            x1, y1 = ROUTER_POS[a]
            x2, y2 = ROUTER_POS[b]
            failed  = ((a, b) in self.failed_links or
                       (b, a) in self.failed_links)
            in_ospf = (a, b) in ospf_edges
            in_rip  = (a, b) in rip_edges

            if failed:
                color, width, dash = C_FAIL, 2, (4, 3)
            elif in_ospf and in_rip:
                color, width, dash = C_BOTH, 4, ()
            elif in_ospf:
                color, width, dash = C_OSPF, 3, ()
            elif in_rip:
                color, width, dash = C_RIP, 3, (6, 3)
            else:
                color, width, dash = C_EDGE, 1, ()

            kw = dict(fill=color, width=width)
            if dash:
                kw['dash'] = dash
            self.canvas.create_line(x1, y1, x2, y2, **kw)
            mx, my = (x1+x2)//2, (y1+y2)//2
            self.canvas.create_text(
                mx+4, my-8, text=str(cost),
                font=('Arial', 7), fill='#546e7a')

        src_r = self.src.get()
        dst_r = self.dst.get()
        for r, (x, y) in ROUTER_POS.items():
            if r == src_r:     outline, ow = C_OSPF, 3
            elif r == dst_r:   outline, ow = C_RIP,  3
            else:              outline, ow = 'white', 2
            self.canvas.create_oval(
                x-NODE_R, y-NODE_R, x+NODE_R, y+NODE_R,
                fill=C_NODE, outline=outline, width=ow)
            self.canvas.create_text(
                x, y, text=r,
                font=('Arial', 8, 'bold'), fill='white')

        labels = []
        if ospf_path:
            labels.append(('OSPF: ' + ' -> '.join(ospf_path), C_OSPF))
        if rip_path:
            labels.append(('RIP:  ' + ' -> '.join(rip_path),  C_RIP))
        for i, (txt, col) in enumerate(labels):
            self.canvas.create_text(
                10, CH - 30 + i*14, anchor='w',
                text=txt, font=('Courier', 8), fill=col)

    def _route(self):
        src, dst = self.src.get(), self.dst.get()
        if src == dst:
            messagebox.showwarning('Input error',
                                   'Source and destination must differ.')
            return

        graph = self._get_graph()
        proto = self.proto.get()
        lines = []
        self._ospf_path = []
        self._rip_path  = []

        if proto in ('OSPF (Dijkstra)', 'Both'):
            (path, cost, expanded), ms = timed(dijkstra, graph, src, dst)
            self._ospf_path = path
            lines += [
                '-- OSPF (Dijkstra) --',
                f'Path      : {" -> ".join(path) if path else "unreachable"}',
                f'Cost      : {cost}',
                f'Hops      : {len(path)-1 if path else "-"}',
                f'Expanded  : {len(expanded)} nodes',
                f'Time      : {ms:.3f} ms',
            ]

        if proto in ('RIP (Bellman-Ford)', 'Both'):
            (path, cost, iters, neg), ms = timed(
                bellman_ford, graph, src, dst, nodes=ROUTERS)
            self._rip_path = path
            if lines:
                lines.append('')
            lines += [
                '-- RIP (Bellman-Ford) --',
                f'Path      : {" -> ".join(path) if path else "unreachable"}',
                f'Cost      : {cost}',
                f'Hops      : {len(path)-1 if path else "-"}',
                f'Iterations: {iters}',
                f'Time      : {ms:.3f} ms',
            ]

        self.stats.set('\n'.join(lines))
        self._draw(self._ospf_path, self._rip_path)

    def _show_table(self):
        src   = self.src.get()
        graph = self._get_graph()

        win = tk.Toplevel(self.root)
        win.title(f'OSPF Routing Table -- {src}')
        win.configure(bg=C_PANEL)

        cols = ('Destination', 'Cost', 'Next Hop', 'Full Path')
        tree = ttk.Treeview(win, columns=cols, show='headings', height=13)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col,
                        width=160 if col == 'Full Path' else 90,
                        anchor='w')

        for r in ROUTERS:
            if r == src:
                continue
            path, cost, _ = dijkstra(graph, src, r)
            next_hop = path[1] if len(path) > 1 else '--'
            tree.insert('', 'end', values=(
                r, cost, next_hop,
                ' -> '.join(path) if path else 'unreachable'))

        tree.pack(padx=10, pady=10)
        tk.Button(win, text='Close', command=win.destroy,
                  bg='#37474f', fg='white').pack(pady=(0, 10))

    def _pick_fail(self):
        win = tk.Toplevel(self.root)
        win.title('Toggle Link Failure')
        win.configure(bg=C_PANEL)
        tk.Label(win, text='Click a link to toggle failed/active:',
                 bg=C_PANEL, fg='white',
                 font=('Arial', 9)).pack(padx=10, pady=(10, 4))

        lb = tk.Listbox(win, width=26, height=20,
                        bg='#37474f', fg='white',
                        selectbackground='#1565c0',
                        font=('Courier', 9))
        lb.pack(padx=10, pady=4)

        link_list = [(a, b) for a, b, _ in LINKS]
        for a, b in link_list:
            tag = ' X' if ((a,b) in self.failed_links or
                           (b,a) in self.failed_links) else ''
            lb.insert(tk.END, f'{a} <-> {b}{tag}')

        def apply():
            sel = lb.curselection()
            if not sel:
                return
            a, b = link_list[sel[0]]
            if (a,b) in self.failed_links or (b,a) in self.failed_links:
                self.failed_links.discard((a, b))
                self.failed_links.discard((b, a))
            else:
                self.failed_links.add((a, b))
            win.destroy()
            self._draw(self._ospf_path, self._rip_path)
            self.stats.set(
                f'Link {a}<->{b} toggled.\n'
                f'Re-run routing to update paths.')

        tk.Button(win, text='Toggle Selected', command=apply,
                  bg=C_FAIL, fg='white',
                  font=('Arial', 9, 'bold')).pack(pady=(4, 10))

    def _reset(self):
        self.failed_links.clear()
        self._ospf_path = []
        self._rip_path  = []
        self._draw([], [])
        self.stats.set('Reset. Select source and destination.')


if __name__ == '__main__':
    root = tk.Tk()
    NetworkRoutingApp(root)
    root.mainloop()
