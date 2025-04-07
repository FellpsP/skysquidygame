import random
from pygame import rect
import math
import pgzrun

# CONSTANTES -------------------------------------------------------------------
PLAYER_SPEED = 3
GRAVITY = 0.6
JUMP = -15
WIDTH = 792
HEIGHT = 600
MAX_VELOCITY = 60
COIN_SPAWN_RATE = 0.05
MAX_ENEMY_SPEED = 3
MAX_ENEMY = 2
BASE_ENEMY_SPEED = 1.2
ENEMY_SPAWN_RATE = 0.07
ENEMY_SPEED_GROWTH = 0.10
MAX_COINS = 5
WIN_SCORE = 100
MIN_SPAWN_DISTANCE = 300
BACKGROUND = "tiles/bg"
MENU_OPTIONS = ["Play", "Sound: ON", "Quit"]
SOUND_JUMP = "jump"
SOUND_COIN = "coin"
SOUND_SELECT = "select"
MUSIC_GAME = "music"
SOUND_HIT = "hit"
HIT_DURATION = 0.3
game_state = "menu"  
selected_option = 0
music_on = True
menu_option_rects = []

PLATFORMS = [
    {'rect': Rect(0, HEIGHT-18, 792, 18), 'type': 'solid'},  
    {'rect': Rect(240, 400, 126, 18), 'type': 'platform'},   
    {'rect': Rect(400, 300, 144, 18), 'type': 'platform'},    
    {'rect': Rect(100, 200, 72, 18), 'type': 'platform'},
    {'rect': Rect(350, 200, 72, 18), 'type': 'platform'},  
    {'rect': Rect(50, 500, 144, 18), 'type': 'platform'},
    {'rect': Rect(600, 200, 90, 18), 'type': 'platform'},
    {'rect': Rect(350, 150, 126, 18), 'type': 'platform'},
    {'rect': Rect(200, 350, 90, 18), 'type': 'platform'},
    {'rect': Rect(500, 450, 144, 18), 'type': 'platform'},  
]
# CLASSES ----------------------------------------------------------------------
class Player(Actor):
    
    def __init__(self):
        super().__init__("tiles/character01", (40, 40))
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        
        # Sistema de animação aprimorado
        self.animations = {
            'idle': {
                'frames': ["tiles/character01"],
                'delay': 200  # Mais lento para animação estática
            },
            'walk': {
                'frames': ["tiles/character01", "tiles/character02"],
                'delay': 240  # Velocidade normal para caminhada
            },
            'jump': {
                'frames': ["tiles/character02"],  # Frame único de pulo
                'delay': 0
            },
            'hit': {
                'frames': ["tiles/character04"],
                'delay': 0
            },
            
        }
        
        self.state = 'idle'
        self.facing_right = True
        self.is_hit = False
        self.hit_timer = 0.0
        
    def update_movement(self):
        # Movimentação horizontal
        self.velocity_x = 0
        if keyboard.left: self.velocity_x = -PLAYER_SPEED
        if keyboard.right: self.velocity_x = PLAYER_SPEED
        self.x += self.velocity_x

        # Gravidade
        if not self.on_ground:
            self.velocity_y = min(self.velocity_y + GRAVITY, MAX_VELOCITY)
            self.y += self.velocity_y

    def update_animation(self):
        if self.is_hit:
            self.image = self.animations['hit']['frames'][0]
            return
        previous_state = self.state
        self.state = self.get_animation_state()
        
        # Resetar animações ao mudar de estado
        if self.state != previous_state:
            if self.state == 'walk':
                self.animations['walk']['index'] = 0
                self.animations['walk']['counter'] = 0  # Resetar contador também
            self.image = self.animations[self.state]['frames'][0]
        
        # Atualizar apenas animação de walk
        if self.state == 'walk':
            walk_data = self.animations['walk']
            walk_data['counter'] += 1
            
            if walk_data['counter'] >= walk_data['delay']:
                walk_data['index'] = (walk_data['index'] + 1) % len(walk_data['frames'])
                self.image = walk_data['frames'][walk_data['index']]
                walk_data['counter'] = 0  # Resetar contador após mudar frame
        
        self.flip_x = not self.facing_right
        
    def get_animation_state(self):
        if not self.on_ground:
            return 'jump'
        elif self.velocity_x != 0:
            return 'walk'
        else:
            return 'idle'
          
    
    def handle_collisions(self, platforms, previous_y):
        self.on_ground = False
        current_rect = Rect(self.x - 12, self.y - 12, 24, 24)
        previous_rect = Rect(self.x - 12, previous_y - 12, 24, 24)

        for platform in platforms:
            p_rect = platform['rect']
            p_type = platform['type']

            if current_rect.colliderect(p_rect):
                # Calcula todas as sobreposições primeiro
                overlaps = {
                    'top': p_rect.top - current_rect.bottom,
                    'bottom': current_rect.top - p_rect.bottom,
                    'left': current_rect.left - p_rect.right,
                    'right': p_rect.left - current_rect.right
                }

                # Encontra a direção da colisão com base na maior penetração
                collision_side = max(overlaps, key=overlaps.get)

                # Colisão pelo topo (aterrissagem)
                if collision_side == 'top' and previous_rect.bottom <= p_rect.top and self.velocity_y >= 0:
                    self.y = p_rect.top - 12
                    self.velocity_y = 0
                    self.on_ground = True
                    break
                # Colisão por baixo (cabeça)
                elif collision_side == 'bottom' and p_type == 'solid':
                    self.y += abs(overlaps['bottom'])  # Ajuste suave
                    self.velocity_y *= 0.5  # Reduz velocidade sem parar bruscamente
                    break
                
                # Colisões laterais para plataformas sólidas
                elif p_type == 'solid':
                    if collision_side == 'left':
                        self.x = p_rect.right + 12
                        self.velocity_x = 0
                    elif collision_side == 'right':
                        self.x = p_rect.left - 12
                        self.velocity_x = 0
                    break

