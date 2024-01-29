from multiprocessing.managers import BaseManager
from multiprocessing import Lock 

while True:
    num_players = int(input("How many players? "))
    if 2 <= num_players <= 5:
        break
    else:
        print("Invalid option. Please enter a number between 2 and 5.")

# Create Lock objects
lock_tokens = Lock()
lock_suites = Lock()
lock_players_cards = Lock()
#Utilisation des remote managers pour la shared memory
colors = ['red', 'blue', 'green', 'yellow', 'purple'][:num_players]
tokens = {"info_tk" : 3 + num_players, "fuse_tk" : 3}
suites = {color: 0 for color in colors}
players_cards = {f"player{i+1}": [] for i in range(num_players)}

# Use the mutex in the get and set functions for tokens
def get_tokens():
    with lock_tokens:
        return tokens

def set_tokens(key, value):
    lock_tokens.acquire()
    tokens[key] = value
    lock_tokens.release()

# Use the mutex in the get and set functions for suites
def get_suites():
    with lock_suites:
        return suites

def set_suites(key, value):
    with lock_suites:
        suites[key] = value

def get_players_cards():
    lock_players_cards.acquire() 
    play = players_cards
    lock_players_cards.release()
    return play

def set_players_cards(key, value):
    lock_players_cards.acquire()
    players_cards[key] = value
    lock_players_cards.release()

class RemoteManager(BaseManager): pass

RemoteManager.register('get_tokens', callable=lambda:tokens)
RemoteManager.register('get_suites', callable=lambda:suites)
RemoteManager.register('get_players_cards', callable=lambda:players_cards)
RemoteManager.register('set_tokens', callable=set_tokens)
RemoteManager.register('set_suites', callable=set_suites)
RemoteManager.register('set_players_cards', callable=set_players_cards)

m = RemoteManager(address=('', 50000), authkey=b'abracadabra')
s = m.get_server()
s.serve_forever()
