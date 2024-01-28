import sys 
#import paramiko
#import errno
import random
import socket
import os 
import signal
#import sysv_ipc as ipc
import threading as th
from multiprocessing.managers import BaseManager
from queue import Queue
import multiprocessing as mp 
from test_button2 import *

class RemoteManager(BaseManager): pass

RemoteManager.register('get_suites')
RemoteManager.register('get_players_cards')
RemoteManager.register('get_tokens')
RemoteManager.register('set_players_cards')
RemoteManager.register('set_tokens')
RemoteManager.register('set_suites')

m = RemoteManager(address=('localhost', 50000), authkey=b'abracadabra')
m.connect()


class HanabiGame:
    def __init__(self, num_players, players_info):
        print("init HanabiGame")
        self.num_players = num_players
        self.colors = ['red', 'blue', 'green', 'yellow', 'purple'][:num_players]
        #self.suites = m.get_suites() je crois que ça n'a pas de sens parce que c'est dans la memoire partagé pas dans la classe 
        self.discard = []
        #self.players_cards = m.get_players_cards()
        #self.tokens = m.get_tokens()
        self.deck_mutex = th.Lock() 
        self.suites_mutex = th.Lock()
        self.playersCards_mutex = th.Lock()
        self.tokens_mutex = th.Lock()
        self.players_info = players_info
        self.send("start")                      
        self.init_deck(num_players)
        print("appel fonction start_game")
        self.start_game()
                       
        
    def init_deck(self, num_players):
        numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        num_cards_in_hand = 5
        
        self.deck_mutex.acquire()
        self.deck = [{'color': color, 'number': number, 'hint_color': False, 'hint_number': False} for color in self.colors for number in numbers]
        random.shuffle(self.deck)
        self.deck_mutex.release()

        self.playersCards_mutex.acquire()
        
        for player in range(num_players):
            hand = []
            for _ in range(num_cards_in_hand):
                self.deck_mutex.acquire()
                card = self.deck.pop()
                self.deck_mutex.release()
                hand.append(card)
            m.set_players_cards(f"player{player+1}", hand)
            print(m.get_players_cards().copy())
        self.playersCards_mutex.release()
        print("fin init_deck")
        self.send("initCards")

    def send(self, mess, player="all"):
        if player == "all":
            for player in self.players_info.values():
                conn = player["socket"][0]
                try:
                    data_encoded = mess.encode()   
                    print(mess, data_encoded)   
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
    
    def play_card(self, playerId):
        #code pour choisir une carte et l'enlever (pop) de players_cards[f"player{player}"](avec interface graphique)

        
        # card_color = card['color']
        # card_number = card['number']
        self.suites_mutex.acquire()
        suites = m.get_suites().copy()
        if card_number == suites[card_color] + 1:
            m.set_suites(card_color,card_number) #card_number doit être int
            self.suites_mutex.release()
            if card_number == 5: 
                self.tokens_sem.acquire()
                info_tk = m.get_tokens()._getvalue()["info_tk"]
                m.set_tokens("info_tk", info_tk+1) 
                self.tokens_sem.release()

        else:
            self.tokens_sem.acquire()
            fuse_tk = m.get_tokens()._getvalue()["fuse_tk"]
            self.set_tokens("fuse_tk", fuse_tk - 1)
            self.tokens_sem.release()

        if len(self.deck) > 0:
            self.deck_sem.acquire()
            self.playersCards_sem.acquire()
            new_card = self.deck.pop()
            hand_player = m.get_players_cards()._getvalue()[f"player{playerId}"]
            hand_player.append(new_card)
            m.set_players_cards(f"player{playerId}", hand_player)
            self.deck_sem.release()
            self.playersCards_sem.release()


    def check_end(self):
        # Check if the third Storm token is turned lightning-side-up
        if self.storm_tk == 0:
            for info in self.players_info.values():
                pid = info["pid"]
                try:
                    os.kill(pid, signal.SIGUSR2)
                    print(f"Signal {signal.SIGUSR2} sent to process with PID: {pid}")
                except ProcessLookupError:
                    print(f"Error: Process with PID: {pid} NOT FOUND")
                except PermissionError:
                    print(f"Error: No permission to send a signal to the process {pid}")

        elif all(card == 0 for card in self.suites.values()):
            print("2")
            pid_players = self.get_pids("player.py")
            for pid in pid_players:
                try:
                    os.kill(pid, signal.SIGUSR1)
                    print(f"Signal {signal.SIGUSR1} sent to process with PID: {pid}")
                except ProcessLookupError:
                    print(f"Error: Process with PID: {pid} NOT FOUND")
                except PermissionError:
                    print(f"Error: No permission to send a signal to the process {pid}")
        
        os._exit(0)          

       
    def player_turn(self, playerId):
        print("hola player_turn")
        end = False
        while not end:
            data = self.receive(playerId)
            print("playerID sent")
            while (data != "end of the turn") or (data != "play card"):
                data = self.receive(playerId)
            if data == "play card":
                self.play_card(playerId)
            else:
                end = True

    def start_game(self):
        print("hola start_game")
        players = list(self.players_info.keys())
        print(players)
        i_player = 0
        running = True
        while running:
            current_player = players[i_player]
            print(current_player)
            self.send(current_player)
            print("appel fonction player_turn")
            self.player_turn(current_player)
            self.check_end()            
            i_player = (i_player + 1) % len(players)
            print(i_player)

 
if __name__ == "__main__":

    players_cards = m.get_players_cards()
    num_players = len(players_cards.keys())
    
    # if len(sys.argv) < 2:
    #     print("required index argument missing, terminating.", file=sys.stderr)
    #     sys.exit(1)
        
    # try:
    #     num_players = int(sys.argv[1])
    # except ValueError:
    #     print("bad index argument: {}, terminating.".format(sys.argv[1]), file=sys.stderr)
    #     sys.exit(2)
        
    # if num_players < 0:
    #     print("negative index argument: {}, terminating.".format(num_players), file=sys.stderr)
    #     sys.exit(3)
    
    # elif num_players > 5:
    #     print("bad index argument (too many players): {}, terminating.".format(num_players), file=sys.stderr)
    #     sys.exit(4)    
    
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
            print(players_info)
            
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