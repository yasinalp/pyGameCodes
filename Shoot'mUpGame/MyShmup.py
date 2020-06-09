import pygame,random,math

BLACK,WHITE = (0,0,0),(255,255,255)
WIDTH,HEIGHT,FPS = 800,600,60
RED,GREEN,BLUE = (255,0,0),(0,255,0),(0,0,255)
player_center = [0,0]
pygame.init()
pygame.mouse.set_cursor((16, 16),(7, 7),(0, 0, 96, 6, 112, 14, 56, 28, 28, 56, 12, 48, 0, 0, 0, 0, 0, 0, 0, 0, 12, 48, 28, 56, 56, 28, 112, 14, 96, 6, 0, 0),(224, 7, 240, 15, 248, 31, 124, 62, 62, 124, 30, 120, 14, 112, 0, 0, 0, 0, 14, 112, 30, 120, 62, 124, 124, 62, 248, 31, 240, 15, 224, 7))
#print(*pygame.cursors.broken_x)
pygame.mixer.init()
pygame.mixer.music.load('snd/tgfcoder-FrozenJam-SeamlessLoop.ogg')
screen = pygame.display.set_mode((WIDTH,HEIGHT))
icon_img = pygame.transform.scale(pygame.image.load("img/playerShip1_orange.png"),(32,32))
pygame.display.set_icon(icon_img)
pygame.display.set_caption('ShmUp!')
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')
def draw_text(surf,text,size,x,y,coordtype='midtop',color=WHITE):
    font_obj = pygame.font.Font(font_name,size)
    text_surface = font_obj.render(text,True,color)
    text_rect = text_surface.get_rect()
    if coordtype == 'midtop':
        text_rect.midtop = x,y
    if coordtype == 'topleft':
        text_rect.topleft = x,y
    surf.blit(text_surface,text_rect)
def draw_shield_bar(surf,x,y,pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = pct
    fill_color = (255-pct*2.55,255,0)
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,fill_color,fill_rect)
    pygame.draw.rect(surf,WHITE,outline_rect,2)

def draw_lives(surf,x,y,lives):
    for i in range(lives):
        img = player_mini_img
        img_rect = img.get_rect()
        img_rect.topleft = (WIDTH/2-42)+(img_rect.width+5)*i,y
        surf.blit(img,img_rect)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.org_img = player_image
        self.org_img.set_colorkey(BLACK)
        self.image = self.org_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2,HEIGHT/2)
        self.radius = self.rect.width*0.35
        self.speedx, self.speedy = 0,0
        self.shield = 100
        self.lives = 3
        self.gunstate = 'normal'
        self.cooldown = 200
        self.cooldown_timer = pygame.time.get_ticks()
        self.upg_gun_timer = pygame.time.get_ticks()
        self.rot_angle = 0
        self.ang_diff_x = 0
        self.ang_diff_y = 0
    def update(self):
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speedx = 5
        else: self.speedx=0
        self.rect.x += self.speedx
        if keystate[pygame.K_UP] or keystate[pygame.K_w]:
            self.speedy = -5
        elif keystate[pygame.K_DOWN] or keystate[pygame.K_s]:
            self.speedy = 5
        else: self.speedy=0
        self.rect.y += self.speedy
        if self.gunstate=='powerup' and pygame.time.get_ticks()-self.upg_gun_timer > 5000:
            pygame.mixer.music.unpause()
            powerup_music.stop()
            self.gunstate = 'normal'
        if pygame.mouse.get_pressed()==(1,0,0):
            # print(pygame.mouse.get_pressed())
            self.shoot()
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.top < 0: self.rect.top=0
        if self.rect.bottom > HEIGHT: self.rect.bottom=HEIGHT
        self.rotate()
        self.player_coordinate()
    def shoot(self):
        now = pygame.time.get_ticks()
        if self.gunstate == 'normal':
            self.cooldown = 250
        elif self.gunstate == 'powerup':
            self.cooldown = 50
        if now-self.cooldown_timer > self.cooldown:
            self.cooldown_timer = now
            random.choice(laser_shoots).play()
            bullet = Bullet(self.rect.centerx,self.rect.centery,self.gunstate,self.rot_angle)
            bullets.add(bullet)
            all_sprites.add(bullet)

    def gun_upgrade(self):
        self.upg_gun_timer = pygame.time.get_ticks()
        self.gunstate = 'powerup'
    def cursor_angle(self):
        (cx,cy) = pygame.mouse.get_pos()
        self.ang_diff_x = (self.rect.centerx-cx)
        self.ang_diff_y = (self.rect.centery-cy)
        if self.ang_diff_x>0:
            theta_deg = 90
            if self.ang_diff_y>0:
                theta_rad = math.atan(self.ang_diff_x/self.ang_diff_y)
                theta_deg = math.degrees(theta_rad)
            elif self.ang_diff_y<0:
                theta_rad = math.atan(self.ang_diff_y/self.ang_diff_x)
                theta_deg = 90+(-math.degrees(theta_rad))
        elif self.ang_diff_x<0:
            theta_deg = -90
            if self.ang_diff_y>0:
                theta_rad = math.atan(self.ang_diff_x/self.ang_diff_y)
                theta_deg = math.degrees(theta_rad)
            if self.ang_diff_y<0:
                theta_rad = math.atan(self.ang_diff_y/self.ang_diff_x)
                theta_deg = -(90+math.degrees(theta_rad))
        elif self.ang_diff_y<0:
            theta_deg = 180
        else: theta_deg=0

        self.rot_angle = int(theta_deg)
        # print(self.rot_angle)
    def rotate(self):
        old_center = self.rect.center
        self.cursor_angle()
        new_image = pygame.transform.rotate(self.org_img,self.rot_angle)
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center
    def player_coordinate(self):
        global player_center
        player_center = self.rect.center
