import os
import sys
import pygame
from configs import config

def inicializar_janela():
    pygame.init()
    tela = pygame.display.set_mode((config.LARGURA, config.ALTURA))
    pygame.display.set_caption("Undead Survival - Apocalypse")
    return tela


def desenhar_mapa(tela, mapa_grade, sprites_dict, camera):
    """Renderiza os blocos do mapa gigante de forma otimizada usando a Câmera."""
    import config
    import pygame

    tamanho_tile = config.TAMANHO_TILE
    for linha_idx, linha in enumerate(mapa_grade):
        for coluna_idx, bloco in enumerate(linha):
            # Calcula a posição real do bloco no mundo
            rect_bloco = pygame.Rect(
                coluna_idx * tamanho_tile,
                linha_idx * tamanho_tile,
                tamanho_tile,
                tamanho_tile,
            )

            # Descobre onde ele deve aparecer na janela com base na posição do Player
            rect_ajustado = camera.aplicar(rect_bloco)

            # SISTEMA DE PERFORMANCE (CULLING): Só renderiza se o bloco estiver de fato aparecendo na janela
            if (
                -tamanho_tile < rect_ajustado.x < config.LARGURA
                and -tamanho_tile < rect_ajustado.y < config.ALTURA
            ):

                # Desenha o chão de concreto base primeiro (para blocos que não são paredes)
                if bloco != 1:
                    if 0 in sprites_dict:
                        tela.blit(sprites_dict[0], rect_ajustado)

                # Desenha o objeto ou parede por cima
                if bloco in sprites_dict:
                    tela.blit(sprites_dict[bloco], rect_ajustado)


def desenhar_menu(tela, fonte, fonte_grande, indice_selecionado):
    titulo = fonte_grande.render("UNDEAD SURVIVAL", True, (220, 30, 30))
    tela.blit(titulo, (config.LARGURA // 2 - titulo.get_width() // 2, 80))

    y_inicial = 240
    espacamento = 50
    for i, opcao in enumerate(config.OPCOES_MENU):
        if i == indice_selecionado:
            texto_opcao = fonte.render(f">  {opcao}  <", True, (255, 50, 50))
        else:
            texto_opcao = fonte.render(opcao, True, (180, 20, 20))
        tela.blit(
            texto_opcao,
            (
                config.LARGURA // 2 - texto_opcao.get_width() // 2,
                y_inicial + (i * espacamento),
            ),
        )

    instrucao_menu = fonte.render(
        "Use as Setas (Cima/Baixo) e ENTER para navegar", True, (70, 70, 70)
    )
    tela.blit(
        instrucao_menu,
        (config.LARGURA // 2 - instrucao_menu.get_width() // 2, config.ALTURA - 40),
    )


def desenhar_opcoes(tela, fonte, fonte_grande, item_selecionado):
    titulo = fonte_grande.render("OPÇÕES DE ÁUDIO", True, (220, 30, 30))
    tela.blit(titulo, (config.LARGURA // 2 - titulo.get_width() // 2, 80))

    cor_m = (255, 50, 50) if item_selecionado == 0 else (180, 20, 20)
    txt_musica = fonte.render(
        f"Música: {int(config.volume_musica * 100)}%", True, cor_m
    )
    tela.blit(txt_musica, (config.LARGURA // 2 - txt_musica.get_width() // 2, 260))

    cor_s = (255, 50, 50) if item_selecionado == 1 else (180, 20, 20)
    txt_sons = fonte.render(
        f"Efeitos de Som: {int(config.volume_sons * 100)}%", True, cor_s
    )
    tela.blit(txt_sons, (config.LARGURA // 2 - txt_sons.get_width() // 2, 320))

    txt_ajuste = fonte.render("Use ← / → para ajustar o volume", True, (120, 120, 120))
    txt_voltar = fonte.render("Pressione ESC para voltar", True, (255, 255, 255))
    tela.blit(txt_ajuste, (config.LARGURA // 2 - txt_ajuste.get_width() // 2, 420))
    tela.blit(
        txt_voltar,
        (config.LARGURA // 2 - txt_voltar.get_width() // 2, config.ALTURA - 80),
    )


def desenhar_hud(tela, fonte, zumbis_restantes, vidas, municao=0, municao_max=30):
    pygame.draw.rect(tela, (30, 30, 30), pygame.Rect(0, 0, config.LARGURA, 50))
    pygame.draw.line(tela, (240, 240, 240), (0, 50), (config.LARGURA, 50), 2)

    txt_missao = fonte.render(f"Zumbis: {zumbis_restantes}", True, (255, 255, 0))
    txt_vidas = fonte.render(f"HP: {vidas}", True, (255, 80, 80))
    
    # Munição fica vermelha quando está baixa
    cor_mun = (255, 60, 60) if municao <= 3 else (255, 255, 255)
    txt_municao = fonte.render(f"Balas: {municao}/{municao_max}", True, cor_mun)

    tela.blit(txt_missao, (20, 13))
    tela.blit(txt_municao, (config.LARGURA // 2 - txt_municao.get_width() // 2, 13))
    tela.blit(txt_vidas, (config.LARGURA - 150, 13))

def desenhar_vitoria(tela, fonte, fonte_grande):
    txt = fonte_grande.render("VOCÊ ESCAPOU!", True, (0, 255, 0))
    txt_sub = fonte.render("Pressione 'R' para voltar ao Menu", True, (255, 255, 255))
    tela.blit(txt, (config.LARGURA // 2 - txt.get_width() // 2, 250))
    tela.blit(txt_sub, (config.LARGURA // 2 - txt_sub.get_width() // 2, 330))


def desenhar_gameover(tela, fonte, fonte_grande):
    txt = fonte_grande.render("VOCÊ FOI PEGO!", True, (255, 0, 0))
    txt_sub = fonte.render("Pressione 'R' para tentar novamente", True, (255, 255, 255))
    tela.blit(txt, (config.LARGURA // 2 - txt.get_width() // 2, 250))
    tela.blit(txt_sub, (config.LARGURA // 2 - txt_sub.get_width() // 2, 330))
