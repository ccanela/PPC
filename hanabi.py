import pygame 
import sys 
import paramiko
import random

class HanabiGame:
    def __init__(self, num_players):
        self.play_pile = []
        self.discarded_cards = []
        self.players_cards = {f"player{i+1}": [] for i in range(num_players)}
        self.initialize_deck(num_players)

    def initialize_deck(self, num_players):
        colors = ['red', 'blue', 'green', 'yellow', 'white']
        numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]

        num_cards_in_hand = 5 if num_players in [2, 3] else 4

        deck = [{'color': color, 'number': number} for color in colors for number in numbers]
        random.shuffle(deck)

        for player in range(num_players):
            for _ in range(num_cards_in_hand):
                card = deck.pop()
                self.players_cards[f"player{player+1}"].append(card)

    def display_game_state(self):
        print("Play Pile:", self.play_pile)
        print("Discarded Cards:", self.discarded_cards)
        for player, cards in self.players_cards.items():
            print(f"{player}'s Cards:", cards)

def initialize_player_window(player_num):
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

player_screens = [initialize_player_window(i+1) for i in range(num_players)]
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