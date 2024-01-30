import sys 
import random
import socket
import os
import signal
from multiprocessing.managers import BaseManager

class RemoteManager(BaseManager): pass

# Register methods that can be called on the server
RemoteManager.register('get_suites')
RemoteManager.register('get_players_cards')
RemoteManager.register('get_tokens')
RemoteManager.register('set_players_cards')
RemoteManager.register('set_tokens')
RemoteManager.register('set_suites')

# Create an instance of RemoteManager
m = RemoteManager(address=('localhost', 50000), authkey=b'abracadabra')
# Connect to the server
m.connect()


class HanabiGame:
    def __init__(self, num_players, players_info):
        """
        Initialize the HanabiGame class with the number of players and their information 
        such as the ID, the socket and pid. 

        Parameters:
        num_players (int): The number of players in the game.
        players_info (dict): A dictionary containing information about the players, including their socket connections and process IDs.
        """
        self.num_players = num_players
        self.colors = ['red', 'blue', 'green', 'yellow', 'purple'][:num_players]
        self.discard = []
        self.players_info = players_info
        self.send("start")                      
        self.init_deck(num_players)
        self.start_game()
    
    def send(self, mess, player="all"):
        """
        Sends a message to a specific player or all players.

        Parameters:
        mess (str): The message to be sent.
        player (str, optional): The ID of the player to send the message to. If "all", the message is sent to all players. Defaults to "all".

        Raises:
        Exception: If there's an error when sending the data.
        """
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
        """
        Receives a message from a specific player.

        Parameters:
        playerId (str): The ID of the player to receive the message from.
        buffer_size (int, optional): The maximum amount of data to be received at once. Defaults to 1024.

        Returns:
        str: The received message, or None if there was an error.

        Raises:
        Exception: If there's an error when receiving the data.
        """
        while True:
            conn = self.players_info[playerId]["socket"][0]
            try:
                data_received = conn.recv(buffer_size)        
                data_decoded = data_received.decode()        
                return data_decoded
            except Exception as e:
                print(f"Error when receiving data : {e}")
                return None                                    
        
    def init_deck(self, num_players):
        """
        Initializes the deck of cards and distributes them among the players.

        Parameters:
        num_players (int): The number of players in the game.

        The deck is a list of dictionaries, where each dictionary represents a card with a color, a number, and two hint flags.
        The deck is shuffled, and each player is dealt a hand of cards from the deck.
        The hands are stored in the shared data managed by the server manager.
        After all cards are dealt, a "initCards" message is sent to all players.
        The function then waits for a "cards initiated" message from each player before returning.

        Raises:
        Exception: If there's an error when receiving the data.
        """
        numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        num_cards_in_hand = 5
        
        self.deck = [{'color': color, 'number': number, 'hint_color': False, 'hint_number': False} for color in self.colors for number in numbers]
        random.shuffle(self.deck)

        for player in range(num_players):
            hand = []
            for _ in range(num_cards_in_hand):
                card = self.deck.pop()
                hand.append(card)
            m.set_players_cards(f"player{player+1}", hand)
        self.send("initCards")
        for i in range(num_players):
            mess = self.receive("player" + str(i+1))
            while mess != "cards initiated":
                mess = self.receive("player" + str(i+1))
                
    def start_game(self):
        """
        Starts the game and manages the turns of the players.

        The function first gets a list of all player IDs. Then, it enters a loop that continues until the game ends.
        In each iteration of the loop, it sends a message to the current player, calls the `player_turn` method for that player, and checks if the game has ended.
        If the game has not ended, it sends a "the game continue" message to all players and waits for an "ok" message from each player.
        Then, it updates the index of the current player, wrapping around to the start of the list if necessary.
        """
        players = list(self.players_info.keys())
        i_player = 0
        running = True
        while running:
            current_player = players[i_player]
            self.send(current_player)
            self.player_turn(current_player)
            self.check_end()
            self.send("the game continue")  
            for i in range(num_players):
                mess = self.receive("player" + str(i+1))
                while mess != "ok":
                    mess = self.receive("player" + str(i+1))          
            i_player = (i_player + 1) % len(players)    
    
    def player_turn(self, playerId):
        """
        Manages a single turn for a specific player.

        Parameters:
        playerId (str): The ID of the player whose turn it is.

        The function enters a loop that continues until the player's turn ends.
        In each iteration of the loop, it receives a message from the player.
        If the message contains "play card", it gets the index of the card from the end of the message and calls the `play_card` method with the player ID and card index.
        If the message does not contain "play card", it ends the player's turn.
        """
        end = False
        while not end:
            data = self.receive(playerId)
            if "play card" in data:
                i_card = int(data[-1])
                self.play_card(playerId, i_card)
            else:
                end = True                   
    
    def play_card(self, playerId, i_card):
        """
        Handles the action of a player playing a card.

        Parameters:
        playerId (str): The ID of the player who is playing the card.
        i_card (int): The index of the card in the player's hand.

        The function first gets a copy of the players' cards and removes the played card from the current player's hand.
        It then checks if the deck has any cards left. If it does, it draws a new card from the deck and adds it to the player's hand.
        Then, it checks if the number on the played card is one more than the highest number of the same color in the suites.
        If it is, the player played successfully and the function updates the suites and possibly the info tokens.
        If it is not, the player played unsuccessfully and the function decreases the number of fuse tokens.
        Finally, it sends a message to all players about the result of the play.
        """
        players_cards = dict(m.get_players_cards().copy())
        card = players_cards[playerId].pop(i_card)
        card_color = card['color']
        card_number = card['number']
        suites = m.get_suites().copy()
        if len(self.deck) > 0:
            new_card = self.deck.pop()
            players_cards[playerId].append(new_card)
            m.set_players_cards(playerId, players_cards[playerId])
        
        if card_number == suites[card_color] + 1:
            message = f"{playerId} played successfully a {card_color} {card_number}."
            m.set_suites(card_color, card_number) 
            if card_number == 5: 
                info_tk = m.get_tokens().copy()["info_tk"]
                m.set_tokens("info_tk", info_tk+1)   
                message += "\nYou have regained an Info Token.\n" 

        else:
            fuse_tk = m.get_tokens().copy()["fuse_tk"]
            m.set_tokens("fuse_tk", fuse_tk - 1)   
            message = f"Bad luck, you lost a Fuse Token.\n"
        self.send(message)

    def check_end(self):
        """
        Checks if the game has ended and handles the end of the game.

        The game ends if either the fuse tokens have run out or all cards in the suites have been played (i.e., the number on each card is 5).

        If the game has ended due to the fuse tokens running out, it sends a SIGUSR2 signal to all player processes and prints a message.
        If the game has ended because all cards have been played, it sends a SIGUSR1 signal to all player processes and prints a message.

        In both cases, it sends an "end of the game" message to all players and then exits the program.

        Raises:
        ProcessLookupError: If a player process with a given PID does not exist.
        PermissionError: If the program does not have permission to send a signal to a player process.
        """
        fuse_tk = m.get_tokens().copy()["fuse_tk"]
        suites = m.get_suites().copy()
        if fuse_tk == 0:
            for info in self.players_info.values():
                pid = info["pid"]
                try:
                    os.kill(pid, signal.SIGUSR2)
                    print(f"Signal {signal.SIGUSR2} sent to process with PID: {pid}")
                except ProcessLookupError:
                    print(f"Error: Process with PID: {pid} NOT FOUND")
                except PermissionError:
                    print(f"Error: No permission to send a signal to the process {pid}")
            self.send("end of the game")                  
            sys.exit(0)        

        elif all(card == 5 for card in suites.values()):
            for info in self.players_info.values():
                pid = info["pid"]
                try:
                    os.kill(pid, signal.SIGUSR1)
                    print(f"Signal {signal.SIGUSR1} sent to process with PID: {pid}")
                except ProcessLookupError:
                    print(f"Error: Process with PID: {pid} NOT FOUND")
                except PermissionError:
                    print(f"Error: No permission to send a signal to the process {pid}")
            
            self.send("end of the game")         
            sys.exit(0)          

 
if __name__ == "__main__":

    players_cards = m.get_players_cards()
    num_players = len(players_cards.keys())
    
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
 