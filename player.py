import sysv_ipc as ipc
import socket
import os 
import signal 
import sys
import multiprocessing as mp
from multiprocessing.managers import BaseManager
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
    """
    This function handles the process for a single player in hanabi game.

    It sets up signal handlers for game end conditions, receives initial data from the server, 
    and enters a main game loop where it handles turns for the player. 

    During a player's turn, it sends actions and messages to other players via a message queue, 
    and receives and processes actions from other players when it's not the player's turn.

    Parameters:
    playerId (str): The ID of the player.
    socket_client (socket): The socket object for communication with the server.
    mq (SysVMessageQueue): The message queue for communication with other players.

    Returns:
    None
    """   
    signal.signal(signal.SIGUSR1, end_game)  #signal for vicotry
    signal.signal(signal.SIGUSR2, end_game)  #signal for loss
   
    data = receive(socket_client)      
    while data != "initCards":
        data = receive(socket_client)  
    send(socket_client, "cards initiated")       
    players_cards = m.get_players_cards().copy()
    num_players = len(players_cards.keys()) 
    running = True
    while running:
        print_board(playerId)
        current_player = receive(socket_client)
        while "player" not in current_player:
            current_player= receive(socket_client)
        print(f"\n\nIt's the turn of {current_player}\n")  
          
        if current_player == playerId:
            action, mess = turn(playerId, socket_client)
            for _ in range(num_players - 1):  # Send message to all players but current_player
                mq.send(action.encode(), type=1)               
                if 'give hint' in action :
                    mq.send(mess.encode(), type=2)    
                mq.send(b"end of the turn", type=3)
            if 'play card' in action:
                print("\n"+mess)      
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
            
        gameContinue = receive(socket_client)
        while 'game' not in gameContinue:            
            gameContinue = receive(socket_client) 
        send(socket_client, "ok")    
    
        
def turn(playerId, socket):
        """
        This function handles a single turn for a player in the game of Hanabi.

        It first prompts the player to choose an action. If there are info tokens left, he can choose to either give a hint or play a card.
        If there aren't any info tokens left, he can only play a card.

        If the player chooses to give a hint, the function calls the give_hint function and returns a tuple with the string "give hint" and the message from give_hint.

        If the player chooses to play a card, he is prompted to enter the index of the card he wants to play. The function then sends a message to the server to play the card and receives a response. 
        It prints the response and returns a tuple with the string "play card" and the response message.

        Parameters:
        playerId (str): The ID of the player.
        socket (socket): The socket object for communication with the server.

        Returns:
        tuple: A tuple containing a string that represents the action taken ("give hint" or "play card") and the message received from the server or from the give_hint function.
        """
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
            message = receive(socket_client)
            print(message)
            return("play card", message)

def give_hint(player):
    """
    This function handles the process of giving a hint in the game of Hanabi.

    It first checks the number of info tokens available and updates it. 
    Then it prompts the player to choose a teammate to give a hint to.

    The player is then shown the teammate's cards and asked to choose a hint type (number or color)
    and the index of the card they want to give a hint about.

    Depending on the hint type chosen, the function updates the hint_color or hint_number 
    attribute of the cards in the teammate's hand that match the chosen card's color or number.

    Finally, it constructs a message about the hint given and returns it.

    Parameters:
    playerId (str): The ID of the player giving the hint.

    Returns:
    str: A message about the hint given.
    """
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
        i_teammate = input()
        if i_teammate in [str(i) for i in range(1, len(players)+1)]:
            break
        else:
            print("Invalid option. Please enter a number between 1 and ",len(players))
   
    teammate = players[int(i_teammate)-1]
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
        card_index = input("Enter the index of the card you want to give a hint about (from 1 to 5) ")
        if card_index in [str(i) for i in range(1, 6)]:
            break
        else:
            print("Invalid option. Please enter a number between 1 and 5. ")
    card_chosen = cards[int(card_index) - 1]

    if hint_type == "color":
        color = card_chosen['color']
        cards_of_color = [card for card in cards if card['color'] == color]
        for card in cards:
            if card in cards_of_color:
                card["hint_color"] = True
                m.set_players_cards(teammate, cards)

    if hint_type == "number":
        num = card_chosen['number'] 
        cards_of_number = [card for card in cards if card['number'] == num]
        for card in cards:
            if card in cards_of_number:
                card["hint_number"] = True
                m.set_players_cards(teammate, cards)
    message = f"{playerId} gave a {hint_type} hint to {teammate} about {card_chosen[hint_type]}"
    return message
   
def end_game(signum, frame):
    """
    This function handles the end of the game.

    It is designed to be used as a signal handler for SIGUSR1 and SIGUSR2 signals. 
    SIGUSR1 indicates a victory, while SIGUSR2 indicates a loss. 

    When a signal is received, the function prints a message indicating the signal number and the game status, 
    and then it terminates the process.

    Parameters:
    signum (int): The signal number. Expected to be either signal.SIGUSR1 or signal.SIGUSR2.
    frame (frame or None): The current stack frame. Not used in this function.

    Returns:
    None
    """
    if signum == signal.SIGUSR1:
        print(f"Signal received: {signum}. Game status: Victory!!!")
    if signum == signal.SIGUSR2:
        print(f"Signal received: {signum}. Game status:  Loss")
    sys.exit(0)
    
