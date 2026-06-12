import pygame
import random
import sys
import os
import math
from configs import config
# ======================================================================
#  CONSTANTES INTERNAS
# ======================================================================

# Dimensões do mapa em tiles
TILES_LARGURA = 80
TILES_ALTURA = 60

# Grade de salas: quantas células de sala existem
CELULAS_X = 6
CELULAS_Y = 4

# Tamanho de cada sala em tiles (mínimo e máximo)
SALA_MIN_W, SALA_MAX_W = 8, 14
SALA_MIN_H, SALA_MAX_H = 6, 10

# Temas disponíveis (afeta quais decorações são colocadas)
TEMAS = ["laboratorio", "enfermaria", "deposito", "controle", "corredor", "banheiro"]

# Tile IDs  (compatíveis com o config.py original)
T_CHAO = 0
T_PAREDE = 1
T_SAIDA = 2
T_SANGUE = 3
T_MACA = 4
T_PC = 5
T_VAZIO = 9  # fora do mapa — tratado como parede para colisão


# ======================================================================
#  GERADOR DE MAPA
# ======================================================================


class GeradorMapa:
    def __init__(self):
        self.grid = [[T_PAREDE] * TILES_LARGURA for _ in range(TILES_ALTURA)]
        self.salas: list[dict] = []
        self.spawn_player = (2, 2)  # tile x, y
        self.tile_saida = (TILES_LARGURA - 4, TILES_ALTURA - 4)

    # ------------------------------------------------------------------

    def gerar(self, seed: int | None = None) -> list[list[int]]:
        if seed is not None:
            random.seed(seed)

        self._colocar_salas()
        self._conectar_salas()
        self._decorar_salas()
        self._colocar_paredes_border()
        self._definir_spawn_e_saida()
        return self.grid

    # ------------------------------------------------------------------

    def _colocar_salas(self):
        """Divide o mapa em células e gera uma sala em cada uma."""
        cel_w = TILES_LARGURA // CELULAS_X
        cel_h = TILES_ALTURA // CELULAS_Y

        for cy in range(CELULAS_Y):
            for cx in range(CELULAS_X):
                # Posição base da célula em tiles
                base_x = cx * cel_w + 1
                base_y = cy * cel_h + 1

                # Dimensão aleatória da sala
                sw = random.randint(SALA_MIN_W, min(SALA_MAX_W, cel_w - 2))
                sh = random.randint(SALA_MIN_H, min(SALA_MAX_H, cel_h - 2))

                # Offset dentro da célula para variedade
                ox = random.randint(0, max(0, cel_w - sw - 2))
                oy = random.randint(0, max(0, cel_h - sh - 2))

                sx = base_x + ox
                sy = base_y + oy

                tema = random.choice(TEMAS)
                self._escavar_sala(sx, sy, sw, sh)
                self.salas.append(
                    {
                        "x": sx,
                        "y": sy,
                        "w": sw,
                        "h": sh,
                        "cx": cx,
                        "cy": cy,
                        "tema": tema,
                        # centro em tiles para conectar corredores
                        "centro_x": sx + sw // 2,
                        "centro_y": sy + sh // 2,
                    }
                )

    def _escavar_sala(self, x, y, w, h):
        for ty in range(y, y + h):
            for tx in range(x, x + w):
                if 0 < tx < TILES_LARGURA - 1 and 0 < ty < TILES_ALTURA - 1:
                    self.grid[ty][tx] = T_CHAO

    # ------------------------------------------------------------------

    def _conectar_salas(self):
        """Conecta cada sala com sua vizinha à direita e abaixo (corredores em L)."""
        cel_w = TILES_LARGURA // CELULAS_X
        cel_h = TILES_ALTURA // CELULAS_Y

        for sala in self.salas:
            cx, cy = sala["cx"], sala["cy"]

            # conecta com a sala à direita
            if cx + 1 < CELULAS_X:
                vizinha = self._sala_em(cx + 1, cy)
                if vizinha:
                    self._escavar_corredor(
                        sala["centro_x"],
                        sala["centro_y"],
                        vizinha["centro_x"],
                        vizinha["centro_y"],
                        largura=random.randint(2, 3),
                    )

            # conecta com a sala abaixo
            if cy + 1 < CELULAS_Y:
                vizinha = self._sala_em(cx, cy + 1)
                if vizinha:
                    self._escavar_corredor(
                        sala["centro_x"],
                        sala["centro_y"],
                        vizinha["centro_x"],
                        vizinha["centro_y"],
                        largura=random.randint(2, 3),
                    )

    def _sala_em(self, cx, cy) -> dict | None:
        for s in self.salas:
            if s["cx"] == cx and s["cy"] == cy:
                return s
        return None

    def _escavar_corredor(self, x1, y1, x2, y2, largura=2):
        """Corredor em L (horizontal depois vertical)."""
        half = largura // 2

        # trecho horizontal
        for tx in range(min(x1, x2), max(x1, x2) + 1):
            for off in range(-half, half + 1):
                ny = y1 + off
                if 0 < tx < TILES_LARGURA - 1 and 0 < ny < TILES_ALTURA - 1:
                    self.grid[ny][tx] = T_CHAO

        # trecho vertical
        for ty in range(min(y1, y2), max(y1, y2) + 1):
            for off in range(-half, half + 1):
                nx = x2 + off
                if 0 < nx < TILES_LARGURA - 1 and 0 < ty < TILES_ALTURA - 1:
                    self.grid[ty][nx] = T_CHAO

    # ------------------------------------------------------------------

    def _decorar_salas(self):
        """Adiciona sangue, macas, PCs etc. conforme o tema da sala."""
        decor_por_tema = {
            "laboratorio": [(T_PC, 0.12), (T_SANGUE, 0.08)],
            "enfermaria": [(T_MACA, 0.15), (T_SANGUE, 0.12)],
            "deposito": [(T_SANGUE, 0.06)],
            "controle": [(T_PC, 0.18), (T_SANGUE, 0.05)],
            "corredor": [(T_SANGUE, 0.04)],
            "banheiro": [(T_SANGUE, 0.20), (T_MACA, 0.06)],
        }

        for sala in self.salas:
            tema = sala["tema"]
            regras = decor_por_tema.get(tema, [])

            for ty in range(sala["y"] + 1, sala["y"] + sala["h"] - 1):
                for tx in range(sala["x"] + 1, sala["x"] + sala["w"] - 1):
                    if self.grid[ty][tx] != T_CHAO:
                        continue
                    for tile_id, chance in regras:
                        if random.random() < chance:
                            self.grid[ty][tx] = tile_id
                            break  # um único item por tile

    # ------------------------------------------------------------------

    def _colocar_paredes_border(self):
        """Garante que a borda exterior seja sempre parede."""
        for tx in range(TILES_LARGURA):
            self.grid[0][tx] = T_PAREDE
            self.grid[TILES_ALTURA - 1][tx] = T_PAREDE
        for ty in range(TILES_ALTURA):
            self.grid[ty][0] = T_PAREDE
            self.grid[ty][TILES_LARGURA - 1] = T_PAREDE

    def _definir_spawn_e_saida(self):
        """Coloca o spawn do player na primeira sala e a saída na última."""
        if self.salas:
            s0 = self.salas[0]
            self.spawn_player = (s0["centro_x"], s0["centro_y"])
            sf = self.salas[-1]
            tx, ty = sf["centro_x"], sf["centro_y"]
            if 0 < tx < TILES_LARGURA - 1 and 0 < ty < TILES_ALTURA - 1:
                self.grid[ty][tx] = T_CHAO  # sem tile de saída visível
            self.tile_saida = (tx, ty)


