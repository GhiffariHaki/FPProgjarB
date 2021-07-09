import socket
import pickle
import threading
import pygame
import sys

pygame.init()

HEIGHT = 500
WIDTH = 350
FONT = "CascadiaCode.ttf"
USERNAME = "POGO"

clock = pygame.time.Clock()

window = pygame.display.set_mode([WIDTH,HEIGHT])

title = pygame.display.set_caption("Chat")
base_font = pygame.font.SysFont(FONT, 22)
user_text = ""

input_rect = pygame.Rect(10,450,140,25)
color_passive = pygame.Color('gray')
color_active = pygame.Color('black')
color_warning = pygame.Color('red')
color = color_passive

rect_status = 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                rect_status = 2
            else:
                rect_status = 1

        if event.type == pygame.KEYDOWN:
            if rect_status != 1:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                    rect_status = 2
                elif len(user_text) == 36:
                    rect_status = 3
                elif event.key == pygame.K_RETURN:
                    user_text = ''
                else:
                    user_text += event.unicode

    window.fill((255,255,255))

    if rect_status == 1:
        color = color_passive
    elif rect_status == 2:
        color = color_active
    else:
        color = color_warning

    pygame.draw.rect(window,color,input_rect,2)

    text_surface = base_font.render(user_text,True,(0,0,0))
    window.blit(text_surface,(input_rect.x + 5, input_rect.y + 5))

    input_rect.w = max(329,text_surface.get_width() + 9)

    pygame.display.flip()
    clock.tick(30)