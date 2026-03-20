import tkinter as tk
from tkinter import messagebox, font
import random
import time
import threading

# ─── PALETA DE COLORES ────────────────────────────────────────────────────────
BG_DARK      = "#0d0d1a"
BG_PANEL     = "#12122a"
BG_CARD      = "#1a1a35"
ACCENT_CYAN  = "#00f5ff"
ACCENT_PINK  = "#ff2d78"
ACCENT_GOLD  = "#ffd700"
TEXT_WHITE   = "#e8e8ff"
TEXT_DIM     = "#6666aa"
CELL_HIDDEN  = "#1e1e40"
CELL_HOVER   = "#2a2a55"
CELL_SAFE    = "#0d0d22"
CELL_BORDER  = "#3333660"
MINE_COLOR   = "#ff2d78"
FLAG_COLOR   = "#ffd700"

NUM_COLORS = {
    1: "#00f5ff", 2: "#00ff88", 3: "#ff2d78", 4: "#a855f7",
    5: "#ff6b35", 6: "#00ffcc", 7: "#ff2d78", 8: "#ffffff"
}

DIFFICULTIES = {
    "Fácil":   (9,  9,  10),
    "Medio":   (16, 16, 40),
    "Difícil": (16, 30, 99),
}


# ─── LÓGICA DEL TABLERO ───────────────────────────────────────────────────────
class Board:
    def __init__(self, rows, cols, mines):
        self.rows  = rows
        self.cols  = cols
        self.mines = mines
        self.grid      = [[0]*cols for _ in range(rows)]
        self.revealed  = [[False]*cols for _ in range(rows)]
        self.flagged   = [[False]*cols for _ in range(rows)]
        self.mine_pos  = set()
        self.generated = False

    def generate(self, safe_r, safe_c):
        forbidden = {(safe_r+dr, safe_c+dc)
                     for dr in range(-1,2) for dc in range(-1,2)
                     if 0 <= safe_r+dr < self.rows and 0 <= safe_c+dc < self.cols}
        candidates = [(r,c) for r in range(self.rows) for c in range(self.cols)
                      if (r,c) not in forbidden]
        self.mine_pos = set(random.sample(candidates, min(self.mines, len(candidates))))
        for (r,c) in self.mine_pos:
            self.grid[r][c] = -1
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != -1:
                    self.grid[r][c] = sum(
                        1 for dr in range(-1,2) for dc in range(-1,2)
                        if (r+dr, c+dc) in self.mine_pos)
        self.generated = True

    def reveal(self, r, c):
        """Returns 'mine', 'safe', or 'already'."""
        if self.revealed[r][c] or self.flagged[r][c]:
            return "already"
        if not self.generated:
            self.generate(r, c)
        self.revealed[r][c] = True
        if self.grid[r][c] == -1:
            return "mine"
        if self.grid[r][c] == 0:
            self._flood(r, c)
        return "safe"

    def _flood(self, r, c):
        for dr in range(-1,2):
            for dc in range(-1,2):
                nr, nc = r+dr, c+dc
                if 0<=nr<self.rows and 0<=nc<self.cols and not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                    self.revealed[nr][nc] = True
                    if self.grid[nr][nc] == 0:
                        self._flood(nr, nc)

    def toggle_flag(self, r, c):
        if not self.revealed[r][c]:
            self.flagged[r][c] = not self.flagged[r][c]

    def is_won(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != -1 and not self.revealed[r][c]:
                    return False
        return True

    def count_flags(self):
        return sum(self.flagged[r][c] for r in range(self.rows) for c in range(self.cols))

    def unrevealed_safe(self):
        return [(r,c) for r in range(self.rows) for c in range(self.cols)
                if not self.revealed[r][c] and not self.flagged[r][c] and self.grid[r][c] != -1]

    def unrevealed_any(self):
        return [(r,c) for r in range(self.rows) for c in range(self.cols)
                if not self.revealed[r][c] and not self.flagged[r][c]]


# ─── VENTANA PRINCIPAL ────────────────────────────────────────────────────────
class MinesweeperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💣 BUSCAMINAS — NEON EDITION")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self._show_menu()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ── MENÚ PRINCIPAL ──────────────────────────────────────────────────────
    def _show_menu(self):
        self._clear()
        self.geometry("520x640")
        self.title("💣 BUSCAMINAS — NEON EDITION")

        # Fondo con canvas decorativo
        canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        # Partículas decorativas
        for _ in range(30):
            x = random.randint(0, 520)
            y = random.randint(0, 640)
            r = random.randint(1, 3)
            color = random.choice([ACCENT_CYAN, ACCENT_PINK, ACCENT_GOLD, "#8888ff"])
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")

        # Título
        canvas.create_text(260, 80, text="💣", font=("Segoe UI Emoji", 56), fill=ACCENT_PINK)
        canvas.create_text(260, 155, text="BUSCAMINAS", font=("Courier New", 34, "bold"), fill=ACCENT_CYAN)
        canvas.create_text(260, 188, text="N E O N   E D I T I O N", font=("Courier New", 12), fill=TEXT_DIM, spacing=4)

        # Línea decorativa
        canvas.create_line(80, 210, 440, 210, fill=ACCENT_CYAN, width=1)

        # ── Modo de juego ──
        canvas.create_text(260, 240, text="MODO DE JUEGO", font=("Courier New", 11, "bold"), fill=TEXT_DIM)

        self._mode_var = tk.StringVar(value="cpu")
        frame_mode = tk.Frame(canvas, bg=BG_CARD, bd=0, highlightbackground=ACCENT_CYAN, highlightthickness=1)
        canvas.create_window(260, 280, window=frame_mode, width=340, height=64)

        rb_cpu = tk.Radiobutton(frame_mode, text="⚡  vs COMPUTADORA",
                                variable=self._mode_var, value="cpu",
                                bg=BG_CARD, fg=ACCENT_CYAN, selectcolor=BG_CARD,
                                activebackground=BG_CARD, activeforeground=ACCENT_CYAN,
                                font=("Courier New", 11, "bold"), indicatoron=0,
                                relief="flat", bd=0, padx=10, pady=8, width=18,
                                highlightthickness=0)
        rb_cpu.pack(side=tk.LEFT, padx=8, pady=8)

        rb_p2 = tk.Radiobutton(frame_mode, text="👥  2 JUGADORES",
                               variable=self._mode_var, value="p2",
                               bg=BG_CARD, fg=ACCENT_PINK, selectcolor=BG_CARD,
                               activebackground=BG_CARD, activeforeground=ACCENT_PINK,
                               font=("Courier New", 11, "bold"), indicatoron=0,
                               relief="flat", bd=0, padx=10, pady=8, width=16,
                               highlightthickness=0)
        rb_p2.pack(side=tk.LEFT, padx=8, pady=8)

        # ── Dificultad ──
        canvas.create_text(260, 330, text="DIFICULTAD", font=("Courier New", 11, "bold"), fill=TEXT_DIM)

        self._diff_var = tk.StringVar(value="Fácil")
        frame_diff = tk.Frame(canvas, bg=BG_PANEL)
        canvas.create_window(260, 368, window=frame_diff, width=360, height=52)

        for diff in ["Fácil", "Medio", "Difícil"]:
            r, c, m = DIFFICULTIES[diff]
            sub = f"{r}×{c} · {m}💣"
            color = {"Fácil": "#00ff88", "Medio": ACCENT_GOLD, "Difícil": ACCENT_PINK}[diff]
            rb = tk.Radiobutton(frame_diff, text=f"{diff}\n{sub}",
                                variable=self._diff_var, value=diff,
                                bg=BG_PANEL, fg=color, selectcolor=BG_CARD,
                                activebackground=BG_PANEL, activeforeground=color,
                                font=("Courier New", 9), indicatoron=0,
                                relief="flat", bd=1, padx=6, pady=4,
                                highlightbackground=color, highlightthickness=1)
            rb.pack(side=tk.LEFT, padx=6, pady=4)

        # ── Nombres ──
        canvas.create_text(260, 415, text="NOMBRES", font=("Courier New", 11, "bold"), fill=TEXT_DIM)

        frame_names = tk.Frame(canvas, bg=BG_PANEL)
        canvas.create_window(260, 450, window=frame_names, width=360, height=40)

        tk.Label(frame_names, text="P1:", bg=BG_PANEL, fg=ACCENT_CYAN,
                 font=("Courier New", 10)).pack(side=tk.LEFT, padx=(6,2))
        self._name1 = tk.Entry(frame_names, bg=BG_CARD, fg=ACCENT_CYAN, insertbackground=ACCENT_CYAN,
                               font=("Courier New", 10), bd=0, width=10, relief="flat")
        self._name1.insert(0, "Jugador 1")
        self._name1.pack(side=tk.LEFT, padx=(0,12))

        tk.Label(frame_names, text="P2:", bg=BG_PANEL, fg=ACCENT_PINK,
                 font=("Courier New", 10)).pack(side=tk.LEFT, padx=(0,2))
        self._name2 = tk.Entry(frame_names, bg=BG_CARD, fg=ACCENT_PINK, insertbackground=ACCENT_PINK,
                               font=("Courier New", 10), bd=0, width=10, relief="flat")
        self._name2.insert(0, "Jugador 2")
        self._name2.pack(side=tk.LEFT)

        # ── Botón JUGAR ──
        btn = tk.Button(canvas, text="▶  INICIAR PARTIDA",
                        command=self._start_game,
                        bg=ACCENT_CYAN, fg=BG_DARK,
                        font=("Courier New", 14, "bold"),
                        bd=0, relief="flat", padx=24, pady=10,
                        activebackground=ACCENT_PINK, activeforeground=BG_DARK,
                        cursor="hand2")
        canvas.create_window(260, 520, window=btn, width=260, height=48)

        # Versión
        canvas.create_text(260, 610, text="v2.0 · Hecho con Python + Tkinter",
                           font=("Courier New", 8), fill=TEXT_DIM)

    # ── INICIAR JUEGO ──────────────────────────────────────────────────────
    def _start_game(self):
        mode = self._mode_var.get()
        diff = self._diff_var.get()
        rows, cols, mines = DIFFICULTIES[diff]
        name1 = self._name1.get() or "Jugador 1"
        name2 = self._name2.get() or "Jugador 2"
        self._clear()
        GameView(self, rows, cols, mines, mode, name1, name2)


# ─── VISTA DEL JUEGO ──────────────────────────────────────────────────────────
class GameView(tk.Frame):
    CELL = 32   # píxeles por celda

    def __init__(self, master, rows, cols, mines, mode, name1, name2):
        super().__init__(master, bg=BG_DARK)
        self.pack(fill=tk.BOTH, expand=True)

        self.master  = master
        self.rows    = rows
        self.cols    = cols
        self.mines   = mines
        self.mode    = mode   # "cpu" | "p2"
        self.name1   = name1
        self.name2   = name2 if mode == "p2" else "CPU"

        # Estado
        self.boards      = [Board(rows, cols, mines), Board(rows, cols, mines)]
        self.current     = 0          # 0 = J1, 1 = J2/CPU
        self.scores      = [0, 0]
        self.game_over   = False
        self.start_time  = None
        self.elapsed     = 0
        self.timer_id    = None

        self._build_ui()
        self._update_status()

    # ── CONSTRUCCIÓN UI ─────────────────────────────────────────────────────
    def _build_ui(self):
        cell = self.CELL
        board_w = self.cols * cell
        board_h = self.rows * cell
        win_w   = max(board_w * 2 + 60, 700)
        win_h   = board_h + 180
        self.master.geometry(f"{win_w}x{win_h}")
        self.master.title(f"💣 BUSCAMINAS  —  {self.rows}×{self.cols}  ·  {self.mines} minas")

        # ── TOP BAR ──
        top = tk.Frame(self, bg=BG_PANEL, height=60)
        top.pack(fill=tk.X)

        btn_menu = tk.Button(top, text="◀ MENÚ", command=self._back_menu,
                             bg=BG_CARD, fg=TEXT_DIM, font=("Courier New", 9),
                             bd=0, relief="flat", padx=10, pady=6,
                             activebackground=ACCENT_PINK, activeforeground=BG_DARK,
                             cursor="hand2")
        btn_menu.pack(side=tk.LEFT, padx=10, pady=10)

        self.timer_lbl = tk.Label(top, text="⏱ 00:00", bg=BG_PANEL, fg=ACCENT_GOLD,
                                  font=("Courier New", 14, "bold"))
        self.timer_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        btn_rst = tk.Button(top, text="↺ REINICIAR", command=self._restart,
                            bg=BG_CARD, fg=ACCENT_CYAN, font=("Courier New", 9, "bold"),
                            bd=0, relief="flat", padx=10, pady=6,
                            activebackground=ACCENT_CYAN, activeforeground=BG_DARK,
                            cursor="hand2")
        btn_rst.pack(side=tk.RIGHT, padx=10, pady=10)

        # ── STATUS BAR ──
        self.status_frame = tk.Frame(self, bg=BG_DARK, height=36)
        self.status_frame.pack(fill=tk.X)

        self.status_lbl = tk.Label(self.status_frame, text="", bg=BG_DARK,
                                   fg=ACCENT_CYAN, font=("Courier New", 12, "bold"))
        self.status_lbl.pack(pady=4)

        # ── BOARDS CONTAINER ──
        boards_frame = tk.Frame(self, bg=BG_DARK)
        boards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        self.board_frames = []
        self.canvases = []
        self.flag_lbls = []

        for i in range(2):
            col_color = ACCENT_CYAN if i == 0 else ACCENT_PINK
            name = self.name1 if i == 0 else self.name2

            outer = tk.Frame(boards_frame, bg=BG_DARK)
            outer.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
            self.board_frames.append(outer)

            # Header del tablero
            hdr = tk.Frame(outer, bg=BG_PANEL, height=36)
            hdr.pack(fill=tk.X)
            tk.Label(hdr, text=name, bg=BG_PANEL, fg=col_color,
                     font=("Courier New", 12, "bold")).pack(side=tk.LEFT, padx=10)

            flag_lbl = tk.Label(hdr, text=f"🚩 {self.mines}", bg=BG_PANEL, fg=ACCENT_GOLD,
                                font=("Courier New", 10))
            flag_lbl.pack(side=tk.RIGHT, padx=10)
            self.flag_lbls.append(flag_lbl)

            score_lbl = tk.Label(hdr, text="⭐ 0", bg=BG_PANEL, fg=col_color,
                                 font=("Courier New", 10))
            score_lbl.pack(side=tk.RIGHT, padx=6)
            # guardar referencia
            hdr.__dict__[f'score_{i}'] = score_lbl

            # Canvas del tablero
            cv = tk.Canvas(outer, width=self.cols*cell, height=self.rows*cell,
                           bg=BG_DARK, highlightthickness=1,
                           highlightbackground=col_color, cursor="crosshair")
            cv.pack(pady=2)
            self.canvases.append(cv)

            if i == 0 or self.mode == "p2":
                cv.bind("<Button-1>",       lambda e, idx=i: self._on_left(e, idx))
                cv.bind("<Button-3>",       lambda e, idx=i: self._on_right(e, idx))
                cv.bind("<Motion>",         lambda e, idx=i: self._on_hover(e, idx))
                cv.bind("<Leave>",          lambda e, idx=i: self._on_leave(idx))

        # Guardar headers
        self._hdrs = [boards_frame.winfo_children()[0].winfo_children()[0] if False else None]
        # Reconstruir referencias de scores
        self._score_lbls = []
        for i, outer in enumerate(self.board_frames):
            hdr = outer.winfo_children()[0]
            lbl = hdr.__dict__.get(f'score_{i}')
            self._score_lbls.append(lbl)

        # ── INSTRUCCIONES ──
        instr = tk.Frame(self, bg=BG_DARK)
        instr.pack(fill=tk.X, padx=10)
        tk.Label(instr, text="Clic izquierdo: revelar  |  Clic derecho: bandera  |  Gana quien revele más celdas sin explotar",
                 bg=BG_DARK, fg=TEXT_DIM, font=("Courier New", 8)).pack()

        self.hover_cell = [None, None]
        self._draw_all()

    # ── DIBUJO ──────────────────────────────────────────────────────────────
    def _draw_all(self):
        for i in range(2):
            self._draw_board(i)

    def _draw_board(self, idx, highlight=None):
        cv    = self.canvases[idx]
        board = self.boards[idx]
        cell  = self.CELL
        cv.delete("all")

        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c*cell, r*cell
                x2, y2 = x1+cell, y1+cell
                is_hover = (highlight == (r,c))

                if board.revealed[r][c]:
                    val = board.grid[r][c]
                    if val == -1:
                        # Mina explotada
                        cv.create_rectangle(x1,y1,x2,y2, fill="#3a0010", outline="#220008")
                        cv.create_text(x1+cell//2, y1+cell//2, text="💣",
                                       font=("Segoe UI Emoji", cell-10))
                    else:
                        cv.create_rectangle(x1,y1,x2,y2, fill=CELL_SAFE, outline="#0a0a1a", width=1)
                        if val > 0:
                            color = NUM_COLORS.get(val, TEXT_WHITE)
                            cv.create_text(x1+cell//2, y1+cell//2, text=str(val),
                                           font=("Courier New", cell//2, "bold"), fill=color)
                else:
                    bg = CELL_HOVER if is_hover else CELL_HIDDEN
                    cv.create_rectangle(x1,y1,x2,y2, fill=bg, outline="#0d0d22", width=1)
                    # Efecto 3D sutil
                    cv.create_line(x1+1,y1+1, x2-1,y1+1, fill="#2a2a50", width=1)
                    cv.create_line(x1+1,y1+1, x1+1,y2-1, fill="#2a2a50", width=1)
                    cv.create_line(x1+1,y2-1, x2-1,y2-1, fill="#0a0a18", width=1)
                    cv.create_line(x2-1,y1+1, x2-1,y2-1, fill="#0a0a18", width=1)

                    if board.flagged[r][c]:
                        cv.create_text(x1+cell//2, y1+cell//2, text="🚩",
                                       font=("Segoe UI Emoji", cell-12))

        # Actualizar contador de banderas
        remaining = self.mines - board.count_flags()
        self.flag_lbls[idx].config(text=f"🚩 {remaining}")

    def _reveal_all_mines(self, idx):
        board = self.boards[idx]
        cv    = self.canvases[idx]
        cell  = self.CELL
        for (r,c) in board.mine_pos:
            if not board.revealed[r][c]:
                x1,y1 = c*cell, r*cell
                x2,y2 = x1+cell, y1+cell
                cv.create_rectangle(x1,y1,x2,y2, fill="#200010", outline="#440020")
                cv.create_text(x1+cell//2, y1+cell//2, text="💣",
                               font=("Segoe UI Emoji", cell-10))

    # ── EVENTOS ─────────────────────────────────────────────────────────────
    def _cell_at(self, event):
        c = event.x // self.CELL
        r = event.y // self.CELL
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r, c
        return None, None

    def _on_hover(self, event, idx):
        r, c = self._cell_at(event)
        if r is not None and not self.boards[idx].revealed[r][c]:
            self.hover_cell[idx] = (r,c)
            self._draw_board(idx, highlight=(r,c))

    def _on_leave(self, idx):
        self.hover_cell[idx] = None
        self._draw_board(idx)

    def _on_left(self, event, idx):
        if self.game_over or self.current != idx:
            return
        r, c = self._cell_at(event)
        if r is None:
            return
        self._do_reveal(idx, r, c)

    def _on_right(self, event, idx):
        if self.game_over or self.current != idx:
            return
        r, c = self._cell_at(event)
        if r is None:
            return
        self.boards[idx].toggle_flag(r, c)
        self._draw_board(idx)

    # ── LÓGICA DE TURNO ─────────────────────────────────────────────────────
    def _do_reveal(self, idx, r, c):
        if self.start_time is None:
            self.start_time = time.time()
            self._tick()

        board  = self.boards[idx]
        result = board.reveal(r, c)
        self._draw_board(idx)

        if result == "mine":
            self._reveal_all_mines(idx)
            # Suma puntos al oponente
            opp = 1 - idx
            self.scores[opp] += 5
            self._update_score_labels()
            name = self.name1 if idx == 0 else self.name2
            self._end_game(f"💥 {name} explotó una mina! +5 pts para {self.name1 if opp==0 else self.name2}")
            return

        # Contar celdas recién reveladas → puntos
        prev = sum(board.revealed[r2][c2] for r2 in range(self.rows) for c2 in range(self.cols))
        # (ya actualizado en reveal)
        revealed_now = sum(board.revealed[r2][c2] for r2 in range(self.rows) for c2 in range(self.cols))
        self.scores[idx] += max(0, revealed_now - (prev - 1))  # aprox
        self._update_score_labels()

        if board.is_won():
            name = self.name1 if idx == 0 else self.name2
            self.scores[idx] += 10
            self._update_score_labels()
            self._end_game(f"🎉 ¡{name} despejó su tablero! +10 pts bonus")
            return

        # Cambiar turno
        self.current = 1 - idx
        self._update_status()

        if self.mode == "cpu" and self.current == 1 and not self.game_over:
            self.after(700, self._cpu_turn)

    def _cpu_turn(self):
        if self.game_over or self.current != 1:
            return
        board = self.boards[1]

        # Estrategia simple: buscar celdas seguras inferibles
        move = self._cpu_smart_move(board)
        if move is None:
            # fallback aleatorio, evitando minas conocidas
            choices = board.unrevealed_any()
            if not choices:
                return
            move = random.choice(choices)

        self._do_reveal(1, move[0], move[1])

    def _cpu_smart_move(self, board):
        """Intenta inferir una celda segura por análisis de vecinos."""
        safe = []
        mines_inf = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if not board.revealed[r][c]:
                    continue
                val = board.grid[r][c]
                if val <= 0:
                    continue
                neighbors = [(r+dr, c+dc) for dr in range(-1,2) for dc in range(-1,2)
                             if (dr,dc)!=(0,0) and 0<=r+dr<self.rows and 0<=c+dc<self.cols]
                hidden  = [n for n in neighbors if not board.revealed[n[0]][n[1]]]
                flagged = [n for n in neighbors if board.flagged[n[0]][n[1]]]
                unflagged_hidden = [n for n in hidden if not board.flagged[n[0]][n[1]]]

                if len(flagged) == val:
                    # Todos los vecinos ocultos son seguros
                    safe.extend(unflagged_hidden)
                if len(hidden) == val:
                    # Todos los vecinos ocultos son minas
                    mines_inf.update(unflagged_hidden)

        safe_real = [c for c in safe if c not in mines_inf]
        if safe_real:
            return random.choice(safe_real)
        # Evitar minas inferidas
        candidates = [c for c in board.unrevealed_any() if c not in mines_inf]
        if candidates:
            return random.choice(candidates)
        return None

    # ── STATUS / SCORES ─────────────────────────────────────────────────────
    def _update_status(self):
        if self.game_over:
            return
        if self.mode == "cpu":
            if self.current == 0:
                txt = f"🎮 Turno de {self.name1}"
                self.status_lbl.config(text=txt, fg=ACCENT_CYAN)
            else:
                self.status_lbl.config(text="🤖 CPU pensando...", fg=ACCENT_PINK)
        else:
            name = self.name1 if self.current == 0 else self.name2
            color = ACCENT_CYAN if self.current == 0 else ACCENT_PINK
            self.status_lbl.config(text=f"🎮 Turno de {name}", fg=color)

        # Resaltar canvas activo
        for i, cv in enumerate(self.canvases):
            active_color = ACCENT_CYAN if i == 0 else ACCENT_PINK
            cv.config(highlightbackground=active_color if i == self.current else TEXT_DIM,
                      highlightthickness=2 if i == self.current else 1)

    def _update_score_labels(self):
        for i, lbl in enumerate(self._score_lbls):
            if lbl:
                lbl.config(text=f"⭐ {self.scores[i]}")

    # ── TIMER ───────────────────────────────────────────────────────────────
    def _tick(self):
        if self.game_over or self.start_time is None:
            return
        self.elapsed = int(time.time() - self.start_time)
        m, s = divmod(self.elapsed, 60)
        self.timer_lbl.config(text=f"⏱ {m:02d}:{s:02d}")
        self.timer_id = self.after(1000, self._tick)

    def _stop_timer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    # ── FIN DE PARTIDA ──────────────────────────────────────────────────────
    def _end_game(self, msg):
        self.game_over = True
        self._stop_timer()

        # Determinar ganador
        if self.scores[0] > self.scores[1]:
            winner = self.name1
            w_color = ACCENT_CYAN
        elif self.scores[1] > self.scores[0]:
            winner = self.name2
            w_color = ACCENT_PINK
        else:
            winner = "¡Empate!"
            w_color = ACCENT_GOLD

        result_msg = (f"{msg}\n\n"
                      f"━━━ RESULTADO FINAL ━━━\n"
                      f"{self.name1}: {self.scores[0]} pts\n"
                      f"{self.name2}: {self.scores[1]} pts\n\n"
                      f"🏆 Ganador: {winner}")

        self.status_lbl.config(text=f"🏆 {winner}  —  {self.name1}: {self.scores[0]}pts  vs  {self.name2}: {self.scores[1]}pts",
                               fg=w_color)

        # Ventana emergente estilizada
        popup = tk.Toplevel(self)
        popup.title("FIN DE PARTIDA")
        popup.configure(bg=BG_DARK)
        popup.resizable(False, False)
        popup.geometry("380x320")
        popup.grab_set()

        tk.Label(popup, text="🏁 FIN DE PARTIDA", bg=BG_DARK, fg=ACCENT_GOLD,
                 font=("Courier New", 16, "bold")).pack(pady=(24,8))

        tk.Label(popup, text=msg, bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Courier New", 10), wraplength=340).pack(pady=4)

        tk.Frame(popup, bg=ACCENT_CYAN, height=1).pack(fill=tk.X, padx=20, pady=8)

        score_frame = tk.Frame(popup, bg=BG_CARD, padx=20, pady=14)
        score_frame.pack(padx=20, pady=4, fill=tk.X)
        tk.Label(score_frame, text=f"{self.name1}   {self.scores[0]} pts",
                 bg=BG_CARD, fg=ACCENT_CYAN, font=("Courier New", 12, "bold")).pack()
        tk.Label(score_frame, text="vs", bg=BG_CARD, fg=TEXT_DIM,
                 font=("Courier New", 9)).pack()
        tk.Label(score_frame, text=f"{self.name2}   {self.scores[1]} pts",
                 bg=BG_CARD, fg=ACCENT_PINK, font=("Courier New", 12, "bold")).pack()
        tk.Label(score_frame, text=f"\n🏆  {winner}",
                 bg=BG_CARD, fg=w_color, font=("Courier New", 14, "bold")).pack()

        btn_frame = tk.Frame(popup, bg=BG_DARK)
        btn_frame.pack(pady=16)
        tk.Button(btn_frame, text="↺  REVANCHA", command=lambda: [popup.destroy(), self._restart()],
                  bg=ACCENT_CYAN, fg=BG_DARK, font=("Courier New", 10, "bold"),
                  bd=0, relief="flat", padx=14, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="◀  MENÚ", command=lambda: [popup.destroy(), self._back_menu()],
                  bg=BG_CARD, fg=TEXT_WHITE, font=("Courier New", 10),
                  bd=0, relief="flat", padx=14, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=8)

    # ── NAVEGACIÓN ──────────────────────────────────────────────────────────
    def _restart(self):
        self._stop_timer()
        for w in self.master.winfo_children():
            w.destroy()
        GameView(self.master, self.rows, self.cols, self.mines,
                 self.mode, self.name1, self.name2)

    def _back_menu(self):
        self._stop_timer()
        for w in self.master.winfo_children():
            w.destroy()
        self.master._show_menu()


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = MinesweeperApp()
    app.mainloop()