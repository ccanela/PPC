import sysv_ipc as ipc
import socket
import os 
import signal 
import sys
import multiprocessing as mp
from multiprocessing.managers import BaseManager
from hanabi1 import HanabiGame as hg
from test_button2 import *
from print_color import print

class RemoteManager(BaseManager): pass
RemoteManager.register('get_suites')
RemoteManager.register('get_players_cards')
RemoteManager.register('get_tokens')
RemoteManager.register('set_players_cards')
RemoteManager.register('set_tokens')
RemoteManager.register('set_suites')

m = RemoteManager(address=('localhost', 50000), authkey=b'abracadabra')
m.connect()

def player_process(playerId, socket_client, mq):
        
    signal.signal(signal.SIGUSR1, end_game)  #signal pour victoire
    signal.signal(signal.SIGUSR2, end_game)  #signal pour game over
    
    data = receive(socket_client)
    while data != "initCards":
        data = receive(socket_client) #je ne sais pas pourquoi il y a ça mais on envoie jamais "initCards" et c'était une boucle infinie
    print_board(playerId)
    players_cards = m.get_players_cards().copy()
    suites = m.get_suites().copy()
    Window(playerId, players_cards, suites)   
    #Nina si tu enleves le commentaire ça marche? Moi ça n'affiche que pour un joueur, l'autre a la fenêtre vide
    print("hola1")
    running = True
    while running:
        current_player = receive(socket_client)
        print("hola2")
        while "player" not in current_player:
            current_player= receive(socket_client)
            print("playerID received")
        print(f"It's the turn of {current_player}")    
        if current_player == playerId:
            action = turn(playerId)
            #Afficher des options de jeu
            mq.send(action, type=1)
            mq.send("end of the turn", type=3)
            send(socket_client, "end of the turn")
            #Afficher fin du tour
                                    
        else:
            action, t = mq.receive(type=1)
            print(f"{current_player} choose to {action}")
            #Afficher "{current_player} choose to {action}"
            mess, t = mq.receive(type=3)      
        # Lógica del jugador aquí
        # Manejar la comunicación con el juego a través del pipe y el socket
        
def turn(player):
        print("Which action do you want to do?\n")
        #mutex
        tokens = m.get_tokens().copy()
        info_tk = tokens["info_tk"]
        if info_tk > 0 :
            action = int(input("1. Give a hint\n2. Play a card\n"))
        else :
            action = int(input("You don't have any info tokens left, you can only play a card. Type 2 to continue\n"))   
            #test qu'il met pas de 1? 

        if action == 1:
            give_hint(player)
        
        elif action == 2:
            i_card = int(input("Type de index of the card you want to play (from 1 to 5)"))
            send("play card")
            #faut chercher une façon de dire au jeu qu'on veut jouer cette carte (on a besoin de l'indice et current_player)
            #hg.play_card(player)  #on ne peut pas lancer la fonction comme ça 
            pass 
        else:
            print("Invalid action. Please try again.")
            turn(player)
          

def give_hint(player):
    
    #hg.tokens_sem.acquire() 
    info_tk = m.get_tokens()._getvalue()["info_tk"]
    print(f"{info_tk-1} info tokens left")
    #Nina j'ai un segmentation fault juste après ça 
    m.set_tokens("info_tk", info_tk -1)      
    #hg.tokens_sem.release()
    
    #Arreter d'afficher les boutons d'option
    #Afficher indication pour choisir carte puis piece number or color
    """ 
    if hint_type == "color":
        color = card['color']
        cards_of_color = [card for card in self.players_cards[teammate] if card['color'] == color]
        self.playersCards_sem.acquire()
        for card in self.players_cards[teammate]:
            if card in cards_of_color:
                card["hint_color"] = True
        self.playersCards_sem.release()        
                    
            
    if hint_type == "number":
        num = card['number']
        cards_of_number = [card for card in self.players_card[teammate] if card['number'] == number]
        self.playersCards_sem.acquire()
        for card in self.players_cards[teammate]:
            if card in cards_of_number:
                card["hint_number"] = True
        self.playersCards_sem.release()  
    """           
def user():
    answer = 3
    while answer != 1:
        print("1. to join the game")
        answer = int(input())
    return    
   
def send(socket_connexion, data):
    try:
        data_encoded = data.encode()      
        socket_connexion.sendall(data_encoded)   
    except Exception as e:
        print(f"Error when sending data : {e}")    
   
        
def receive(socket_connexion, buffer_size=1024):
    try:
        data_received = socket_connexion.recv(buffer_size)        
        data_decoded = data_received.decode()        
        return data_decoded
    except Exception as e:
        print(f"Error when receiving data : {e}")
        return None     

def print_board(playerId):
    suites = m.get_suites().copy()
    players_cards = m.get_players_cards().copy()
    tokens = m.get_tokens().copy()
    print("\nBoard :\n\n")
    print(f"\nFuse Tokens : {tokens['fuse_tk']}")
    print(f"\nInfo Tokens : {tokens['info_tk']}")
    print("\nSuites :", end="  ")
    for color, num in suites:
        print(num, color=color, end="  ")
    print("\n\n\nHands :\n")        
    for player, cards in players_cards :
        if player == playerId :
            
            print(f"Me :", end="  ")
            for card in cards :
                num = card["number"]
                color = card["color"]
                if card["hint_color"] and card["hint_number"]:
                    print(num, color=color, end="  ")
                elif card["hint_color"]:
                    print("-", color=color, end="  ")
                elif card["hint_number"] :
                    print(num, end="  ")
                else :
                    print("-", end="  ") 
            
        else :
            
            print(f"{player} :", end="  ")
            for card in cards :
                num = card["number"]
                color = card["color"]
                if card["hint_color"] :
                    print(num, color=color, end="")
                else:
                    print(num, end="")
                if card["hint_number"] :
                    print("*", end="  ")
                else :
                    print(end="  ")    
                             
   
def end_game(signum, frame):
    print("2")
    if signum == signal.SIGUSR1:
        print(f"Signal received: {signum}. Game status: Victory!!!")
        #timer ou affichage
    if signum == signal.SIGUSR2:
        print(f"Signal received: {signum}. Game status:  Loss")
        #affichage ou timer 
    #vider toutes les ressources avant de faire "exit"
    os._exit(0)
        

if __name__ == "__main__" :
    key = 100
    mq = ipc.MessageQueue(key, ipc.IPC_CREAT)
    pid = os.getpid()
    user()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_client :
        host = 'localhost'
        port = 12345
        socket_client.connect((host, port))
        print("Connected")
        send(socket_client, str(pid))
        playerId = receive(socket_client)
        print(f"You are the {playerId}")
    
        data = receive(socket_client)
        while data != "start":
            data = receive(socket_client)
            
        print("Starting game")
        
        player_process(playerId, socket_client, mq)                          