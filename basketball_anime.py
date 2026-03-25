import pygame
import math
import random
import sys
import urllib.request
import io

# --- Configuración ---
WIDTH, HEIGHT = 900, 650
FPS = 60
GRAVITY = 0.35
BALL_RADIUS = 18
BOUNCE_DAMPING = 0.55
BOARD_BOUNCE   = 0.5

# Colores
WHITE       = (255, 255, 255)
ORANGE      = (230, 100,  20)
DARK_ORANGE = (160,  60,   5)
WOOD        = (180, 110,  50)
WOOD_DARK   = (140,  80,  30)
SKY         = ( 15,  15,  40)
NEON_PINK   = (255,  80, 180)
NEON_CYAN   = ( 80, 255, 240)
GOLD        = (255, 215,   0)
GRAY        = ( 80,  80, 100)
NET_COLOR   = (220, 220, 220)
RIM_RED     = (210,  45,  45)

# ══════════════════════════════════════════════════════════════
#  IMÁGENES — agrega rutas locales o URLs aquí
#  Ejemplos de ruta local:  r"C:/Users/madma/Pictures/waifu1.jpg"
#                           "waifu1.jpg"  (misma carpeta que el .py)
# ══════════════════════════════════════════════════════════════
WAIFU_API_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Anime_Girl.svg/960px-Anime_Girl.svg.png",
    "https://rukminim2.flixcart.com/image/480/480/kuof5ow0/wall-decoration/i/s/c/anime-anime-girls-sweater-kantai-collection-wallpaper-1-p022-original-imag7qxqayhgwbae.jpeg?q=90",
    "https://m.media-amazon.com/images/I/71Sg8jSiRyL._AC_UF894,1000_QL80_.jpg",
    "https://images.stockcake.com/public/5/6/3/56302345-c0b1-4da4-8795-0297c928d97d_medium/elegant-anime-girl-stockcake.jpg",
    "https://png.pngtree.com/png-clipart/20250318/original/pngtree-anime-girl-embracing-her-stomach-in-a-delicate-expression-image-clipart-png-image_20679807.png",
    "https://m.media-amazon.com/images/I/51Q33uZVByL._AC_UF894,1000_QL80_.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Anime_Girl.svg/960px-Anime_Girl.svg.png",
    "https://rukminim2.flixcart.com/image/480/480/kuof5ow0/wall-decoration/i/s/c/anime-anime-girls-sweater-kantai-collection-wallpaper-1-p022-original-imag7qxqayhgwbae.jpeg?q=90",
]

WAIFU_NAMES = [
    "Hinata-chan ♡", "Neko-senpai ✨", "Shinobu 🦋",
    "Megumin 💥",    "Zero Two 💘",    "Rem-chan ⭐",
    "Asuna-hime 🌸", "Nezuko 🎋",
]


def load_image_from_api(src):
    """Carga una imagen desde ruta local o URL http/https."""
    try:
        # ── Ruta local ──
        if not src.startswith("http"):
            print(f"[imagen] Cargando local: {src}")
            surface = pygame.image.load(src).convert()
            print(f"[imagen] OK local: {src}")
            return pygame.transform.scale(surface, (220, 300))
        # ── URL remota ──
        print(f"[imagen] Descargando: {src[:70]}...")
        req = urllib.request.Request(src, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "image/webp,image/jpeg,image/png,image/gif,*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
        })
        img_data = urllib.request.urlopen(req, timeout=12).read()
        print(f"[imagen] Descargado {len(img_data)} bytes, cargando en pygame...")
        surface = pygame.image.load(io.BytesIO(img_data)).convert()
        print(f"[imagen] OK! tamaño: {surface.get_size()}")
        return pygame.transform.scale(surface, (220, 300))
    except Exception as e:
        print(f"[imagen] FALLO {src[:60]}: {e}")
        return _make_placeholder()


def _make_placeholder():
    surf = pygame.Surface((220, 300))
    for y in range(300):
        r = int(200 * (1 - y / 300))
        g = int(60  + 100 * (y / 300))
        b = int(180 +  60 * (y / 300))
        pygame.draw.line(surf, (r, g, b), (0, y), (220, y))
    f = pygame.font.SysFont("Arial", 32, bold=True)
    surf.blit(f.render("(◕‿◕✿)", True, WHITE),    (20, 120))
    surf.blit(f.render("Waifu!",  True, NEON_PINK), (60, 165))
    return surf


