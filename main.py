import pygame
import random
import sys
import time
import math
import os

# ==================== Константи ====================
WIDTH, HEIGHT = 800, 600
FPS = 60
SCROLL_THRESHOLD = HEIGHT // 4
PLATFORM_WIDTH = 120
PLATFORM_HEIGHT = 20
MIN_HORIZONTAL_DISTANCE = 120
MAX_HORIZONTAL_DISTANCE = 280
MIN_VERTICAL_DISTANCE = 80
MAX_VERTICAL_DISTANCE = 140
PLATFORM_CHECK_RADIUS = 100
MAX_PLATFORMS = 30
MAX_ACORNS = 20
ACORN_SIZE = 35
MAX_JUMP_HEIGHT = abs(-22 ** 2) / (2 * 0.8)
MAX_HORIZONTAL_DISTANCE = abs(-22) * 10 / 0.8
JUMP_POWER = -22
GRAVITY = 0.8
MAX_HORIZONTAL_SPEED = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
BROWN = (139, 69, 19)
ACORN_COLOR = (210, 105, 30)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)

# Ініціалізація Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moose Speedrun: Acorn Chase")
clock = pygame.time.Clock()

# Завантаження звукових ефектів і музики
menu_music = pygame.mixer.music.load("menu_music.mp3") if os.path.exists("menu_music.mp3") else None
jump_sound = pygame.mixer.Sound("jump.wav") if os.path.exists("jump.wav") else None
collect_sound = pygame.mixer.Sound("collect.wav") if os.path.exists("collect.wav") else None
break_sound = pygame.mixer.Sound("break.wav") if os.path.exists("break.wav") else None
if menu_music:
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Циклічне відтворення

# UI елементи
FONT = pygame.font.Font(None, 48)  # Збільшено розмір шрифту для логотипу
SMALL_FONT = pygame.font.Font(None, 24)
UI_SURFACE = pygame.Surface((WIDTH, 130))
UI_SURFACE.set_alpha(180)
UI_SURFACE.fill((20, 20, 20))  # Темний фон
INSTRUCTION_BG = pygame.Surface((270, 70))
INSTRUCTION_BG.set_alpha(180)
INSTRUCTION_BG.fill((20, 20, 20))
WARNING_BG = pygame.Surface((300, 25))
WARNING_BG.set_alpha(200)
WARNING_BG.fill((20, 20, 20))
OVERLAY = pygame.Surface((WIDTH, HEIGHT))
OVERLAY.set_alpha(180)
OVERLAY.fill(BLACK)

# ==================== Завантаження ресурсів ====================
def load_image(path, size):
    try:
        if os.path.exists(path):
            image = pygame.image.load(path)
            return pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Помилка завантаження {path}: {e}")
    return None

def load_background():
    bg = load_image("background.png", (WIDTH, HEIGHT))
    if not bg:
        bg = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            color_intensity = int(135 + (120 * y / HEIGHT))
            color = (135, color_intensity, 200)
            pygame.draw.line(bg, color, (0, y), (WIDTH, y))
        print("Використовується резервний фон")
    return bg

def load_moose_image():
    moose = load_image("moose.png", (50, 50))
    if not moose:
        moose = pygame.Surface((50, 50))
        moose.fill(BROWN)
        pygame.draw.ellipse(moose, (101, 67, 33), (15, 25, 25, 20))
        pygame.draw.ellipse(moose, BROWN, (10, 15, 15, 12))
        pygame.draw.line(moose, (160, 82, 45), (12, 10), (8, 5), 2)
        pygame.draw.line(moose, (160, 82, 45), (12, 10), (16, 5), 2)
        pygame.draw.line(moose, (160, 82, 45), (20, 12), (16, 7), 2)
        pygame.draw.line(moose, (160, 82, 45), (20, 12), (24, 7), 2)
        pygame.draw.line(moose, (101, 67, 33), (20, 40), (18, 48), 3)
        pygame.draw.line(moose, (101, 67, 33), (30, 40), (32, 48), 3)
        pygame.draw.circle(moose, BLACK, (15, 20), 2)
        pygame.draw.circle(moose, WHITE, (16, 19), 1)
        print("Використовується резервний лось")
    return moose

