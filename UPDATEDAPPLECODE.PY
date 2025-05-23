import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Falling Apples")

# Load background image
background = pygame.image.load(r"C:\\Users\\vignan\\Desktop\\background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load sounds
pygame.mixer.music.load(r"C:\\Users\\vignan\\Desktop\\music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

collision_sound = pygame.mixer.Sound(r"C:\\Users\\vignan\\Desktop\\explosion.wav")
collision_sound.set_volume(0.7)

additional_collision_sound = pygame.mixer.Sound(r"C:\\Users\\vignan\\Desktop\\catch.wav")
additional_collision_sound.set_volume(0.7)

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Define game clock 
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont(None, 30)

# Load heart image for lives
heart_image = pygame.image.load(r"C:\\Users\\vignan\\Desktop\\heart.png")
heart_image = pygame.transform.scale(heart_image, (25, 25))

# Basket class
class Basket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"C:\\Users\\vignan\\Desktop\\bb.png")
        self.image = pygame.transform.scale(self.image, (60, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.base_speed = 5
        self.speed = self.base_speed

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

# Apple class
class Apple(pygame.sprite.Sprite):
    def __init__(self, color=None, is_black=False, is_custom=False):
        super().__init__()
        self.is_black = is_black
        self.color = color
        self.is_custom = is_custom
        self.missed = False

        if color == "RED":
            self.image = pygame.image.load(r"C:\\Users\\vignan\\Desktop\\hlo.png")
            self.image = pygame.transform.scale(self.image, (30, 30))
        elif is_black:
            self.image = pygame.image.load(r"C:\\Users\\vignan\\Desktop\\hh.png")
            self.image = pygame.transform.scale(self.image, (30, 30))
        elif is_custom:
            self.image = pygame.image.load(r"C:\\Users\\vignan\\Desktop\\oy.png")
            self.image = pygame.transform.scale(self.image, (50, 50))
        else:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 0, 0), (15, 15), 15)

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - 30)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(3, 6)

    def update(self):
        if not power_state["freeze"]:
            self.rect.y += int(self.speed * (0.5 if power_state["slow_apples"] else 1))

        if self.rect.top > HEIGHT:
            self.missed = True

# Power state tracking
power_state = {
    "double_score": False,
    "slow_apples": False,
    "fast_basket": False,
    "freeze": False,
    "active_until": 0,
    "message": ""
}

def activate_power(power):
    power_state["double_score"] = power == "double_score"
    power_state["slow_apples"] = power == "slow_apples"
    power_state["fast_basket"] = power == "fast_basket"
    power_state["freeze"] = power == "freeze"
    power_state["message"] = {
        "double_score": "Double Score!",
        "slow_apples": "Apples Slowed!",
        "fast_basket": "Basket Faster!",
        "freeze": "Apples Frozen!",
        "lose_points": "Oops! -5 Points"
    }.get(power, "")

    if power == "lose_points":
        return 1

    return 3000 if power == "freeze" else 5000

# Sprite groups
all_sprites = pygame.sprite.Group()
apples = pygame.sprite.Group()

basket = Basket()
all_sprites.add(basket)

# Game variables
score = 0
lives = 3
last_black_apple_time = pygame.time.get_ticks()
apple_spawn_rate = 2000
last_apple_spawn_time = pygame.time.get_ticks()
red_apple_count = 0
game_over = False

# Main game loop
while True:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if game_over:
        game_over_text = font.render("GAME OVER!", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 3, HEIGHT // 2))
        pygame.display.flip()
        clock.tick(60)
        continue

    if pygame.time.get_ticks() - last_apple_spawn_time > apple_spawn_rate:
        if random.random() < 0.75:
            apple = Apple(color="RED")
            all_sprites.add(apple)
            apples.add(apple)
            red_apple_count += 1
        elif red_apple_count >= 2:
            apple = Apple(is_custom=True)
            all_sprites.add(apple)
            apples.add(apple)
            red_apple_count = 0
        last_apple_spawn_time = pygame.time.get_ticks()

    if pygame.time.get_ticks() - last_black_apple_time > 7000:
        apple = Apple(color="BLACK", is_black=True)
        all_sprites.add(apple)
        apples.add(apple)
        last_black_apple_time = pygame.time.get_ticks()

    if pygame.time.get_ticks() > power_state["active_until"]:
        power_state.update({
            "double_score": False,
            "slow_apples": False,
            "fast_basket": False,
            "freeze": False,
            "message": ""
        })
        basket.speed = basket.base_speed

    basket.speed = basket.base_speed * 2 if power_state["fast_basket"] else basket.base_speed
    all_sprites.update()

    caught = pygame.sprite.spritecollide(basket, apples, True)
    for apple in caught:
        collision_sound.play()
        additional_collision_sound.play()
        if apple.is_black:
            power = random.choice(["double_score", "slow_apples", "fast_basket", "freeze", "lose_points"])
            duration = activate_power(power)
            if power == "lose_points":
                score -= 5
            else:
                power_state["active_until"] = pygame.time.get_ticks() + duration
            score += 2 if power_state["double_score"] else 1
        elif apple.color == "RED":
            score += 1
        else:
            game_over = True

    missed_apples = [apple for apple in apples if apple.missed and not apple.is_black and not apple.is_custom]
    for apple in missed_apples:
        apples.remove(apple)
        all_sprites.remove(apple)
        lives -= 1
        if lives <= 0:
            game_over = True

    missed_black_apples = [apple for apple in apples if apple.missed and apple.is_black]
    for apple in missed_black_apples:
        apples.remove(apple)
        all_sprites.remove(apple)

    missed_custom_apples = [apple for apple in apples if apple.missed and apple.is_custom]
    for apple in missed_custom_apples:
        apples.remove(apple)
        all_sprites.remove(apple)

    for i in range(lives):
        screen.blit(heart_image, (WIDTH - (i + 1) * 30, 10))

    all_sprites.draw(screen)

    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    if power_state["message"]:
        power_text = font.render(power_state["message"], True, (0, 0, 255))
        screen.blit(power_text, (10, 40))

    pygame.display.flip()
    clock.tick(60)
 