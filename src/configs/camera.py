import sys
import os
import pygame
import math
from configs import config


class Camera:
    def __init__(self):
        self.offset_x     = 0
        self.offset_y     = 0
        self.largura_tela = config.LARGURA
        self.altura_tela  = config.ALTURA
        self._surf_sombra = pygame.Surface(
            (config.LARGURA, config.ALTURA), pygame.SRCALPHA
        )
        # Cache do grid de tiles para ray casting eficiente
        self._grid_cache      = None
        self._tile_size_cache = 0

    def focar(self, rect_alvo: pygame.Rect):
        self.offset_x = rect_alvo.centerx - self.largura_tela // 2
        self.offset_y = rect_alvo.centery - self.altura_tela  // 2

    def aplicar(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(
            rect.x - self.offset_x,
            rect.y - self.offset_y,
            rect.width,
            rect.height,
        )

    def configurar_grid(self, mapa_matriz: list, tamanho_tile: int):
        """
        Pré-processa o mapa em um set de tiles sólidos para lookup O(1).
        Chame uma vez após criar o mapa.
        """
        self._grid_cache      = set()
        self._tile_size_cache = tamanho_tile
        for lin, linha in enumerate(mapa_matriz):
            for col, bloco in enumerate(linha):
                if bloco == 1:   # parede
                    self._grid_cache.add((col, lin))

    def _tile_solido(self, mundo_x: int, mundo_y: int) -> bool:
        """Verifica se a coordenada de mundo cai em tile sólido — O(1)."""
        if not self._grid_cache:
            return False
        col = mundo_x // self._tile_size_cache
        lin = mundo_y // self._tile_size_cache
        return (col, lin) in self._grid_cache

    def desenhar_campo_visao(self, tela, rect_jogador, paredes=None):
        """
        Lanterna com sombras. Usa lookup de grid em O(1) por passo,
        bem mais rápido que testar todos os rects de parede.
        """
        RAIO         = 200
        NUM_RAIOS    = 60    # 60 raios é suave o suficiente e muito mais leve
        PASSO        = 8     # px por iteração do raio
        ALPHA_ESCURO = 210

        cx = rect_jogador.centerx - self.offset_x
        cy = rect_jogador.centery - self.offset_y

        self._surf_sombra.fill((0, 0, 0, ALPHA_ESCURO))

        usa_raycasting = self._grid_cache is not None

        tiles_visiveis = set()  # ← adiciona isso
    
        if usa_raycasting:
          pontos = [(cx, cy)]
          for i in range(NUM_RAIOS):
            angulo = (2 * math.pi / NUM_RAIOS) * i
            dx = math.cos(angulo) * PASSO
            dy = math.sin(angulo) * PASSO
            px, py = float(cx), float(cy)

            for _ in range(RAIO // PASSO):
                px += dx
                py += dy
                mundo_x = int(px) + self.offset_x
                mundo_y = int(py) + self.offset_y
                # ← coleta tile a cada passo do raio
                tiles_visiveis.add((mundo_x // self._tile_size_cache,
                                    mundo_y // self._tile_size_cache))
                if self._tile_solido(mundo_x, mundo_y):
                    break
            pontos.append((int(px), int(py)))

        if len(pontos) >= 3:
            pygame.draw.polygon(self._surf_sombra, (0, 0, 0, 0), pontos)
            pygame.draw.polygon(self._surf_sombra, (0, 0, 0, ALPHA_ESCURO // 4),
                                pontos, width=14)
        else:
        # Fallback: marca círculo de tiles como visíveis
            for col in range(-RAIO // self._tile_size_cache - 1, RAIO // self._tile_size_cache + 2):
                for lin in range(-RAIO // self._tile_size_cache - 1, RAIO // self._tile_size_cache + 2):
                    tiles_visiveis.add((
                    rect_jogador.centerx // self._tile_size_cache + col,
                    rect_jogador.centery // self._tile_size_cache + lin,
                ))

        tela.blit(self._surf_sombra, (0, 0))
        return tiles_visiveis  # ← retorna o set