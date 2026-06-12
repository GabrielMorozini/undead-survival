import sys
import pygame
import os
import random
from configs import config


class GerenciadorAudio:
    def __init__(self):
        pygame.mixer.init()

        pasta = os.path.join("..", "assets", "music")
        if not os.path.exists(pasta):
            pasta = os.path.join("assets", "music")

        self.musica_menu = os.path.join(pasta, "ente_evil.mp3")

        # Lista de músicas de gameplay — toca em ordem aleatória
        nomes_gameplay = [
            "zander_noriega_-_dragged_through_hellfire_abomination.wav",
            "3HR.MT_.3.mp3",
            "good_as_nu_heavy_loop.mp3",
            "good_as_nu_intro_loop.mp3",
            "Tri-Tachyon - 4HR.DM8_.mp3",
        ]
        self.musicas_gameplay = [
            os.path.join(pasta, n) for n in nomes_gameplay
            if os.path.exists(os.path.join(pasta, n))
        ]
        self._fila_gameplay = []
        self.tem_musica = False

    def tocar_menu(self):
        self._tocar(self.musica_menu, loop=True)

    def tocar_gameplay(self):
        # Monta fila aleatória e toca a primeira
        self._fila_gameplay = random.sample(
            self.musicas_gameplay, len(self.musicas_gameplay)
        )
        self._proxima_faixa()

    def _proxima_faixa(self):
        if not self._fila_gameplay:
            # Fila acabou — embaralha de novo
            self._fila_gameplay = random.sample(
                self.musicas_gameplay, len(self.musicas_gameplay)
            )
        caminho = self._fila_gameplay.pop(0)
        self._tocar(caminho, loop=False)

    def atualizar(self):
        """Chame no loop principal para detectar fim de faixa e passar para a próxima."""
        if self.tem_musica and not pygame.mixer.music.get_busy():
            self._proxima_faixa()

    def _tocar(self, caminho, loop=False):
        if os.path.exists(caminho):
            try:
                pygame.mixer.music.load(caminho)
                pygame.mixer.music.set_volume(config.volume_musica)
                pygame.mixer.music.play(-1 if loop else 0)
                self.tem_musica = True
                print(f"-> Tocando: {os.path.basename(caminho)}")
            except Exception as e:
                print(f"Erro ao tocar música: {e}")
        else:
            print(f"-> Arquivo não encontrado: {caminho}")

    def parar(self):
        pygame.mixer.music.stop()
        self.tem_musica = False

    def atualizar_volumes(self, opcao_audio, direcao):
        if opcao_audio == 0:
            config.volume_musica = max(0.0, min(1.0, config.volume_musica + direcao))
            pygame.mixer.music.set_volume(config.volume_musica)
        else:
            config.volume_sons = max(0.0, min(1.0, config.volume_sons + direcao))