class Coin(Actor):
    def __init__(self, pos):
        super().__init__("tiles/sidecoin", pos)
        self.anim_frames = ["tiles/sidecoin", "tiles/truecoin"]
        self.anim_frame = 0
        self.anim_counter = 0
        self.anim_delay = 5

    def update(self):
        self.anim_counter += 1
        if self.anim_counter >= self.anim_delay:
            self.anim_frame = (self.anim_frame + 1) % len(self.anim_frames)
            self.image = self.anim_frames[self.anim_frame]
            self.anim_counter = 0

class Enemy(Actor):
    def __init__(self, pos):
        super().__init__("tiles/enemy01", pos)
        self.anim_frames = ["tiles/enemy01", "tiles/enemy02", "tiles/enemy03"]
        self.anim_frame = 0
        self.anim_counter = 0
        self.anim_delay = 5
        self.facing_right = True

    def update(self, player_pos):
        # Perseguição
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 50:
            speed = BASE_ENEMY_SPEED if distance > 200 else BASE_ENEMY_SPEED * 0.7
            self.x += (dx/distance) * speed
            self.y += (dy/distance) * speed

        # Animação
        self.anim_counter += 1
        if self.anim_counter >= self.anim_delay:
            self.anim_frame = (self.anim_frame + 1) % len(self.anim_frames)
            self.anim_counter = 0
        
        self.image = self.anim_frames[self.anim_frame]
        self.flip_x = dx < 0

# VARIÁVEIS GLOBAIS -----------------------------------------------------------
player = Player()
coins = []
enemies = []
score = 0
game_over = False
game_won = False
current_difficulty = 1

# FUNÇÕES DE GERENCIAMENTO -----------------------------------------------------
def spawn_enemy():
    attempts = 0
    while attempts < 50:
        x = random.choice([random.randint(-50,50), random.randint(WIDTH-50, WIDTH+50)])
        y = random.randint(50, HEIGHT-50)
        new_enemy = Enemy((x, y))
        
        # Verificar colisão inicial
        valid = True
        for platform in PLATFORMS:
            if new_enemy.colliderect(platform['rect']):
                valid = False
                break
        if valid and not new_enemy.colliderect(player):
            enemies.append(new_enemy)
            break
        attempts += 1

