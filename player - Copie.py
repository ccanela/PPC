import sysv_ipc as ipc
import socket
import os 
import signal 
import sys



def player_process(self, player_num):
    signal.signal(signal.SIGUSR1, end_game)  #signal pour victoire
    signal.signal(signal.SIGUSR2, end_game)  #signal pour game over
    player_name = f"player{player_num}"
    player_hand = self.players_cards[player_name]
    HOST_int = "localhost"
    PORT_int = 6666 + player_num

    server_socket_int = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_int.bind((HOST_int, PORT_int))
    server_socket_int.listen(1)
    client_socket_int, address = server_socket_int.accept()

    running = True
    while running:
        
        pass
        # Lógica del jugador aquí
        # Manejar la comunicación con el juego a través del pipe y el socket
        
def turn(self, player):
        print(f"It's {player}'s turn.")
        
        if self.info_tk < 0 :
            #Arreter d'afficher l'option give a hint
            pass
        else :
            #Afficher l'option give a hint    
            pass
        
        action = input("Choose an action (give hint or play card): ")
        # il manque: check if info_tk > 0 
        if action == "give hint":
            # Ensure it's not another player's turn
            # Implement the logic for giving a hint here
            self.give_hint(player)

        elif action == "play card":
            # Implement the logic for playing a card here
            self.play_card(player)
        
        elif action == "discard":
            self.discard(player)    
        else:
            print("Invalid action. Please try again.")

def give_hint(self, player):
    #avant d'appeler la fonction il faut voir s'il y a de info_tk disponibles c-a-d info_tk >  
    
    self.tokens_sem.acquire()
    self.info_tk -= 1 
    self.tokens_sem.release()
    
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
      
        
   
def end_game(signum, frame):
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
    user()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_client :
        host = 'localhost'
        numplayer = 0
        port = 12345
        socket_client.connect((host, port))
        print("Connected")
    
        data = receive(socket_client)
        while data != "1":
            print("c")
            data = receive(socket_client)
        print("Starting game")             