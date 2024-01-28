from multiprocessing.managers import BaseManager

num_players = int(input("How many players? "))

#Utilisation des remote managers pour la shared memory
colors = ['red', 'blue', 'green', 'yellow', 'white'][:num_players]
tokens = {"info_tk" : 3, "fuse_tk" : 3}
suites = {color: 0 for color in colors}
players_cards = {f"player{i+1}": [] for i in range(num_players)}

def set_players_cards(key, value):
    players_cards[key] = value

def set_tokens(key, value):
    tokens[key] = value

def set_suites(key, value): 
    suites[key] = value

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
