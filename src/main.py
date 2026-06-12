import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import pygame 
from player import Player
from configs import config
from configs import screens
from configs import controllers_screen
from configs.audio import GerenciadorAudio
from configs.camera import Camera
from configs import config, screens, controllers_screen
from maps.mapa import Mapa
from logics.game_logic import SistemaJogo

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()

# --- MIRA ---
pygame.mouse.set_visible(False)
pasta_ui = os.path.join("..", "assets", "sprite", "Life Asset Pack", "Character", "UI")
if not os.path.exists(pasta_ui):
    pasta_ui = os.path.join("assets", "sprite", "Life Asset Pack", "Character", "UI")
caminho_mira = os.path.join(pasta_ui, "LaserDot.png")
try:
    mira_img = pygame.image.load(caminho_mira).convert_alpha()
    mira_img = pygame.transform.scale(mira_img, (24, 24))
except Exception:
    mira_img = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(mira_img, (255, 0, 0), (8, 8), 6)

pygame.mixer.init()

# --- MÚSICA ---
pasta_musica = os.path.join("..", "assets", "music")
if not os.path.exists(pasta_musica):
    pasta_musica = os.path.join("assets", "music")
caminho_musica = os.path.join(pasta_musica, "ente_evil.mp3")
if os.path.exists(caminho_musica):
    try:
        som_ambiente = pygame.mixer.Sound(caminho_musica)
        print("-> SUCESSO: Música carregada!")
    except Exception as e:
        print(f"-> AVISO: {e}")

tela         = screens.inicializar_janela()
relogio      = pygame.time.Clock()
fonte        = pygame.font.SysFont("Arial", 22, bold=True)
fonte_grande = pygame.font.SysFont("Arial", 50, bold=True)

audio   = GerenciadorAudio()
audio.tocar_menu()
mapa    = Mapa()
sistema = SistemaJogo()
jogador = Player()
camera  = Camera()

camera.configurar_grid(mapa.matriz, config.TAMANHO_TILE)

estado_jogo             = "MENU"
indice_selecionado      = 0
opcao_audio_selecionada = 0
tiles_visiveis          = set()
indice_pausa            = 0
OPCOES_PAUSA            = ["Continuar", "Menu Principal", "Sair"]

# --- MINI MAPA ---
def desenhar_minimapa(tela, mapa, jogador, grupo_zumbis, camera):
    from maps.mapa import TILES_LARGURA, TILES_ALTURA

    # Configurações do minimapa
    MM_W, MM_H   = 160, 120
    MM_X, MM_Y   = config.LARGURA - MM_W - 10, 10
    ESCALA_X     = MM_W / TILES_LARGURA
    ESCALA_Y     = MM_H / TILES_ALTURA
    T            = config.TAMANHO_TILE

    # Fundo
    surf = pygame.Surface((MM_W, MM_H), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 160))

    # Tiles de parede
    for lin, linha in enumerate(mapa.matriz):
        for col, bloco in enumerate(linha):
            if bloco == 1:  # parede
                px = int(col * ESCALA_X)
                py = int(lin * ESCALA_Y)
                pygame.draw.rect(surf, (80, 80, 90), (px, py, max(1, int(ESCALA_X)), max(1, int(ESCALA_Y))))

    # Zumbis — bolinhas vermelhas
    for zumbi in grupo_zumbis:
        zx = int((zumbi.pos_x / T) * ESCALA_X)
        zy = int((zumbi.pos_y / T) * ESCALA_Y)
        pygame.draw.circle(surf, (220, 30, 30), (zx, zy), 2)

    # Jogador — bolinha branca
    jx = int((jogador.rect.centerx / T) * ESCALA_X)
    jy = int((jogador.rect.centery / T) * ESCALA_Y)
    pygame.draw.circle(surf, (255, 255, 255), (jx, jy), 3)

    # Borda
    pygame.draw.rect(surf, (180, 180, 180), (0, 0, MM_W, MM_H), 1)

    tela.blit(surf, (MM_X, MM_Y))

