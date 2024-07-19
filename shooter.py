import pygame
import random
import sqlite3

WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Inicializar pygame y mixer
pygame.init()
pygame.mixer.init()

# Configurar pantalla y reloj
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter")
clock = pygame.time.Clock()

# Función para dibujar texto
def draw_text(surface, text, size, x, y):
    font = pygame.font.SysFont("serif", size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Función para dibujar barra de escudo
def draw_shield_bar(surface, x, y, percentage):
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (percentage / 100) * BAR_LENGTH
    border = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill)
    pygame.draw.rect(surface, WHITE, border, 2)

# Clases del juego
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.shield = 100

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        laser_sound.play()

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = random.choice(meteor_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-140, -100)
        self.speedy = random.randrange(1, 10)
        self.speedx = random.randrange(-5, 5)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < -40 or self.rect.right > WIDTH + 40:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-140, -100)
            self.speedy = random.randrange(1, 10)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/laser1.png").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = explosion_anim[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # VELOCIDAD DE LA EXPLOSION

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Función para mostrar la pantalla de inicio y game over
def show_go_screen(message, score=None, user=None, history=None, new_record=False):
    pygame.mixer.music.load("assets/start_music.ogg")
    pygame.mixer.music.play(loops=-1)

    screen.blit(background, [0, 0])
    draw_text(screen, "SHOOTER", 65, WIDTH // 2, HEIGHT // 8)
    draw_text(screen, message, 27, WIDTH // 2, HEIGHT // 4)
    if score is not None and user is not None:
        draw_text(screen, f"{user} has hecho {score} puntos", 22, WIDTH // 2, HEIGHT // 4 + 40)
        if new_record:
            draw_text(screen, "¡Nuevo récord!", 30, WIDTH // 2, HEIGHT // 4 + 80)
    
    if history:
        draw_text(screen, "Últimos 10 juegos:", 20, WIDTH // 2, HEIGHT // 4 + 130)  # Ajustar la posición vertical inicial
        for i, (name, score) in enumerate(history):
            draw_text(screen, f"{name}: {score}", 18, WIDTH // 2, HEIGHT // 4 + 160 + i * 25)  # Ajustar el espacio entre líneas

    draw_text(screen, "Presiona Enter para volver a jugar", 20, WIDTH // 2, HEIGHT // 4 + 160 + len(history) * 25 + 20)

    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    waiting = False

    pygame.mixer.music.stop()

# Cargar imágenes de meteoros
meteor_images = []
meteor_list = ["assets/meteorGrey_big1.png", "assets/meteorGrey_big2.png", "assets/meteorGrey_big3.png", "assets/meteorGrey_big4.png",
               "assets/meteorGrey_med1.png", "assets/meteorGrey_med2.png", "assets/meteorGrey_small1.png", "assets/meteorGrey_small2.png",
               "assets/meteorGrey_tiny1.png", "assets/meteorGrey_tiny2.png"]
for img in meteor_list:
    meteor_images.append(pygame.image.load(img).convert())

# Cargar imágenes de explosión
explosion_anim = []
for i in range(9):
    file = "assets/regularExplosion0{}.png".format(i)
    img = pygame.image.load(file).convert()
    img.set_colorkey(BLACK)
    img_scale = pygame.transform.scale(img, (70, 70))
    explosion_anim.append(img_scale)

# Cargar imagen de fondo
background = pygame.image.load("assets/background.png").convert()

# Cargar sonidos
laser_sound = pygame.mixer.Sound("assets/laser5.ogg")
explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
pygame.mixer.music.load("assets/music.ogg")
pygame.mixer.music.set_volume(0.1)

# Conectar a la base de datos y crear tabla si no existe
conn = sqlite3.connect('scores.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        score INTEGER NOT NULL
    )
''')
conn.commit()

def get_username():
    screen.fill(BLACK)
    draw_text(screen, "Enter your name:", 22, WIDTH // 2, HEIGHT // 2 - 50)
    pygame.display.flip()
    name = ""
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name:
                        waiting = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
        screen.fill(BLACK)
        draw_text(screen, "INGRESE SU NOMBRE:", 22, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(screen, name, 22, WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()
    return name

def get_last_scores(limit=10):
    cursor.execute('SELECT name, score FROM scores ORDER BY id DESC LIMIT ?', (limit,))
    return cursor.fetchall()

def get_high_score():
    cursor.execute('SELECT MAX(score) FROM scores')
    return cursor.fetchone()[0]

# Variables del juego
WIN_SCORE = 500
game_over = True
running = True
score = 0
username = None

# Bucle principal del juego
while running:
    if game_over:
        username = get_username()
        history = get_last_scores()
        high_score = get_high_score()
        show_go_screen("Presiona Enter para comenzar", score, username, history)
        game_over = False
        all_sprites = pygame.sprite.Group()
        meteor_list = pygame.sprite.Group()
        bullets = pygame.sprite.Group()

        player = Player()
        all_sprites.add(player)
        for i in range(8):
            meteor = Meteor()
            all_sprites.add(meteor)
            meteor_list.add(meteor)

        score = 0
        pygame.mixer.music.play(loops=-1)

    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    all_sprites.update()

    # Colisiones - meteoro - laser
    hits = pygame.sprite.groupcollide(meteor_list, bullets, True, True)
    for hit in hits:
        score += 10
        explosion_sound.play()
        explosion = Explosion(hit.rect.center)
        all_sprites.add(explosion)
        meteor = Meteor()
        all_sprites.add(meteor)
        meteor_list.add(meteor)

    # Colisiones - jugador - meteoro
    hits = pygame.sprite.spritecollide(player, meteor_list, True)
    for hit in hits:
        player.shield -= 25
        meteor = Meteor()
        all_sprites.add(meteor)
        meteor_list.add(meteor)
        if player.shield <= 0:
            game_over = True
            cursor.execute('INSERT INTO scores (name, score) VALUES (?, ?)', (username, score))
            conn.commit()
            history = get_last_scores()
            high_score = get_high_score()
            if score > high_score:
                new_record = True
            else:
                new_record = False
            show_go_screen("HAS PERDIDO", score, username, history, new_record)

    # Verificar si el jugador ha ganado
    if score >= WIN_SCORE:
        game_over = True
        cursor.execute('INSERT INTO scores (name, score) VALUES (?, ?)', (username, score))
        conn.commit()
        history = get_last_scores()
        high_score = get_high_score()
        if score > high_score:
            new_record = True
        else:
            new_record = False
        show_go_screen("HAS GANADO", score, username, history, new_record)

    screen.blit(background, [0, 0])
    all_sprites.draw(screen)
    draw_text(screen, str(score), 25, WIDTH // 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    pygame.display.flip()

pygame.quit()
conn.close()






