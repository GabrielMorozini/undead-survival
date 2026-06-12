import pygame
import math
import random
import os
from configs import config

# --- CONFIGURAÇÕES ---
VELOCIDADE_MIN = 1.5
VELOCIDADE_MAX = 3.5
ALCANCE_VISAO  = 280
ALCANCE_ATAQUE = 22
COOLDOWN_DANO  = 800  # ms
TOTAL_ZUMBIS   = 100

_NOMES_SPRITES = [
    "ZombieLabcoat1.png",
    "ZombieLabcoat2.png",
    "ZombiePrisonerBrute.png",
    "ZombiePrisonerSkinny.png",
]

_imagens_carregadas: list[pygame.Surface] = []


def _carregar_imagens():
    global _imagens_carregadas
    if _imagens_carregadas:
        return

    pasta = os.path.join("..", "assets", "sprite", "Life Asset Pack", "Characters", "Zombies")

    for nome in _NOMES_SPRITES:
        caminho = os.path.join(pasta, nome)
        if os.path.exists(caminho):
            try:
                surf = pygame.image.load(caminho).convert_alpha()
                surf = pygame.transform.scale(surf, (42, 42))
                _imagens_carregadas.append(surf)
                print(f"[Zumbi] Carregado: {nome}")
            except Exception as e:
                print(f"[Zumbi] Erro em {caminho}: {e}")
        else:
            print(f"[Zumbi] Não encontrado: {caminho}")

    if not _imagens_carregadas:
        surf = pygame.Surface((38, 38), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (80, 160, 80, 230), (0, 0, 38, 38))
        pygame.draw.circle(surf, (220, 30, 30), (13, 14), 4)
        pygame.draw.circle(surf, (220, 30, 30), (25, 14), 4)
        _imagens_carregadas.append(surf)
        print("[Zumbi] Usando placeholder.")


class Zumbi(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, velocidade: float,
                 limite_x: float, limite_y: float):  # ← limites adicionados
        super().__init__()

        _carregar_imagens()

        self._img_base  = random.choice(_imagens_carregadas)
        self.image      = self._img_base
        self.rect       = self.image.get_rect(center=(int(x), int(y)))

        self.pos_x      = float(x)
        self.pos_y      = float(y)
        self.velocidade = velocidade
        self.perseguindo = False
        self.ultimo_dano = 0
        self.vivo        = True
        self._ruido_ang  = random.uniform(-0.10, 0.10)
        self._angulo_atual = 0.0
        self._limite_x   = limite_x  # ← salva limites
        self._limite_y   = limite_y

    def update(self, player_rect: pygame.Rect, paredes: list, dt: int):
        if not self.vivo:
            return

        cx   = player_rect.centerx
        cy   = player_rect.centery
        dist = math.hypot(cx - self.pos_x, cy - self.pos_y)

        if dist <= ALCANCE_VISAO:
            self.perseguindo = True
        elif dist > ALCANCE_VISAO * 1.2:
            self.perseguindo = False

        if self.perseguindo and dist > 2:
            angulo = math.atan2(cy - self.pos_y, cx - self.pos_x) + self._ruido_ang
            self._angulo_atual = angulo
            dx = math.cos(angulo) * self.velocidade
            dy = math.sin(angulo) * self.velocidade

            # Eixo X
            self.pos_x += dx
            self.rect.centerx = int(self.pos_x)
            for parede in paredes:
                if self.rect.colliderect(parede):
                    if dx > 0:
                        self.rect.right = parede.left
                    else:
                        self.rect.left  = parede.right
                    self.pos_x = float(self.rect.centerx)
                    break

            # Eixo Y
            self.pos_y += dy
            self.rect.centery = int(self.pos_y)
            for parede in paredes:
                if self.rect.colliderect(parede):
                    if dy > 0:
                        self.rect.bottom = parede.top
                    else:
                        self.rect.top    = parede.bottom
                    self.pos_y = float(self.rect.centery)
                    break

        # Clamp com limites reais do mapa
        MARGEM = config.TAMANHO_TILE
        self.pos_x = max(MARGEM, min(self.pos_x, self._limite_x - MARGEM))
        self.pos_y = max(MARGEM, min(self.pos_y, self._limite_y - MARGEM))

        # Rotaciona sprite
        graus      = -math.degrees(self._angulo_atual)
        self.image = pygame.transform.rotate(self._img_base, graus)
        self.rect  = self.image.get_rect(center=(int(self.pos_x), int(self.pos_y)))

    def tentar_causar_dano(self, player_rect: pygame.Rect) -> bool:
        now  = pygame.time.get_ticks()
        dist = math.hypot(
            player_rect.centerx - self.pos_x,
            player_rect.centery - self.pos_y,
        )
        if dist <= ALCANCE_ATAQUE and (now - self.ultimo_dano) >= COOLDOWN_DANO:
            self.ultimo_dano = now
            return True
        return False

    def morrer(self):
        self.vivo = False
        self.kill()


# ======================================================================
#  SPAWNER
# ======================================================================
def spawnar_zumbis(
    mapa_matriz: list, tamanho_tile: int, pos_player: tuple,
    total_zumbis: int = 100
) -> pygame.sprite.Group:
    grupo   = pygame.sprite.Group()
    linhas  = len(mapa_matriz)
    colunas = len(mapa_matriz[0]) if linhas > 0 else 0
    margem  = 3

    # Limites reais do mapa em pixels
    limite_x = colunas * tamanho_tile
    limite_y = linhas  * tamanho_tile

    tiles_chao = []
    for lin in range(margem, linhas - margem):
        for col in range(margem, colunas - margem):
            bloco = mapa_matriz[lin][col]
            if bloco not in (0, 4, 5, 6, 7):
                continue
            vizinhos_ok = all(
                mapa_matriz[lin + dl][col + dc] not in (1, 9)
                for dl in (-1, 0, 1)
                for dc in (-1, 0, 1)
            )
            if not vizinhos_ok:
                continue
            cx = col * tamanho_tile + tamanho_tile // 2
            cy = lin  * tamanho_tile + tamanho_tile // 2
            if math.hypot(cx - pos_player[0], cy - pos_player[1]) > 350:
                tiles_chao.append((cx, cy))

    if not tiles_chao:
        print("[Spawner] Nenhum tile de chão válido encontrado!")
        return grupo

    random.shuffle(tiles_chao)

    for i in range(total_zumbis):
        tile = tiles_chao[i % len(tiles_chao)]
        vel  = random.triangular(
            VELOCIDADE_MIN, VELOCIDADE_MAX,
            (VELOCIDADE_MIN + VELOCIDADE_MAX) / 2
        )
        grupo.add(Zumbi(float(tile[0]), float(tile[1]), vel, limite_x, limite_y))

    print(f"[Spawner] {len(grupo)} zumbis em {len(tiles_chao)} tiles válidos.")
    return grupo