def load_acorn_image():
    acorn = load_image("acorns.png", (ACORN_SIZE, ACORN_SIZE))
    if not acorn:
        acorn = pygame.Surface((ACORN_SIZE, ACORN_SIZE))
        acorn.fill(ACORN_COLOR)
        center_x, center_y = ACORN_SIZE // 2, ACORN_SIZE // 2
        pygame.draw.circle(acorn, (160, 82, 45), (center_x, center_y + 5), 12)
        pygame.draw.circle(acorn, (139, 69, 19), (center_x, center_y - 5), 8)
        pygame.draw.circle(acorn, (255, 215, 0), (center_x - 3, center_y - 3), 3)
        print("Використовується резервний жолудь")
    return acorn

def load_platform_image():
    platform = load_image("my_platform.png", (PLATFORM_WIDTH, PLATFORM_HEIGHT))
    if not platform:
        platform = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        platform.fill(GREEN)
        print("Використовується резервна платформа")
    return platform

def load_break_animation():
    frames = []
    for i in range(1, 4):
        frame = load_image(f"my_platform_break{i}.png", (PLATFORM_WIDTH, PLATFORM_HEIGHT))
        if frame:
            frames.append(frame)
    return frames if frames else [load_platform_image()]

background_image = load_background()
moose_image = load_moose_image()
acorn_image = load_acorn_image()
platform_image = load_platform_image()
break_frames = load_break_animation()

# ==================== Клас Гравця ====================
class Moose(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = [moose_image, pygame.transform.flip(moose_image, True, False)]
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 150))
        self.speed_x = 0
        self.speed_y = 0
        self.on_ground = False
        self.score = 0
        self.health = 3
        self.current_platform = None
        self.platform_stand_time = 0
        self.last_platform = None
        self.animation_frame = 0
        self.animation_timer = 0
        self.facing_right = True

    def update(self):
        keys = pygame.key.get_pressed()
        self.speed_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.speed_x = -MAX_HORIZONTAL_SPEED
            if self.facing_right:
                self.facing_right = False
                self.image = self.images[1]
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.speed_x = MAX_HORIZONTAL_SPEED
            if not self.facing_right:
                self.facing_right = True
                self.image = self.images[0]
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.speed_y = JUMP_POWER
            self.on_ground = False
            self.last_platform = self.current_platform
            self.current_platform = None
            self.platform_stand_time = 0
            if jump_sound:
                jump_sound.play()
        self.speed_y += GRAVITY
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0
        if self.on_ground and self.current_platform:
            self.platform_stand_time += 1/FPS
        if self.speed_x != 0:
            self.animation_timer += 1
            if self.animation_timer > 10:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 2
                self.image = self.images[self.animation_frame if self.facing_right else 1]

# ==================== Клас Платформи ====================
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=PLATFORM_WIDTH, height=PLATFORM_HEIGHT, platform_type="normal"):
        super().__init__()
        self.width = width
        self.height = height
        self.platform_type = platform_type
        self.image = platform_image.copy()
        self.breaking_time = 0
        self.is_breaking = False
        self.break_threshold = 6.0
        self.rect = self.image.get_rect(topleft=(x, y))
        self.break_frames = break_frames
        self.current_frame = 0
        if platform_type == "moving":
            self.direction = random.choice([-1, 1])
            self.speed = 2
            self.start_x = x
            self.range = 80

    def update(self):
        if self.platform_type == "moving":
            self.rect.x += self.direction * self.speed
            if abs(self.rect.x - self.start_x) > self.range:
                self.direction *= -1
        if self.is_breaking:
            self.breaking_time += 1/FPS
            if self.breaking_time >= self.break_threshold / len(self.break_frames) * (self.current_frame + 1):
                self.current_frame = min(self.current_frame + 1, len(self.break_frames) - 1)
                self.image = self.break_frames[self.current_frame]
            if self.breaking_time >= self.break_threshold:
                if break_sound:
                    break_sound.play()
                self.kill()

    def start_breaking(self):
        self.is_breaking = True

    def stop_breaking(self):
        self.is_breaking = False
        self.breaking_time = 0
        self.image = platform_image.copy()

