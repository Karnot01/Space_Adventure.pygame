# Pygame Proyecto Final - Aventura espacial

# 1 - Importar paquetes
import pygame
from pygame.locals import *
import random

# 2 - Definir constantes
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WINDOW_WIDTH = 1900
WINDOW_HEIGHT = 1020
FRAMES_PER_SECOND = 90

# 3 - Inicializar el mundo
pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# 4 - Objetos del juego
class Game:
    def __init__(self):
        pygame.display.set_caption("Aventura Espacial")
        self.screen = window
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = False
        self.game_won = False
        self.all_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(self)
        self.level = Level(self)
        self.enemies_killed = 0
        self.enemy_generation = True
        self.blast_sound = self.load_sound('sounds/blast_sound.mp3')
        self.electrical = self.load_sound('sounds/electrical.mp3')
        self.max_levels = 10

    def load_sound(self, path, volume=0.09):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound

    # Iniciar un nuevo juego
    def new_game(self):
        self.playing = True
        self.game_won = False
        self.all_sprites.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.enemies.empty()
        self.powerups.empty()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.level.start_new_level()  # Generar enemigos al iniciar el nivel
        self.run()

    # Bucle del juego
    def run(self):
        while self.playing:
            self.clock.tick(FRAMES_PER_SECOND)
            self.handle_events()
            self.update()
            self.draw()
    
    # Bucle de eventos
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    # Bucle del juego - Actualizar
    def update(self):
        self.all_sprites.update()
        self.check_collisions()

        if self.enemy_generation:
            self.generate_enemies()
    
    def play_blast_sound(self):
        self.blast_sound.play()

    # Colisiones entre balas de player y enemigos
    def check_collisions(self):
        self.handle_player_hits()
        self.handle_enemy_hits()

        # Subir de nivel cada 10 enemigos eliminados
        if self.enemies_killed >= 10:
            self.level.level_num += 1
            self.enemies_killed = 0  # Resetear contador de enemigos eliminados
            if self.level.level_num > self.max_levels:
                self.game_won = True
                self.playing = False
            else:
                self.level.start_new_level()
        
    def handle_player_hits(self):
        player_hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for hit in player_hits:
            print("Player hit by enemy bullet!")
            self.player.take_damage(self.level.enemy_bullet_damage)
            self.electrical.play()
            self.all_sprites.add(Blast(hit.rect.centerx, hit.rect.centery, 'images/blast_player.png'))
            if self.player.health <= 0:
                print("Player health <= 0")
                self.play_blast_sound()
                self.playing = False

    def handle_enemy_hits(self):
        enemy_hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, True)
        for hit in enemy_hits:
            self.play_blast_sound()
            self.all_sprites.add(Blast(hit.rect.centerx, hit.rect.centery, 'images/blast_enemy.png'))
            self.enemies_killed += 1
            
    # Generar enemigos
    def generate_enemies(self):
        if len(self.enemies) < self.level.max_enemies and self.enemy_generation:
            enemy = Enemy(self, self.level.enemy_health, self.level.enemy_bullet_delay)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    # Bucle del juego - Dibujar
    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    # Mostrar pantallas
    def show_screen(self, image_path, texts):
        background_image = pygame.image.load(image_path).convert()
        self.screen.blit(background_image, (0, 0))
        for text in texts:
            self.draw_text(*text)
        pygame.display.flip()
        self.wait_for_key()

    # Mostrar pantalla de inicio
    def show_start_screen(self):
        texts = [
            ("Aventura Espacial", 48, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4),
            ("Usa las flechas para moverte, Espacio para disparar", 22, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
            ("Presiona Enter para comenzar", 22, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3/4)
        ]
        self.show_screen('images/start_screen.png', texts)

    # Mostrar pantalla de game over
    def show_go_screen(self):
        texts = [
            ("Presiona Enter para reiniciar", 22, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3)
        ]
        self.show_screen('images/game_over.png', texts)

    # Mostrar pantalla de You win
    def show_win_screen(self):
        texts = [
            ("Presiona Enter para reiniciar", 22, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3)
        ]
        self.show_screen('images/you_win.png', texts)

    # Esperar respuesta del teclado
    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FRAMES_PER_SECOND)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        waiting = False

    # Dibujar texto
    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(pygame.font.match_font('arial'), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

# 5 - Objetos de las balas
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color, damage):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = speed
        self.damage = damage

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT:
            self.kill()

class PlayerBullet(Bullet):
    def __init__(self, x, y, damage):
        super().__init__(x, y, -10, (0, 0, 255), damage)

class EnemyBullet(Bullet):
    def __init__(self, x, y, damage):
        super().__init__(x, y, 10, (255, 0, 0), damage)

# 6 - Objetos de las explosiones
class Blast(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.lifetime = 30

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

# 7 - Objetos de las naves
class Ship(pygame.sprite.Sprite):
    def __init__(self, game, image_path, speed, health):
        super().__init__()
        self.game = game
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = speed
        self.health = health

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.game.play_blast_sound()
            self.kill()

class Player(Ship):
    def __init__(self, game):
        super().__init__(game, 'images/player_ship.png', 5, 100)
        self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50)
        self.shoot_delay = 500
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        self.move(keys)
        self.stay_in_bounds()
        if keys[pygame.K_SPACE]:
            self.shoot()
        if self.health <= 0:
            self.game.running = False

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def stay_in_bounds(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            bullet = PlayerBullet(self.rect.centerx, self.rect.top, self.game.level.player_bullet_damage)
            self.game.player_bullets.add(bullet)
            self.game.all_sprites.add(bullet)
            self.last_shot = now

class Enemy(Ship):
    def __init__(self, game, health, bullet_delay):
        super().__init__(game, 'images/enemy_ship.png', random.randint(1, 5), health)
        self.rect.x = random.randint(0, WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.shoot_delay = bullet_delay * 1000 / FRAMES_PER_SECOND
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now

    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, self.game.level.enemy_bullet_damage)
        self.game.enemy_bullets.add(bullet)
        self.game.all_sprites.add(bullet)

# 8 - Objetos del efecto del movimiento hacia arriba
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT + 10:
            self.kill()

# 9 - Nivelaje
class Level:
    def __init__(self, game):
        self.game = game
        self.level_num = 1
        self.max_enemies = 10
        self.player_bullet_damage = 20
        self.enemy_bullet_damage = 1
        self.enemy_bullet_delay = 50 # segundos
        self.enemy_health = 50

    def start_new_level(self):
        self.game.enemies_killed = 0
        self.game.enemy_generation = True
        self.max_enemies += 5
        self.player_bullet_damage -= 2
        self.enemy_bullet_damage += 5
        self.enemy_bullet_delay *= 0.8  # Reducir el retraso de disparo de los enemigos
        for _ in range(self.max_enemies):
            enemy = Enemy(self.game, self.enemy_health, self.enemy_bullet_delay)
            self.game.all_sprites.add(enemy)
            self.game.enemies.add(enemy)
        self.level_num += 1

# 10 - Cierre de codigo
if __name__ == "__main__":
    try:
        g = Game()
        g.show_start_screen()
        while g.running:
            g.new_game()
            if g.running:
                if g.game_won:
                    g.show_win_screen()
                else:
                    g.show_go_screen()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()

