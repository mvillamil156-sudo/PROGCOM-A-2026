"""

  PIEDRA · PAPEL · TIJERA · LAGARTO · SPOCK                         
  vs CPU  |  2 Jugadores   
                                                                     
   Reglas (10 relaciones):                                            
   ✂ Tijera  corta    📄 Papel                                        
   📄 Papel  envuelve 🪨 Piedra                                       
  🪨 Piedra aplasta  🦎 Lagarto                                      
  🦎 Lagarto devora  📄 Papel                                        
  🦎 Lagarto envenena🖖 Spock                                        
   🖖 Spock  vaporiza 🪨 Piedra                                       
   🖖 Spock  rompe    ✂ Tijera                                        
  ✂ Tijera  decapita 🦎 Lagarto                                      
   📄 Papel  desautoriza🖖 Spock                                      
   🪨 Piedra aplasta  ✂ Tijera                                        

"""

import tkinter as tk
from tkinter import font as tkfont
import random, time, math

# ─── PALETA: cómic cyberpunk oscuro ────────────────────────────────
BG      = "#0a0a12"
BG2     = "#12121e"
BG3     = "#1a1a2e"
BORDER  = "#2a2a50"
YELLOW  = "#f5c518"
YELLOW2 = "#fde68a"
CYAN    = "#00d4ff"
RED     = "#ff3366"
GREEN   = "#00ff88"
PURPLE  = "#b44fff"
WHITE   = "#f0f0ff"
GRAY    = "#6060a0"
DIM     = "#30304a"

# ─── DATOS DEL JUEGO ───────────────────────────────────────────────
OPCIONES = ["Piedra", "Papel", "Tijera", "Lagarto", "Spock"]

EMOJIS = {
    "Piedra":  "🪨",
    "Papel":   "📄",
    "Tijera":  "✂️",
    "Lagarto": "🦎",
    "Spock":   "🖖",
}

COLORES = {
    "Piedra":  "#f59e0b",
    "Papel":   "#3b82f6",
    "Tijera":  "#ef4444",
    "Lagarto": "#10b981",
    "Spock":   "#8b5cf6",
}

# (ganador, perdedor) → acción
REGLAS: dict[tuple, str] = {
    ("Tijera",  "Papel"):   "✂️ Tijera CORTA 📄 Papel",
    ("Papel",   "Piedra"):  "📄 Papel ENVUELVE 🪨 Piedra",
    ("Piedra",  "Lagarto"): "🪨 Piedra APLASTA 🦎 Lagarto",
    ("Lagarto", "Papel"):   "🦎 Lagarto DEVORA 📄 Papel",
    ("Lagarto", "Spock"):   "🦎 Lagarto ENVENENA 🖖 Spock",
    ("Spock",   "Piedra"):  "🖖 Spock VAPORIZA 🪨 Piedra",
    ("Spock",   "Tijera"):  "🖖 Spock ROMPE ✂️ Tijera",
    ("Tijera",  "Lagarto"): "✂️ Tijera DECAPITA 🦎 Lagarto",
    ("Papel",   "Spock"):   "📄 Papel DESAUTORIZA 🖖 Spock",
    ("Piedra",  "Tijera"):  "🪨 Piedra APLASTA ✂️ Tijera",
}

def determinar_ganador(j: str, cpu: str) -> tuple[str, str]:
    """Retorna ('jugador'|'cpu'|'empate', descripción)
       En modo 2P: 'jugador'=J1 gana, 'cpu'=J2 gana."""
    if j == cpu:
        return "empate", f"¡EMPATE!  {EMOJIS[j]} vs {EMOJIS[cpu]}"
    if (j, cpu) in REGLAS:
        return "jugador", REGLAS[(j, cpu)]
    return "cpu", REGLAS[(cpu, j)]