# ======================================================================
#  CLASSE MAPA — mantém compatibilidade com o resto do projeto
# ======================================================================


class Mapa:
    def __init__(self, seed: int | None = None):
        self.sprites: dict[int, pygame.Surface] = {}
        self.paredes_fisicas: list[pygame.Rect] = []
        self.zona_saida_rect: pygame.Rect | None = None
        self.spawn_player_px: tuple[int, int] = (100, 100)

        # Gera o mapa proceduralmente
        gerador = GeradorMapa()
        self.matriz = gerador.gerar(seed=seed)
        self.spawn_player_px = (
            gerador.spawn_player[0] * config.TAMANHO_TILE + config.TAMANHO_TILE // 2,
            gerador.spawn_player[1] * config.TAMANHO_TILE + config.TAMANHO_TILE // 2,
        )

        self._carregar_sprites()
        self._gerar_colisoes()

    # ------------------------------------------------------------------

    def _carregar_sprites(self):
        """Carrega e fatiaa os tilesets — mesma lógica do mapa.py original."""
        pasta = os.path.join("..", "assets", "sprite", "Life Asset Pack", "Tilesets")
        if not os.path.exists(pasta):
            pasta = os.path.join("assets", "sprite", "Life Asset Pack", "Tilesets")

        T = config.TAMANHO_TILE

        # --- Chão de concreto ---
        try:
            img = pygame.image.load(
                os.path.join(pasta, "ColourfulTileset.png")
            ).convert_alpha()
            self.sprites[T_CHAO] = pygame.transform.scale(
                img.subsurface(pygame.Rect(0, 0, 16, 16)), (T, T)
            )
        except Exception:
            s = pygame.Surface((T, T))
            s.fill((25, 25, 25))
            self.sprites[T_CHAO] = s

        # --- Parede de metal ---
        try:
            img = pygame.image.load(
                os.path.join(pasta, "MetalGrateTileset.png")
            ).convert_alpha()
            self.sprites[T_PAREDE] = pygame.transform.scale(
                img.subsurface(pygame.Rect(0, 0, 64, 64)), (T, T)
            )
        except Exception:
            s = pygame.Surface((T, T))
            s.fill((45, 45, 50))
            self.sprites[T_PAREDE] = s

        # --- Decorações ---
        try:
            img = pygame.image.load(
                os.path.join(pasta, "BackgroundItemsTileset.png")
            ).convert_alpha()
            recortes = {
                T_SAIDA: pygame.Rect(704, 768, 64, 64),
                T_SANGUE: pygame.Rect(64, 704, 64, 64),
                T_MACA: pygame.Rect(64, 128, 64, 64),
                T_PC: pygame.Rect(576, 576, 64, 64),
            }
            for tile_id, rect in recortes.items():
                self.sprites[tile_id] = pygame.transform.scale(
                    img.subsurface(rect), (T, T)
                )
        except Exception as e:
            print(f"[Mapa] Erro ao carregar decorações: {e}")
            saida = pygame.Surface((T, T))
            saida.fill((0, 150, 255))
            self.sprites[T_SAIDA] = saida
            self.sprites[T_SANGUE] = self.sprites[T_CHAO]
            self.sprites[T_MACA] = self.sprites[T_CHAO]
            self.sprites[T_PC] = self.sprites[T_CHAO]

    # ------------------------------------------------------------------

    def _gerar_colisoes(self):
        self.paredes_fisicas.clear()
        T = config.TAMANHO_TILE
        for linha_idx, linha in enumerate(self.matriz):
            for col_idx, bloco in enumerate(linha):
                rect = pygame.Rect(col_idx * T, linha_idx * T, T, T)
                if bloco == T_PAREDE:
                    self.paredes_fisicas.append(rect)
    # ------------------------------------------------------------------

    def desenhar(
        self, tela: pygame.Surface, camera_offset_x: int, camera_offset_y: int
    ):
        """
        Renderiza apenas os tiles visíveis na tela (frustum culling simples).
        Compatível com o sistema de câmera do projeto.
        """
        T = config.TAMANHO_TILE
        largura_tela = tela.get_width()
        altura_tela = tela.get_height()

        # Calcula quais tiles estão na tela
        col_inicio = max(0, camera_offset_x // T)
        col_fim = min(len(self.matriz[0]), (camera_offset_x + largura_tela) // T + 2)
        lin_inicio = max(0, camera_offset_y // T)
        lin_fim = min(len(self.matriz), (camera_offset_y + altura_tela) // T + 2)

        for lin in range(lin_inicio, lin_fim):
            for col in range(col_inicio, col_fim):
                bloco = self.matriz[lin][col]
                if bloco == T_VAZIO:
                    continue

                sprite = self.sprites.get(bloco)
                if sprite is None:
                    sprite = self.sprites.get(T_CHAO)  # fallback

                px = col * T - camera_offset_x
                py = lin * T - camera_offset_y
                tela.blit(sprite, (px, py))

    # ------------------------------------------------------------------

    @property
    def largura_px(self) -> int:
        return TILES_LARGURA * config.TAMANHO_TILE

    @property
    def altura_px(self) -> int:
        return TILES_ALTURA * config.TAMANHO_TILE

    def tiles_chao(self) -> list[tuple[int, int]]:
        """
        Retorna lista de posições em pixel (centro de cada tile de chão).
        Usado pelo spawner de zumbis.
        """
        T = config.TAMANHO_TILE
        resultado = []
        for lin, linha in enumerate(self.matriz):
            for col, bloco in enumerate(linha):
                if bloco != T_PAREDE and bloco != T_VAZIO:
                    resultado.append(
                        (
                            col * T + T // 2,
                            lin * T + T // 2,
                        )
                    )
        return resultado
