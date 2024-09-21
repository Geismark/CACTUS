# ============== DO NOT MOVE ==============
import src.logger.__init__ as log_init
# ============== DO NOT MOVE ==============
log_init.custom_file_name_start = "server_"
# ============== DO NOT MOVE ==============

import socket, threading
from queue import Queue
from src.logger.logger import get_logger
from src.classes.data_handler import DataHandler
from datetime import datetime
from src.utils.socket_util import get_socket_id
import copy

log = get_logger("Server")
RECV_SIZE = 4096


class ServerManager:
    def __init__(self, init_data_state_dict=None):
        self.data_state = init_data_state_dict

    def _server_setup(self):
        self.data_queue = Queue()  # [[client_socket, json.loads(msg_dict)], ...]
        self.clients = {}
        self.new_clients = {}
        self.run_client_threads = True
        if not self.data_state:
            self.data_state = {
            "WORDS": {"ADD": {}},
            "Users": {"ADD": {}},
            "Chat": {"ADD": {}},
            }
        self.words_state = self.data_state["WORDS"]["ADD"]
        self.users_notes_dict = self.data_state["Users"]["ADD"]
        self.chat_history = self.data_state["Chat"]["ADD"]
        self.chat_index = 0
        self.processing_thread = None
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen()
        log.info(
            f"Server bound & listening: {self.host if self.host else '*'}:{self.port}"
        )
    
    def start_server(self, host="127.0.0.1", port="13750", password="1234"):
        self.host = host
        self.port = int(port)
        self.password = password
        self._server_setup()
        self.server_sock.settimeout(1) # allows server socket KeyboardInterrupt
        self._start_processing_thread()
        try:
            self.wait_for_new_client_loop()
        except KeyboardInterrupt:
            log.warning("Server closed by KeyboardInterrupt.")
        finally:
            self.close_server()
        
    def close_server(self):
        self.run_client_threads = False
        self.server_sock.close()
        self.new_clients.clear()
        self.clients.clear()
        log.info("Server shutdown.")

    def wait_for_new_client_loop(self):
        while True:
            try:
                client_socket, addr = self.server_sock.accept()
                log.info(f"Accepted new client: {addr}")
                log.detail(client_socket)
                self.add_new_client(client_socket, addr)
                self._start_client_thread(client_socket)
            except socket.timeout:
                log.trace("socket.timeout - check for KeyboardInterrupt")

    def add_new_client(self, client_socket, addr):
        self.new_clients[client_socket] = {
            "fileno": client_socket.fileno(),
            "addr": addr,
            "id_str": get_socket_id(client_socket),
        }
    
    def _start_client_thread(self, client_socket):
        client_thread = threading.Thread(
            target=self.handle_client, args=(client_socket,), daemon=True
        )
        client_thread.start()

    def _start_processing_thread(self):
        if self.processing_thread:
            log.error("Processing thread already exists")
            return
        self.processing_thread = threading.Thread(
            target=self.process_data_thread, daemon=True
        )
        self.processing_thread.start()

    def _setup_client_thread(self, client_socket):
        data_handler = DataHandler(client_socket, self.data_queue)
        addr_ip = client_socket.getpeername()
        client_id = f"{client_socket.fileno()}-{addr_ip[0]}:{addr_ip[1]}"
        return data_handler, client_id
    
    def handle_client(self, client_socket):
        data_handler, client_id = self._setup_client_thread(client_socket)
        log.detail(
            f"Client thread started: {client_id} {threading.current_thread().name}"
        )
        
        thread_client_connected = True
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
        client_socket.shutdown(2)
        client_socket.close()
        log.detail(f"Thread closed: {client_id} {threading.current_thread().name}")

    def process_data_thread(self):
        while self.run_client_threads:
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
            if not self.clients.get(client_socket):
                log.warning(
                    f"Message received from unauthenticated client: {get_socket_id(client_socket)}"
                )
                continue
            self.process_message_from_authenticated_user(client_socket, message)

    def process_message_from_authenticated_user(self, client_socket, data):
        time = data.get("time")
        if init := data.get("Init", {}):
            pass
        self._process_Meta(client_socket, data.get("Meta", {}))
        self._process_WORDS(client_socket, data.get("WORDS", {}))
        self._process_Users(client_socket, data.get("Users", {}))
        self._process_Chat(client_socket, data.get("Chat", {}))

    def _process_Init(self, client_socket, init):
        if init:
            log.warning(f"Received Init from authenticated user: {init}")

    def _process_Meta(self, client_socket, meta):
        if meta:
            log.warning(f"Received Meta from authenticated user: {meta}")

    def _process_WORDS(self, client_socket, words):
        if not words:
            return
        if add := words.get("ADD"):
            self._process_WORDS_add(client_socket, add)
        if edit := words.get("EDIT"):
            self._process_WORDS_edit(client_socket, edit)
        if remove := words.get("REMOVE"):
            self._process_WORDS_remove(client_socket, remove)

    def _process_WORDS_add(self, client_socket, add):
        for word_index, context in add.items():
            word_index = int(word_index)
            if word_index in self.words_state.keys():
                DataHandler.send_dict_message_to_sockets(
                    [client_socket], {"status": 410}
                )
                break
            self.words_state[word_index] = context
            self.broadcast_update_to_all_authenticated_clients(
                {"WORDS": {"ADD": {word_index: context}}}
            )

    def _process_WORDS_edit(self, client_socket, edit):
        for word_index, context in edit.items():
            word_index = int(word_index)
            if word_index not in self.words_state.keys():
                DataHandler.send_dict_message_to_sockets(
                    [client_socket], {"status": 411}
                )
                break
            self.words_state[word_index] = context
            self.broadcast_update_to_all_authenticated_clients(
                {"WORDS": {"EDIT": {word_index: context}}}
            )

    def _process_WORDS_remove(self, client_socket, remove):
        for word_index in remove:
            word_index = int(word_index)
            if word_index not in self.words_state.keys():
                DataHandler.send_dict_message_to_sockets(
                    [client_socket], {"status": 412}
                )
                break
            self.words_state.pop(word_index)
            self.broadcast_update_to_all_authenticated_clients(
                {"WORDS": {"REMOVE": [word_index]}}
            )

    def _process_Users(self, client_socket, users):
        if users:
            if users.get("ADD"):
                log.error(
                    f"User tried to ADD User: {get_socket_id(client_socket)} {users}"
                )
            if edit := users.get("EDIT"):
                for iid, note in edit.items():
                    self.users_notes_dict[int(iid)][1] = note
                    user_note_list = self.users_notes_dict[int(iid)]
                    self.broadcast_update_to_all_authenticated_clients(
                        {"Users": {"EDIT": {iid: user_note_list}}}
                    )
            if users.get("REMOVE"):
                log.error(
                    f"User tried to REMOVE User: {get_socket_id(client_socket)} {users}"
                )

    def _process_Chat(self, client_socket, chat):
        if not chat:
            return
        if add := chat.get("ADD"):
            time = datetime.now().strftime("%H:%M:%S")
            for message in add:
                message_data = [time, f"[{client_socket.fileno()}] {self.clients[client_socket]["callsign"]}", message]
                self.chat_history[self.chat_index] = message_data
                self.broadcast_update_to_all_authenticated_clients(
                    {"Chat": {"ADD": {self.chat_index: message_data}}}
                )
                self.chat_index += 1
        if chat.get("EDIT"):
            log.warning(f"Chat edit doesn't exist: {chat=}")
        if chat.get("REMOVE"):
            log.warning(f"Chat remove doesn't exist: {chat=}")


    def broadcast_update_to_all_authenticated_clients(self, dict_message):
        '''Takes a message and sends it to all authenticated clients.'''
        DataHandler.send_dict_message_to_sockets(self.clients.keys(), dict_message)

    def authenticate_new_client(self, client_socket, message_dict):
        '''Takes a message from a new/unauthenticated client and attempts to authenticate it.\n
        If client is authenticated, sends Meta message and setup to client and returns True.\n
        If client is not authenticated, sends Meta message to client and returns False.'''
        if not self.validate_password(client_socket, message_dict):
            return
        if not self.validate_callsign(
            client_socket, callsign := message_dict.get("Init", {}).get("callsign")
        ):
            return
        self.add_client_and_callsign_to_dicts(client_socket, callsign)
        self.send_new_client_auth_message(client_socket)
        self.send_new_client_setup(client_socket, message_dict)
        return True

    def send_new_client_auth_message(self, client_socket):
        '''Sends Meta message to client_socket indicating successful authentication.'''
        DataHandler.send_dict_message_to_sockets(
            [client_socket], {"Meta": {"authenticated": True}}
        )

    def send_new_client_setup(self, client_socket, message_dict):
        '''Checks if client requests setup, sends setup if requested.'''
        if message_dict.get("Init", {}).get("request_setup"):
            log.detail(f"Client requests setup: {get_socket_id(client_socket)}")
            self.send_client_setup_or_resync(client_socket, status_code=100)
        else:
            log.warning(f"Client did not request setup: {get_socket_id(client_socket)}")

    def validate_password(self, client_socket, message_dict):
        '''Checks if password is valid, returns True if valid, False if not.\n
        Sends Meta message to client if password is invalid.'''
        if not message_dict.get("Init", {}).get("password") == self.password:
            DataHandler.send_dict_message_to_sockets(
                [client_socket], {"Meta": {"password": False}}
            )
            return False
        return True

    def add_client_and_callsign_to_dicts(self, client_socket, callsign):
        '''Takes a client_socket and callsign.\n
        Sends new client callsign and note to current clients.\n
        Removes socket from new_clients dict and adds it to clients dict.\n
        Adds callsign to clients dict and adds callsign to users_notes_dict.'''
        self.broadcast_update_to_all_authenticated_clients(
            {"Users": {"ADD": {client_socket.fileno(): [callsign, "None"]}}}
        )
        self.clients[client_socket] = self.new_clients.pop(client_socket)
        self.clients[client_socket]["callsign"] = callsign
        self.users_notes_dict[client_socket.fileno()] = [callsign, "None"]

    def remove_client_from_client_dicts_and_users(self, client_socket):
        self.clients.pop(client_socket, None)
        self.new_clients.pop(client_socket, None)
        self.users_notes_dict.pop(client_socket.fileno(), None)
        self.broadcast_update_to_all_authenticated_clients(
            {"Users": {"REMOVE": [client_socket.fileno()]}}
        )

    def validate_callsign(self, client_socket, callsign):
        '''Checks if callsign is valid, returns True if valid, False if not.\n
        Sends Meta message to client_socket if callsign is invalid.'''
        if not len(callsign) >= 3:
            DataHandler.send_dict_message_to_sockets(
                [client_socket], {"Meta": {"callsign": False}}
            )
            return False
        return True

    def send_client_setup_or_resync(self, client_socket, status_code=None):
        message = copy.deepcopy(self.data_state)
        if not status_code:
            status_code = 100
        message["status"] = status_code
        DataHandler.send_dict_message_to_sockets([client_socket], message)


if __name__ == "__main__":
    server = ServerManager()
    server.start_server(host="")
