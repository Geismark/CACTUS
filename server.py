import socket, selectors, traceback, threading
from queue import Queue
from src.logger.logger import get_logger

log = get_logger("server.py", custom_file_name_start="server_")


class ServerManager:
    def __init__(self):
        pass

    def start_server(self, host="127.0.0.1", port="1375"):
        # set host to "" if wanting to accept from all IPs
        self.host = host
        self.port = int(port)
        self.clients = {}
        # AF_INET -> IPv4   SOCK_STREAM -> TCP
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.server_sock:
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # prevents bind() => OSError if forced closed a connection => TIME_WAIT
        # TIME_WAIT lasts ~2mins, if restart server in that time, error
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen()  # default backlog = 5
        # self.server_sock.setblocking(False)
        log.info(
            f"Server bound & listening: {self.host if self.host else '*'}:{self.port}"
        )
        self.server_sock.settimeout(1)
        # try-while-try loop is required, otherwise cannot interrupt blocking socket.accept
        # this way allows keyboard interrupt to stop server
        try:
            while True:
                try:
                    # wait for new client
                    client_socket, addr = self.server_sock.accept()
                    username = client_socket.recv(1024).decode()
                    log.info(f"New client: {username} {addr}")
                    log.debug(client_socket)
                except socket.timeout:
                    log.trace("socket.timeout check for KeyboardInterrupt")
                    pass
        except KeyboardInterrupt:
            log.warning("Server closed by KeyboardInterrupt.")
        finally:
            self.server_sock.close()


if __name__ == "__main__":
    server = ServerManager()
    server.start_server()
