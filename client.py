import socket, threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from src.logger.logger import get_logger

log = get_logger("client.py")

TESTING = True
testing_address = "127.0.0.1"
testing_port = 1375
testing_callsign = "Red Crown"

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((host, port))
# sock.send("test1".encode())


class Client(tk.Tk):
    def __init__(self):
        self.client_socket = None
        super().__init__()
        self.gui_setup()
        if TESTING:
            self.set_connect_defaults(testing_address, testing_port, testing_callsign)

    def gui_setup(self):
        self.geometry("400x100")
        self.resizable(False, False)
        # Notebook & tabs
        self.notebook = ttk.Notebook(self)
        self.tab_connect = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_connect, text="Connect")
        self.tab_tactical = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tactical, text="Tactical")
        self.notebook.pack()
        self.notebook.bind("<<NotebookTabChanged>>", None)
        # self.notebook.hide(self.tab_tactical)
        # self.notebook.tab(self.tab_tactical, state="disabled")
        # Callsign
        self.callsign_label = tk.Label(self.tab_connect, text="Callsign:")
        self.callsign_label.grid(row=1, column=0, sticky="e")
        self.callsign_text = tk.Entry(self.tab_connect, text=testing_callsign)
        self.callsign_text.grid(row=1, column=1, sticky="w")
        # address
        self.address_label = tk.Label(self.tab_connect, text="Address:")
        self.address_label.grid(row=0, column=0, sticky="e")
        self.address_text = tk.Entry(self.tab_connect)
        self.address_text.grid(row=0, column=1, sticky="w")
        # port
        self.port_label = tk.Label(self.tab_connect, text="Port:")
        self.port_label.grid(row=0, column=2, sticky="e")
        self.port_text = tk.Entry(self.tab_connect)
        self.port_text.grid(row=0, column=3, sticky="w")
        # button
        self.connect_button = tk.Button(
            self.tab_connect, text="Connect", command=self.connect_to_server
        )
        self.connect_button.grid(row=1, column=3)
        self.connect_feedback_label = tk.Label(self.tab_connect, text="")
        self.connect_feedback_label.grid(row=2, column=0, columnspan=4)

        # self.main_textbox = scrolledtext.ScrolledText(self, height=30, width=80)
        # self.main_textbox.grid(row=1, column=0, columnspan=7)

        # self.input_box = tk.Entry(self, width=80)
        # self.input_box.grid(row=2, column=0, columnspan=6)
        # self.send_button = tk.Button(self, text="Send", command=self.send_to_server)
        # self.send_button.grid(row=2, column=7)

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_feedback_label.config(text="")
        self.address = self.address_text.get()
        self.port = int(self.port_text.get())
        self.callsign = self.callsign_text.get()
        try:
            self.client_socket.connect((self.address, self.port))
            self.client_socket.send(self.callsign.encode("utf-8"))
            self.listen_thread = threading.Thread(target=self.listen_to_server)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            self.set_element_states(
                [
                    self.address_text,
                    self.port_text,
                    self.callsign_text,
                    self.connect_button,
                ],
                "disable",
            )
            self.connect_feedback_label.config(text="Connection Success")
            log.debug(f"Connection Successful: {self.address}:{self.port}")
        except ConnectionRefusedError:
            log.debug(
                f"Attempted connection: {self.address}:{self.port} - Connection Refused"
            )
            self.connect_feedback_label.config(text="Connection Refused")
            # self.connect_button.config(fg="red")

    def listen_to_server(self):
        log.debug("listening thread started - NYI")

    def set_element_states(self, elements: list, state: str) -> None:
        for el in elements:
            el["state"] = state

    def send_to_server(self):
        pass

    def set_connect_defaults(self, address, port, callsign):
        self.address_text.insert(0, address)
        self.port_text.insert(0, port)
        self.callsign_text.insert(0, callsign)


if __name__ == "__main__":
    app = Client()
    app.mainloop()
