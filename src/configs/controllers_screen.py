import os
import sys
import pygame
from configs import config
import sys, os

def desenhar_controles(tela, fonte, fonte_grande=None):
    tela.fill((10, 10, 15))

    VERMELHO  = (220, 40,  40)
    BRANCO    = (220, 220, 220)
    CINZA     = (140, 140, 140)
    CINZA_ESC = (60,  60,  70)
    AMARELO   = (255, 200, 50)

    def tecla(texto, x, y):
        surf = fonte.render(f"[ {texto} ]", True, AMARELO)
        tela.blit(surf, (x, y))
        return surf.get_width()

    def linha(chave, descricao, y):
        w = tecla(chave, 160, y)
        txt = fonte.render(descricao, True, CINZA)
        tela.blit(txt, (160 + w + 16, y))

    # Título
    titulo = fonte_grande.render("CONTROLES", True, VERMELHO) if fonte_grande else fonte.render("CONTROLES", True, VERMELHO)
    tela.blit(titulo, (config.LARGURA // 2 - titulo.get_width() // 2, 60))

    # Subtítulo
    sub = fonte.render("GUIA DO JOGADOR", True, CINZA_ESC)
    tela.blit(sub, (config.LARGURA // 2 - sub.get_width() // 2, 60 + titulo.get_height() + 6))

    y = 160

    # Seção Movimento
    sec = fonte.render("— MOVIMENTO —", True, VERMELHO)
    tela.blit(sec, (config.LARGURA // 2 - sec.get_width() // 2, y)); y += 40
    linha("W A S D",    "Mover o personagem",          y); y += 36
    linha("↑ ← ↓ →",   "Alternativa de movimento",    y); y += 50

    # Seção Combate
    sec = fonte.render("— COMBATE —", True, VERMELHO)
    tela.blit(sec, (config.LARGURA // 2 - sec.get_width() // 2, y)); y += 40
    linha("CTRL",       "Atirar (gasta munição)",       y); y += 36
    linha("Mouse",      "Mirar na direção do cursor",   y); y += 50

    # Seção Sistema
    sec = fonte.render("— SISTEMA —", True, VERMELHO)
    tela.blit(sec, (config.LARGURA // 2 - sec.get_width() // 2, y)); y += 40
    linha("ESC",        "Voltar ao menu",               y); y += 36
    linha("R",          "Reiniciar após game over",     y); y += 50

    # Dica inferior
    dica = fonte.render("Pressione ESC para voltar", True, CINZA_ESC)
    tela.blit(dica, (config.LARGURA // 2 - dica.get_width() // 2, config.ALTURA - 60))