# ════════════════════════════════════════════
#  BALL  —  física con rebotes reales
# ════════════════════════════════════════════
class Ball:
    def __init__(self, x, y):
        self.x  = float(x)
        self.y  = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.launched = False
        self.scored   = False
        self.bounces  = 0
        self.angle    = 0.0

    def launch(self, tx, ty):
        dx, dy  = tx - self.x, ty - self.y
        t       = 42
        self.vx = dx / t
        self.vy = dy / t - 0.5 * GRAVITY * t
        self.launched = True

    def update(self, hoop):
        if not self.launched:
            return
        self.vy   += GRAVITY
        self.x    += self.vx
        self.y    += self.vy
        self.angle += self.vx * 0.05   # spin visual

        # ── Aro izquierdo ──
        rlx, rly = hoop.x, hoop.y + hoop.rim_h / 2
        if math.hypot(self.x - rlx, self.y - rly) < BALL_RADIUS + 5 and self.bounces < 5:
            self._bounce_off(rlx, rly, BOUNCE_DAMPING)
            self.bounces += 1

        # ── Aro derecho ──
        rrx, rry = hoop.x + hoop.rim_w, hoop.y + hoop.rim_h / 2
        if math.hypot(self.x - rrx, self.y - rry) < BALL_RADIUS + 5 and self.bounces < 5:
            self._bounce_off(rrx, rry, BOUNCE_DAMPING)
            self.bounces += 1

        # ── Tablero (cara izquierda) ──
        bx  = hoop.x + hoop.rim_w + 4
        by1 = hoop.y - 40
        by2 = by1 + hoop.board_h
        if (self.x + BALL_RADIUS >= bx and
                self.x - BALL_RADIUS <= bx + hoop.board_w and
                by1 <= self.y <= by2 and
                self.vx > 0 and self.bounces < 5):
            self.x   = bx - BALL_RADIUS - 1
            self.vx  = -abs(self.vx) * BOARD_BOUNCE
            self.vy *= 0.85
            self.bounces += 1

    def _bounce_off(self, px, py, damping):
        dx, dy = self.x - px, self.y - py
        dist   = math.hypot(dx, dy) or 1
        nx, ny = dx / dist, dy / dist
        dot    = self.vx * nx + self.vy * ny
        self.vx = (self.vx - 2 * dot * nx) * damping
        self.vy = (self.vy - 2 * dot * ny) * damping
        overlap = BALL_RADIUS + 5 - dist
        self.x += nx * (overlap + 1)
        self.y += ny * (overlap + 1)

    def draw(self, screen):
        px, py = int(self.x), int(self.y)
        pygame.draw.circle(screen, (10, 10, 30), (px + 4, py + 4), BALL_RADIUS)
        pygame.draw.circle(screen, ORANGE,       (px, py),          BALL_RADIUS)
        # Líneas que giran con la pelota
        for off in [0, math.pi / 2]:
            a = self.angle + off
            ax = px + int(math.cos(a) * BALL_RADIUS)
            ay = py + int(math.sin(a) * BALL_RADIUS)
            bx = px - int(math.cos(a) * BALL_RADIUS)
            by = py - int(math.sin(a) * BALL_RADIUS)
            pygame.draw.line(screen, DARK_ORANGE, (ax, ay), (bx, by), 2)
        pygame.draw.circle(screen, DARK_ORANGE, (px, py), BALL_RADIUS, 2)