rodando = True
while rodando:
    dt = relogio.tick(60)

    for evento in pygame.event.get():                        # ← for começa aqui
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:                    # ← dentro do for
            if estado_jogo == "JOGANDO" and evento.key == pygame.K_ESCAPE:
                estado_jogo = "PAUSADO"
                indice_pausa = 0

            elif estado_jogo == "PAUSADO":
                if evento.key == pygame.K_ESCAPE:
                    estado_jogo = "JOGANDO"
                elif evento.key == pygame.K_UP:
                    indice_pausa = (indice_pausa - 1) % len(OPCOES_PAUSA)
                elif evento.key == pygame.K_DOWN:
                    indice_pausa = (indice_pausa + 1) % len(OPCOES_PAUSA)
                elif evento.key == pygame.K_RETURN:
                    if indice_pausa == 0:
                        estado_jogo = "JOGANDO"
                    elif indice_pausa == 1:
                        audio.parar()
                        audio.tocar_menu()
                        estado_jogo = "MENU"
                    elif indice_pausa == 2:
                        rodando = False

            elif estado_jogo == "MENU":
                indice_selecionado = config.gerenciar_eventos_menu(
                    evento, indice_selecionado, config.OPCOES_MENU
                )
                if evento.key == pygame.K_RETURN:
                    if indice_selecionado == 0:
                        mapa = Mapa()
                        sistema.iniciar(jogador, mapa)
                        camera.configurar_grid(mapa.matriz, config.TAMANHO_TILE)
                        audio.parar()
                        audio.tocar_gameplay()
                        estado_jogo = "JOGANDO"
                    elif indice_selecionado == 1:
                        estado_jogo = "OPCOES"
                    elif indice_selecionado == 2:
                        estado_jogo = "CONTROLES"
                    elif indice_selecionado == 3:
                        rodando = False

            elif estado_jogo == "OPCOES":
                if evento.key == pygame.K_ESCAPE:
                    estado_jogo = "MENU"
                elif evento.key in [pygame.K_UP, pygame.K_DOWN]:
                    opcao_audio_selecionada = 1 - opcao_audio_selecionada
                elif evento.key == pygame.K_LEFT:
                    audio.atualizar_volumes(opcao_audio_selecionada, -0.1)
                elif evento.key == pygame.K_RIGHT:
                    audio.atualizar_volumes(opcao_audio_selecionada, 0.1)

            elif estado_jogo == "CONTROLES" and evento.key == pygame.K_ESCAPE:
                estado_jogo = "MENU"

            elif estado_jogo in ["GAMEOVER", "VITORIA"] and evento.key == pygame.K_r:
                audio.parar()
                estado_jogo = "MENU"
    # ← for termina aqui

    if estado_jogo == "JOGANDO":
        jogador.update(mapa.paredes_fisicas)
        estado_jogo = sistema.atualizar(jogador, mapa, camera, dt)
        camera.focar(jogador.rect)
        audio.atualizar()

    tela.fill((15, 15, 15))

    if estado_jogo == "MENU":
        screens.desenhar_menu(tela, fonte, fonte_grande, indice_selecionado)
    elif estado_jogo == "OPCOES":
        screens.desenhar_opcoes(tela, fonte, fonte_grande, opcao_audio_selecionada)
    elif estado_jogo == "CONTROLES":
        controllers_screen.desenhar_controles(tela, fonte, fonte_grande)
    elif estado_jogo == "VITORIA":
        screens.desenhar_vitoria(tela, fonte, fonte_grande)
    elif estado_jogo == "GAMEOVER":
        screens.desenhar_gameover(tela, fonte, fonte_grande)
    elif estado_jogo == "JOGANDO":
        mapa.desenhar(tela, camera.offset_x, camera.offset_y)
        

        for item in sistema.itens_municao:
            col = item.rect.centerx // config.TAMANHO_TILE
            lin = item.rect.centery // config.TAMANHO_TILE
            if (col, lin) in tiles_visiveis:
                tela.blit(item.image, camera.aplicar(item.rect))

        tiles_visiveis = camera.desenhar_campo_visao(tela, jogador.rect)

        rect_jogador_camera = camera.aplicar(jogador.rect)
        jogador.mirar(rect_jogador_camera)
        rect_atualizado = jogador.image.get_rect(center=rect_jogador_camera.center)
        tela.blit(jogador.image, rect_atualizado)

        for bala in sistema.balas:
            tela.blit(bala.image, camera.aplicar(bala.rect))

        sistema.desenhar_zumbis(tela, camera.offset_x, camera.offset_y,
                                tiles_visiveis, config.TAMANHO_TILE)

        screens.desenhar_hud(
            tela, fonte,
            sistema.zumbis_restantes,
            sistema.vidas,
            jogador.municao,
            jogador.municao_maxima,
        )
        desenhar_minimapa(tela, mapa, jogador, sistema.grupo_zumbis, camera)
        mx, my = pygame.mouse.get_pos()
        tela.blit(mira_img, (mx - mira_img.get_width() // 2, my - mira_img.get_height() // 2))

    elif estado_jogo == "PAUSADO":
        # Fundo congelado
        mapa.desenhar(tela, camera.offset_x, camera.offset_y)
        sistema.desenhar_zumbis(tela, camera.offset_x, camera.offset_y,
                                tiles_visiveis, config.TAMANHO_TILE)
        camera.desenhar_campo_visao(tela, jogador.rect)

        # Overlay escuro semitransparente
        overlay = pygame.Surface((config.LARGURA, config.ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        tela.blit(overlay, (0, 0))

        # Título
        txt_pausa = fonte_grande.render("PAUSADO", True, (255, 255, 255))
        tela.blit(txt_pausa, (config.LARGURA // 2 - txt_pausa.get_width() // 2, 180))

        # Opções
        for i, opcao in enumerate(OPCOES_PAUSA):
            cor = (255, 220, 50) if i == indice_pausa else (180, 180, 180)
            txt_opcao = fonte.render(opcao, True, cor)
            tela.blit(txt_opcao, (config.LARGURA // 2 - txt_opcao.get_width() // 2, 300 + i * 50))

        mx, my = pygame.mouse.get_pos()
        tela.blit(mira_img, (mx - mira_img.get_width() // 2, my - mira_img.get_height() // 2))

    pygame.display.flip()

pygame.quit()