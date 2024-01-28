import sysv_ipc as ipc
import socket
import os 
import signal 
import sys
import multiprocessing as mp
from multiprocessing.managers import BaseManager
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

def player_process(playerId, socket_client, mq):
        
    signal.signal(signal.SIGUSR1, end_game)  #signal pour victoire
    signal.signal(signal.SIGUSR2, end_game)  #signal pour game over
    
    data = receive(socket_client)
    while data != "initCards":
        data = receive(socket_client) #je ne sais pas pourquoi il y a ça mais on envoie jamais "initCards" et c'était une boucle infinie
    print_board(playerId)
    players_cards = m.get_players_cards().copy()
    suites = m.get_suites().copy()
    #Window(playerId, players_cards, suites)   
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
            mq.send(action.encode(), type=1)
            mq.send(b"end of the turn", type=3)
            send(socket_client, "end of the turn")
                                    
        else:
            action, t = mq.receive(type=1)
            print(f"{current_player} choose to {action}")
            mess, t = mq.receive(type=3)      
    
        
def turn(playerId):
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
            give_hint(playerId)
        
        elif action == 2:
            i_card = int(input("Type de index of the card you want to play (from 1 to 5)"))
            send("play card")

            #faut chercher une façon de dire au jeu qu'on veut jouer cette carte (on a besoin de l'indice et current_player)

            pass 
        else:
            print("Invalid action. Please try again.")
            turn(playerId)
    
          

def give_hint(player):
    info_tk = m.get_tokens()._getvalue()["info_tk"]
    print(f"{info_tk-1} info tokens left")
    m.set_tokens("info_tk", info_tk-1)

    # Ask the player who they want to give a hint to
    players = list(m.get_players_cards().copy().keys())
    players.remove(playerId)
    print("Which player do you want to give a hint to?")
    i_teammate = int(input("".join(f"{i+1}. {player}\n" for i, player in enumerate(players))))
    teammate = players[i_teammate-1]
    # Get the teammate's cards
    players_cards = m.get_players_cards().copy()

    # Show the teammate's cards
    print("Your teammate's cards are: ")
    print(players_cards[teammate])

    # Ask the player if they want to give a number or color hint
    hint_type = input("Do you want to give a number or color hint?")

    # Ask the player the index of the card they want to give a hint about
    card_index = int(input("Enter the index of the card you want to give a hint about (from 1 to 5)"))
    card = players_cards[teammate][card_index - 1]

    if hint_type == "color":
        color = card['color']
        cards_of_color = [card for card in players_cards[teammate] if card['color'] == color]
        for card in players_cards[teammate]:
            if card in cards_of_color:
                card["hint_color"] = True

    if hint_type == "number":
        num = card['number'] 
        cards_of_number = [card for card in players_cards[teammate] if card['number'] == num]
        for card in players_cards[teammate]:
            if card in cards_of_number:
                card["hint_number"] = True
    message = f"{playerId} gave a {hint_type} hint to {teammate} about {card[hint_type]}"
    for player in players:
        mq.send(message.encode(), type=2)  
    
  
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