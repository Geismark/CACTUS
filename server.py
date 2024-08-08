import src.logger.__init__ as log_init

log_init.server_custom_file_start = [True]

import socket, traceback, threading
from queue import Queue
from src.logger.logger import get_logger
from src.classes.data_handler import DataHandler
from datetime import datetime
from src.utils.socket_util import get_socket_id
import copy

log = get_logger("Server")
RECV_SIZE = 4096


class ServerManager:
    def __init__(self):
        pass

    def start_server(self, host="127.0.0.1", port="13750", password="1234"):
        # set host to "" if wanting to accept from all IPs
        self.host = host
        self.data_queue = Queue()  # [[client_socket, json.loads(msg_dict)], ...]
        self.port = int(port)
        self.password = password
        self.clients = {}
        self.new_clients = {}
        self.run_client_threads = True
        self.data_state = {
            "WORDS": {"ADD": {}},
            "Users": {"ADD": {}},
            "Chat": {"ADD": {}},
        }
        self.words_state = self.data_state["WORDS"]["ADD"]
        self.users_notes_dict = self.data_state["Users"]["ADD"]
        self.chat_history = self.data_state["Chat"]["ADD"]
        # AF_INET -> IPv4   SOCK_STREAM -> TCP
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.server_sock:
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # prevents bind() => OSError if forced closed a connection => TIME_WAIT
        # TIME_WAIT lasts ~2mins, if restart server in that time, error
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen()  # default backlog == 5
        log.info(
            f"Server bound & listening: {self.host if self.host else '*'}:{self.port}"
        )
        self.server_sock.settimeout(1)
        # timeout is for server socket and not related to client socket timeout
        # timeout is to allow for KeyboardInterrupt to be caught
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
                    self.new_clients[client_socket] = {
                        "fileno": client_socket.fileno(),
                        "addr": addr,
                        "id_str": get_socket_id(client_socket),
                    }
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_socket,), daemon=True
                    )
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
        self.remove_client_from_client_dicts_and_users(client_socket)
        # shutdown(2) = SHUT_RDWR meaning no more reads or writes
        client_socket.shutdown(2)
        client_socket.close()
        log.detail(f"Thread closed: {client_id} {threading.current_thread().name}")

    def process_data_thread(self):
        while self.run_client_threads:
            client_socket, message = self.data_queue.get()
            print(f"{self.words_state=}")
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
            if not self.clients.get(client_socket):
                log.warning(
                    f"Message received from unauthenticated client: {get_socket_id(client_socket)}"
                )
                continue
            self.process_message(client_socket, message)

    def process_message(self, client_socket, data):
        time = data.get("time")
        # ============== Init ==============
        if init := data.get("Init", {}):
            pass
        # ============== Meta ==============
        if meta := data.get("Meta", {}):
            pass
        # ============== WORDS ==============
        if words := data.get("WORDS", {}):
            if add := words.get("ADD"):
                for word_index, context in add.items():
                    word_index = int(word_index)
                    if word_index in self.words_state.keys():
                        DataHandler.send_dict_message_to_sockets(
                            [client_socket], {"status": 410}
                        )
                        break
                    self.words_state[word_index] = context
                    self.broadcast_update_all_clients(
                        {"WORDS": {"ADD": {word_index: context}}}
                    )

            if edit := words.get("EDIT"):
                for word_index, context in edit.items():
                    word_index = int(word_index)
                    if word_index not in self.words_state.keys():
                        DataHandler.send_dict_message_to_sockets(
                            [client_socket], {"status": 411}
                        )
                        break
                    self.words_state[word_index] = context
                    self.broadcast_update_all_clients(
                        {"WORDS": {"EDIT": {word_index: context}}}
                    )
            if remove := words.get("REMOVE"):
                for word_index in remove:
                    word_index = int(word_index)
                    if word_index not in self.words_state.keys():
                        DataHandler.send_dict_message_to_sockets(
                            [client_socket], {"status": 412}
                        )
                        break
                    self.words_state.pop(word_index)
                    self.broadcast_update_all_clients(
                        {"WORDS": {"REMOVE": [word_index]}}
                    )
        # ============== Users ==============
        if users := data.get("Users", {}):
            if add := users.get("ADD"):
                log.error(
                    f"User tried to ADD User: {get_socket_id(client_socket)} {data}"
                )
            if edit := users.get("EDIT"):
                for iid, note in edit.items():
                    self.users_notes_dict[int(iid)][1] = note
                    user_note_list = self.users_notes_dict[int(iid)]
                    self.broadcast_update_all_clients(
                        {"Users": {"EDIT": {iid: user_note_list}}}
                    )
            if remove := users.get("REMOVE"):
                log.error(
                    f"User tried to REMOVE User: {get_socket_id(client_socket)} {data}"
                )

    def broadcast_update_all_clients(self, dict_message):
        DataHandler.send_dict_message_to_sockets(self.clients.keys(), dict_message)

    def authenticate_new_client(self, client_socket, message_dict):
        if not self.validate_password(client_socket, message_dict):
            return
        if not self.validate_callsign(
            client_socket, callsign := message_dict.get("Init", {}).get("callsign")
        ):
            return
        if requests_setup := message_dict.get("Init", {}).get("request_setup"):
            log.detail(f"Client requests setup: {get_socket_id(client_socket)}")
            self.send_client_setup_or_resync(client_socket, status_code=100)
        else:
            log.debug(f"Client did not request setup: {get_socket_id(client_socket)}")
        # "add user" must come after setup sent, otherwise sent twice
        self.add_client_and_callsign_to_dicts(client_socket, callsign)
        DataHandler.send_dict_message_to_sockets(
            [client_socket], {"Meta": {"authenticated": True}}
        )
        return True

    def validate_password(self, client, message_dict):
        if not message_dict.get("Init", {}).get("password") == self.password:
            DataHandler.send_dict_message_to_sockets(
                [client], {"Meta": {"password": False}}
            )
            return False
        return True

    def add_client_and_callsign_to_dicts(self, client_socket, callsign):
        self.clients[client_socket] = self.new_clients.pop(client_socket)
        self.clients[client_socket]["callsign"] = callsign
        self.users_notes_dict[client_socket.fileno()] = [callsign, "None"]
        self.broadcast_update_all_clients(
            {"Users": {"ADD": {client_socket.fileno(): [callsign, "None"]}}}
        )

    def remove_client_from_client_dicts_and_users(self, client_socket):
        self.clients.pop(client_socket, None)
        self.new_clients.pop(client_socket, None)
        self.users_notes_dict.pop(client_socket.fileno(), None)
        self.broadcast_update_all_clients(
            {"Users": {"REMOVE": [client_socket.fileno()]}}
        )

    def validate_callsign(self, client_socket, callsign):
        if not len(callsign) >= 3:
            DataHandler.send_dict_message_to_sockets(
                [client_socket], {"Meta": {"callsign": False}}
            )
            return False
        return True

    def send_client_setup_or_resync(self, client_socket, status_code=None):
        message = copy.deepcopy(self.data_state)
        if status_code:
            message["status"] = status_code
        else:
            status_code = 100
        message["Users"] = {"ADD": self.users_notes_dict}
        DataHandler.send_dict_message_to_sockets([client_socket], message)


if __name__ == "__main__":
    server = ServerManager()
    server.start_server(host="")
