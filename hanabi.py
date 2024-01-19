import pygame 
import sys 
import paramiko

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Hanabi Game')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update the screen
    pygame.display.flip()

    
play_pile = []
discarded_cards = []
players_cards: {
    "player1": [], 
    "player2": []
    }                   #on pourra rajouter les autres joueurs