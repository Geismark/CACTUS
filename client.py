import socket, threading, traceback
import tkinter as tk
from src.logger.logger import get_logger
from src.classes.client_gui import ClientGUI
from src.utils.words_util import letter_to_int
from src.classes.data_handler import DataHandler
from errno import ENOTSOCK
from queue import Queue

log = get_logger("Client")

TESTING = True
testing_address = "127.0.0.1"
testing_port = 13750
testing_callsign = "Red Crown"
testing_password = "1234"


class Client(tk.Tk):
    def __init__(self):
        self.client_socket = None
        self.connected = False
        self.server_message_queue = None
        self.processing_thread = None
        self.listen_thread = None
        self.chat_history = None
        super().__init__()
        self.gui_setup()
        if TESTING:
            self.set_connect_defaults(
                testing_address, testing_port, testing_callsign, testing_password
            )

    def gui_setup(self):
        ClientGUI.gui_setup(self)

    def disconnect_from_server(self, feedback):
        """Disconnects client from server, closes socket, stops listening and processing theads, and updates GUI"""
        self.connected = False
        self.client_socket.shutdown(2)
        self.client_socket.close()
        self.client_socket = None
        self.toggle_connect_tab_elements(False)
        self.set_connect_feedback(text=feedback)
        self.server_message_queue.put((None, None))
        self.server_message_queue = None
        self.chat_history = None
        log.debug(f"Disconnected from server - threads: {len(threading.enumerate())}")

    def connect_setup(self):
        self.server_message_queue = Queue()
        self.connect_feedback_label.config(text="")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = self.address_text.get()
        self.port = int(self.port_text.get())
        self.callsign = self.callsign_text.get()
        self.password = self.password_text.get()
        self.chat_history = {}

    def connect_to_server(self):
        self.connect_setup()
        if self.check_indicators_in_text_list([self.password, self.callsign]):
            self.set_connect_feedback(text="Invalid characters in input")
            return

        try:
            self.send_server_init_connect_messages()
            self.update_client_as_connected()
            self.reset_gui_and_start_threads()
        except ConnectionRefusedError as e:
            log.debug(
                f"Attempted connection: {self.address}:{self.port} - Connection Refused"
            )
            log.debug(e)
            self.set_connect_feedback(text="Connection Refused")
            # self.connect_button.config(fg="red")

    def update_client_as_connected(self):
        self.connected = True
        self.toggle_connect_tab_elements(True)
        self.set_connect_feedback(text="Connection Successful")
        log.debug(f"Connection Successful: {self.address}:{self.port}")

    def reset_gui_and_start_threads(self):
        ClientGUI.reset_gui()
        self.start_processing_thread()
        self.start_listening_thread()

    def send_server_init_connect_messages(self):
        connect_message_dict = self.get_connect_message_dict()
        self.client_socket.connect((self.address, self.port))
        DataHandler.send_dict_message_to_sockets(
            [self.client_socket], connect_message_dict
        )

    def get_connect_message_dict(self):
        msg_dict = {
            "Init": {
                "callsign": self.callsign,
                "password": self.password,
                "request_setup": True,
            }
        }
        return msg_dict

    def start_processing_thread(self):
        if not self.processing_thread or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(
                target=self._process_message_thread, daemon=True
            )
            self.processing_thread.start()
        else:
            log.error("Processing thread already running")

    def start_listening_thread(self):
        if not self.listen_thread or not self.listen_thread.is_alive():
            self.listen_thread = threading.Thread(
                target=self._listen_to_server_thread, daemon=True
            )
            self.listen_thread.start()
        else:
            log.error("Listening thread already running")

    def _listen_to_server_thread(self):
        log.debug("Listening thread started")
        data_handler = DataHandler(self.client_socket, self.server_message_queue)
        try:
            while self.connected:
                enc_message = self.client_socket.recv(4096)
                if not enc_message:
                    log.debug("Server socket closed, disconnecting")
                    self.disconnect_from_server("Server closed")
                    break
                data_handler.process_recv_data(enc_message)

        except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
            self.disconnect_from_server("Connection Lost")
            log.debug("Connection Lost (reset/aborted/refused)")
        except OSError as e:
            # ENOTSOCK -> OSError: [WinError 10038] An operation was attempted on something that is not a socket
            if e.errno == ENOTSOCK:
                log.debug("Client Socket closed [10038] - traceback in log.trace")
                log.trace(f"{traceback.format_exc()}")
            else:
                log.error(f"Error in listening thread\n\t{e}")
                raise e
        log.debug("Listening thread closed")

    def set_widget_states(self, elements: list, state: str) -> None:
        for el in elements:
            el["state"] = state

    def toggle_connect_tab_elements(self, connected: bool) -> None:
        if connected:
            inputs_state = "disable"
            self.connect_button.config(
                text="Disconnect",
                command=lambda: self.disconnect_from_server("Disconnected"),
            )
        else:
            inputs_state = "normal"
            self.connect_button.config(text="Connect", command=self.connect_to_server)
        self.set_widget_states(
            [
                self.address_text,
                self.port_text,
                self.callsign_text,
            ],
            inputs_state,
        )

    def set_connect_defaults(self, address, port, callsign, password):
        self.address_text.insert(0, address)
        self.port_text.insert(0, port)
        self.callsign_text.insert(0, callsign)
        self.password_text.insert(0, password)

    def set_connect_feedback(self, text):
        self.connect_feedback_label.config(text=text)

    def get_WORDS_word_text_remove(self):
        return (
            self.words_input_word_entry.get(),
            self.words_input_text.get("1.0", "end-1c"),
            self.words_input_remove.instate(["selected"]),
        )

    def update_words(self):
        feedback = self.words_input_feedback_label
        if not self.connected:
            feedback.config(text="Not connected")
            log.detail(
                f"Tried updating words, but not connected: {self.client_socket=}"
            )
            return
        word, text, remove = self.get_WORDS_word_text_remove()
        if not word:
            feedback.config(text="No WORD in input")
            log.trace(f"No WORD in input {word=}")
            return
        feedback.config(text="")
        log.trace(f"Update words: {word=}, {text=}, {remove=}")
        if self.check_indicators_in_text_list([text, word]):
            feedback.config(text="Invalid characters in input: †‡")
            log.detail(f"Invalid characters in input: †‡ {text=} {word=}")
            return
        message = self.get_words_message_dict(word, text, remove)
        DataHandler.send_dict_message_to_sockets([self.client_socket], message)
        self.words_input_word_entry.delete(0, "end")
        self.words_input_text.delete("1.0", "end")

    def get_words_message_dict(self, word, text, remove):
        word_index = letter_to_int(word)
        if remove:
            message = {"WORDS": {"REMOVE": [word_index]}}
        else:
            existing_words = self.words_treeview.get_children()
            log.trace(f"Existing words: {existing_words}\n\t{word_index=}")
            if str(word_index) in existing_words:
                message = {"WORDS": {"EDIT": {word_index: text}}}
            else:
                message = {"WORDS": {"ADD": {word_index: text}}}
        return message

    def update_users(self):
        feedback = self.users_input_feedback_label
        if not self.connected:
            feedback.config(text="Not connected")
            log.detail(
                f"Tried updating users, but not connected: {self.client_socket=}"
            )
            return
        if not (user_str := self.get_selected_user_str()):
            feedback.config(text="No USER in input")
            log.debug(f"No USER in input {user_str=}")
            return
        feedback.config(text="")
        if (user_values := ClientGUI.get_user_values_from_user_str(user_str)) == False:
            feedback.config(text="Invalid USER selected")
            log.debug(f"Invalid USER selected: {user_str=}")
            return
        iid, callsign, note = user_values
        text = self.users_input_edit_text.get("1.0", "end-1c")
        log.trace(f"Update users: {iid=} {callsign=} {note=} {text=}")
        if self.check_indicators_in_text_list([text, str(iid)]):
            feedback.config(text="Invalid characters in input: †‡")
            log.detail(f"Invalid characters in input: †‡ {text=} {iid=}")
            return
        message = {"Users": {"EDIT": {iid: text}}}
        DataHandler.send_dict_message_to_sockets([self.client_socket], message)
        self.users_input_edit_text.delete("1.0", "end")

    def get_selected_user_str(self):
        user_str = self.users_select_user_combobox.get()
        return user_str

    def send_chat_message(self):
        message = self.chat_input_entry.get()
        if not message:
            log.debug("No message in input: {message=}")
            return
        log.trace(f"Sending chat message: {message=}")
        self.chat_input_entry.delete(0, "end")
        message_dict = {"Chat": {"ADD": [message]}}
        DataHandler.send_dict_message_to_sockets([self.client_socket], message_dict)

    def check_indicators_in_text_list(self, text_list: list[str]):
        indicators = set("†‡")
        for text in text_list:
            if any((i in indicators) for i in text):
                log.detail(f"Indicators †‡ found in text: {text}")
                return True
        return False

    def _process_message_thread(self):
        log.debug("Processing thread started")
        while self.connected:
            client_socket, data = self.server_message_queue.get()
            if (client_socket, data) == (None, None):
                log.debug("Processing thread closing (None, None)")
                return
            log.debug(f"Processing message: {data}")
            time = data.get("time")
            # Status must be processed first to allow for gui reset on resync
            if status := data.get("status"):
                self.process_message_status_code(status)
            self._process_Init(data.get("Init", {}))
            self._process_Meta(data.get("Meta", {}))
            self._process_WORDS(data.get("WORDS", {}))
            self._process_Users(data.get("Users", {}))
            self._process_Chat(data.get("Chat", {}))
        log.info("Processing thread closing (disconnected)")

    def _process_Init(self, init):
        if init:
            log.warning(f"Init data received from server, not expected.\n\t{init}")

    def _process_Meta(self, meta):
        if meta.get("password") == False:
            self.connected = False
            log.info("Server rejected connection due to incorrect password")
            self.disconnect_from_server("Authentication failed (password)")
            return
        if meta.get("callsign") == False:
            self.connected = False
            log.info("Server rejected connection due to invalid callsign")
            self.disconnect_from_server("Authentication failed (callsign)")
            return
        if meta.get("authenticated") == True:
            log.info("Client is now authenticated")
            self.set_connect_feedback("Authenticated")

    def _process_WORDS(self, words):
        for iid, context in words.get("ADD", {}).items():
            ClientGUI.add_words_treeview_row(self.words_treeview, iid, context)
        for iid, context in words.get("EDIT", {}).items():
            ClientGUI.edit_words_treeview_row(self.words_treeview, iid, context)
        for iid in words.get("REMOVE", []):
            ClientGUI.remove_treeview_row(self.words_treeview, iid)

    def _process_Users(self, users):
        for iid, user_note_list in users.get("ADD", {}).items():
            ClientGUI.add_users_treeview_row(self.users_treeview, iid, user_note_list)
        for iid, user_note_list in users.get("EDIT", {}).items():
            ClientGUI.edit_users_treeview_row(self.users_treeview, iid, user_note_list)
        for iid in users.get("REMOVE", []):
            ClientGUI.remove_treeview_row(self.users_treeview, iid)

    def _process_Chat(self, chat):
        for index, message in chat.get("ADD", {}).items():
            self.chat_history[index] = message
            ClientGUI.add_chat_message(message)

    def process_message_status_code(self, status):
        status_str = f"Status: {status} - "
        match status:
            case 100:
                log.info("Received status 100 - resetting GUI and chat history")
                self.chat_history = {}
                ClientGUI.reset_gui()
            case 400:
                log.warning(
                    status_str
                    + "Client is not authenticated and did not provide Init data"
                )
            case 410:
                log.debug(status_str + "client tried to ADD when WORD already exists")
                self.words_input_feedback_label.config(
                    text="Adding WORD already exists"
                )
            case 411:
                log.debug(status_str + "client tried to EDIT when WORD doesn't exist")
                self.words_input_feedback_label.config(
                    text="Editing WORD which doesn't exist"
                )
            case 412:
                log.debug(status_str + "client tried to REMOVE when WORD doesn't exist")
                self.words_input_feedback_label.config(
                    text="Removing WORD which doesn't exist"
                )
            case 420:
                log.debug(status_str + "client tried to EDIT when USER doesn't exist")
                self.users_input_feedback_label.config(text="User doesn't exist")


if __name__ == "__main__":
    app = Client()
    app.mainloop()
