import sysv_ipc as ipc
import socket
import os 
import signal 
import sys
import multiprocessing as mp
from multiprocessing.managers import BaseManager
from affichage import *
from print_color import print as printc

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
        data = receive(socket_client)  
    print(data)    
    players_cards = m.get_players_cards().copy()
    num_players = len(players_cards.keys())
    print(players_cards)
    suites = m.get_suites().copy()
    w = Window(playerId, players_cards, suites)   
    print("hola1")
    running = True
    while running:
        print_board(playerId)
        current_player = receive(socket_client)
        while "player" not in current_player:
            current_player= receive(socket_client)
        print(f"\nIt's the turn of {current_player}\n")    
        if current_player == playerId:
            action, mess = turn(playerId, socket_client)
            for _ in range(num_players - 1):  # Send message to all players but current_player
                mq.send(action.encode(), type=1)
                if 'play card' in action:
                    message = receive(socket_client)
                    print("\n"+message)
                elif 'give hint' in action :
                    mq.send(mess.encode(), type=2)    
                mq.send(b"end of the turn", type=3)
            send(socket_client, "end of the turn")
            print("End of your turn.")
                                    
        else:
            action, t = mq.receive(type=1)
            print(f"{current_player} choose to {action.decode()}")
            if 'play card' in action.decode():
                message = receive(socket_client)
                print("\n"+message)
            elif 'give hint' in action.decode():
                hint, t = mq.receive(type=2)
                print("\n"+hint.decode())
            mess, t = mq.receive(type=3) 
            print(f"End of the turn of {current_player}.")
                 
    
        
def turn(playerId, socket):
        print("Which action do you want to do?\n")
        tokens = m.get_tokens().copy()
        info_tk = tokens["info_tk"]
        while True:
            if info_tk > 0 :
                action = input("1. Give a hint\n2. Play a card\n")
            else :
                action = input("You don't have any info tokens left, you can only play a card. Type 2 to continue\n")
            if action.isdigit() and (info_tk > 0 and action in ['1', '2'] or action == '2'):
                action = int(action)
                break
            else:
                print("Invalid action. Please try again.")

        if action == 1:
            message = give_hint(playerId)
            return("give hint", message)

        elif action == 2:
            while True:
                i_card = input("Type the index of the card you want to play (from 1 to 5) ")
                if i_card.isdigit() and 1 <= int(i_card) <= 5:
                    i_card = int(i_card)
                    break
                else:
                    print("Invalid card index. Please try again.")
            send(socket, f"play card {str(i_card -1)}")
            done = receive(socket)
            return("play card", None)
          

def give_hint(player):
    info_tk = m.get_tokens()._getvalue()["info_tk"]
    print(f"{info_tk-1} info tokens left")
    m.set_tokens("info_tk", info_tk-1)

    # Ask the player who they want to give a hint to
    players = list(m.get_players_cards().copy().keys())
    players.remove(playerId)
    while True:
        print("Which player do you want to give a hint to ? ")
        for i, player in enumerate(players): 
            print(f"{i+1}. {player}")
        i_teammate = int(input())
        if 1 <= i_teammate <= len(players):
            break
        else:
            print("Invalid option. Please enter a number between 1 and ",len(players))
    teammate = players[i_teammate-1]
    # Get the teammate's cards
    players_cards = m.get_players_cards().copy()

    # Show the teammate's cards
    print("Your teammate's cards are : ")
    cards = players_cards[teammate]
    for card in cards :
        printc(card["number"], color=card["color"], end=" ")    

    # Ask the player if they want to give a number or color hint
    while True:
        hint_type = input("\nDo you want to give a number or color hint? ")
        if hint_type in ["number", "color"]:
            break
        else:
            print("Invalid option. Please enter 'number' or 'color'.")

    # Ask the player the index of the card they want to give a hint about
    while True:
        card_index = int(input("Enter the index of the card you want to give a hint about (from 1 to 5) "))
        if 1 <= card_index <= 5:
            break
        else:
            print("Invalid option. Please enter a number between 1 and 5. ")
    card = cards[card_index - 1]

    if hint_type == "color":
        color = card['color']
        cards_of_color = [card for card in cards if card['color'] == color]
        for card in cards:
            if card in cards_of_color:
                card["hint_color"] = True
                m.set_players_cards(teammate, cards)

    if hint_type == "number":
        num = card['number'] 
        cards_of_number = [card for card in cards if card['number'] == num]
        for card in cards:
            if card in cards_of_number:
                card["hint_number"] = True
                m.set_players_cards(teammate, cards)
    message = f"{playerId} gave a {hint_type} hint to {teammate} about {card[hint_type]}"
    return message
    
  
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
    printc("\n\n\nBoard :\n", format='bold')
    print(f"\nFuse Tokens : {tokens['fuse_tk']}")
    print(f"Info Tokens : {tokens['info_tk']}")
    print("\n\nSuites :", end="  ")
    for color, num in suites.items():
        printc(num, color=color, end="  ")
    print("\n\n\nHands :")        
    for player, cards in players_cards.items():
        if player == playerId :
            
            print(f"\nMe ({playerId}) :", end="  ")
            for card in cards :
                num = card["number"]
                color = card["color"]
                if card["hint_color"] and card["hint_number"]:
                    printc(num, color=color, end="  ")
                elif card["hint_color"]:
                    printc("-", color=color, end="  ")
                elif card["hint_number"] :
                    print(num, end="  ")
                else :
                    print("-", end="  ") 
            
        else :
            
            print(f"\n{player} :", end="  ")
            for card in cards :
                num = card["number"]
                color = card["color"]
                printc(num, color=color, end="")
                if card["hint_color"] :
                    print("c", end="")
                if card["hint_number"] :
                    print("n", end="")
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
    #mq.close()
    #socket_client.close()
    #normalement sys.exit(0) s'occupe de vider toutes les ressources 
    sys.exit(0)
        

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
        print(data)
        while data != "start":
            data = receive(socket_client)
            
        print("Starting game")
        
        player_process(playerId, socket_client, mq)                          