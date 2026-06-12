import pygame
import os
import math

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.largura = 40
        self.altura = 40
        
        pasta_characters = os.path.join("..", "assets", "sprite", "Life Asset Pack", "Characters", "Player")
        if not os.path.exists(pasta_characters):
            pasta_characters = os.path.join("assets", "sprite", "Life Asset Pack", "Characters", "Player")
            
        caminho_sprite = os.path.join(pasta_characters, "PlayerPistol.png")

        try:
            folha_sprite = pygame.image.load(caminho_sprite).convert_alpha()
            quadrado_player = folha_sprite.subsurface(pygame.Rect(0, 0, 48, 48))
            self.image_base = pygame.transform.scale(quadrado_player, (self.largura, self.altura))
        except Exception as e:
            print(f"Erro ao carregar sprite: {e}")
            self.image_base = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
            pygame.draw.circle(self.image_base, (0, 180, 90), (self.largura // 2, self.altura // 2), self.largura // 2)
            
        self.image = self.image_base.copy()
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100
        self.velocidade = 4

        # --- MUNIÇÃO ---
        self.municao = 12
        self.municao_maxima = 30
        self.cooldown_tiro = 0  # Evita atirar 60x por segundo

    def atirar(self):
        """Retorna True se conseguiu atirar, False se não tem munição."""
        if self.municao > 0 and self.cooldown_tiro <= 0:
            self.municao -= 1
            self.cooldown_tiro = 20  # Frames de espera entre tiros
            return True
        return False

    def adicionar_municao(self, quantidade):
        self.municao = min(self.municao + quantidade, self.municao_maxima)

    def update(self, paredes):
        teclas = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dx = -self.velocidade
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dx = self.velocidade
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dy = -self.velocidade
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dy = self.velocidade

        self.rect.x += dx
        for parede in paredes:
            if self.rect.colliderect(parede):
                if dx > 0: self.rect.right = parede.left
                if dx < 0: self.rect.left = parede.right

        self.rect.y += dy
        for parede in paredes:
            if self.rect.colliderect(parede):
                if dy > 0: self.rect.bottom = parede.top
                if dy < 0: self.rect.top = parede.bottom

        # Diminui o cooldown a cada frame
        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= 1

    def mirar(self, pos_jogador_tela):
        pos_mouse = pygame.mouse.get_pos()
        dx = pos_mouse[0] - pos_jogador_tela.centerx
        dy = pos_mouse[1] - pos_jogador_tela.centery
        angulo_radianos = math.atan2(-dy, dx)
        angulo_graus = math.degrees(angulo_radianos)
        self.image = pygame.transform.rotate(self.image_base, angulo_graus)