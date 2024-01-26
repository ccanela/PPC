import pygame 
import sys 
import paramiko
import errno
import random
import socket
import os 
import signal
import sysv_ipc as ipc
import threading as th
import psutil
import multiprocessing as mp 
#from test_button2 import Button

class State:
    WAITING = 1
    PLAYING = 2
    
class HanabiGame:
    def __init__(self, num_players, players_info):
        self.num_players = num_players
        self.colors = ['red', 'blue', 'green', 'yellow', 'white'][:num_players]
        self.suites = mp.Manager().dict({color: 0 for color in self.colors}) 
        self.discard = []
        self.players_cards = {f"player{i+1}": [] for i in range(num_players)}
        self.discarded_cards = []
        self.info_tk = mp.Value('i', num_players + 3)  
        self.playerStates = [State.WAITING for _ in range(num_players)]
        self.storm_tk = mp.Value('i', 3)  
        self.deck_sem = th.Semaphore(1) 
        self.suites_sem = th.Semaphore(1)
        self.playersCards_sem = th.Semaphore(1)
        self.tokens_sem = th.Semaphore(1)
        self.playerStates_sem = [th.Semaphore(1) for _ in range(num_players)]
        self.players_info = players_info
        
        self.send("start")
                        
        self.init_deck(num_players)       
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

    def send(self, mess, player="all"):
        if player == "all":
            for player in self.players_info.values():
                conn = player["socket"][0]
                try:
                    data_encoded = mess.encode()      
                    conn.sendall(data_encoded)    
                except Exception as e:
                    print(f"Error when sending data : {e}")
        else :
            conn = self.players_info[player]["socket"][0] 
            try:
                data_encoded = mess.encode()      
                conn.sendall(data_encoded)    
            except Exception as e:
                print(f"Error when sending data : {e}")              
                    
    def receive(self, playerId, buffer_size=1024):
        while True:
            conn = self.players_info[playerId]["socket"][0]
            try:
                data_received = conn.recv(buffer_size)        
                data_decoded = data_received.decode()        
                return data_decoded
            except Exception as e:
                print(f"Error when receiving data : {e}")
                return None                 
    
    def play_card(self, player):
        #code pour choisir une carte et l'enlever (pop) de players_cards[f"player{player}"](avec interface graphique)

        card_color = card['color']
        card_number = card['number']

        if card_number == self.suites[card_color] + 1:
            self.suites_sem.acquire()
            self.suites[card_color] = card_number
            self.suites_sem.release()
            if card_number == 5: 
                self.tokens_sem.acquire()
                info_tk += 1 
                self.tokens_sem.release()

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
            for info in players_info.values():
                pid = info["pid"]
                try:
                    os.kill(pid, signal.SIGUSR2)
                    print(f"Signal {signal.SIGUSR2} sent to process with PID: {pid}")
                except ProcessLookupError:
                    print(f"Error: No se puede encontrar el proceso con PID {pid}")
                except PermissionError:
                    print(f"Error: No se tiene permiso para enviar la señal al proceso con PID {pid}")

        elif all(card == 0 for card in self.suites.values()):
            print("2")
            pid_players = self.get_pids("player.py")
            for pid in pid_players:
                try:
                    os.kill(pid, signal.SIGUSR1)
                    print(f"Signal {signal.SIGUSR1} sent to process with PID: {pid}")
                except ProcessLookupError:
                    print(f"Error: No se puede encontrar el proceso con PID {pid}")
                except PermissionError:
                    print(f"Error: No se tiene permiso para enviar la señal al proceso con PID {pid}")
        
        os._exit(0)          

       
    def player_turn(self, player_num):
        # Lógica específica del turno del jugador
        # Aquí debes usar self.pipe para enviar y recibir información del proceso del juego
        pass

    def start_game(self):
       
        running = True
        while running:
            pass
            # Lógica del juego aquí
            # Manejar la comunicación con los jugadores a través de los sockets y las colas

 
if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("required index argument missing, terminating.", file=sys.stderr)
        sys.exit(1)
        
    try:
        num_players = int(sys.argv[1])
    except ValueError:
        print("bad index argument: {}, terminating.".format(sys.argv[1]), file=sys.stderr)
        sys.exit(2)
        
    if num_players < 0:
        print("negative index argument: {}, terminating.".format(num_players), file=sys.stderr)
        sys.exit(3)
    
    elif num_players > 5:
        print("bad index argument (too many players): {}, terminating.".format(num_players), file=sys.stderr)
        sys.exit(4)    
    
    players_connected = 0 
    players_info = {}
    host = 'localhost'
    port = 12345
    print("Open to connections")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server :
        socket_server.bind((host, port))
        socket_server.listen(num_players)
        while players_connected < num_players :
            conn, addr = socket_server.accept()
            players_connected += 1
            pid = conn.recv(1024)
            pid = pid.decode()           
            playerId = f"player{players_connected}" 
            conn.sendall(playerId.encode())      
            players_info[playerId] = {"socket": (conn, addr), "pid": int(pid)}
            
        print("Starting game")       
        
        
        HanabiGame(num_players, players_info) 
 
 
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