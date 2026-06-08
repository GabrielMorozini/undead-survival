import pygame
from player.default import Player

# Inicialização
pygame.init()
tela = pygame.display.set_mode((800, 600))
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 24)

# Instanciando o jogador
jogador = Player()
rodando = True

while rodando:
    # 1. Checar eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # 2. Atualizar lógica
    jogador.update()

    # 3. Desenhar na tela
    tela.fill((0, 0, 0))  # Limpa a tela com preto

    # Desenha o jogador
    tela.blit(jogador.image, jogador.rect)

    # Exibe informações de Debug (Posição + Letras Coletadas)
    texto_pos = fonte.render(
        f"Posição: {jogador.rect.x}, {jogador.rect.y}", True, (255, 255, 255)
    )
    texto_letras = fonte.render(
        f"Letras: {''.join(jogador.letras_coletadas)}", True, (255, 255, 0)
    )

    tela.blit(texto_pos, (10, 10))
    tela.blit(texto_letras, (10, 40))

    pygame.display.flip()
    relogio.tick(60)

    # No seu loop principal:
print(
    f"DEBUG: Jogador em ({jogador.rect.x}, {jogador.rect.y}) | Letras: {jogador.letras_coletadas}"
)

pygame.quit()