def gameRules():
    """
    This function prints the rules of the game Hanabi.

    The rules are printed in a formatted and colored way for better readability. 
    The rules cover the game's objective, the gameplay mechanics, the conditions for winning and losing, 
    and the actions that players can take during their turn.

    Parameters:
    None

    Returns:
    None
    """
    printc('\n\nHanabi Game', format='bold', color='cyan')
    printc("\n\nRules : \n", format='bold')  
    print("This is a cooperative game where you can only see the cards of other players.\n"+
          "The board is composed by as many suites as number of players. The suites are in ascending order.\n"
          "When your turn comes, you can either play one of your cards or give a hint to an other player\n"+
          "To play a card, the suit of the same color on the board must contain the previous number of the card you want to play.\n"+
          "If the card you want to play is not valid, you lose one Fuse Token.\nIf you achieve one complete suite (from 1 to 5), you regain one Info Token."+
          "To give a hint to an other player, you need to have at least\none Info Token (you lose it while you are giving the hint).\n"+
          "When a color hint is given about a card, the player is advertised for all the cards of this color. Same for the number hint.\n"+
          "All the players can see when a hint is given. The card is followed by 'n'\nif this is a number hint or/and by 'c' if this is a color hint."+
          "When you lose all your Fuse Tokens, you lose the Hanabi Game.\nBut if you manage to complete all the suites before that happens, you win !!\n\n"          
          )  

def print_board(playerId):
    """
    This function prints the current state of the game board in the game of Hanabi.

    It retrieves the current state of the suites, players cards, and tokens from the game model. 
    It then prints the number of fuse and info tokens, the current state of the suites, and the cards in each player's hand.

    For the playerId's (the one using that terminal) cards, it prints the number and color of the card if both color and number hints have been given, 
    a dash and the color if only a color hint has been given, the number if only a number hint has been given, 
    and a dash if no hints have been given.

    For other players' cards, it prints the number and color of the card, followed by a 'c' if a color hint has been given 
    and a 'n' if a number hint has been given.

    Parameters:
    playerId (str): The ID of the player whose perspective the board should be printed from.

    Returns:
    None
    """
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
    
def send(socket_connexion, data):
    """
    This function sends data over a socket connection.

    It first encodes the data into bytes, then sends it over the socket connection using the sendall method, 
    which ensures that all the data is sent. If an error occurs during this process, it catches the exception and prints an error message.

    Parameters:
    socket_connexion (socket): The socket object for the connection.
    data (str): The data to be sent.

    Returns:
    None
    """
    try:
        data_encoded = data.encode()      
        socket_connexion.sendall(data_encoded)   
    except Exception as e:
        print(f"Error when sending data : {e}")    
   
        
def receive(socket_connexion, buffer_size=1024):
    """
    This function receives data over a socket connection.

    It tries to receive data from the socket connection using the recv method, which blocks until data is available. 
    The amount of data to be received at a time is specified by the buffer_size parameter. 
    The received data is then decoded from bytes to a string.

    If an error occurs during this process, it catches the exception, prints an error message, and returns None.

    Parameters:
    socket_connexion (socket): The socket object for the connection.
    buffer_size (int, optional): The maximum amount of data to be received at once. Defaults to 1024.

    Returns:
    str: The received data as a string, or None if an error occurred.
    """
    try:
        data_received = socket_connexion.recv(buffer_size)        
        data_decoded = data_received.decode() 
        return data_decoded
    except Exception as e:
        print(f"Error when receiving data : {e}")
        return None       
    
def user():
    """
    This function handles the user's decision to join the game.

    It prompts the user with an option to join the game. The user is repeatedly asked until they choose the option to join the game by entering '1'.

    Parameters:
    None

    Returns:
    None
    """
    answer = 3
    while answer != 1:
        print("1. to join the game")
        answer = int(input())
    return  


"""
This script is the main entry point for a player in the game of Hanabi.

When run, it does the following:

1. Creates a unique key for a message queue and creates the queue.
2. Gets the process ID of the current process.
3. Displays the game rules.
4. Handles the user's decision to join the game.
5. Creates a new socket object and establishes a connection to the server.
6. Sends the process ID to the server and receives the player ID from the server.
7. Waits for the server to send the "start" message.
8. Starts the player process, which handles the game logic for the player.

The player process is run in a separate function, player_process, which takes the player ID, the socket object, and the message queue as parameters.
"""
if __name__ == "__main__" :
    key = 100
    mq = ipc.MessageQueue(key, ipc.IPC_CREAT)
    pid = os.getpid()
    gameRules()
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
        # print(data)
        while data != "start":
            data = receive(socket_client)
            
        print("Starting game")
        
        player_process(playerId, socket_client, mq)                          