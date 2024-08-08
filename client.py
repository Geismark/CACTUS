import socket, threading, traceback, re
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from src.logger.logger import get_logger
from src.classes.client_gui import ClientGUI
from src.utils.words_util import letter_to_int
from src.classes.data_handler import DataHandler
from src.utils.socket_util import get_socket_id
from errno import ENOTSOCK
from queue import Queue

log = get_logger("Client")

TESTING = True
testing_address = "127.0.0.1"
testing_port = 13750
testing_callsign = "Red Crown"
testing_password = "1234"

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((host, port))
# sock.send("test1".encode())


class Client(tk.Tk):
    def __init__(self):
        self.client_socket = None
        self.connected = False
        self.server_message_queue = None
        self.processing_thread = None
        super().__init__()
        self.gui_setup()
        if TESTING:
            self.set_connect_defaults(
                testing_address, testing_port, testing_callsign, testing_password
            )

    def gui_setup(self):
        ClientGUI.gui_setup(self)

    def disconnect_from_server(self, feedback):
        # must come first to stop socket.recv() before losing socket
        self.connected = False
        self.client_socket.shutdown(2)  # 2 = SHUT_RDWR meaning no more reads or writes
        self.client_socket.close()
        self.toggle_connect_tab_elements(False)
        self.set_connect_feedback(text=feedback)
        self.server_message_queue.put(None)
        self.server_message_queue = (None, None)
        log.debug(f"Disconnected from server - threads: {len(threading.enumerate())}")

    def connect_to_server(self):
        self.server_message_queue = Queue()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_feedback_label.config(text="")
        self.address = self.address_text.get()
        self.port = int(self.port_text.get())
        self.callsign = self.callsign_text.get()
        self.password = self.password_text.get()
        if self.check_indicators_in_text_list([self.password, self.callsign]):
            self.set_connect_feedback(text="Invalid characters in input")
            return
        connect_message_dict = {
            "Init": {
                "callsign": self.callsign,
                "password": self.password,
                "request_setup": True,  # should be True always (for now)
            }
        }
        try:
            self.client_socket.connect((self.address, self.port))
            DataHandler.send_dict_message_to_sockets(
                [self.client_socket], connect_message_dict
            )
            self.connected = True  # TODO update widgets by 'connected'
            self.toggle_connect_tab_elements(True)
            self.set_connect_feedback(text="Connection Successful")
            log.debug(f"Connection Successful: {self.address}:{self.port}")
            ClientGUI.reset_gui()
            self.check_processing_thread()
            self.listen_thread = threading.Thread(target=self.listen_to_server)
            self.listen_thread.daemon = True
            self.listen_thread.start()
        except ConnectionRefusedError as e:
            log.debug(
                f"Attempted connection: {self.address}:{self.port} - Connection Refused"
            )
            log.debug(e)
            self.set_connect_feedback(text="Connection Refused")
            # self.connect_button.config(fg="red")

    def check_processing_thread(self):
        if not self.processing_thread or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(
                target=self.process_message_thread, daemon=True
            )
            self.processing_thread.start()

    def listen_to_server(self):
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
            if (
                e.errno == ENOTSOCK
            ):  # ENOTSOCK -> OSError: [WinError 10038] An operation was attempted on something that is not a socket
                log.debug("Client Socket closed [10038] - traceback in log.trace")
                log.trace(f"{traceback.format_exc()}")
            else:
                log.error(f"Error in listening thread\n\t{e}")
                raise e
        log.debug("Listening thread closed")

    def set_element_states(self, elements: list, state: str) -> None:
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
            self.set_connect_feedback(text="Disconnected")
        self.set_element_states(
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

    def update_words(self):
        feedback = self.words_input_feedback_label
        if not self.connected:
            feedback.config(text="Not connected")
            log.detail(
                f"Tried updating words, but not connected: {self.client_socket=}"
            )
            return
        word = self.words_input_word_entry.get()
        if not word:
            feedback.config(text="No WORD in input")
            log.trace(f"No WORD in input {word=}")
            return
        feedback.config(text="")
        # 1.0 = line 1, character 0; end-1c = end of text without adding newline
        # https://stackoverflow.com/a/14824164
        text = self.words_input_text.get("1.0", "end-1c")
        remove = self.words_input_remove.instate(["selected"])
        log.trace(f"Update words: {word=}, {text=}, {remove=}")
        if self.check_indicators_in_text_list([text, word]):
            feedback.config(text="Invalid characters in input: †‡")
            log.detail(f"Invalid characters in input: †‡ {text=} {word=}")
            return
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
        DataHandler.send_dict_message_to_sockets([self.client_socket], message)
        self.words_input_word_entry.delete(0, "end")
        self.words_input_text.delete("1.0", "end")

    def update_users(self):
        feedback = self.users_input_feedback_label
        if not self.connected:
            feedback.config(text="Not connected")
            log.detail(
                f"Tried updating users, but not connected: {self.client_socket=}"
            )
            return
        user_str = self.users_select_user_combobox.get()
        if not user_str:
            feedback.config(text="No USER in input")
            log.debug(f"No USER in input {user_str=}")
            return
        feedback.config(text="")
        user_values = ClientGUI.get_user_values_from_user_str(user_str)
        if user_values == False:
            feedback.config(text="Invalid USER selected")
            log.debug(f"Invalid USER selected: {user_str=}")
            return
        iid, callsign, note = user_values

        # 1.0 = line 1, character 0; end-1c = end of text without adding newline
        # https://stackoverflow.com/a/14824164
        text = self.users_input_edit_text.get("1.0", "end-1c")
        log.trace(f"Update users: {iid=} {callsign=} {note=} {text=}")
        if self.check_indicators_in_text_list([text, str(iid)]):
            feedback.config(text="Invalid characters in input: †‡")
            log.detail(f"Invalid characters in input: †‡ {text=} {iid=}")
            return
        message = {"Users": {"EDIT": {iid: text}}}
        DataHandler.send_dict_message_to_sockets([self.client_socket], message)
        self.users_input_edit_text.delete("1.0", "end")

    def send_chat_message(self):
        message = self.chat_input_entry.get()
        if not message:
            log.debug("No message in input: {message=}")
            return
        log.trace(f"Sending chat message: {message=}")
        self.chat_input_entry.delete(0, "end")
        message_dict = {"Chat": message}
        DataHandler.send_dict_message_to_sockets([self.client_socket], message_dict)

    def check_indicators_in_text_list(self, text_list: list[str]):
        indicators = set("†‡")
        for text in text_list:
            if any((i in indicators) for i in text):
                log.detail(f"Indicators †‡ found in text: {text}")
                return True
        return False

    def process_message_thread(self):
        log.debug("Processing thread started")
        while self.connected:
            client_socket, data = self.server_message_queue.get()
            if (client_socket, data) == (None, None):
                log.debug("Processing thread received None, closing")
                break

            log.debug(f"Processing message: {data}")
            socket_id = get_socket_id(client_socket)
            # ============== status/time ==============
            time = data.get("time")
            status = data.get("status")
            if status:
                self.process_message_status_code(status)
            # ============== Init ==============
            if init := data.get("Init", {}):  # init only sent to server
                log.warning(f"Init data received from server, not expected.\n\t{data}")
            # ============== Meta ==============
            meta = data.get("Meta", {})
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
            # ============== WORDS ==============
            words = data.get("WORDS", {})
            # add
            for iid, context in words.get("ADD", {}).items():
                ClientGUI.add_words_treeview_row(self.words_treeview, iid, context)
            # edit
            for iid, context in words.get("EDIT", {}).items():
                ClientGUI.edit_treeview_row(self.words_treeview, iid, context)
            # remove
            for iid in words.get("REMOVE", []):
                ClientGUI.remove_treeview_row(self.words_treeview, iid)
            # ============== Users ==============
            users = data.get("Users", {})
            # add
            for iid, user_note_list in users.get("ADD", {}).items():
                ClientGUI.add_users_treeview_row(
                    self.users_treeview, iid, user_note_list
                )
            for iid, user_note_list in users.get("EDIT", {}).items():
                ClientGUI.edit_users_treeview_row(
                    self.users_treeview, iid, user_note_list
                )
            # remove
            for iid in users.get("REMOVE", []):
                ClientGUI.remove_treeview_row(self.users_treeview, iid)

        log.info("Processing thread closed (disconnected)")

    def process_message_status_code(self, status):
        status_str = f"Status: {status} - "
        match status:
            case 100:
                pass
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


if __name__ == "__main__":
    app = Client()
    app.mainloop()
