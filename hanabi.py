import pygame 
import sys 
import paramiko
import random

class HanabiGame:
    def __init__(self, num_players):
        self.play_pile = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0, 'white': 0}
        self.discarded_cards = []
        self.players_cards = {f"player{i+1}": [] for i in range(num_players)}
        self.note_tk = 8
        self.note_tk_used = 0
        self.storm_tk = 3
        self.init_deck(num_players)

    def init_deck(self, num_players):
        colors = ['red', 'blue', 'green', 'yellow', 'white']
        numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]

        num_cards_in_hand = 5 if num_players in [2, 3] else 4

        self.deck = [{'color': color, 'number': number} for color in colors for number in numbers]
        random.shuffle(self.deck)

        for player in range(num_players):
            for _ in range(num_cards_in_hand):
                card = self.deck.pop()
                self.players_cards[f"player{player+1}"].append(card)

    def turn(self, player):
        print(f"It's {player}'s turn.")
        action = input("Choose an action (give hint, discard card, play card): ")
        # il manque: check if note_tk > 0 
        if action == "give hint":
            # Ensure it's not another player's turn
            if player != self.current_player:
                print("You can't give hints on another player's turn.")
                return
            # Implement the logic for giving a hint here
            self.give_hint(player)
        elif action == "discard card":
            # Implement the logic for discarding a card here
            self.discard_card(player)
        elif action == "play card":
            # Implement the logic for playing a card here
            self.play_card(player)
        else:
            print("Invalid action. Please try again.")

    def give_hint(self, player):
        # avant d'appeler la fonction il faut voir s'il y a de note_tk disponibles c-a-d note_tk > 0 
        self.note_tk -= 1 
        self.note_tk_used += 1 

        """ A travers l'interface graphique le jouer doit choisir: 
        -Color or Number hint? 
        - To which player? 
        - Which color/number?  """
        
        #teammate = le joueur choisit à qui il veut donner une info. 

        #card = choisit une carte sur laquelle il veut donner une info  

        #hint_type = (logique interface graphique pour choisir quel type de hint on veut donner)

        if hint_type == "color":
        # Let the player choose a color
        # This will also need to be done through the Pygame interface
            color = card['color']

            # Find all cards of that color in the teammate's hand
            cards_of_color = [card for card in self.players_cards[teammate] if card['color'] == color]
            #Code pour montrer au teammate quelles cartes ont le couleur choisit 
        
        if hint_type == "number":
            num = card['number']
            cards_of_number = [card for card in self.players_card[teammate] if card['number']== number]



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


    def play_card(self, player):
        #code pour choisir une carte et l'enlever (pop) de players_cards[f"player{player}"](avec interface graphique)

        card_color = card['color']
        card_number = card['number']

        if card_number == self.play_pile[card_color] + 1:
            self.play_pile[card_color] = card_number
        else:
            self.storm_tk -= 1

        if len(self.deck) > 0:
            new_card = self.deck.pop()
            self.players_cards[f"player{player}"].append(new_card)


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

def init_player_window(player_num):
    pygame.init()
    screen_width, screen_height = 400, 300
    screen = pygame.Surface((screen_width, screen_height))
    pygame.display.set_caption(f'Player {player_num} - Hanabi Game')
    return screen

def run_remote_game(player_num, ip, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=username, password=password)

    # Aquí debes especificar la ruta y el nombre del script del juego que deseas ejecutar
    game_script_path = "/path/to/your/game/script.py"
    command = f"python {game_script_path} {player_num}"

    stdin, stdout, stderr = client.exec_command(command)
    print(stdout.read())
    print(stderr.read())

    client.close()

            
# Example usage
num_players = int(input("Enter the number of players (from 2 to 5): "))
while num_players < 2 or num_players > 5:
    print("Invalid number of players. Please try again.")
    num_players = int(input("Enter the number of players (from 2 to 5): "))

hanabi_game = HanabiGame(num_players)

player_screens = [init_player_window(i+1) for i in range(num_players)]
window_sizes = [(400, 300), (400, 300), (400, 300), (400, 300), (400, 300)]

pygame.display.set_caption('Hanabi Game')

player_ips = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]
player_usernames = ["user1", "user2", "user3"]
player_passwords = ["pass1", "pass2", "pass3"]

for i in range(num_players):
    run_remote_game(i+1, player_ips[i], player_usernames[i], player_passwords[i])

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for i, screen in enumerate(player_screens):
        # Draw the player-specific elements on each screen
        # You can add code here to display the cards for each player
        pygame.display.set_caption(f'Player {i+1} - Hanabi Game')
        pygame.display.set_mode(window_sizes[i]).blit(screen, (0, 0))
        pygame.display.flip()

pygame.quit()
sys.exit()