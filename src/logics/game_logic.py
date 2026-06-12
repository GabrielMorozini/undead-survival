import sys
import pygame
import math
import os
import random
from zombie import spawnar_zumbis, TOTAL_ZUMBIS
from configs import config

# ======================================================================
#  BALA
# ======================================================================

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, alvo_x, alvo_y):
        super().__init__()
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 100), (3, 3), 3)
        self.rect = self.image.get_rect(center=(x, y))
        dx = alvo_x - x
        dy = alvo_y - y
        distancia = math.hypot(dx, dy) or 1
        self.vel_x = (dx / distancia) * 12
        self.vel_y = (dy / distancia) * 12
        self.pos_x = float(x)
        self.pos_y = float(y)

    def update(self, paredes):
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        if not (-500 < self.pos_x < 6000 and -500 < self.pos_y < 6000):
            self.kill()
            return
        for parede in paredes:
            if self.rect.colliderect(parede):
                self.kill()
                return


# ======================================================================
#  ITEM DE MUNIÇÃO
# ======================================================================

class ItemMunicao(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 220, 0), (2, 4, 12, 8))
        pygame.draw.rect(self.image, (200, 160, 0), (2, 4, 12, 8), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.quantidade = 6


# ======================================================================
#  GERENCIADOR DE SONS DE ZUMBI
# ======================================================================

class SonsZumbi:
    def __init__(self):
        self.sons_dor = []
        self.sons_ambiente = []
        self._ultimo_ambiente = 0
        self._intervalo_ambiente = random.randint(3000, 7000)
        self.som_aviso = None

        pasta = os.path.join("..", "assets", "sfx", "zombie")
        if not os.path.exists(pasta):
            pasta = os.path.join("assets", "sfx", "zombie")

        for nome in ["zombie Dying.wav"]:
            caminho = os.path.join(pasta, nome)
            if os.path.exists(caminho):
                try:
                    s = pygame.mixer.Sound(caminho)
                    s.set_volume(0.6)
                    self.sons_dor.append(s)
                except Exception as e:
                    print(f"[Som] Erro dor: {e}")

        for nome in [
            "ZombiesMoans - Track 5 - ZombieMoan1.wav",
            "ZombiesMoans - Track 6 - ZombieMoan2.wav",
            "ZombiesMoans - Track 7 - ZombieMoan3.wav",
            "Moans_preview.mp3",
        ]:
            caminho = os.path.join(pasta, nome)
            if os.path.exists(caminho):
                try:
                    s = pygame.mixer.Sound(caminho)
                    s.set_volume(0.3)
                    self.sons_ambiente.append(s)
                except Exception as e:
                    print(f"[Som] Erro ambiente: {e}")

        caminho_aviso = os.path.join(pasta, "i_see_you_voice.mp3")
        if os.path.exists(caminho_aviso):
            try:
                self.som_aviso = pygame.mixer.Sound(caminho_aviso)
                self.som_aviso.set_volume(0.5)
            except Exception as e:
                print(f"[Som] Erro aviso: {e}")

        print(f"[Som] {len(self.sons_dor)} dor, {len(self.sons_ambiente)} ambiente carregados.")

    def tocar_dor(self):
        if self.sons_dor:
            random.choice(self.sons_dor).play()

    def tocar_aviso(self):
        if self.som_aviso:
            self.som_aviso.play()

    def atualizar_ambiente(self, num_zumbis: int):
        if not self.sons_ambiente or num_zumbis == 0:
            return
        agora = pygame.time.get_ticks()
        if agora - self._ultimo_ambiente >= self._intervalo_ambiente:
            random.choice(self.sons_ambiente).play()
            self._ultimo_ambiente = agora
            self._intervalo_ambiente = random.randint(3000, 7000)


class SonsJogo:
    def __init__(self):
        self.som_tiro  = None
        self.som_morte = None

        pasta_shot  = os.path.join("..", "assets", "sfx", "shot")
        pasta_death = os.path.join("..", "assets", "sfx", "death")
        if not os.path.exists(pasta_shot):
            pasta_shot  = os.path.join("assets", "sfx", "shot")
        if not os.path.exists(pasta_death):
            pasta_death = os.path.join("assets", "sfx", "death")

        try:
            arquivos = [f for f in os.listdir(pasta_shot) if os.path.isfile(os.path.join(pasta_shot, f))]
            if arquivos:
                s = pygame.mixer.Sound(os.path.join(pasta_shot, arquivos[0]))
                s.set_volume(0.5)
                self.som_tiro = s
                print(f"[Som] Tiro carregado: {arquivos[0]}")
        except Exception as e:
            print(f"[Som] Erro tiro: {e}")

        try:
            s = pygame.mixer.Sound(os.path.join(pasta_death, "1.mp3"))
            s.set_volume(0.8)
            self.som_morte = s
            print("[Som] Morte carregada.")
        except Exception as e:
            print(f"[Som] Erro morte: {e}")

    def tocar_tiro(self):
        if self.som_tiro:
            self.som_tiro.play()

    def tocar_morte(self):
        if self.som_morte:
            self.som_morte.play()

# ======================================================================
#  SISTEMA PRINCIPAL DO JOGO
# ======================================================================

class SistemaJogo:
    def __init__(self):
        self.vidas         = 1
        self.zumbis_mortos = 0
        self.itens_municao = pygame.sprite.Group()
        self.balas         = pygame.sprite.Group()
        self.grupo_zumbis  = pygame.sprite.Group()
        self._mapa_ref     = None
        self._sons         = SonsZumbi()  # ← sons inicializados aqui
        self._sons_jogo = SonsJogo()

    def iniciar(self, jogador, mapa):
        self._mapa_ref     = mapa
        self.vidas         = 1
        self.zumbis_mortos = 0
        jogador.rect.centerx = mapa.spawn_player_px[0]
        jogador.rect.centery = mapa.spawn_player_px[1]
        jogador.municao = 12
        self.balas.empty()
        self._gerar_itens_municao(mapa)
        self.grupo_zumbis = spawnar_zumbis(
            mapa.matriz,
            config.TAMANHO_TILE,
            pos_player=(jogador.rect.centerx, jogador.rect.centery),
        )

    def resetar(self, jogador, mapa):
        self.iniciar(jogador, mapa)

    def _gerar_itens_municao(self, mapa):
        self.itens_municao.empty()
        tiles = mapa.tiles_chao()
        if not tiles:
            return
        random.shuffle(tiles)
        qtd   = min(40, max(10, len(tiles) // 30))
        passo = max(1, len(tiles) // qtd)
        for i in range(0, len(tiles), passo):
            x, y = tiles[i]
            self.itens_municao.add(ItemMunicao(x - 8, y - 8))

    def atualizar(self, jogador, mapa, camera, dt: int) -> str:
        teclas = pygame.key.get_pressed()
        ctrl   = teclas[pygame.K_LCTRL] or teclas[pygame.K_RCTRL]

        # --- TIRO ---
        if ctrl and jogador.municao > 0:
            if jogador.atirar():
                self._sons_jogo.tocar_tiro()
                mx, my = pygame.mouse.get_pos()
                bala = Bala(
                    jogador.rect.centerx, jogador.rect.centery,
                    mx + camera.offset_x, my + camera.offset_y,
                )
                self.balas.add(bala)

        # --- BALAS ---
        self.balas.update(mapa.paredes_fisicas)
        for bala in list(self.balas):
            if math.hypot(bala.pos_x - jogador.rect.centerx,
                          bala.pos_y - jogador.rect.centery) > 1200:
                bala.kill()

        # --- ZUMBIS ---
        for zumbi in list(self.grupo_zumbis):
            zumbi.update(jogador.rect, mapa.paredes_fisicas, dt)

        # --- BALAS ACERTAM ZUMBIS ---
        acertos = pygame.sprite.groupcollide(
            self.grupo_zumbis, self.balas,
            dokilla=False, dokillb=True,
        )
        for zumbi in list(acertos.keys()):
            if zumbi.alive() and zumbi.vivo:  # ← dupla checagem
                zumbi.morrer()
                self.zumbis_mortos += 1
                self._sons.tocar_dor()

        # --- ZUMBIS CAUSAM DANO ---
        for zumbi in list(self.grupo_zumbis):
            if zumbi.tentar_causar_dano(jogador.rect):
                self.vidas -= 1
            if self.vidas <= 0:
                     self._sons_jogo.tocar_morte()
            if hasattr(jogador, "receber_dano"):
                      jogador.receber_dano()

        # --- MUNIÇÃO ---
        for item in pygame.sprite.spritecollide(jogador, self.itens_municao, True):
            jogador.adicionar_municao(item.quantidade)
            print(f"[+] Munição: {jogador.municao}")

        # --- SONS AMBIENTE ---
        self._sons.atualizar_ambiente(len(self.grupo_zumbis))

        # --- FIM DE JOGO ---
        if self.vidas <= 0:
            return "GAMEOVER"

        # Vitória: matar TODOS os zumbis
        if len(self.grupo_zumbis) == 0:
            return "VITORIA"

        return "JOGANDO"

    def desenhar_zumbis(self, tela, camera_offset_x, camera_offset_y, tiles_visiveis: set, tamanho_tile: int):
        for zumbi in self.grupo_zumbis:
          col = int(zumbi.pos_x) // tamanho_tile
          lin = int(zumbi.pos_y) // tamanho_tile
          if (col, lin) in tiles_visiveis:
            tela.blit(
                zumbi.image,
                (zumbi.rect.x - camera_offset_x,
                 zumbi.rect.y - camera_offset_y),
            )

    @property
    def zumbis_restantes(self) -> int:
        return len(self.grupo_zumbis)