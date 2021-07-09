from contextlib import nullcontext
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

msg_history = []

clock = pygame.time.Clock()

window = pygame.display.set_mode([WIDTH,HEIGHT])
title = pygame.display.set_caption("Chat")

base_font = pygame.font.SysFont(FONT, 22)

user_msg = ""

history_rect = pygame.Rect(10,25,140,420)
input_rect = pygame.Rect(10,450,140,25)
color_passive = pygame.Color('gray')
color_active = pygame.Color('black')
color_warning = pygame.Color('red')
color = color_passive

rect_status = 1

while True:
    window.fill((255,255,255))

    msg_count = len(msg_history)

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
                    user_msg = user_msg[:-1]
                    rect_status = 2
                elif len(user_msg) == 36:
                    rect_status = 3
                elif event.key == pygame.K_RETURN:
                    if msg_count == 14:
                        msg_history = msg_history[1:]
                        msg_history.append(user_msg)
                    else:
                        msg_history.append(user_msg)

                    user_msg = ''

                else:
                    user_msg += event.unicode

    pygame.draw.rect(window,color_passive,history_rect,2)
    history_rect.w = max(100,329)

    y = 0
    for msg in msg_history:
        history_surface = base_font.render(msg,True,(0,0,0))
        window.blit(history_surface,(15, 30 + y * 30))
        y += 1

    if rect_status == 1:
        color = color_passive
    elif rect_status == 2:
        color = color_active
    else:
        color = color_warning

    pygame.draw.rect(window,color,input_rect,2)

    text_surface = base_font.render(user_msg,True,(0,0,0))
    window.blit(text_surface,(input_rect.x + 5, input_rect.y + 5))

    input_rect.w = max(329,text_surface.get_width() + 9)

    pygame.display.flip()
    clock.tick(30)