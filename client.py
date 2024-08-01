import socket, threading, traceback
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from src.logger.logger import get_logger
from src.classes.client_gui import ClientGUI
from src.utils.words_util import int_to_letter
from src.classes.data_handler import DataHandler
from errno import ENOTSOCK

log = get_logger("client.py")

TESTING = True
testing_address = "127.0.0.1"
testing_port = 1375
testing_callsign = "Red Crown"
testing_password = "1234"

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((host, port))
# sock.send("test1".encode())


class Client(tk.Tk):
    def __init__(self):
        self.client_socket = None
        self.connected = False
        # TODO never reference self.connected directly, go through self.set_connected()
        super().__init__()
        self.gui_setup()
        if TESTING:
            self.set_connect_defaults(
                testing_address, testing_port, testing_callsign, testing_password
            )

    def gui_setup(self):
        ClientGUI.gui_setup(self)

    def disconnect_from_server(self):
        # must come first to stop socket.recv() before losing socket
        self.connected = False
        self.client_socket.shutdown(2)  # 2 = SHUT_RDWR meaning no more reads or writes
        self.client_socket.close()
        self.toggle_connect_tab_elements(False)
        self.set_connect_feedback(text="Disconnected")

    def connect_to_server(self):
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
                "Callsign": self.callsign,
                "Password": self.password,
                "Request Setup": True,  # should be True always, testing only
            }
        }
        try:
            self.client_socket.connect((self.address, self.port))
            DataHandler.send_dict_message_to_server(
                self.client_socket, connect_message_dict
            )
            self.connected = True  # TODO update widgets by 'connected'
            self.toggle_connect_tab_elements(True)
            self.set_connect_feedback(text="Connection Successful")
            log.debug(f"Connection Successful: {self.address}:{self.port}")
            self.listen_thread = threading.Thread(target=self.listen_to_server)
            self.listen_thread.daemon = True
            self.listen_thread.start()
        except ConnectionRefusedError:
            log.debug(
                f"Attempted connection: {self.address}:{self.port} - Connection Refused"
            )
            self.set_connect_feedback(text="Connection Refused")
            # self.connect_button.config(fg="red")

    def listen_to_server(self):
        try:
            while self.connected:
                data_bytes = self.client_socket.recv(4096)
                log.debug("listening thread started - NYI")
        except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
            self.connected = False
            self.toggle_connect_tab_elements(False)
            self.set_connect_feedback(text="Connection Lost")
            log.debug("Connection Lost")
        except OSError as e:
            if (
                e.errno == ENOTSOCK
            ):  # ENOTSOCK -> OSError: [WinError 10038] An operation was attempted on something that is not a socket
                log.debug("Client Socket closed [10038] - traceback in log.trace")
            log.trace(f"{traceback.format_exc()}")
        log.debug("Listening thread closed")

    def set_element_states(self, elements: list, state: str) -> None:
        for el in elements:
            el["state"] = state

    def toggle_connect_tab_elements(self, connected: bool) -> None:
        if connected:
            inputs_state = "disable"
            self.connect_button.config(
                text="Disconnect", command=self.disconnect_from_server
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

    def send_to_server(self):
        message = "NYI"
        self.client_socket.send(message.encode("utf-8"))

    def set_connect_defaults(self, address, port, callsign, password):
        self.address_text.insert(0, address)
        self.port_text.insert(0, port)
        self.callsign_text.insert(0, callsign)
        self.password_text.insert(0, "1234")

    def set_connect_feedback(self, text):
        self.connect_feedback_label.config(text=text)

    def update_words(self):
        word = self.words_input_word_entry.get()
        text = self.words_input_text.get()
        if not self.check_indicators_in_text_list([text]):

            pass

    def check_indicators_in_text_list(self, text_list):
        indicators = set("†‡")
        for text in text_list:
            if any((i in indicators) for i in text):
                log.detail(f"Indicators †‡ found in text: {text}")
                return True
        return False


if __name__ == "__main__":
    app = Client()
    app.mainloop()
