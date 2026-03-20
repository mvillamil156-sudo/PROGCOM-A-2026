"""
╔══════════════════════════════════════════════════════════════╗
║          A R K A N O I D  ·  S Y N T H W A V E  8 0 s       ║
║              Python · Tkinter · Zero dependencies            ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
import math, random, time, colorsys

# ══════════════════════════════════════════════════════
#  CONSTANTES
# ══════════════════════════════════════════════════════
W, H        = 700, 820
FPS         = 60
DT          = 1 / FPS

PAD_W, PAD_H    = 100, 12
BALL_R          = 8
BRICK_W, BRICK_H = 60, 22
BRICK_COLS      = 9
BRICK_ROWS_BASE = 6
BRICK_X0        = (W - BRICK_COLS * (BRICK_W + 4)) // 2
BRICK_Y0        = 90

# Paleta synthwave
C_BG      = "#07071a"
C_GRID    = "#12123a"
C_PAD     = "#ff2d78"
C_BALL    = "#ffffff"
C_HUD     = "#00f5ff"
C_TITLE   = "#ff2d78"

BRICK_PALETTES = [
    # (fill, glow)
    ("#ff2d78", "#ff80aa"),   # rosa
    ("#00f5ff", "#80faff"),   # cyan
    ("#ffd700", "#ffe566"),   # dorado
    ("#a855f7", "#cc99ff"),   # violeta
    ("#00ff88", "#80ffbb"),   # verde neon
    ("#ff6b35", "#ffaa80"),   # naranja
    ("#e040fb", "#f09aff"),   # magenta
    ("#1de9b6", "#80f5e0"),   # turquesa
]

POWERUP_TYPES = ["wide", "multi", "slow", "laser", "life", "small"]
POWERUP_COLORS = {
    "wide":  "#ffd700",
    "multi": "#00f5ff",
    "slow":  "#00ff88",
    "laser": "#ff2d78",
    "life":  "#ff80aa",
    "small": "#a855f7",
}
POWERUP_ICONS = {
    "wide":  "►◄",
    "multi": "×3",
    "slow":  "▼▼",
    "laser": "↑↑",
    "life":  "♥",
    "small": "◄►",
}


def clamp(v, lo, hi): return max(lo, min(hi, v))
def lerp(a, b, t): return a + (b - a) * t

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def blend(c1, c2, t):
    r1,g1,b1 = hex_to_rgb(c1)
    r2,g2,b2 = hex_to_rgb(c2)
    return rgb_to_hex(lerp(r1,r2,t), lerp(g1,g2,t), lerp(b1,b2,t))



class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(60, 240)
        self.x, self.y   = x, y
        self.vx = math.cos(angle)*speed
        self.vy = math.sin(angle)*speed
        self.life = random.uniform(0.4, 0.9)
        self.max_life = self.life
        self.r  = random.uniform(2, 5)
        self.color = color
        self.shape = random.choice(["circle","rect","spark"])
        self.spin  = random.uniform(-8, 8)
        self.angle = random.uniform(0, 6.28)

    def update(self, dt):
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy += 180 * dt       # gravedad suave
        self.vx *= 0.98
        self.life -= dt
        self.angle += self.spin * dt

    def alive(self): return self.life > 0

    def alpha_color(self):
        t = max(0, self.life / self.max_life)
        return blend(self.color, C_BG, 1-t)



class Ball:
    BASE_SPEED = 380

    def __init__(self, x, y, vx=None, vy=None):
        self.x, self.y = x, y
        ang = random.uniform(-0.9, 0.9)
        spd = self.BASE_SPEED
        self.vx = vx if vx is not None else math.sin(ang)*spd
        self.vy = vy if vy is not None else -math.cos(ang)*spd
        self.trail = []
        self.active = True
        self.laser = False   # modo laser (atraviesa bloques)

    def update(self, dt, pad_x, pad_y, pad_w, walls_only=False):
        steps = 3
        dts = dt / steps
        hit_result = None
        for _ in range(steps):
            self.x += self.vx * dts
            self.y += self.vy * dts
            # Paredes
            if self.x - BALL_R < 0:
                self.x = BALL_R; self.vx = abs(self.vx)
            if self.x + BALL_R > W:
                self.x = W - BALL_R; self.vx = -abs(self.vx)
            if self.y - BALL_R < 0:
                self.y = BALL_R; self.vy = abs(self.vy)
            # Paleta
            if not walls_only:
                if (self.vy > 0 and
                    pad_x <= self.x <= pad_x + pad_w and
                    pad_y <= self.y + BALL_R <= pad_y + PAD_H + 6):
                    rel = (self.x - (pad_x + pad_w/2)) / (pad_w/2)
                    angle = rel * 1.1
                    spd = math.hypot(self.vx, self.vy)
                    self.vx = math.sin(angle) * spd
                    self.vy = -abs(math.cos(angle)) * spd
                    self.y  = pad_y - BALL_R - 1
                    hit_result = "pad"
            # Fuera por abajo
            if self.y - BALL_R > H:
                self.active = False
                break
        # Trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12:
            self.trail.pop(0)
        return hit_result

    def speed(self): return math.hypot(self.vx, self.vy)

    def normalize_speed(self, target=None):
        if target is None: target = self.BASE_SPEED
        s = self.speed()
        if s > 0:
            self.vx = self.vx / s * target
            self.vy = self.vy / s * target



class Brick:
    def __init__(self, x, y, hp, palette_idx, special=None):
        self.x, self.y = x, y
        self.hp = hp
        self.max_hp = hp
        self.palette_idx = palette_idx
        self.special = special    # None / "indestructible" / "powerup"
        self.hit_anim = 0.0       # 0..1 flash
        self.shake_x  = 0.0

    def fill(self):
        if self.special == "indestructible":
            t = (math.sin(time.time()*2)+1)/2
            return blend("#444466", "#8888aa", t)
        if self.hp == 1:
            return BRICK_PALETTES[self.palette_idx % len(BRICK_PALETTES)][0]
        # multi-hp → más oscuro
        base = BRICK_PALETTES[self.palette_idx % len(BRICK_PALETTES)][0]
        return blend(base, "#050510", 0.4*(self.max_hp - self.hp)/self.max_hp)

    def glow(self):
        if self.special == "indestructible":
            return "#aaaacc"
        return BRICK_PALETTES[self.palette_idx % len(BRICK_PALETTES)][1]

    def rect(self):
        return (self.x, self.y, self.x+BRICK_W, self.y+BRICK_H)

    def hit(self):
        if self.special == "indestructible":
            self.hit_anim = 1.0
            self.shake_x = 4.0
            return False   # no destruido
        self.hp -= 1
        self.hit_anim = 1.0
        self.shake_x = 3.0
        return self.hp <= 0

    def update(self, dt):
        if self.hit_anim > 0:
            self.hit_anim = max(0, self.hit_anim - dt*6)
        if abs(self.shake_x) > 0.1:
            self.shake_x *= -0.5
        else:
            self.shake_x = 0



class PowerUp:
    def __init__(self, x, y, ptype):
        self.x, self.y = x, y
        self.type   = ptype
        self.vy     = 110
        self.active = True
        self.pulse  = 0.0

    def update(self, dt):
        self.y    += self.vy * dt
        self.pulse = (self.pulse + dt * 4) % (2*math.pi)
        if self.y > H: self.active = False

    def rect(self): return (self.x-18, self.y-10, self.x+18, self.y+10)



class Laser:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vy = -700
        self.active = True

    def update(self, dt):
        self.y += self.vy * dt
        if self.y < 0: self.active = False



def make_level(level):
    """Retorna lista de Brick según el nivel."""
    bricks = []
    rows = min(BRICK_ROWS_BASE + level, 11)
    gx, gy = BRICK_W + 4, BRICK_H + 5
    cx = BRICK_X0

    patterns = [
        # 0: clásico
        lambda r,c: True,
        # 1: damero
        lambda r,c: (r+c) % 2 == 0,
        # 2: pirámide
        lambda r,c: c >= r//2 and c < BRICK_COLS - r//2,
        # 3: X
        lambda r,c: abs(c - BRICK_COLS//2) == abs(r - rows//2) or
                    (c + r - rows//2) % (BRICK_COLS//3+1) == 0,
        # 4: espiral (todos + indestructibles en borde)
        lambda r,c: True,
    ]
    pattern = patterns[level % len(patterns)]

    for r in range(rows):
        for c in range(BRICK_COLS):
            if not pattern(r, c):
                continue
            x = cx + c * gx
            y = BRICK_Y0 + r * gy

            hp = 1
            special = None

            # HP extra en niveles altos
            if level >= 3 and r < 2:
                hp = 2
            if level >= 5 and r == 0:
                hp = 3

            # Indestructibles en borde nivel 4+
            if level >= 4 and (r == 0 or c == 0 or c == BRICK_COLS-1):
                if random.random() < 0.15:
                    special = "indestructible"
                    hp = 99

            # Power-up aleatorio
            if special is None and random.random() < 0.12:
                special = "powerup"

            pal = (r + level * 2 + c // 3) % len(BRICK_PALETTES)
            bricks.append(Brick(x, y, hp, pal, special))
    return bricks



class Arkanoid:
    def __init__(self, root):
        self.root = root
        root.title("ARKANOID · SYNTHWAVE 80s")
        root.configure(bg=C_BG)
        root.resizable(False, False)

        self.cv = tk.Canvas(root, width=W, height=H, bg=C_BG,
                            highlightthickness=0)
        self.cv.pack()

        self._bind_keys()
        self._init_state()
        self._draw_background()
        self._show_title()


    def _init_state(self):
        self.state       = "title"   # title / playing / paused / dead / win / gameover
        self.level       = 1
        self.score       = 0
        self.hi_score    = 0
        self.lives       = 3
        self.combo       = 0
        self.combo_timer = 0.0

        # Paleta
        self.pad_x   = W//2 - PAD_W//2
        self.pad_y   = H - 70
        self.pad_w   = PAD_W
        self.pad_target_x = self.pad_x

        # Power-ups activos
        self.laser_active   = False
        self.laser_timer    = 0.0
        self.multi_active   = False
        self.slow_timer     = 0.0

        self.balls     = []
        self.bricks    = []
        self.particles = []
        self.powerups  = []
        self.lasers    = []

        # Teclado
        self.keys      = set()
        self.mouse_x   = W // 2

        # Animación fondo
        self.bg_phase  = 0.0
        self.stars     = [(random.uniform(0,W), random.uniform(0,H),
                           random.uniform(0.5,2.5), random.choice(["#ffffff","#8888ff","#ff88cc","#88ffcc"]))
                          for _ in range(120)]
        self.grid_lines = []
        self._build_grid()

        self.last_time  = time.time()
        self.frame_id   = None

    def _start_level(self):
        self.bricks = make_level(self.level)
        self._reset_ball()
        self.state   = "playing"
        self.pad_w   = PAD_W
        self.laser_active = False
        self.multi_active = False
        self.slow_timer   = 0.0
        self.powerups.clear()
        self.lasers.clear()
        self.particles.clear()

    def _reset_ball(self):
        bx = self.pad_x + self.pad_w // 2
        by = self.pad_y - BALL_R - 2
        self.balls = [Ball(bx, by)]
        self.ball_on_pad = True

    def _build_grid(self):
        """Líneas de perspectiva tipo 80s."""
        self.grid_lines = []
        vp_x, vp_y = W//2, H + 100   # punto de fuga
        # verticales
        for i in range(18):
            bx = i * (W/17)
            self.grid_lines.append(("v", bx, H*0.55, vp_x, vp_y))
        # horizontales
        for i in range(10):
            t  = i / 9
            yt = lerp(H*0.55, H, t**1.4)
            self.grid_lines.append(("h", yt))


    def _bind_keys(self):
        self.root.bind("<KeyPress>",   self._key_down)
        self.root.bind("<KeyRelease>", self._key_up)
        self.root.bind("<Motion>",     self._mouse_move)
        self.root.bind("<Button-1>",   self._mouse_click)

    def _key_down(self, e):
        k = e.keysym.lower()
        self.keys.add(k)
        if k == "space":
            if self.state == "title":     self._start_new_game()
            elif self.state == "playing": self._launch_ball()
            elif self.state in ("dead","win","gameover"): pass
            elif self.state == "paused":  self.state = "playing"
        if k == "p":
            if self.state == "playing": self.state = "paused"
            elif self.state == "paused": self.state = "playing"
        if k == "r" and self.state in ("gameover","win"):
            self._init_state()
            self._show_title()

    def _key_up(self, e):
        self.keys.discard(e.keysym.lower())

    def _mouse_move(self, e):
        self.mouse_x = e.x

    def _mouse_click(self, e):
        if self.state == "title":     self._start_new_game()
        elif self.state == "playing": self._launch_ball()
        elif self.state in ("dead",): self._respawn()

    def _launch_ball(self):
        if hasattr(self, "ball_on_pad") and self.ball_on_pad:
            self.ball_on_pad = False


    def _start_new_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.combo = 0
        self._start_level()
        if self.frame_id:
            self.root.after_cancel(self.frame_id)
        self.last_time = time.time()
        self._loop()

    def _respawn(self):
        if self.lives > 0:
            self._reset_ball()
            self.state = "playing"
        else:
            self.state = "gameover"


    def _loop(self):
        now = time.time()
        dt  = min(now - self.last_time, 0.05)
        self.last_time = now
        self.bg_phase += dt * 0.4

        self._update(dt)
        self._render()

        self.frame_id = self.root.after(int(1000/FPS), self._loop)


    def _update(self, dt):
        if self.state != "playing":
            # Actualizar partículas siempre
            for p in self.particles: p.update(dt)
            self.particles = [p for p in self.particles if p.alive()]
            return

        # ── Paleta ──
        speed = 680
        if "left"  in self.keys or "a" in self.keys:
            self.pad_x -= speed * dt
        if "right" in self.keys or "d" in self.keys:
            self.pad_x += speed * dt
        # Ratón suave
        target = self.mouse_x - self.pad_w // 2
        self.pad_x = lerp(self.pad_x, target, min(1, dt * 18))
        self.pad_x = clamp(self.pad_x, 0, W - self.pad_w)

        # ── Bola en paleta ──
        if hasattr(self, "ball_on_pad") and self.ball_on_pad:
            for b in self.balls:
                b.x = self.pad_x + self.pad_w // 2
                b.y = self.pad_y - BALL_R - 2
            return

        # ── Factor velocidad ──
        spd_factor = 0.55 if self.slow_timer > 0 else 1.0
        if self.slow_timer > 0: self.slow_timer -= dt

        # ── Bolas ──
        for ball in self.balls:
            # Escalar velocidad
            target_spd = Ball.BASE_SPEED * spd_factor
            s = ball.speed()
            if abs(s - target_spd) > 20:
                ball.normalize_speed(lerp(s, target_spd, dt*3))

            ball.update(dt, self.pad_x, self.pad_y, self.pad_w)
            if not ball.active:
                continue

            # Colisión con ladrillos
            self._check_ball_bricks(ball)

        # Eliminar bolas muertas
        self.balls = [b for b in self.balls if b.active]
        if not self.balls:
            self.lives -= 1
            self._explode_pad()
            if self.lives <= 0:
                self.state = "gameover"
                self._spawn_particles_burst(W//2, H//2, "#ff2d78", 80)
            else:
                self.state = "dead"
                self.root.after(1200, self._respawn)

        # ── Lasers ──
        if self.laser_active:
            self.laser_timer -= dt
            if self.laser_timer <= 0:
                self.laser_active = False
            # Disparar cada 0.18s
            if not hasattr(self, "_laser_cd"):
                self._laser_cd = 0
            self._laser_cd -= dt
            if self._laser_cd <= 0:
                self._laser_cd = 0.18
                lx = self.pad_x + 6
                rx = self.pad_x + self.pad_w - 6
                self.lasers.append(Laser(lx, self.pad_y))
                self.lasers.append(Laser(rx, self.pad_y))

        for laser in self.lasers:
            laser.update(dt)
            if not laser.active: continue
            for brick in self.bricks[:]:
                bx1,by1,bx2,by2 = brick.rect()
                if bx1 <= laser.x <= bx2 and by1 <= laser.y <= by2:
                    laser.active = False
                    destroyed = brick.hit()
                    if destroyed:
                        self._on_brick_destroyed(brick)
                    break
        self.lasers = [l for l in self.lasers if l.active]

        # ── Power-ups ──
        for pu in self.powerups:
            pu.update(dt)
            if not pu.active: continue
            px1,py1,px2,py2 = pu.rect()
            if (px2 >= self.pad_x and px1 <= self.pad_x + self.pad_w and
                py2 >= self.pad_y and py1 <= self.pad_y + PAD_H):
                self._apply_powerup(pu.type)
                pu.active = False
                self._spawn_particles_burst(pu.x, pu.y, POWERUP_COLORS[pu.type], 20)
        self.powerups = [p for p in self.powerups if p.active]

        # ── Ladrillos ──
        for b in self.bricks:
            b.update(dt)

        # ── Partículas ──
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

        # ── Combo decay ──
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        # ── Nivel completado ──
        destructible = [b for b in self.bricks if b.special != "indestructible"]
        if not destructible:
            self._level_complete()

    def _check_ball_bricks(self, ball):
        if ball.laser:
            return
        for brick in self.bricks[:]:
            bx1,by1,bx2,by2 = brick.rect()
            bx1 += brick.shake_x; bx2 += brick.shake_x

            # AABB vs círculo
            cx = clamp(ball.x, bx1, bx2)
            cy = clamp(ball.y, by1, by2)
            dx = ball.x - cx
            dy = ball.y - cy
            dist = math.hypot(dx, dy)
            if dist >= BALL_R:
                continue

            # Reflexión
            if abs(dx) > abs(dy):
                ball.vx = -ball.vx
                ball.x  = bx1 - BALL_R if ball.vx < 0 else bx2 + BALL_R
            else:
                ball.vy = -ball.vy
                ball.y  = by1 - BALL_R if ball.vy < 0 else by2 + BALL_R

            destroyed = brick.hit()
            if destroyed:
                self._on_brick_destroyed(brick)
            else:
                self._spawn_particles_burst(
                    (bx1+bx2)//2, (by1+by2)//2, brick.glow(), 5)
            break

    def _on_brick_destroyed(self, brick):
        self.bricks.remove(brick)
        cx = brick.x + BRICK_W//2
        cy = brick.y + BRICK_H//2

        # Combo
        self.combo += 1
        self.combo_timer = 1.8
        pts = 10 * self.combo * self.level
        self.score += pts
        if self.score > self.hi_score:
            self.hi_score = self.score

        # Partículas
        self._spawn_particles_burst(cx, cy, brick.glow(), 18)

        # Score float
        self._add_score_float(cx, cy, pts)

        # Power-up
        if brick.special == "powerup":
            ptype = random.choice(POWERUP_TYPES)
            self.powerups.append(PowerUp(cx, cy, ptype))

    def _level_complete(self):
        self.state = "win"
        self.score += 500 * self.level
        self._spawn_particles_burst(W//2, H//3, "#ffd700", 100)
        self.root.after(2200, self._next_level)

    def _next_level(self):
        self.level += 1
        self.combo  = 0
        self._start_level()

    def _apply_powerup(self, ptype):
        if ptype == "wide":
            self.pad_w = min(PAD_W * 1.7, 200)
            self.root.after(8000, lambda: setattr(self, "pad_w", PAD_W))
        elif ptype == "small":
            self.pad_w = max(PAD_W * 0.55, 44)
            self.root.after(6000, lambda: setattr(self, "pad_w", PAD_W))
        elif ptype == "multi":
            new_balls = []
            for b in self.balls[:3]:
                ang = math.atan2(b.vy, b.vx)
                for da in [-0.4, 0.4]:
                    nb = Ball(b.x, b.y,
                              math.cos(ang+da)*b.speed(),
                              math.sin(ang+da)*b.speed())
                    new_balls.append(nb)
            self.balls.extend(new_balls)
        elif ptype == "slow":
            self.slow_timer = 7.0
        elif ptype == "laser":
            self.laser_active = True
            self.laser_timer  = 9.0
        elif ptype == "life":
            self.lives = min(self.lives + 1, 6)

    def _explode_pad(self):
        for _ in range(30):
            self._spawn_particles_burst(
                self.pad_x + random.uniform(0, self.pad_w),
                self.pad_y + PAD_H//2, C_PAD, 1)


    def __init_score_floats(self):
        if not hasattr(self, "_score_floats"):
            self._score_floats = []

    def _add_score_float(self, x, y, pts):
        self.__init_score_floats()
        self._score_floats.append([x, y, pts, 1.2])


    def _spawn_particles_burst(self, x, y, color, n):
        for _ in range(n):
            self.particles.append(Particle(x, y, color))


    def _render(self):
        cv = self.cv
        cv.delete("all")

        self._draw_background()

        if self.state == "title":
            self._draw_title_screen()
            return

        self._draw_bricks()
        self._draw_particles()
        self._draw_powerups()
        self._draw_lasers()
        self._draw_balls()
        self._draw_pad()
        self._draw_hud()
        self._draw_score_floats()

        if self.state == "paused":
            self._draw_overlay("⏸  PAUSA", "Presiona P para continuar", "#ffd700")
        elif self.state == "dead":
            self._draw_overlay("💀  PERDISTE UNA VIDA", f"Vidas restantes: {self.lives}", "#ff2d78")
        elif self.state == "win":
            self._draw_overlay(f"✨  NIVEL {self.level} COMPLETADO!", f"+{500*self.level} puntos bonus", "#00f5ff")
        elif self.state == "gameover":
            self._draw_game_over()


    def _draw_background(self):
        cv = self.cv
        # Gradiente cielo (rectángulos)
        for i in range(20):
            t  = i / 19
            y0 = int(t * H * 0.6)
            y1 = int((t+0.05) * H * 0.6) + 2
            r = int(lerp(7, 30, t))
            g = int(lerp(7, 5,  t))
            b = int(lerp(26, 40, t))
            cv.create_rectangle(0, y0, W, y1, fill=rgb_to_hex(r,g,b), outline="")

        # Sol / luna degradado
        sun_y  = int(H * 0.38)
        sun_r  = 70
        for i in range(sun_r, 0, -4):
            t = i / sun_r
            r = int(lerp(255, 200, t))
            g = int(lerp(80,  20,  t))
            b = int(lerp(120, 60,  t))
            cv.create_oval(W//2-i, sun_y-i, W//2+i, sun_y+i,
                           fill=rgb_to_hex(r,g,b), outline="")

        # Líneas del sol
        for k in range(8):
            y = sun_y + k * 10 + 6
            if y > sun_y + sun_r: break
            dx = math.sqrt(max(0, sun_r**2 - (y-sun_y)**2))
            lw = max(1, int(3*(1-k/8)))
            cv.create_line(W//2-dx, y, W//2+dx, y, fill="#07071a", width=lw)

        # Estrellas
        ph = self.bg_phase
        for (sx, sy, sr, sc) in self.stars:
            twinkle = 0.5 + 0.5*math.sin(ph*3 + sx*0.1)
            if sy > H*0.45: continue
            a = int(twinkle * 180)
            r2 = sr * twinkle
            col = blend(sc, C_BG, 1 - twinkle*0.8)
            cv.create_oval(sx-r2, sy-r2, sx+r2, sy+r2, fill=col, outline="")

        # Grid perspectiva
        grid_top = H * 0.58
        # Piso
        cv.create_rectangle(0, grid_top, W, H, fill="#080818", outline="")

        glow_col = blend("#ff2d78", "#a855f7", 0.5 + 0.5*math.sin(ph))

        # Líneas horizontales
        for i in range(14):
            t  = (i / 13) ** 1.5
            y  = lerp(grid_top, H, t)
            # Perspectiva: alpha decrece hacia el horizonte
            alpha = t
            col   = blend(glow_col, "#080818", 1 - alpha * 0.6)
            cv.create_line(0, y, W, y, fill=col, width=max(1,int(alpha*2)))

        # Líneas verticales (convergen)
        vp_x = W // 2
        for i in range(17):
            bx = i * (W/16)
            alpha = 1 - abs(bx - vp_x) / (W/2)
            col = blend(glow_col, "#080818", 1 - alpha*0.5)
            cv.create_line(bx, H, vp_x, grid_top, fill=col, width=1)

        # Línea horizonte brillante
        cv.create_line(0, grid_top, W, grid_top, fill=glow_col, width=2)
        cv.create_line(0, grid_top+1, W, grid_top+1,
                       fill=blend(glow_col, C_BG, 0.7), width=1)

        # Zona de juego lateral tenue
        cv.create_line(2, 60, 2, grid_top, fill="#1a1a40", width=2)
        cv.create_line(W-2, 60, W-2, grid_top, fill="#1a1a40", width=2)


    def _draw_bricks(self):
        cv = self.cv
        for brick in self.bricks:
            bx1,by1,bx2,by2 = brick.rect()
            sx = brick.shake_x
            bx1+=sx; bx2+=sx

            fill = brick.fill()
            glow = brick.glow()

            # Sombra
            cv.create_rectangle(bx1+3,by1+3,bx2+3,by2+3,
                                 fill=blend(fill, C_BG, 0.7), outline="")

            # Glow exterior
            if brick.hit_anim > 0:
                t = brick.hit_anim
                cv.create_rectangle(bx1-3,by1-3,bx2+3,by2+3,
                                     fill="", outline=blend(glow,"#ffffff",t),
                                     width=int(1+t*3))

            # Cuerpo
            cv.create_rectangle(bx1,by1,bx2,by2, fill=fill, outline="")

            # Borde superior brillante (iluminación)
            cv.create_line(bx1+1,by1+1, bx2-1,by1+1,
                           fill=blend(glow,"#ffffff",0.5), width=1)
            cv.create_line(bx1+1,by1+1, bx1+1,by2-1,
                           fill=blend(glow,"#ffffff",0.3), width=1)

            # Borde outline
            cv.create_rectangle(bx1,by1,bx2,by2, fill="", outline=glow, width=1)

            # HP restante
            if brick.max_hp > 1 and brick.special != "indestructible":
                for h in range(brick.hp):
                    dot_x = bx1 + 5 + h * 8
                    dot_y = by1 + BRICK_H//2
                    cv.create_oval(dot_x-3,dot_y-3,dot_x+3,dot_y+3,
                                   fill="#ffffff", outline="")

            # Indestructible
            if brick.special == "indestructible":
                cv.create_text((bx1+bx2)//2, (by1+by2)//2,
                               text="◆", fill="#ccccee",
                               font=("Courier New", 10, "bold"))

            # Power-up indicator
            if brick.special == "powerup":
                t2 = (math.sin(time.time()*4)+1)/2
                col2 = blend("#ffd700","#ff2d78",t2)
                cv.create_text((bx1+bx2)//2, (by1+by2)//2,
                               text="★", fill=col2,
                               font=("Courier New", 9, "bold"))


    def _draw_particles(self):
        cv = self.cv
        for p in self.particles:
            col = p.alpha_color()
            r   = max(1, p.r * (p.life/p.max_life))
            if p.shape == "circle":
                cv.create_oval(p.x-r,p.y-r,p.x+r,p.y+r, fill=col, outline="")
            elif p.shape == "rect":
                a = p.angle
                cos_a, sin_a = math.cos(a)*r, math.sin(a)*r
                pts = [
                    p.x+cos_a-sin_a, p.y+sin_a+cos_a,
                    p.x+cos_a+sin_a, p.y+sin_a-cos_a,
                    p.x-cos_a+sin_a, p.y-sin_a-cos_a,
                    p.x-cos_a-sin_a, p.y-sin_a+cos_a,
                ]
                cv.create_polygon(*pts, fill=col, outline="")
            else:  # spark
                ex = p.x + p.vx*0.015
                ey = p.y + p.vy*0.015
                cv.create_line(p.x,p.y,ex,ey, fill=col, width=max(1,int(r)))


    def _draw_powerups(self):
        cv = self.cv
        for pu in self.powerups:
            t = math.sin(pu.pulse)
            scale = 1 + 0.12*t
            col = POWERUP_COLORS[pu.type]
            r = 18 * scale
            # Glow
            cv.create_oval(pu.x-r-3,pu.y-12-3,pu.x+r+3,pu.y+12+3,
                           fill=blend(col, C_BG, 0.6), outline="")
            # Cápsula
            cv.create_oval(pu.x-r,pu.y-11,pu.x+r,pu.y+11, fill=col, outline="")
            cv.create_oval(pu.x-r,pu.y-11,pu.x+r,pu.y+11,
                           fill="", outline=blend(col,"#ffffff",0.5), width=1)
            # Icono
            cv.create_text(pu.x, pu.y, text=POWERUP_ICONS[pu.type],
                           fill="#000000", font=("Courier New", 10, "bold"))


    def _draw_lasers(self):
        cv = self.cv
        for laser in self.lasers:
            t = (math.sin(time.time()*20)+1)/2
            col = blend("#ff2d78","#ffffff",t*0.5)
            cv.create_line(laser.x, laser.y, laser.x, laser.y-22,
                           fill=col, width=3)
            cv.create_line(laser.x, laser.y, laser.x, laser.y-22,
                           fill=blend(col,"#ffffff",0.4), width=1)


    def _draw_balls(self):
        cv = self.cv
        for ball in self.balls:
            # Trail
            for i, (tx,ty) in enumerate(ball.trail):
                t = i / len(ball.trail)
                r = BALL_R * t * 0.7
                col = blend("#00f5ff", C_BG, 1-t*0.6)
                if r > 0.5:
                    cv.create_oval(tx-r,ty-r,tx+r,ty+r, fill=col, outline="")

            # Glow
            for gr in [BALL_R+6, BALL_R+3]:
                gcol = blend("#00f5ff", C_BG, 0.6)
                cv.create_oval(ball.x-gr,ball.y-gr,ball.x+gr,ball.y+gr,
                               fill=gcol, outline="")

            # Bola
            cv.create_oval(ball.x-BALL_R,ball.y-BALL_R,
                           ball.x+BALL_R,ball.y+BALL_R,
                           fill="#ffffff", outline="#00f5ff", width=1)

            # Brillo
            cv.create_oval(ball.x-BALL_R+2,ball.y-BALL_R+2,
                           ball.x-BALL_R+6,ball.y-BALL_R+6,
                           fill="#ccffff", outline="")


    def _draw_pad(self):
        cv = self.cv
        px = self.pad_x
        py = self.pad_y
        pw = self.pad_w

        col = C_PAD
        if self.laser_active:
            t = (math.sin(time.time()*8)+1)/2
            col = blend("#ff2d78","#ffd700",t)

        # Sombra
        cv.create_rectangle(px+4,py+4,px+pw+4,py+PAD_H+4,
                             fill=blend(col, C_BG, 0.7), outline="")
        # Glow
        for g in [6, 3]:
            cv.create_rectangle(px-g,py-g,px+pw+g,py+PAD_H+g,
                                 fill=blend(col,C_BG,0.75), outline="")
        # Cuerpo
        cv.create_rectangle(px,py,px+pw,py+PAD_H, fill=col, outline="")
        # Borde superior brillante
        cv.create_line(px+1,py+1, px+pw-1,py+1, fill=blend(col,"#ffffff",0.6), width=2)
        # Outline
        cv.create_rectangle(px,py,px+pw,py+PAD_H,
                             fill="", outline=blend(col,"#ffffff",0.4), width=1)

        # Cañones laser
        if self.laser_active:
            for lx in [px+4, px+pw-4]:
                cv.create_rectangle(lx-3,py-8,lx+3,py,
                                    fill="#ffd700", outline="#ffaa00")


    def _draw_hud(self):
        cv  = self.cv
        ph  = self.bg_phase

        # Barra superior
        cv.create_rectangle(0,0,W,54, fill="#07071a", outline="")
        cv.create_line(0,54,W,54, fill=C_HUD, width=1)

        # Score
        cv.create_text(14, 14, text="SCORE", anchor="w",
                       fill=TEXT_DIM, font=("Courier New", 8))
        cv.create_text(14, 32, text=f"{self.score:08d}", anchor="w",
                       fill=C_HUD, font=("Courier New", 16, "bold"))

        # Hi-Score
        cv.create_text(W//2, 14, text="HI-SCORE", anchor="center",
                       fill=TEXT_DIM, font=("Courier New", 8))
        cv.create_text(W//2, 32, text=f"{self.hi_score:08d}", anchor="center",
                       fill=ACCENT_GOLD if self.hi_score > 0 else TEXT_DIM,
                       font=("Courier New", 16, "bold"))

        # Nivel
        cv.create_text(W-14, 14, text=f"NIVEL", anchor="e",
                       fill=TEXT_DIM, font=("Courier New", 8))
        cv.create_text(W-14, 32, text=f"{self.level:02d}", anchor="e",
                       fill="#a855f7", font=("Courier New", 16, "bold"))

        # Vidas
        for i in range(self.lives):
            hx = 20 + i*22
            cv.create_text(hx, H-18, text="♥",
                           fill=C_PAD, font=("Courier New", 14, "bold"))

        # Combo
        if self.combo >= 3 and self.combo_timer > 0:
            t = self.combo_timer / 1.8
            col = blend("#ffd700","#ff2d78", 1-t)
            cv.create_text(W//2, H-22, text=f"COMBO ×{self.combo}",
                           fill=col, font=("Courier New", 13, "bold"))

        # Power-ups activos
        px_i = W - 10
        if self.laser_active:
            t2 = self.laser_timer / 9.0
            cv.create_text(px_i, H-42, text=f"LASER {self.laser_timer:.0f}s",
                           anchor="e", fill="#ff2d78",
                           font=("Courier New", 9, "bold"))
            px_i -= 0
        if self.slow_timer > 0:
            cv.create_text(px_i, H-26, text=f"SLOW {self.slow_timer:.0f}s",
                           anchor="e", fill="#00ff88",
                           font=("Courier New", 9, "bold"))


    def _draw_score_floats(self):
        self.__init_score_floats()
        cv  = self.cv
        dt2 = 1/FPS
        alive = []
        for sf in self._score_floats:
            x, y, pts, life = sf
            sf[1] -= 40 * dt2
            sf[3] -= dt2
            if sf[3] > 0:
                alpha = min(1, sf[3])
                col   = blend("#ffd700", C_BG, 1-alpha)
                cv.create_text(x, y, text=f"+{pts}",
                               fill=col, font=("Courier New", 11, "bold"))
                alive.append(sf)
        self._score_floats = alive


    def _draw_overlay(self, title, sub, color):
        cv = self.cv
        cv.create_rectangle(0, H//2-60, W, H//2+60,
                            fill=blend(C_BG,"#000000",0.3), outline="")
        cv.create_rectangle(60, H//2-55, W-60, H//2+55,
                            fill=C_BG, outline=color, width=2)
        cv.create_text(W//2, H//2-18, text=title, fill=color,
                       font=("Courier New", 18, "bold"))
        cv.create_text(W//2, H//2+16, text=sub, fill=TEXT_DIM,
                       font=("Courier New", 11))

    def _draw_game_over(self):
        cv = self.cv
        # Fondo semitransparente
        cv.create_rectangle(0,0,W,H, fill=blend(C_BG,"#000000",0.2), outline="")
        cv.create_rectangle(80,H//2-130,W-80,H//2+140,
                            fill="#07071a", outline=C_PAD, width=2)

        t = (math.sin(self.bg_phase*2)+1)/2
        tc = blend("#ff2d78","#ffd700",t)

        cv.create_text(W//2, H//2-100, text="GAME OVER",
                       fill=tc, font=("Courier New", 32, "bold"))
        cv.create_line(100,H//2-72,W-100,H//2-72, fill=C_PAD, width=1)
        cv.create_text(W//2, H//2-48, text=f"PUNTUACIÓN FINAL",
                       fill=TEXT_DIM, font=("Courier New", 10))
        cv.create_text(W//2, H//2-18, text=f"{self.score:08d}",
                       fill=C_HUD, font=("Courier New", 28, "bold"))
        cv.create_text(W//2, H//2+22, text=f"RÉCORD: {self.hi_score:08d}",
                       fill="#ffd700", font=("Courier New", 12))
        cv.create_text(W//2, H//2+60, text=f"Nivel alcanzado: {self.level}",
                       fill=TEXT_DIM, font=("Courier New", 11))
        cv.create_line(100,H//2+86,W-100,H//2+86, fill=C_PAD, width=1)
        cv.create_text(W//2, H//2+108, text="Presiona  R  para reiniciar",
                       fill=TEXT_DIM, font=("Courier New", 10))


    def _show_title(self):
        self.state = "title"
        if self.frame_id:
            self.root.after_cancel(self.frame_id)
        self.last_time = time.time()
        self._loop()

    def _draw_title_screen(self):
        cv  = self.cv
        ph  = self.bg_phase
        t   = (math.sin(ph*1.5)+1)/2
        tc  = blend("#ff2d78","#00f5ff",t)

        # Logo
        cv.create_text(W//2, 200, text="ARKANOID",
                       fill=tc, font=("Courier New", 58, "bold"))
        # Sombra glitch
        cv.create_text(W//2+3, 203, text="ARKANOID",
                       fill=blend("#ff2d78",C_BG,0.5),
                       font=("Courier New", 58, "bold"))

        cv.create_text(W//2, 256, text="· SYNTHWAVE 80s EDITION ·",
                       fill=blend("#a855f7","#00f5ff",t),
                       font=("Courier New", 13))

        # Línea decorativa
        cv.create_line(W//2-180, 278, W//2+180, 278, fill="#ff2d78", width=1)

        # Power-ups descripción
        items = [
            ("►◄ WIDE",   "Paleta más ancha",      "#ffd700"),
            ("×3 MULTI",  "Triplica las bolas",    "#00f5ff"),
            ("▼▼ SLOW",   "Bolas lentas 7s",       "#00ff88"),
            ("↑↑ LASER",  "Cañones láser 9s",      "#ff2d78"),
            ("♥  VIDA",   "Vida extra",             "#ff80aa"),
            ("◄► SMALL",  "Paleta pequeña 6s",     "#a855f7"),
        ]
        for i,(icon,desc,col) in enumerate(items):
            row = i // 2
            col_idx = i % 2
            x = W//2 - 130 + col_idx * 260
            y = 320 + row * 38
            cv.create_rectangle(x-90,y-14,x+90,y+14,
                                fill=blend(col,C_BG,0.85), outline=col, width=1)
            cv.create_text(x-60, y, text=icon, fill=col,
                           font=("Courier New", 10, "bold"), anchor="w")
            cv.create_text(x+10, y, text=desc, fill=TEXT_DIM,
                           font=("Courier New", 9), anchor="w")

        # Controles
        cv.create_text(W//2, 455, text="CONTROLES",
                       fill=TEXT_DIM, font=("Courier New", 9))
        ctrl = "Ratón / ← → :  mover    |    Espacio / Clic:  lanzar    |    P:  pausa"
        cv.create_text(W//2, 474, text=ctrl,
                       fill=TEXT_DIM, font=("Courier New", 9))

        # Start
        pulse = 0.6 + 0.4*math.sin(ph*3)
        sc    = blend("#ffffff",C_BG,1-pulse)
        cv.create_text(W//2, 530, text="▶  CLICK O ESPACIO PARA JUGAR  ◀",
                       fill=sc, font=("Courier New", 14, "bold"))

        # Partículas decorativas en título
        self._draw_particles()

    # ── TEXTO DIM helper ────────────────────────────────────────────────────


# Constante local para texto apagado
TEXT_DIM  = "#5555aa"
ACCENT_GOLD = "#ffd700"


# ══════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    root.title("ARKANOID · SYNTHWAVE 80s")
    root.configure(bg="#07071a")
    root.resizable(False, False)

    app = Arkanoid(root)

    # Spawn partículas decorativas en título
    for _ in range(60):
        app.particles.append(
            Particle(random.uniform(0,W), random.uniform(0,H*0.55),
                     random.choice(["#ff2d78","#00f5ff","#ffd700","#a855f7","#00ff88"])))

    root.mainloop()
