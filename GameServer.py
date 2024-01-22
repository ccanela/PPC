import socket
import sys
import threading
import paramiko

class GameServer(paramiko.ServerInterface):
    def __init__(self, game):
        self.game = game
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # Aquí puedes implementar tu propia lógica de autenticación
        if (username == 'usuario') and (password == 'contraseña'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def run_server(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.listen(100)
            print("[+] Listening for connection ...")
            client, addr = sock.accept()
        except Exception as e:
            print("[-] Listen/bind/accept failed: " + str(e))
            sys.exit(1)
        print("[+] Got a connection!")

        try:
            session = paramiko.Transport(client)
            session.add_server_key(paramiko.RSAKey(filename="test_rsa.key"))
            session.start_server(server=self)
        except paramiko.SSHException as x:
            print("[-] SSH negotiation failed.")
