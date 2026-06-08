import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0)) # Jogador verde por enquanto
        self.rect = self.image.get_rect(topleft=(100, 100))
        
        # Inventário de letras coletadas
        self.letras_coletadas = []

    def coletar_letra(self, letra):
        self.letras_coletadas.append(letra)
        print(f"Letra coletada: {letra}. Inventário: {self.letras_coletadas}")

    def update(self):
        # Lógica de movimento virá aqui depois
        pass