# ==================== Клас Жолудя ====================
class Acorn(pygame.sprite.Sprite):
    def __init__(self, x, y, platform):
        super().__init__()
        self.image = acorn_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.platform = platform
        self.relative_x = x - platform.rect.centerx
        self.relative_y = y - platform.rect.top

    def update(self):
        if self.platform and self.platform.alive():
            self.rect.centerx = self.platform.rect.centerx + self.relative_x
            self.rect.top = self.platform.rect.top + self.relative_y
        else:
            self.kill()

# ==================== Клас Частинок ====================
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill((139, 69, 19))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = random.randint(-5, 0)
        self.speed_x = random.randint(-2, 2)
        self.lifetime = 30

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

# ==================== Глобальні змінні ====================
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
acorns = pygame.sprite.Group()
particles = pygame.sprite.Group()
moose = None
highest_y = HEIGHT - 200
last_x = WIDTH // 2
start_time = time.time()
level = 1
max_level = 5
game_over = False
scroll_offset = 0
game_state = "menu"  # "menu", "playing", "game_over"
logo_alpha = 0  # Для анімації логотипу
logo_fade_in = True

# ==================== Функції генерації платформ ====================
def is_position_too_close(x, y, existing_platforms, min_distance=PLATFORM_CHECK_RADIUS):
    for platform in existing_platforms:
        distance = math.sqrt((x - platform.rect.centerx)**2 + (y - platform.rect.centery)**2)
        if distance < min_distance:
            return True
    return False

