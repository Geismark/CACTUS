import socket, selectors, traceback, threading
from queue import Queue
from src.logger.logger import get_logger
from src.classes.data_handler import DataHandler
from datetime import datetime
from src.utils.socket_util import get_socket_id
import json

log = get_logger("server.py", custom_file_name_start="server_")
RECV_SIZE = 4096


class ServerManager:
    def __init__(self):
        pass

    def start_server(self, host="127.0.0.1", port="1375", password="1234"):
        # set host to "" if wanting to accept from all IPs
        self.host = host
        self.data_queue = Queue()  # [[client_socket, json.loads(msg_dict)], ...]
        self.port = int(port)
        self.password = password
        self.clients = {}  # conn: {} - will likely use list value later
        self.new_clients = {}
        self.run_client_threads = True
        self.data_state = {}
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
        self.processing_thread = threading.Thread(
            target=self.process_data_thread, daemon=True
        )
        self.processing_thread.start()
        # try-while-try loop is required, otherwise cannot interrupt blocking socket.accept
        # this way allows keyboard interrupt to stop server
        # https://stackoverflow.com/questions/34871191/cant-close-socket-on-keyboardinterrupt
        try:
            while True:
                try:
                    # wait for new client
                    client_socket, addr = self.server_sock.accept()
                    log.info(f"Accepted new client: {addr}")
                    log.detail(client_socket)
                    self.new_clients[client_socket] = [client_socket.fileno(), addr]
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_socket,)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except socket.timeout:
                    log.trace("socket.timeout check for KeyboardInterrupt")
                    # if self.clients:
                    #     self.broadcast_update_all_clients({"test": True})
                    pass
        except KeyboardInterrupt:
            log.warning("Server closed by KeyboardInterrupt.")
        finally:
            self.run_client_threads = False
            self.server_sock.close()
            self.new_clients.clear()
            self.clients.clear()

    def handle_client(self, client_socket):
        log.detail(
            f"Thread started: {client_socket.getpeername()} {threading.current_thread().name}"
        )
        data_handler = DataHandler(client_socket, self.data_queue)
        thread_client_connected = True
        addr_ip = client_socket.getpeername()
        client_id = f"{client_socket.fileno()}-{addr_ip[0]}:{addr_ip[1]}"
        while self.run_client_threads and thread_client_connected:
            try:
                enc_message = client_socket.recv(RECV_SIZE)
                if not enc_message:
                    log.info(f"Client disconnected: {client_id}")
                    thread_client_connected = False
                    break
                data_handler.process_recv_data(enc_message)
            except (ConnectionResetError, ConnectionAbortedError):
                log.info(f"Client forcibly disconnected: {client_id}")
                thread_client_connected = False
                break
        self.remove_client_from_client_dicts(client_socket)
        # shutdown(2) = SHUT_RDWR meaning no more reads or writes
        client_socket.shutdown(2)
        client_socket.close()
        log.detail(f"Thread closed: {client_id} {threading.current_thread().name}")

    def process_data_thread(self):
        while self.run_client_threads:
            # "if Queue" returns True, even if empty
            if not self.data_queue.empty():
                continue
            # don't want to block on get() as it would prevent breaking the while loop
            client_socket, message = self.data_queue.get()
            log.debug(f"Processing message from: {client_socket}\n\t{message}")
            if client_socket in self.new_clients:
                if self.authenticate_new_client(client_socket, message):
                    log.info(f"Client authenticated: {get_socket_id(client_socket)}")
                else:
                    log.info(
                        f"Client failed authentication: {get_socket_id(client_socket)}"
                    )
                continue
                # only messages recieved after authentication are processed
                # messages trying to authenticate (success or fail)
            log.warning("Message processing not implemented")

    def broadcast_update_all_clients(self, dict_message):
        DataHandler.send_dict_message_to_sockets(self.clients.keys(), dict_message)

    def send_new_client_setup(self, client_socket):
        test_dict = {"WORDS": {"ADD": {0: "Texaco INOP", 1: "Magic Midnight"}}}
        DataHandler.send_dict_message_to_sockets([client_socket], test_dict)

    def authenticate_new_client(self, client_socket, message_dict):
        if not message_dict.get("Init", {}).get("password") == self.password:
            DataHandler.send_dict_message_to_sockets(
                [client_socket], {"Meta": {"password": False}}
            )
            return False
        if not self.validate_callsign(
            callsign := message_dict.get("Init", {}).get("callsign")
        ):
            DataHandler.send_dict_message_to_sockets(
                [client_socket], {"Meta": {"callsign": False}}
            )
            return False

        self.clients[client_socket] = self.new_clients.pop(client_socket)
        requests_setup = message_dict.get("Init", {}).get("request_setup")
        if requests_setup:
            log.detail(f"Client requests setup: {get_socket_id(client_socket)}")
            self.send_new_client_setup(client_socket)
        else:
            log.warning(f"Client did not request setup: {get_socket_id(client_socket)}")
        DataHandler.send_dict_message_to_sockets(
            [client_socket], {"Meta": {"authenticated": True}}
        )
        return True

    def remove_client_from_client_dicts(self, client_socket):
        self.clients.pop(client_socket, None)
        self.new_clients.pop(client_socket, None)

    def validate_callsign(self, callsign):
        return len(callsign) >= 3


if __name__ == "__main__":
    server = ServerManager()
    server.start_server()
