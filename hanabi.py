import pygame 
import sys 
import paramiko
import random
import socket
import threading as th
import multiprocessing as mp 
from test_button2 import Button

class State:
    WAITING = 1
    PLAYING = 2
    
class HanabiGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.colors = ['red', 'blue', 'green', 'yellow', 'white'][:num_players]
        self.suites = mp.Manager().dict({color: 0 for color in self.colors}) 
        self.discard = []
        self.players_cards = {f"player{i+1}": [] for i in range(num_players)}
        self.discarded_cards = []
        self.info_tk = mp.Value('i', num_players + 3)  
        self.playerStates = [State.WAITING for _ in range(num_players)]
        self.storm_tk = mp.Value('i', 3)  
        self.init_deck(num_players)
        self.players_pipes = [mp.Pipe() for _ in range(num_players)]
        self.message_queue = mp.Queue() 
        self.deck_sem = th.Semaphore(0) 
        self.suites_sem = th.Semaphore(0)
        self.playersCards_sem = th.Semaphore(0)
        self.tokens_sem = th.Semaphore(0)
        self.playerStates_sem = [th.Semaphore(0) for _ in range(num_players)]
        print(self.players_cards)

    def init_deck(self, num_players):
        numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        num_cards_in_hand = 5
        
        self.deck_sem.acquire()
        self.deck = [{'color': color, 'number': number, 'hint_color': False, 'hint_number': False} for color in self.colors for number in numbers]
        random.shuffle(self.deck)
        self.deck_sem.release()

        for player in range(num_players):
            for _ in range(num_cards_in_hand):
                self.deck_sem.acquire()
                card = self.deck.pop()
                self.deck_sem.release()
                self.playersCards_sem.acquire()
                self.players_cards[f"player{player+1}"].append(card)
                self.playersCards_sem.release()

            
    
    def play_card(self, player):
        #code pour choisir une carte et l'enlever (pop) de players_cards[f"player{player}"](avec interface graphique)

        card_color = card['color']
        card_number = card['number']

        if card_number == self.play_pile[card_color] + 1:
            self.suites_sem.acquire()
            self.suites[card_color] = card_number
            self.suites_sem.release()
        else:
            self.tokens_sem.acquire()
            self.storm_tk -= 1
            self.tokens_sem.release()

        if len(self.deck) > 0:
            self.deck_sem.acquire()
            self.playersCards_sem.acquire()
            new_card = self.deck.pop()
            self.players_cards[f"player{player}"].append(new_card)
            self.deck_sem.release()
            self.playersCards_sem.release()


    def check_end(self):
        # Check if the third Storm token is turned lightning-side-up
        if self.storm_tk == 0:
            return "storm"

        if all(card['number'] == 5 for card in self.play_pile.values()):
            return "victory"

        # Check if the last card from the draw deck has been drawn
        if len(self.deck) == 0:
            return "last turn"

        return "continue"
    
    def player_turn(self, player_num):
        # Lógica específica del turno del jugador
        # Aquí debes usar self.pipe para enviar y recibir información del proceso del juego
        pass

    def start_game(self):
        player_processes = []
        for i in range(self.num_players):
            player_process = mp.Process(target=self.player_process, args=(i + 1, self.players_pipes[i][1]))
            player_process.start()
            player_processes.append(player_process)

        # Configurar y gestionar la comunicación a través de sockets
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server :
            host, port = 'localhost', 12345
            socket_server.bind((host, port))
            socket_server.listen(self.num_players)

            player_sockets = []
            for i in range(self.num_players):
                conn, addr = socket_server.accept()
                player_sockets.append(conn, addr)

        # Iniciar el bucle principal del juego
        running = True
        while running:
            pass
            # Lógica del juego aquí
            # Manejar la comunicación con los jugadores a través de los sockets y las colas

        # Cierre adecuado de procesos y recursos...
        for player_process in player_processes:
            player_process.join()

 
if __name__ == "__main__":
    num_players = int(input("Enter the number of players (from 2 to 5): "))
    while num_players < 2 or num_players > 5:
        print("Invalid number of players. Please try again.")
        num_players = int(input("Enter the number of players (from 2 to 5): "))

    game_pipe, _ = mp.Pipe()
    game_process = mp.Process(target=HanabiGame, args=(num_players,))
    game_process.start()

""" 
game = HanabiGame(5)

pygame.init()
screen = pygame.display.set_mode((800, 600))
buttons = []
for i, card in enumerate(game.players_cards["player1"]): 
    button = Button(f'{card["number"]}_{card["color"]}.png', (100 + i*60, 100), scale=0.1) 
    buttons.append(button)
    

running = True
while running:
    screen.fill((200, 255, 255))
    for button in buttons:
        button.draw(screen)
        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for button in buttons:
            button.handle_event(event)
    

pygame.quit()
#game_process.join()

 """
 
 
 
""" 
def discard_card(self, player):
    # Avant de faire l'appel on doit regarder que note_tk_used > 0 sinon on peut pas "discard_card"
    self.note_tk_used -= 1
    self.note_tk += 1

    #card_to_discard = le jouer choisira a travers l'interface graphique 

    # Remove the chosen card from the player's hand
    self.players_cards[player].remove(card_to_discard)

    # Add the discarded card to the discard pile
    self.discarded_cards.append(card_to_discard)

    # Draw another card into the player's hand
    if len(self.deck) > 0:
        new_card = self.deck.pop()
        self.players_cards[player].append(new_card)

"""