class Enemies(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(enemy_image_list)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0,WIDTH-100)
        self.rect.y = random.randint(-100,HEIGHT-500)
        self.radius = self.rect.width*0.35
        self.speedx = random.randint(-1,1)
        self.speedy = random.randint(1,8)
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT or self.rect.left>WIDTH or self.rect.right<0:
            self.kill()
            enemy = Enemies()
            all_sprites.add(enemy)
            enemies.add(enemy)
        elif self.rect.bottom > 0 and random.random()>0.995:
            rocket = Rockets(self.rect.center)
            rockets.add(rocket)
            all_sprites.add(rocket)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,guntype,angle):
        pygame.sprite.Sprite.__init__(self)
        self.angle = angle
        if guntype == 'normal':
            new_image = pygame.transform.rotate(bullet_image, self.angle)
        elif guntype == 'powerup':
            new_image = pygame.transform.rotate(upg_bullet_image, self.angle)
        self.image = new_image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.radius = self.rect.width*0.35
        self.speedx = -15*math.sin(math.radians(angle))
        self.speedy = -15*math.cos(math.radians(angle))
        
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top < 0 or self.rect.bottom>HEIGHT or self.rect.left<0 or self.rect.right>WIDTH:
            self.kill()
class Rockets(pygame.sprite.Sprite):
    def __init__(self,enemycenter):
        pygame.sprite.Sprite.__init__(self)
        self.angle = collision_angle(enemycenter, player_center)
        self.image = pygame.transform.rotate(random.choice(rocket_images),self.angle)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = enemycenter
        self.radius = self.rect.width * 0.35
        self.speedx = -8 * math.sin(math.radians(self.angle))
        self.speedy = -8 * math.cos(math.radians(self.angle))
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top < 0 or self.rect.bottom>HEIGHT or self.rect.left<0 or self.rect.right>WIDTH:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animations[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame=0
        self.frame_rate=50
        self.frame_timer = pygame.time.get_ticks()
    def update(self):
        now = pygame.time.get_ticks()
        if now-self.frame_timer>self.frame_rate:
            self.frame_timer = now
            self.frame += 1
            if self.frame == len(explosion_animations[self.size]):
                self.kill()
            else:
                self.image = explosion_animations[self.size][self.frame]
class Pow(pygame.sprite.Sprite):
    def __init__(self,center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','gun'])
        self.image = pow_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.radius = self.rect.width*0.35
        self.speedy = 1
    def update(self):
        self.rect.y += self.speedy
def collision_angle(center1,center2):
    (center2x,center2y) = center2[0],center2[1]
    (center1x,center1y) = center1[0],center1[1]
    ang_diff_x = (center1x-center2x)
    ang_diff_y = (center1y-center2y)
    if ang_diff_x>0:
        theta_deg = 90
        if ang_diff_y>0:
            theta_rad = math.atan(ang_diff_x/ang_diff_y)
            theta_deg = math.degrees(theta_rad)
        elif ang_diff_y<0:
            theta_rad = math.atan(ang_diff_y/ang_diff_x)
            theta_deg = 90+(-math.degrees(theta_rad))
    elif ang_diff_x<0:
        theta_deg = -90
        if ang_diff_y>0:
            theta_rad = math.atan(ang_diff_x/ang_diff_y)
            theta_deg = math.degrees(theta_rad)
        if ang_diff_y<0:
            theta_rad = math.atan(ang_diff_y/ang_diff_x)
            theta_deg = -(90+math.degrees(theta_rad))
    elif ang_diff_y<0:
        theta_deg = 180
    else: theta_deg=0
    return theta_deg
#image files
background_image = pygame.image.load('img/starfield.png').convert()
welcome_image = pygame.image.load('img/WelcomeScreen.png').convert()
welcome_image.set_colorkey(BLACK)
player_image_big = pygame.image.load('img/playerShip1_orange.png').convert()
player_image_big.set_colorkey(BLACK)
player_image = pygame.transform.scale(player_image_big,(86,76))
player_mini_img = pygame.transform.scale(player_image_big,(32,32))
bullet_image_big = pygame.image.load('img/laserRed16.png').convert()
bullet_image = pygame.transform.scale(bullet_image_big,(15,20))
upg_bullet_image_big = pygame.image.load('img/upg_laserRed16.png').convert()
upg_bullet_image = pygame.transform.scale(upg_bullet_image_big,(15,20))
rocket_images = []
for i in range(4):
    rocket_image = pygame.image.load('img/spaceRockets_00{}.png'.format(i+1)).convert()
    rocket_image.set_colorkey(BLACK)
    rocket_images.append(rocket_image)
enemy_image_list = []
for i in range(1,6):
    enemy_image_big = pygame.image.load('img/enemyBlack{}.png'.format(i)).convert()
    enemy_image = pygame.transform.scale(enemy_image_big,(70,60))
    enemy_image_list.append(enemy_image)
explosion_animations = {}
explosion_animations['lg'] = []
explosion_animations['sm'] = []
for i in range(9):
    exp_file = pygame.image.load('img/regularExplosion0{}.png'.format(i)).convert()
    exp_file.set_colorkey(BLACK)
    exp_lg = pygame.transform.scale(exp_file,(70,70))
    explosion_animations['lg'].append(exp_lg)
for i in range(9):
    exp_file = pygame.image.load('img/regularExplosion0{}.png'.format(i)).convert()
    exp_file.set_colorkey(BLACK)
    exp_sm = pygame.transform.scale(exp_file,(32,32))
    explosion_animations['sm'].append(exp_sm)
pow_images = {}
pow_images['shield'] = pygame.image.load('img/shield_gold.png')
pow_images['gun'] = pygame.image.load('img/bolt_gold.png')
#sound files
laser_shoots = [pygame.mixer.Sound('snd/Laser_Shoot1.wav'),pygame.mixer.Sound('snd/Laser_Shoot2.wav')]
for laser_shoot in laser_shoots:
    laser_shoot.set_volume(0.5)
get_shield_sounds = [pygame.mixer.Sound('snd/Get_shield1.wav'),pygame.mixer.Sound('snd/Get_shield2.wav')]
shield_hit_sounds = [pygame.mixer.Sound('snd/Shield_Hit1.wav'),pygame.mixer.Sound('snd/Shield_Hit2.wav')
                    ,pygame.mixer.Sound('snd/Shield_Hit3.wav'),pygame.mixer.Sound('snd/Shield_Hit4.wav')]
powerup_sounds = [pygame.mixer.Sound('snd/Powerup1.wav'),pygame.mixer.Sound('snd/Powerup2.wav')
                    ,pygame.mixer.Sound('snd/Powerup3.wav')]
powerup_music = pygame.mixer.Sound('snd/tgfcoder-FrozenJam-SeamlessLoop-1.5x.ogg')
explosion_sounds = []
for i in range(1,6):
    exp_sound = pygame.mixer.Sound('snd/Exp{}.wav'.format(i))
    explosion_sounds.append(exp_sound)

pygame.mixer.music.play()
running = True
gamestate = 'welcome'
pause_timer = pygame.time.get_ticks()
while running:
    #Process inputs
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_p and gamestate=='game_on' and pygame.time.get_ticks()-pause_timer>250:
            pause_timer = pygame.time.get_ticks()
            gamestate = 'pause'
    if gamestate == 'initialize':
        all_sprites = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        rockets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player_Group = pygame.sprite.Group()
        player = Player()
        player_Group.add(player)
        all_sprites.add(player)
        for i in range(5):
            enemy = Enemies()
            all_sprites.add(enemy)
            enemies.add(enemy)
        gamestate = 'game_on'
        score = 0
    #Oyun öncesi kısım
    if gamestate == 'welcome':
        screen.blit(background_image, (0, 0))
        screen.blit(welcome_image,(0,0))
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE]:
            gamestate = 'initialize'
        elif keystate[pygame.K_ESCAPE]:
            running = False
    # Game is paused
    if gamestate == 'pause':
        draw_text(screen,"Press 'P' to continue",36,WIDTH/2,HEIGHT*2/5)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        if pygame.key.get_pressed()[pygame.K_p]:
            if pygame.time.get_ticks()-pause_timer>250:
                pause_timer = pygame.time.get_ticks()
                gamestate = 'game_on'
    # Game is running
    if gamestate == 'game_on':
        #Update objects
        all_sprites.update()
        #Check collisions
        hits = pygame.sprite.groupcollide(enemies,bullets,True,True,pygame.sprite.collide_circle)
        for hit in hits:
            score += 1
            if random.random()>0.9:
                pwup = Pow(hit.rect.center)
                all_sprites.add(pwup)
                powerups.add(pwup)
            expl = Explosion(hit.rect.center,'lg')
            all_sprites.add(expl)
            random.choice(explosion_sounds).play()
            enemy = Enemies()
            all_sprites.add(enemy)
            enemies.add(enemy)
        hits = pygame.sprite.spritecollide(player,powerups,True,pygame.sprite.collide_circle)
        for hit in hits:
            if hit.type == 'shield':
                random.choice(get_shield_sounds).play()
                player.shield += 10
                if player.shield > 100: player.shield=100
            if hit.type == 'gun':
                random.choice(powerup_sounds).play()
                player.gun_upgrade()
                pygame.mixer.music.pause()
                powerup_music.play()
        hits = pygame.sprite.spritecollide(player,enemies,False,pygame.sprite.collide_circle)
        for hit in hits:
            random.choice(shield_hit_sounds).play()
            theta = collision_angle(player.rect.center,hit.rect.center)
            player.shield -= 34
            player.rect.x -= 8*player.speedx
            player.rect.y -= 8*player.speedy
            hit.rect.x -= 5*hit.radius*math.sin(math.radians(theta))
            hit.rect.y -= 5*hit.radius*math.cos(math.radians(theta))
            if player.shield <= 0:
                if player.lives >= 1:
                    player.lives -= 1
                    player.shield = 100
                else: gamestate = 'gameover'
        hits = pygame.sprite.spritecollide(player, rockets, True, pygame.sprite.collide_circle)
        for hit in hits:
            random.choice(shield_hit_sounds).play()
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            random.choice(explosion_sounds).play()
            theta = collision_angle(player.rect.center, hit.rect.center)
            player.shield -= 10
            if player.shield <= 0:
                if player.lives >= 1:
                    player.lives -= 1
                    player.shield = 100
                else:
                    gamestate = 'gameover'

        #Draw objects
        screen.blit(background_image,(0,0))
        all_sprites.draw(screen)
        draw_shield_bar(screen, WIDTH - 105, 5, player.shield)
        draw_lives(screen, 0, 5, player.lives)
        draw_text(screen,'SCORE:{}'.format(int(score)),28,5,5,'topleft')
    # GAMEOVER state
    if gamestate == 'gameover':
        try:
            with open('highscore.txt',"r") as f:
                highscore = f.read()
                print('highscore:{}'.format(highscore))
                f.close()
        except FileNotFoundError:
            highscore = 0
        if score > int(highscore):
            with open('highscore.txt', "w") as f:
                f.seek(0)
                f.write(str(score))
        gamestate = 'gameover2'
    if gamestate == 'gameover2':

        screen.blit(background_image,(0,0))
        draw_text(screen,'GAME OVER!',72,WIDTH/2,HEIGHT*2/5,'midtop',(240,20,20))
        draw_text(screen,'YOUR SCORE:{}!'.format(score),36,WIDTH/2,HEIGHT/4,'midtop',(230,230,230))
        draw_text(screen,'HIGH SCORE:{}'.format(highscore),36,WIDTH/2,HEIGHT/8)
        draw_text(screen,'Press SPACE to restart',24,WIDTH/2,HEIGHT*3/4)
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE]:
            gamestate = 'initialize'
        elif keystate[pygame.K_ESCAPE]:
            running = False
    #Flip
    # print(gamestate)
    # print(clock.get_fps())
    pygame.display.flip()
    clock.tick(FPS)