def spawn_coin():
    attempts = 0
    while attempts < 100:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        new_coin = Coin((x, y))
        
        valid = True
        for platform in PLATFORMS:
            if new_coin.colliderect(platform['rect']):
                valid = False
                break
        if valid:
            coins.append(new_coin)
            break
        attempts += 1
 
def draw_textured_platform(plat_rect, plat_type):
    tile_size = 18
    tile_prefix = "solid" if plat_type == "solid" else "platform"
    
    # Verificação de tamanho
    if plat_rect.width % tile_size != 0:
        raise ValueError(f"Largura da plataforma deve ser múltipla de {tile_size}px")

    # Posicionamento preciso
    x = int(plat_rect.x)  # Garante coordenada inteira
    y = int(plat_rect.y)
    
    # Left tile
    screen.blit(f"tiles/{tile_prefix}_left", (x, y))
    x += tile_size
    
    # Mid tiles (preenchem o centro)
    mid_tiles = (plat_rect.width // tile_size) - 2
    for _ in range(mid_tiles):
        screen.blit(f"tiles/{tile_prefix}_mid", (x, y))
        x += tile_size  # Avança exatamente 24 pixels
    
    # Right tile
    screen.blit(f"tiles/{tile_prefix}_right", (x, y))
    
 
    
# LOOP PRINCIPAL ---------------------------------------------------------------
def update():
    global score, game_over, game_won, current_difficulty

    if game_state != "playing" or game_over or game_won:
        return

    # Atualizar jogador
    if not player.is_hit:
        previous_y = player.y
        player.update_movement()
        player.handle_collisions(PLATFORMS, previous_y)
        player.update_animation()
    
    # Pulo
    if keyboard.space and player.on_ground and not game_over:
        player.velocity_y = JUMP
        player.on_ground = False
        if music_on:
            sounds.jump.play()

    if player.is_hit:
        # Pausa a lógica do jogo durante o hit
        player.velocity_x = 0
        player.velocity_y = 0
        enemies.clear()
        coins.clear()
        
    # Manter na tela
    player.x = clamp(player.x, 12, WIDTH-12)

    # Inimigos
    for enemy in enemies:
        enemy.update((player.x, player.y))
        if enemy.colliderect(player):
            player.is_hit = True
            player.hit_timer = HIT_DURATION
            if music_on:    
                music.stop()
                sounds.hit.play()
            break     
            
    if player.is_hit:
        player.hit_timer -= 1/60  # Atualiza timer baseado em 60 FPS
        if player.hit_timer <= 0:
            game_over = True
    # Moedas
    for coin in coins[:]:
        coin.update()
        if coin.colliderect(player):
            coins.remove(coin)
            if music_on:
                sounds.coin.play()  
            
            if score >= 50:
                score += 3
            else:
                current_difficulty_temp = 1 + (score // 5)
                if current_difficulty_temp >= 2:
                    score += 2
                else:
                    score += 1

    # Dificuldade
    current_difficulty = 1 + (score // 5)
    if random.random() < 0.02 + (min(current_difficulty,5)*0.05):
        if len(enemies) < current_difficulty//2:
            spawn_enemy()
    
    if len(coins) < MAX_COINS and random.random() < COIN_SPAWN_RATE:
        spawn_coin()

    if score >= WIN_SCORE:
        game_won = True
def reset_game():
    global player, coins, enemies, score, game_over, game_won, current_difficulty
    
    
    player = Player()
    player.is_hit = False
    coins = []
    enemies = []
    score = 0
    game_over = False
    game_won = False
    current_difficulty = 1
    player.hit_timer = 0.0  
    music.stop()
    if music_on:
        music.play(MUSIC_GAME)
    if not music_on:
        sounds.hit.stop()          
def on_key_down(key):
    global selected_option, game_state, music_on
    
    if key == keys.ESCAPE:
        if game_state == "playing":
            game_state = "menu"
            reset_game()
    
    if game_state == "menu":
        if key == keys.DOWN:
            selected_option = (selected_option + 1) % len(MENU_OPTIONS)
        elif key == keys.UP:
            selected_option = (selected_option - 1) % len(MENU_OPTIONS)
        elif key == keys.RETURN:
            if selected_option == 0:  # Play
                reset_game()
                game_state = "playing"
            elif selected_option == 1:  # Sound
                music_on = not music_on
                if not music_on:
                    for sound in [SOUND_JUMP, SOUND_COIN, SOUND_HIT]:
                        try:
                            getattr(sounds, sound).stop()
                        except:
                            pass
                    music.stop()
                else:
                    music.play(MUSIC_GAME)            
            else:  # Quit
                quit()
                               
def on_mouse_down(pos):
    global selected_option, game_state, music_on
    
    if game_state != "menu":
        return
    
    # Verifica clique nas opções
    for i, rect in enumerate(menu_option_rects):
        if rect.collidepoint(pos):
            selected_option = i
            # Executa a ação correspondente
            if selected_option == 0:  # Play
                reset_game()
                game_state = "playing"
                if music_on:
                    music.play(MUSIC_GAME)
            elif selected_option == 1:  # Sound
                music_on = not music_on
                if not music_on:
                    for sound in [SOUND_JUMP, SOUND_COIN, SOUND_HIT]:
                        try:
                            getattr(sounds, sound).stop()
                        except:
                            pass
                    music.stop()
                else:
                    music.play(MUSIC_GAME)
            elif selected_option == 2:  # Quit
                quit()
                
def draw_menu():
    global menu_option_rects
    screen.clear()
    screen.blit(BACKGROUND, (0,0))
    
    # Título
    screen.draw.text(
        "Sky Squiddy Game",
        center=(WIDTH//2, 100),
        fontsize=72,
        color=(255, 215, 0)
    )
    menu_option_rects = []
    for i, option in enumerate(MENU_OPTIONS):
        color = (255, 0, 0) if i == selected_option else (255, 255, 255)
        text = "Sound: ON" if (i == 1 and music_on) else "Sound: OFF" if (i == 1) else option
       
        text_width = len(text) * 20  
        text_height = 40
        x = WIDTH//2 - text_width//2
        y = 250 + i*50 - text_height//2
       
        menu_option_rects.append(Rect(x, y, text_width, text_height))
        
        screen.draw.text(
            text,
            center=(WIDTH//2, 250 + i*50),
            fontsize=40,
            color=color)
        
    if music_on: 
        if not music.is_playing(MUSIC_GAME):
            music.play(MUSIC_GAME)
    else: 
        music.stop()        

def draw():
    global game_state
    
    if game_state == "menu":
        draw_menu()
        
    elif game_state == "playing":
        screen.clear()
        screen.blit(BACKGROUND, (0,0))
    
        for platform in PLATFORMS:
            draw_textured_platform(platform['rect'], platform['type'])  
    
        for coin in coins:
            coin.draw()
    
        for enemy in enemies:
            enemy.draw()
    
        player.draw()
        
        if player.is_hit:  
            player.image = "tiles/character04"
            player.draw()
        
        screen.draw.text(f"Score: {score}", topleft=(10,10), fontsize=40)
        screen.draw.text(f"Dificuldade: {current_difficulty}", topleft=(10,50), fontsize=30)
    # HUD
        if game_won:
            screen.draw.text("PARABÉNS", center=(WIDTH//2, HEIGHT//2), fontsize=60, color='blue')
            screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=40, color='blue')
            
            if keyboard.ESCAPE:
                game_state = "menu"
        elif game_over:
            player.draw()
            screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=60, color='red')
            screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=40, color='red')
            
            if keyboard.ESCAPE:
                if music_on:
                    music.stop()
                game_state = "menu"
             
def clamp(n, minn, maxn): 
    return max(minn, min(n, maxn))

pgzrun.go()