# ════════════════════════════════════════════
#  HOOP
# ════════════════════════════════════════════
class Hoop:
    def __init__(self, x, y):
        self.x        = x
        self.y        = y
        self.rim_w    = 58
        self.rim_h    = 8
        self.board_w  = 12
        self.board_h  = 85
        self.pole_h   = 210
        self.flash    = 0

    def score_flash(self): self.flash = 14

    def draw(self, screen):
        # Poste
        pygame.draw.rect(screen, GRAY,
            (self.x + self.rim_w + self.board_w + 6, self.y - 30, 14, self.pole_h),
            border_radius=4)
        # Tablero
        bc = (255, 255, 200) if self.flash else (225, 225, 255)
        bl = GOLD            if self.flash else NEON_CYAN
        pygame.draw.rect(screen, bc,
            (self.x + self.rim_w + 4, self.y - 40, self.board_w, self.board_h),
            border_radius=3)
        pygame.draw.rect(screen, bl,
            (self.x + self.rim_w + 4, self.y - 40, self.board_w, self.board_h),
            3, border_radius=3)
        # Cuadrado de tiro en el tablero
        pygame.draw.rect(screen, bl,
            (self.x + self.rim_w + 4, self.y - 20, self.board_w, 35), 2)

        # Aro
        rc = GOLD   if self.flash else RIM_RED
        rh = (255, 180, 0) if self.flash else (255, 80, 80)
        pygame.draw.rect(screen, rc, (self.x, self.y, self.rim_w, self.rim_h), border_radius=4)
        pygame.draw.rect(screen, rh, (self.x, self.y, self.rim_w, self.rim_h), 2, border_radius=4)

        # Red
        ns   = 7
        ntop = self.y + self.rim_h
        nbot = ntop + 52
        for i in range(ns + 1):
            fx = self.x + i * (self.rim_w // ns)
            bx = self.x + self.rim_w // 2 + (i - ns // 2) * 3
            pygame.draw.line(screen, NET_COLOR, (fx, ntop), (bx, nbot), 1)
        for j in range(4):
            ty = ntop + 13 * (j + 1)
            sp = j * 2
            pygame.draw.line(screen, NET_COLOR,
                (self.x + 3 + sp, ty), (self.x + self.rim_w - 3 - sp, ty), 1)
        if self.flash: self.flash -= 1

    def check_score(self, ball):
        cx = self.x + self.rim_w / 2
        cy = self.y + self.rim_h / 2
        return (abs(ball.x - cx) < self.rim_w / 2 - BALL_RADIUS + 8 and
                abs(ball.y - cy) < 20 and
                ball.vy > 1.5)


# ════════════════════════════════════════════
#  HELPERS UI
# ════════════════════════════════════════════
class ScorePopup:
    def __init__(self, x, y, text, color):
        self.x, self.y, self.text, self.color = x, y, text, color
        self.life = 90
    def update(self): self.life -= 1; self.y -= 1.4
    def draw(self, screen, font):
        a = max(0, int(255 * self.life / 90))
        s = font.render(self.text, True, self.color)
        s.set_alpha(a)
        screen.blit(s, (self.x - s.get_width() // 2, int(self.y)))


class WaifuDisplay:
    def __init__(self, image, name):
        self.image, self.name = image, name
        self.life  = 260
        self.x     = WIDTH // 2 - 110
        self.y     = HEIGHT // 2 - 160
        self.scale = 0.0
    def update(self):
        self.life -= 1
        self.scale = min(1.0, self.scale + 0.08)
    def draw(self, screen, font_sm):
        if self.life <= 0: return
        a = 255 if self.life > 50 else int(255 * self.life / 50)
        panel = pygame.Surface((264, 368), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 170))
        pygame.draw.rect(panel, (*NEON_PINK, a), (0, 0, 264, 368), 3, border_radius=14)
        screen.blit(panel, (self.x - 22, self.y - 22))
        img = pygame.transform.scale(self.image,
            (int(220 * self.scale), int(300 * self.scale)))
        screen.blit(img, (self.x + (220 - img.get_width()) // 2,
                          self.y + (300 - img.get_height()) // 2))
        txt = font_sm.render(f"✨ {self.name} ✨", True, NEON_PINK)
        txt.set_alpha(a)
        screen.blit(txt, (self.x + 110 - txt.get_width() // 2, self.y + 312))


class Particle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        a = random.uniform(0, 2 * math.pi)
        s = random.uniform(2.5, 8)
        self.vx = math.cos(a) * s
        self.vy = math.sin(a) * s - 3.5
        self.color = random.choice([NEON_PINK, NEON_CYAN, GOLD, WHITE, ORANGE, (180, 255, 120)])
        self.life = random.randint(35, 65)
        self.r    = random.randint(3, 8)
    def update(self):
        self.vy += 0.18; self.x += self.vx; self.y += self.vy; self.life -= 1
    def draw(self, screen):
        a = max(0, int(255 * self.life / 65))
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (self.r, self.r), self.r)
        screen.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


# ════════════════════════════════════════════
#  CANCHA
# ════════════════════════════════════════════
def draw_court(screen):
    screen.fill(SKY)
    random.seed(42)
    for _ in range(100):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT - 130)
        pygame.draw.circle(screen, (190, 190, 255), (sx, sy), 1)
    # Luna
    pygame.draw.circle(screen, (240, 240, 200), (820, 60), 32)
    pygame.draw.circle(screen, SKY,              (833, 52), 28)
    # Piso madera
    pygame.draw.rect(screen, WOOD, (0, HEIGHT - 100, WIDTH, 100))
    for i in range(0, WIDTH, 42):
        pygame.draw.line(screen, WOOD_DARK, (i, HEIGHT - 100), (i + 21, HEIGHT), 1)
    pygame.draw.line(screen, (220, 180, 80),
        (WIDTH // 2 - 130, HEIGHT - 100), (WIDTH // 2 + 130, HEIGHT - 100), 2)
    pygame.draw.circle(screen, (220, 180, 80), (210, HEIGHT - 100), 65, 2)


# ════════════════════════════════════════════
#  TRAYECTORIA PREDICTIVA
# ════════════════════════════════════════════
def precompute_trajectory(sx, sy, tx, ty, hoop, steps=35):
    pts = []
    t   = 42
    pvx = (tx - sx) / t
    pvy = (ty - sy) / t - 0.5 * GRAVITY * t
    px, py = float(sx), float(sy)
    bx = hoop.x + hoop.rim_w + 4

    for _ in range(steps):
        pvy += GRAVITY
        px  += pvx
        py  += pvy
        if px + BALL_RADIUS >= bx and pvx > 0:
            pvx = -abs(pvx) * BOARD_BOUNCE
        pts.append((int(px), int(py)))
        if py > HEIGHT: break
    return pts


# ════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🏀 Anime Basketball!")
    clock = pygame.time.Clock()

    font_big   = pygame.font.SysFont("Arial", 38, bold=True)
    font_med   = pygame.font.SysFont("Arial", 26, bold=True)
    font_sm    = pygame.font.SysFont("Arial", 20, bold=True)
    font_score = pygame.font.SysFont("Arial", 52, bold=True)

    hoop       = Hoop(610, 225)
    ball_start = (175, HEIGHT - 145)
    ball       = Ball(*ball_start)

    score        = 0
    attempts     = 0
    max_attempts = 10
    popups       = []
    particles    = []
    waifu_disp   = None
    aiming       = False
    trajectory   = []
    game_over    = False
    loaded_imgs  = {}

    def get_image(idx):
        if idx not in loaded_imgs:
            url = WAIFU_API_URLS[idx % len(WAIFU_API_URLS)]
            loaded_imgs[idx] = (load_image_from_api(url),
                                WAIFU_NAMES[idx % len(WAIFU_NAMES)])
        return loaded_imgs[idx]

    running = True
    while running:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False; break
            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    main(); return
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not ball.launched: aiming = True
            if event.type == pygame.MOUSEMOTION and aiming:
                trajectory = precompute_trajectory(*ball_start, mx, my, hoop)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if aiming and not ball.launched:
                    aiming = False
                    ball.launch(mx, my)
                    attempts += 1
                    trajectory = []

        # ── Update ──
        if ball.launched:
            ball.update(hoop)
            if hoop.check_score(ball) and not ball.scored:
                ball.scored = True
                score += 1
                hoop.score_flash()
                popups.append(ScorePopup(hoop.x + 29, hoop.y - 25, "+1  ¡CANASTA! 🏀", GOLD))
                for _ in range(55):
                    particles.append(Particle(hoop.x + 29, hoop.y + 15))
                img, name = get_image(score - 1)
                waifu_disp = WaifuDisplay(img, name)
            if ball.y > HEIGHT + 30 or ball.x < -50 or ball.x > WIDTH + 50:
                if not ball.scored:
                    popups.append(ScorePopup(ball_start[0], ball_start[1] - 30,
                                             "¡Fallaste! 😅", (255, 80, 80)))
                ball = Ball(*ball_start)
                aiming = False; trajectory = []

        for p in popups[:]:
            p.update()
            if p.life <= 0: popups.remove(p)
        for pt in particles[:]:
            pt.update()
            if pt.life <= 0: particles.remove(pt)
        if waifu_disp:
            waifu_disp.update()
            if waifu_disp.life <= 0: waifu_disp = None
        if attempts >= max_attempts and not ball.launched:
            game_over = True

        # ── Draw ──
        draw_court(screen)
        hoop.draw(screen)

        if aiming and trajectory:
            for i, pt in enumerate(trajectory):
                a = max(0, 210 - i * 7)
                r = max(2, 7 - i // 5)
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 210, 60, a), (r, r), r)
                screen.blit(s, (pt[0]-r, pt[1]-r))

        ball.draw(screen)
        for pt in particles: pt.draw(screen)
        if waifu_disp: waifu_disp.draw(screen, font_sm)
        for pop in popups: pop.draw(screen, font_big)

        screen.blit(font_score.render(f"🏀 {score}", True, GOLD), (20, 15))
        screen.blit(font_med.render(f"Tiros: {attempts}/{max_attempts}", True, NEON_CYAN), (20, 75))
        hint = font_sm.render("Clic + mueve para apuntar  •  suelta para lanzar", True, (150, 150, 200))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 32))

        if game_over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 20, 185))
            screen.blit(ov, (0, 0))
            for f, t, c, dy in [
                (font_score, "¡FIN DEL JUEGO!", NEON_PINK, -90),
                (font_big,   f"Puntuación: {score} / {max_attempts}", GOLD, -20),
                (font_med,   "Presiona  R  para reiniciar", NEON_CYAN, 50),
            ]:
                s = f.render(t, True, c)
                screen.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2 + dy))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