def find_valid_position(reference_x, reference_y, attempts=20):
    safe_horizontal = int(MAX_HORIZONTAL_DISTANCE * 0.7)
    safe_vertical = int(MAX_JUMP_HEIGHT * 0.6)
    for _ in range(attempts):
        horizontal_offset = random.randint(MIN_HORIZONTAL_DISTANCE, safe_horizontal)
        vertical_offset = random.randint(MIN_VERTICAL_DISTANCE, safe_vertical)
        direction = random.choice([-1, 1])
        new_x = reference_x + (horizontal_offset * direction)
        new_y = reference_y - vertical_offset
        new_x = max(PLATFORM_WIDTH//2 + 20, min(WIDTH - PLATFORM_WIDTH//2 - 20, new_x))
        if not is_position_too_close(new_x, new_y, platforms):
            return new_x, new_y
    return reference_x + random.choice([-150, 150]), reference_y - 100

def create_platform_with_spacing(reference_x, reference_y):
    x, y = find_valid_position(reference_x, reference_y)
    platform_type = "moving" if random.random() < 0.08 else "normal"
    width = PLATFORM_WIDTH + random.randint(20, 60) if random.random() < 0.4 else PLATFORM_WIDTH
    platform = Platform(x - width//2, y, width, PLATFORM_HEIGHT, platform_type)
    all_sprites.add(platform)
    platforms.add(platform)
    if random.random() < 0.7:
        acorn_x = platform.rect.centerx
        acorn_y = platform.rect.top - (ACORN_SIZE // 2)
        acorn = Acorn(acorn_x, acorn_y, platform)
        acorns.add(acorn)
        all_sprites.add(acorn)
    return x, y

def ensure_reachable_platforms(player_x, reference_y):
    left_zone = (player_x - MAX_HORIZONTAL_DISTANCE * 0.8, player_x - 60)
    right_zone = (player_x + 60, player_x + MAX_HORIZONTAL_DISTANCE * 0.8)
    vertical_zone = (reference_y - MAX_JUMP_HEIGHT * 0.7, reference_y + 50)
    platforms_in_left = platforms_in_right = 0
    for platform in platforms:
        if vertical_zone[0] <= platform.rect.centery <= vertical_zone[1]:
            if left_zone[0] <= platform.rect.centerx <= left_zone[1]:
                platforms_in_left += 1
            elif right_zone[0] <= platform.rect.centerx <= right_zone[1]:
                platforms_in_right += 1
    created_platforms = []
    if platforms_in_left == 0:
        x = random.randint(max(50, int(left_zone[0])), int(left_zone[1]))
        y = reference_y - random.randint(80, 120)
        if not is_position_too_close(x, y, platforms, PLATFORM_CHECK_RADIUS//2):
            platform = Platform(x - PLATFORM_WIDTH//2, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
            all_sprites.add(platform)
            platforms.add(platform)
            created_platforms.append((x, y))
    if platforms_in_right == 0:
        x = random.randint(int(right_zone[0]), min(WIDTH-50, int(right_zone[1])))
        y = reference_y - random.randint(80, 120)
        if not is_position_too_close(x, y, platforms, PLATFORM_CHECK_RADIUS//2):
            platform = Platform(x - PLATFORM_WIDTH//2, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
            all_sprites.add(platform)
            platforms.add(platform)
            created_platforms.append((x, y))
    return created_platforms

# ==================== Очищення об’єктів ====================
def cleanup_offscreen_objects():
    for sprite in list(all_sprites):
        if sprite.rect.top > HEIGHT + 300:
            sprite.kill()

# ==================== Ініціалізація гри ====================
def init_game():
    global moose, highest_y, last_x, start_time, level, game_over
    all_sprites.empty()
    platforms.empty()
    acorns.empty()
    particles.empty()
    moose = Moose()
    all_sprites.add(moose)
    start_platform = Platform(WIDTH//2 - 100, HEIGHT - 80, 200, 30)
    all_sprites.add(start_platform)
    platforms.add(start_platform)
    highest_y = HEIGHT - 200
    last_x = WIDTH // 2
    start_time = time.time()
    level = 1
    game_over = False
    for _ in range(8):
        last_x, highest_y = create_platform_with_spacing(last_x, highest_y)

# ==================== Інтерфейс ====================
def draw_ui():
    elapsed_time = time.time() - start_time
    screen.blit(UI_SURFACE, (0, 0))
    screen.blit(FONT.render(f"Час: {elapsed_time:.1f}с", True, WHITE), (10, 10))
    screen.blit(FONT.render(f"Жолуді: {moose.score}", True, WHITE), (10, 40))
    screen.blit(FONT.render(f"Рівень: {level}", True, WHITE), (10, 70))
    screen.blit(SMALL_FONT.render(f"Здоров’я: {moose.health}", True, WHITE), (10, 100))
    if moose.current_platform and moose.current_platform.is_breaking:
        remaining_time = moose.current_platform.break_threshold - moose.current_platform.breaking_time
        screen.blit(WARNING_BG, (WIDTH//2 - 150, 95))
        screen.blit(SMALL_FONT.render(f"ПЛАТФОРМА РУЙНУЄТЬСЯ! {remaining_time:.1f}с", True, RED), (WIDTH//2 - 140, 100))
    if moose.score < 2 and game_state == "playing":
        screen.blit(INSTRUCTION_BG, (WIDTH - 280, 0))
        screen.blit(SMALL_FONT.render("WASD або стрілки - рух", True, WHITE), (WIDTH - 270, 10))
        screen.blit(SMALL_FONT.render("Пробіл/W/↑ - стрибок", True, WHITE), (WIDTH - 270, 30))
        screen.blit(SMALL_FONT.render("Збирайте жолуді!", True, GREEN), (WIDTH - 270, 50))

def draw_menu():
    global logo_alpha, logo_fade_in
    screen.blit(background_image, (0, 0))
    # Анімація логотипу
    logo = FONT.render("Moose Speedrun", True, WHITE)
    logo_surface = pygame.Surface(logo.get_size(), pygame.SRCALPHA)
    logo_surface.blit(logo, (0, 0))
    logo_surface.set_alpha(logo_alpha)
    screen.blit(logo_surface, (WIDTH//2 - logo.get_width()//2, HEIGHT//2 - 100))
    # Оновлення анімації
    if logo_fade_in:
        logo_alpha = min(logo_alpha + 5, 255)
        if logo_alpha == 255:
            logo_fade_in = False
    else:
        logo_alpha = max(logo_alpha - 5, 0)
        if logo_alpha == 0:
            logo_fade_in = True
    # Кнопка старту
    start_text = SMALL_FONT.render("Натисніть SPACE щоб почати", True, WHITE)
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 20))
    # Додаткові опції
    options_text = SMALL_FONT.render("N - Нова гра | Q - Вихід", True, WHITE)
    screen.blit(options_text, (WIDTH//2 - options_text.get_width()//2, HEIGHT//2 + 60))

def draw_game_over():
    final_time = time.time() - start_time
    screen.blit(OVERLAY, (0, 0))
    end_text = FONT.render("Вітаємо! Ви пройшли всі рівні!" if level > max_level else "Гру завершено!", True, WHITE)
    screen.blit(end_text, (WIDTH // 2 - (200 if level > max_level else 100), HEIGHT // 2 - 60))
    screen.blit(FONT.render(f"Жолуді: {moose.score}", True, WHITE), (WIDTH // 2 - 80, HEIGHT // 2 - 20))
    screen.blit(FONT.render(f"Час: {final_time:.1f}с", True, WHITE), (WIDTH // 2 - 60, HEIGHT // 2 + 10))
    screen.blit(FONT.render("Натисніть R щоб почати знову", True, WHITE), (WIDTH // 2 - 160, HEIGHT // 2 + 50))

# ==================== Ініціалізація ====================
init_game()

# ==================== Головний цикл ====================
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_SPACE:
                    game_state = "playing"
                    if menu_music:
                        pygame.mixer.music.stop()
                    init_game()
                elif event.key == pygame.K_n:
                    game_state = "playing"
                    if menu_music:
                        pygame.mixer.music.stop()
                    init_game()
                elif event.key == pygame.K_q:
                    running = False
            elif game_state == "game_over" and event.key == pygame.K_r:
                game_state = "menu"
                init_game()

    if game_state == "playing":
        all_sprites.update()
        # Колізії з платформами
        hits = pygame.sprite.spritecollide(moose, platforms, False)
        platform_collision = False
        for platform in hits:
            if (moose.speed_y >= 0 and 
                moose.rect.bottom <= platform.rect.top + 15 and
                moose.rect.centerx >= platform.rect.left - 15 and
                moose.rect.centerx <= platform.rect.right + 15):
                moose.rect.bottom = platform.rect.top
                moose.speed_y = 0
                moose.on_ground = True
                platform_collision = True
                if moose.current_platform != platform:
                    if moose.current_platform and moose.current_platform != moose.last_platform:
                        moose.current_platform.stop_breaking()
                    moose.current_platform = platform
                    moose.platform_stand_time = 0
                if platform.platform_type == "moving":
                    moose.rect.x += platform.direction * platform.speed
                break
        if not platform_collision:
            moose.on_ground = False
            if moose.current_platform and moose.current_platform != moose.last_platform:
                moose.current_platform.stop_breaking()
                moose.current_platform = None
                moose.platform_stand_time = 0
        if moose.current_platform and moose.platform_stand_time > 1.0:
            moose.current_platform.start_breaking()
        collected = pygame.sprite.spritecollide(moose, acorns, True)
        if collected:
            moose.score += len(collected)
            if collect_sound:
                collect_sound.play()
            for _ in range(10):
                particle = Particle(moose.rect.centerx, moose.rect.centery)
                particles.add(particle)
                all_sprites.add(particle)
        if moose.rect.top < SCROLL_THRESHOLD:
            scroll_amount = SCROLL_THRESHOLD - moose.rect.top
            scroll_offset += scroll_amount
            moose.rect.y += scroll_amount
            for sprite in all_sprites:
                if sprite != moose:
                    sprite.rect.y += scroll_amount
        top_platform_y = min([p.rect.y for p in platforms] + [HEIGHT])
        generation_count = 0
        while top_platform_y > -scroll_offset - 400 and generation_count < 5:
            ensure_reachable_platforms(moose.rect.centerx, top_platform_y - 100)
            last_x, new_y = create_platform_with_spacing(last_x, top_platform_y - 100)
            top_platform_y = new_y
            generation_count += 1
        cleanup_offscreen_objects()
        if moose.rect.top > HEIGHT + 50:
            moose.health -= 1
            if moose.health <= 0:
                game_over = True
            else:
                moose.rect.center = (WIDTH // 2, HEIGHT - 150)
                scroll_offset = 0
        if moose.score >= level * 8:
            level += 1
            if level > max_level:
                game_over = True
        if game_over:
            game_state = "game_over"

    # Малювання
    screen.blit(background_image, (0, 0))
    all_sprites.draw(screen)
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_ui()
    elif game_state == "game_over":
        draw_game_over()

    pygame.display.flip()

pygame.quit()
sys.exit()