# ─── PARTÍCULA ─────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        a = random.uniform(0, 2 * math.pi)
        s = random.uniform(40, 160)
        self.x, self.y = x, y
        self.vx = math.cos(a) * s
        self.vy = math.sin(a) * s - 60
        self.life = random.uniform(0.5, 1.2)
        self.max_life = self.life
        self.r = random.uniform(2, 6)
        self.color = color

    def update(self, dt):
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy += 200 * dt
        self.life -= dt

    def alive(self): return self.life > 0

    def current_color(self):
        t = max(0, self.life / self.max_life)
        h = self.color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r2 = int(r * t + 10 * (1 - t))
        g2 = int(g * t + 10 * (1 - t))
        b2 = int(b * t + 18 * (1 - t))
        return f"#{r2:02x}{g2:02x}{b2:02x}"


# ─── APLICACIÓN PRINCIPAL ──────────────────────────────────────────
class RPSTLSApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("🖖 Piedra · Papel · Tijera · Lagarto · Spock")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.geometry("860x680")

        # Estado
        self.score   = {"jugador": 0, "cpu": 0, "empate": 0}
        self.historial: list[dict] = []
        self.particles: list[Particle] = []
        self.seleccion_jugador: str | None = None
        self.animando = False
        self._anim_id = None
        self._shake   = 0

        # Modo de juego
        self.modo = tk.StringVar(value="cpu")   # "cpu" | "2p"
        self._j1_nombre = "J1"
        self._j2_nombre = "J2"
        self._eleccion_j1: str | None = None    # para modo 2P secreto

        self._init_fonts()
        self._build_ui()
        self._loop()

    def _init_fonts(self):
        self.f_title  = tkfont.Font(family="Courier New", size=18, weight="bold")
        self.f_big    = tkfont.Font(family="Courier New", size=15, weight="bold")
        self.f_med    = tkfont.Font(family="Helvetica",   size=11, weight="bold")
        self.f_body   = tkfont.Font(family="Helvetica",   size=10)
        self.f_emoji  = tkfont.Font(family="Segoe UI Emoji", size=32)
        self.f_emoji_sm = tkfont.Font(family="Segoe UI Emoji", size=20)
        self.f_sm     = tkfont.Font(family="Helvetica",   size=9)
        self.f_mono   = tkfont.Font(family="Courier New", size=9)

    # ──────────────────────────────────────────────────────────────
    #  BUILD UI
    # ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── TOP BAR ──
        top = tk.Frame(self, bg=BG2, height=52)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        tk.Label(top, text="🖖  PIEDRA · PAPEL · TIJERA · LAGARTO · SPOCK",
                 bg=BG2, fg=YELLOW, font=self.f_big).pack(side=tk.LEFT, padx=16, pady=12)

        tk.Button(top, text="📋 REGLAS", command=self._show_rules,
                  bg=DIM, fg=WHITE, relief="flat",
                  font=self.f_sm, padx=10, pady=4,
                  cursor="hand2").pack(side=tk.RIGHT, padx=12, pady=10)

        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X)

        # ── BARRA DE MODO ──
        mode_bar = tk.Frame(self, bg=BG3, height=40)
        mode_bar.pack(fill=tk.X)
        mode_bar.pack_propagate(False)

        tk.Label(mode_bar, text="MODO:", bg=BG3, fg=GRAY,
                 font=self.f_sm).pack(side=tk.LEFT, padx=(14, 6), pady=10)

        for val, txt, col in [("cpu", "🤖  vs CPU", CYAN), ("2p", "👥  2 Jugadores", PURPLE)]:
            rb = tk.Radiobutton(mode_bar, text=txt, variable=self.modo, value=val,
                                bg=BG3, fg=col, selectcolor=BG3,
                                activebackground=BG3, activeforeground=col,
                                font=self.f_sm, indicatoron=0,
                                relief="flat", padx=10, pady=4,
                                highlightthickness=1,
                                highlightbackground=col,
                                cursor="hand2",
                                command=self._on_modo_cambio)
            rb.pack(side=tk.LEFT, padx=5, pady=6)

        # Etiqueta de estado del turno (modo 2P)
        self._turno_lbl = tk.Label(mode_bar, text="", bg=BG3,
                                    fg=CYAN, font=self.f_med)
        self._turno_lbl.pack(side=tk.LEFT, padx=20)

        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X)

        # ── MAIN AREA ──
        main = tk.Frame(self, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # Columna izquierda: arena + botones
        left = tk.Frame(main, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Columna derecha: historial
        right = tk.Frame(main, bg=BG2, width=220)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10,0))
        right.pack_propagate(False)

        self._build_arena(left)
        self._build_choices(left)
        self._build_scoreboard(left)
        self._build_historial(right)

    # ── ARENA ──────────────────────────────────────────────────────
    def _build_arena(self, parent):
        arena_wrap = tk.Frame(parent, bg=BG3, bd=1, relief="solid",
                              highlightbackground=BORDER, highlightthickness=1)
        arena_wrap.pack(fill=tk.X, pady=(0, 8))

        self.canvas = tk.Canvas(arena_wrap, width=590, height=200,
                                bg=BG3, highlightthickness=0)
        self.canvas.pack()

        self._draw_arena_idle()

    def _draw_arena_idle(self, waiting_j2=False):
        cv = self.canvas
        cv.delete("all")
        # Fondo decorativo
        cv.create_rectangle(0, 0, 600, 200, fill=BG3, outline="")
        # Línea central
        cv.create_line(295, 10, 295, 190, fill=BORDER, width=1, dash=(4,4))

        lbl_izq = self._j1_nombre if self.modo.get() == "2p" else "TÚ"
        lbl_der = self._j2_nombre if self.modo.get() == "2p" else "CPU"

        if waiting_j2:
            # J1 ya eligió — mostrar su elección oculta
            cv.create_text(150, 100, text="✅", fill=GREEN,
                           font=tkfont.Font(family="Segoe UI Emoji", size=52))
            cv.create_text(150, 160, text="¡Listo! Oculto",
                           fill=GREEN, font=self.f_sm)
            cv.create_text(440, 100, text="?", fill=GRAY,
                           font=tkfont.Font(family="Courier New", size=72, weight="bold"))
            cv.create_text(295, 185, text=f"── Turno de {lbl_der} ──",
                           fill=PURPLE, font=self.f_sm)
        else:
            cv.create_text(150, 100, text="?", fill=GRAY,
                           font=tkfont.Font(family="Courier New", size=72, weight="bold"))
            cv.create_text(440, 100, text="?", fill=GRAY,
                           font=tkfont.Font(family="Courier New", size=72, weight="bold"))
            hint = f"── Turno de {lbl_izq} ──" if self.modo.get() == "2p" else "── Elige tu opción ──"
            cv.create_text(295, 185, text=hint, fill=GRAY, font=self.f_sm)

        cv.create_text(150, 30, text=lbl_izq, fill=CYAN   if self.modo.get()=="2p" else GRAY, font=self.f_med)
        cv.create_text(440, 30, text=lbl_der, fill=PURPLE if self.modo.get()=="2p" else GRAY, font=self.f_med)

        # Partículas decorativas
        for p in self.particles:
            r = max(1, p.r * (p.life / p.max_life))
            col = p.current_color()
            cv.create_oval(p.x-r, p.y-r, p.x+r, p.y+r,
                           fill=col, outline="")

    def _draw_arena_result(self, j: str, cpu: str, resultado: str, descripcion: str):
        cv = self.canvas
        cv.delete("all")

        sx = self._shake
        col_j   = COLORES[j]
        col_cpu = COLORES[cpu]

        lbl_izq = self._j1_nombre if self.modo.get() == "2p" else "TÚ"
        lbl_der = self._j2_nombre if self.modo.get() == "2p" else "CPU"

        # Fondo con color del ganador
        if resultado == "jugador":
            cv.create_rectangle(0, 0, 295, 200, fill=self._dim(col_j, 0.15), outline="")
            cv.create_rectangle(295, 0, 600, 200, fill=self._dim(col_cpu, 0.05), outline="")
        elif resultado == "cpu":
            cv.create_rectangle(0, 0, 295, 200, fill=self._dim(col_j, 0.05), outline="")
            cv.create_rectangle(295, 0, 600, 200, fill=self._dim(col_cpu, 0.15), outline="")
        else:
            cv.create_rectangle(0, 0, 600, 200, fill=self._dim(YELLOW, 0.08), outline="")

        cv.create_line(295, 10, 295, 190, fill=BORDER, width=1, dash=(4,4))

        # Emojis jugadores
        cv.create_text(150 + sx, 95, text=EMOJIS[j],
                       font=tkfont.Font(family="Segoe UI Emoji", size=52))
        cv.create_text(440 - sx, 95, text=EMOJIS[cpu],
                       font=tkfont.Font(family="Segoe UI Emoji", size=52))

        # Labels dinámicos
        j_col   = col_j   if resultado == "jugador" else (YELLOW if resultado == "empate" else GRAY)
        cpu_col = col_cpu if resultado == "cpu"      else (YELLOW if resultado == "empate" else GRAY)

        cv.create_text(150, 22, text=lbl_izq, fill=j_col,   font=self.f_med)
        cv.create_text(440, 22, text=lbl_der, fill=cpu_col, font=self.f_med)
        cv.create_text(150, 165, text=j,   fill=col_j,   font=self.f_sm)
        cv.create_text(440, 165, text=cpu, fill=col_cpu, font=self.f_sm)

        # Resultado central — texto adaptado al modo
        if self.modo.get() == "2p":
            res_txt = {
                "jugador": f"¡{self._j1_nombre} GANA! 🎉",
                "cpu":     f"¡{self._j2_nombre} GANA! 🎉",
                "empate":  "¡EMPATE! 🤝",
            }[resultado]
        else:
            res_txt = {"jugador": "¡GANASTE!", "cpu": "¡PERDISTE!", "empate": "¡EMPATE!"}[resultado]

        res_col = {"jugador": GREEN, "cpu": RED, "empate": YELLOW}[resultado]

        cv.create_text(295, 100, text=res_txt, fill=res_col,
                       font=tkfont.Font(family="Courier New", size=15, weight="bold"))

        # Descripción de la regla
        cv.create_text(295, 183, text=descripcion[:55],
                       fill=WHITE, font=self.f_sm)

        # VS badge
        cv.create_oval(276, 82, 314, 118, fill=BG2, outline=BORDER, width=2)
        cv.create_text(295, 100, text="VS", fill=BORDER,
                       font=tkfont.Font(family="Courier New", size=9, weight="bold"))

        # Partículas
        for p in self.particles:
            r = max(1, p.r * (p.life / p.max_life))
            col = p.current_color()
            cv.create_oval(p.x-r, p.y-r, p.x+r, p.y+r,
                           fill=col, outline="")

    # ── BOTONES DE ELECCIÓN ────────────────────────────────────────
    def _build_choices(self, parent):
        lbl_f = tk.Frame(parent, bg=BG)
        lbl_f.pack(pady=(4, 2))
        self._choices_hint = tk.Label(lbl_f, text="── Elige tu arma ──",
                                       bg=BG, fg=GRAY, font=self.f_sm)
        self._choices_hint.pack()

        btn_f = tk.Frame(parent, bg=BG)
        btn_f.pack(pady=(0, 6))

        self._choice_buttons = {}
        for opcion in OPCIONES:
            col  = COLORES[opcion]
            emoji = EMOJIS[opcion]

            b = tk.Frame(btn_f, bg=DIM, cursor="hand2",
                         bd=0, relief="flat",
                         highlightthickness=2,
                         highlightbackground=BORDER)
            b.pack(side=tk.LEFT, padx=5)

            emo_lbl = tk.Label(b, text=emoji, bg=DIM,
                               font=self.f_emoji_sm, padx=12, pady=4)
            emo_lbl.pack()
            txt_lbl = tk.Label(b, text=opcion, bg=DIM,
                               fg=WHITE, font=self.f_sm, pady=4)
            txt_lbl.pack()

            self._choice_buttons[opcion] = (b, emo_lbl, txt_lbl, col)

            def on_click(o=opcion): self._jugada(o)
            def on_enter(e, fr=b, c=col):
                fr.config(bg=self._dim(c, 0.25),
                          highlightbackground=c)
                for w in fr.winfo_children():
                    w.config(bg=self._dim(c, 0.25))
            def on_leave(e, fr=b, c=col):
                fr.config(bg=DIM, highlightbackground=BORDER)
                for w in fr.winfo_children():
                    w.config(bg=DIM)

            for widget in [b, emo_lbl, txt_lbl]:
                widget.bind("<Button-1>", lambda e, o=opcion: self._jugada(o))
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

    # ── MARCADOR ───────────────────────────────────────────────────
    def _build_scoreboard(self, parent):
        sf = tk.Frame(parent, bg=BG2,
                      highlightthickness=1, highlightbackground=BORDER)
        sf.pack(fill=tk.X, pady=(0, 4))

        for i, (key, label, col) in enumerate([
            ("jugador", "TÚ",     GREEN),
            ("empate",  "EMPATE", YELLOW),
            ("cpu",     "CPU",    RED),
        ]):
            col_f = tk.Frame(sf, bg=BG2)
            col_f.grid(row=0, column=i, padx=20, pady=8, sticky="ew")
            sf.columnconfigure(i, weight=1)

            name_lbl = tk.Label(col_f, text=label, bg=BG2, fg=col, font=self.f_sm)
            name_lbl.pack()
            setattr(self, f"_name_lbl_{key}", name_lbl)

            lbl = tk.Label(col_f, text="0", bg=BG2, fg=col,
                           font=tkfont.Font(family="Courier New",
                                            size=28, weight="bold"))
            lbl.pack()
            setattr(self, f"_score_lbl_{key}", lbl)

        self._resultado_lbl = tk.Label(sf, text="",
                                        bg=BG2, fg=WHITE, font=self.f_med)
        self._resultado_lbl.grid(row=1, column=0, columnspan=3, pady=(0,6))

    # ── HISTORIAL ──────────────────────────────────────────────────
    def _build_historial(self, parent):
        tk.Label(parent, text="📋  HISTORIAL",
                 bg=BG2, fg=YELLOW, font=self.f_med).pack(pady=(10,4))
        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X)

        wrap = tk.Frame(parent, bg=BG2)
        wrap.pack(fill=tk.BOTH, expand=True)

        self._hist_canvas = tk.Canvas(wrap, bg=BG2,
                                       highlightthickness=0, width=200)
        sb = tk.Scrollbar(wrap, orient="vertical",
                          command=self._hist_canvas.yview,
                          bg=BG2, troughcolor=BG3)
        self._hist_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._hist_canvas.pack(fill=tk.BOTH, expand=True)

        self._hist_inner = tk.Frame(self._hist_canvas, bg=BG2)
        self._hist_win   = self._hist_canvas.create_window(
            (0, 0), window=self._hist_inner, anchor="nw")

        self._hist_inner.bind("<Configure>",
            lambda e: self._hist_canvas.configure(
                scrollregion=self._hist_canvas.bbox("all")))
        self._hist_canvas.bind("<Configure>",
            lambda e: self._hist_canvas.itemconfig(
                self._hist_win, width=e.width))

        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, side=tk.BOTTOM)
        btn_reset = tk.Button(parent, text="🔄 REINICIAR",
                              command=self._reset,
                              bg=DIM, fg=WHITE, relief="flat",
                              font=self.f_sm, padx=8, pady=5,
                              cursor="hand2")
        btn_reset.pack(side=tk.BOTTOM, pady=6, padx=8, fill=tk.X)

    # ──────────────────────────────────────────────────────────────
    #  CALLBACKS DE MODO
    # ──────────────────────────────────────────────────────────────
    def _on_modo_cambio(self):
        """Llamado al cambiar el Radiobutton de modo."""
        if self.modo.get() == "2p":
            self._pedir_nombres_2p()
        else:
            self._j1_nombre = "J1"
            self._j2_nombre = "J2"
            self._reset()

    # ──────────────────────────────────────────────────────────────
    #  LÓGICA DEL JUEGO
    # ──────────────────────────────────────────────────────────────
    def _jugada(self, eleccion: str):
        if self.animando:
            return

        if self.modo.get() == "cpu":
            self._jugada_cpu(eleccion)
        else:
            self._jugada_2p(eleccion)

    # ── MODO CPU ───────────────────────────────────────────────────
    def _jugada_cpu(self, jugador: str):
        self.animando = True
        cpu_eleccion  = random.choice(OPCIONES)
        resultado, descripcion = determinar_ganador(jugador, cpu_eleccion)
        self._resolver_ronda(jugador, cpu_eleccion, resultado, descripcion)

    # ── MODO 2 JUGADORES (elección secreta por turnos) ─────────────
    def _jugada_2p(self, eleccion: str):
        if self._eleccion_j1 is None:
            # Turno de J1 — guardar en secreto
            self._eleccion_j1 = eleccion
            self._highlight_button(eleccion)
            self._turno_lbl.config(
                text=f"✅ {self._j1_nombre} eligió — Turno de {self._j2_nombre}",
                fg=PURPLE)
            self._choices_hint.config(
                text=f"── {self._j2_nombre}: elige tu arma ──", fg=PURPLE)
            self._draw_arena_idle(waiting_j2=True)
        else:
            # Turno de J2 — resolver
            self.animando = True
            j1 = self._eleccion_j1
            j2 = eleccion
            self._eleccion_j1 = None
            resultado, descripcion = determinar_ganador(j1, j2)
            self._turno_lbl.config(text="")
            self._choices_hint.config(text="── Elige tu arma ──", fg=GRAY)
            self._resolver_ronda(j1, j2, resultado, descripcion)

    # ── RESOLVER RONDA (común a ambos modos) ───────────────────────
    def _resolver_ronda(self, j1: str, j2: str, resultado: str, descripcion: str):
        # Actualizar marcador
        self.score[resultado] += 1
        self._score_lbl_jugador.config(text=str(self.score["jugador"]))
        self._score_lbl_cpu.config(text=str(self.score["cpu"]))
        self._score_lbl_empate.config(text=str(self.score["empate"]))

        # Etiqueta de resultado adaptada al modo
        if self.modo.get() == "2p":
            res_txt = {
                "jugador": f"¡{self._j1_nombre} gana! 🎉",
                "cpu":     f"¡{self._j2_nombre} gana! 🎉",
                "empate":  "¡EMPATE! 🤝",
            }[resultado]
        else:
            res_txt = {"jugador": "¡GANASTE! 🎉", "cpu": "¡CPU GANA! 😤", "empate": "¡EMPATE! 🤝"}[resultado]

        res_col = {"jugador": GREEN, "cpu": RED, "empate": YELLOW}[resultado]
        self._resultado_lbl.config(text=res_txt, fg=res_col)

        # Resaltar botón elegido
        self._highlight_button(j1)

        # Historial
        self.historial.insert(0, {
            "j": j1, "cpu": j2,
            "resultado": resultado, "desc": descripcion
        })
        self._update_historial()

        # Partículas
        color_p = {"jugador": GREEN, "cpu": RED, "empate": YELLOW}[resultado]
        for _ in range(30):
            self.particles.append(
                Particle(random.uniform(50, 540),
                         random.uniform(30, 160), color_p))

        # Shake si pierde (solo modo CPU)
        if resultado == "cpu" and self.modo.get() == "cpu":
            self._shake = 8

        # Animar revelación
        self._animate_reveal(j1, j2, resultado, descripcion)

    def _animate_reveal(self, j, cpu, resultado, desc, step=0):
        """Animación de 3 pasos: cuenta atrás → revela."""
        if step < 3:
            labels = ["3...", "2...", "1..."]
            cv = self.canvas
            cv.delete("all")
            cv.create_rectangle(0, 0, 600, 200, fill=BG3, outline="")
            cv.create_text(295, 100, text=labels[step],
                           fill=YELLOW,
                           font=tkfont.Font(family="Courier New",
                                            size=52, weight="bold"))
            self.after(300, lambda: self._animate_reveal(j, cpu, resultado, desc, step+1))
        else:
            self._draw_arena_result(j, cpu, resultado, desc)
            self.after(1800, self._end_animation)

    def _end_animation(self):
        self.animando = False
        self._shake   = 0
        self._reset_buttons()
        # Restaurar etiqueta de turno en modo 2P
        if self.modo.get() == "2p":
            self._choices_hint.config(
                text=f"── {self._j1_nombre}: elige tu arma ──", fg=CYAN)
            self._turno_lbl.config(text="")

    def _highlight_button(self, elegida: str):
        for opcion, (frame, emo, txt, col) in self._choice_buttons.items():
            if opcion == elegida:
                frame.config(bg=self._dim(col, 0.35),
                             highlightbackground=col)
                for w in [emo, txt]:
                    w.config(bg=self._dim(col, 0.35))
            else:
                frame.config(bg=self._dim(DIM, 0.4),
                             highlightbackground=BORDER)
                for w in [emo, txt]:
                    w.config(bg=self._dim(DIM, 0.4))

    def _reset_buttons(self):
        for opcion, (frame, emo, txt, col) in self._choice_buttons.items():
            frame.config(bg=DIM, highlightbackground=BORDER)
            for w in [emo, txt]:
                w.config(bg=DIM)

    def _update_historial(self):
        for w in self._hist_inner.winfo_children():
            w.destroy()
        is_2p = self.modo.get() == "2p"
        for i, entry in enumerate(self.historial[:30]):
            col = {"jugador": GREEN, "cpu": RED, "empate": YELLOW}[entry["resultado"]]
            if is_2p:
                ico = {
                    "jugador": f"🏆{self._j1_nombre[:3]}",
                    "cpu":     f"🏆{self._j2_nombre[:3]}",
                    "empate":  "🔁",
                }[entry["resultado"]]
            else:
                ico = {"jugador": "✅", "cpu": "❌", "empate": "🔁"}[entry["resultado"]]
            row = tk.Frame(self._hist_inner, bg=BG2 if i%2==0 else BG3)
            row.pack(fill=tk.X, pady=0)
            tk.Label(row, text=f"{ico} {EMOJIS[entry['j']]} vs {EMOJIS[entry['cpu']]}",
                     bg=row.cget("bg"), fg=col,
                     font=tkfont.Font(family="Segoe UI Emoji", size=10)).pack(
                         side=tk.LEFT, padx=6, pady=3)
        # Scroll al top
        self.after(50, lambda: self._hist_canvas.yview_moveto(0))

    def _reset(self):
        self.score    = {"jugador": 0, "cpu": 0, "empate": 0}
        self.historial = []
        self.particles = []
        self._eleccion_j1 = None
        self._score_lbl_jugador.config(text="0")
        self._score_lbl_cpu.config(text="0")
        self._score_lbl_empate.config(text="0")
        self._resultado_lbl.config(text="")
        self._turno_lbl.config(text="")
        self._update_historial()
        self._draw_arena_idle()
        self._reset_buttons()
        self.animando = False

        # Actualizar etiquetas del marcador según modo
        if self.modo.get() == "2p":
            self._name_lbl_jugador.config(text=self._j1_nombre)
            self._name_lbl_cpu.config(text=self._j2_nombre)
            self._choices_hint.config(
                text=f"── {self._j1_nombre}: elige tu arma ──", fg=CYAN)
        else:
            self._name_lbl_jugador.config(text="TÚ")
            self._name_lbl_cpu.config(text="CPU")
            self._choices_hint.config(text="── Elige tu arma ──", fg=GRAY)

    def _pedir_nombres_2p(self):
        """Ventana para configurar nombres en modo 2 jugadores."""
        dlg = tk.Toplevel(self)
        dlg.title("👥 Nombres de jugadores")
        dlg.configure(bg=BG)
        dlg.geometry("320x200")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self)

        tk.Label(dlg, text="👥  Modo 2 Jugadores",
                 bg=BG, fg=PURPLE,
                 font=tkfont.Font(family="Courier New", size=13, weight="bold")
                 ).pack(pady=(16, 8))

        for i, (attr, label, col) in enumerate([
            ("_j1_nombre", "Jugador 1:", CYAN),
            ("_j2_nombre", "Jugador 2:", PURPLE),
        ]):
            row = tk.Frame(dlg, bg=BG)
            row.pack(pady=4)
            tk.Label(row, text=label, bg=BG, fg=col,
                     font=self.f_sm, width=12, anchor="e").pack(side=tk.LEFT)
            var = tk.StringVar(value=getattr(self, attr))
            entry = tk.Entry(row, textvariable=var, bg=BG3, fg=WHITE,
                             insertbackground=col, relief="solid",
                             font=self.f_sm, width=14, bd=1)
            entry.pack(side=tk.LEFT, padx=6, ipady=4)
            entry.__dict__["_var"]  = var
            entry.__dict__["_attr"] = attr
            dlg.__dict__[f"_entry_{i}"] = entry

        def ok():
            for key in ["_entry_0", "_entry_1"]:
                e = dlg.__dict__[key]
                val = e.__dict__["_var"].get().strip() or e.__dict__["_attr"].replace("_","").upper()
                setattr(self, e.__dict__["_attr"], val[:12])
            dlg.destroy()
            self._reset()

        tk.Button(dlg, text="✅  Jugar", command=ok,
                  bg=PURPLE, fg=BG, relief="flat",
                  font=self.f_med, padx=16, pady=6,
                  cursor="hand2").pack(pady=12)

    # ── VENTANA DE REGLAS ──────────────────────────────────────────
    def _show_rules(self):
        dlg = tk.Toplevel(self)
        dlg.title("📋 Reglas del juego")
        dlg.configure(bg=BG)
        dlg.geometry("460x500")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self)

        tk.Label(dlg, text="📋  REGLAS — Las 10 relaciones",
                 bg=BG, fg=YELLOW,
                 font=tkfont.Font(family="Courier New", size=13, weight="bold")
                 ).pack(pady=(16, 4))
        tk.Frame(dlg, bg=BORDER, height=1).pack(fill=tk.X, padx=20)

        frame = tk.Frame(dlg, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for i, ((ganador, perdedor), accion) in enumerate(REGLAS.items()):
            col = COLORES[ganador]
            row = tk.Frame(frame, bg=BG2 if i % 2 == 0 else BG3)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=f"  {accion}",
                     bg=row.cget("bg"), fg=col,
                     font=tkfont.Font(family="Helvetica", size=10),
                     anchor="w").pack(fill=tk.X, padx=6, pady=5)

        tk.Button(dlg, text="✖  Cerrar", command=dlg.destroy,
                  bg=DIM, fg=WHITE, relief="flat",
                  font=self.f_sm, padx=16, pady=6,
                  cursor="hand2").pack(pady=12)

    # ── LOOP DE ANIMACIÓN ─────────────────────────────────────────
    def _loop(self):
        dt = 1 / 30
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

        if self._shake > 0:
            self._shake = int(self._shake * -0.6)
            if abs(self._shake) < 1:
                self._shake = 0

        # Solo redibujar partículas si están activas y hay resultado
        if self.particles and self.animando:
            # Forzar redibujado para mostrar partículas sobre el canvas actual
            # Las partículas se dibujan dentro del canvas via _draw_arena_result
            pass

        self.after(33, self._loop)

    # ── UTILIDAD DE COLOR ─────────────────────────────────────────
    @staticmethod
    def _dim(hex_color: str, t: float) -> str:
        """Mezcla hex_color con BG oscuro según t (0=oscuro, 1=puro)."""
        h = hex_color.lstrip("#")
        if len(h) != 6:
            return hex_color
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        bg_r, bg_g, bg_b = 10, 10, 18  # BG
        r2 = int(r*t + bg_r*(1-t))
        g2 = int(g*t + bg_g*(1-t))
        b2 = int(b*t + bg_b*(1-t))
        return f"#{r2:02x}{g2:02x}{b2:02x}"


# ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = RPSTLSApp()
    app.mainloop()
