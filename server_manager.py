from multiprocessing.managers import BaseManager


num_players = int(input("How many players?"))

#Utilisation des remote managers pour la shared memory
colors = ['red', 'blue', 'green', 'yellow', 'white'][:num_players]
tokens = {"information_tokens" : 3, "fuse_tokens" : 3}
suites = {color: 0 for color in colors}
players_cards = {f"player{i+1}": [] for i in range(num_players)}

class RemoteManager(BaseManager): pass

RemoteManager.register('get_tokens', callable=lambda:tokens)
RemoteManager.register('get_suites', callable=lambda:suites)
RemoteManager.register('get_players_cards', callable=lambda:players_cards)


m = RemoteManager(address=('', 50000), authkey=b'abracadabra')
s = m.get_server()
s.serve_forever()
