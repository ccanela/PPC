from multiprocessing.managers import BaseManager
from multiprocessing import Lock 

# Prompt the user to enter the number of players
while True:
    num_players = int(input("How many players? "))
    if 2 <= num_players <= 5:
        break
    else:
        print("Invalid option. Please enter a number between 2 and 5.")
print("You can now run the Game.")

# Initialize locks for shared resources
lock_tokens = Lock()
lock_suites = Lock()
lock_players_cards = Lock()

# Initialize game state (shared ressources too)
colors = ['red', 'blue', 'green', 'yellow', 'purple'][:num_players]
tokens = {"info_tk" : 3 + num_players, "fuse_tk" : 3}
suites = {color: 0 for color in colors}
players_cards = {f"player{i+1}": [] for i in range(num_players)}

# Define functions to get and set shared resources
def get_tokens():
    with lock_tokens:
        return tokens

def set_tokens(key, value):
    with lock_tokens:
        tokens[key] = value

def get_suites():
    with lock_suites:
        return suites

def set_suites(key, value):
    with lock_suites:
        suites[key] = value

def get_players_cards():
    with lock_players_cards:
        return players_cards

def set_players_cards(key, value):
    with lock_players_cards:
        players_cards[key] = value

class RemoteManager(BaseManager): pass

# Register methods that can be called on the server
RemoteManager.register('get_tokens', callable=lambda:tokens)
RemoteManager.register('get_suites', callable=lambda:suites)
RemoteManager.register('get_players_cards', callable=lambda:players_cards)
RemoteManager.register('set_tokens', callable=set_tokens)
RemoteManager.register('set_suites', callable=set_suites)
RemoteManager.register('set_players_cards', callable=set_players_cards)

# Create an instance of RemoteManager and start the server
m = RemoteManager(address=('', 50000), authkey=b'abracadabra')
s = m.get_server()
s.serve_forever()
