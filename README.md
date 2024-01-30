***Hanabi Multiplayer Game***
This project is a multiplayer version of the card game Hanabi, implemented in Python using multiprocessing. The game consists of three main components: a server manager (server_manager.py), the game logic (hanabi.py), and the player logic (player.py).

***Components***
- Server Manager (server_manager.py)
The server manager is responsible for managing shared data between different processes. It uses Python's multiprocessing.managers.BaseManager to create a server that holds the shared data and allows other processes to manipulate them using proxies.

- Hanabi Game (hanabi.py)
This script contains the main game logic. It initializes the game, manages the turns of the players, and sends and receives messages to and from the players.

- Player (player.py)
This script represents a player in the game. It receives messages from the game, processes them, and sends responses back to the game.

***How to Run***
You first have to install the following librairies: sysv_ipc, print_color and multiprocessing.managers
Start the server manager by running python server_manager.py.
Start the game by running python hanabi.py.
Start a player by running python player.py. Repeat this step for each player in the game.
Please note that the game, server manager, and players should all be run in separate terminal windows or processes.
