import tkinter as tk
from tkinter import ttk


class ClientGUI:
    @classmethod
    def gui_setup(self, window: tk.Tk):
        window.geometry("700x230")
        # window.resizable(False, False)
        # Notebook & tabs
        window.notebook = ttk.Notebook(window)
        window.tab_connect = ttk.Frame(window.notebook)
        window.notebook.add(window.tab_connect, text="Connect")
        window.tab_tactical = ttk.Frame(window.notebook)
        window.notebook.add(window.tab_tactical, text="Tactical")
        window.notebook.pack()
        window.notebook.bind("<<NotebookTabChanged>>", None)
        # self.notebook.hide(self.tab_tactical)
        # self.notebook.tab(self.tab_tactical, state="disabled")
        self.setup_tab_connect(window, window.tab_connect)
        self.setup_tab_tactical(window, window.tab_tactical)

    @classmethod
    def setup_tab_connect(self, window, tab):
        # Callsign
        window.callsign_label = tk.Label(tab, text="Callsign:")
        window.callsign_label.grid(row=1, column=0, sticky="e")
        window.callsign_text = tk.Entry(tab)
        window.callsign_text.grid(row=1, column=1, sticky="w")
        # address
        window.address_label = tk.Label(tab, text="Address:")
        window.address_label.grid(row=0, column=0, sticky="e")
        window.address_text = tk.Entry(tab)
        window.address_text.grid(row=0, column=1, sticky="w")
        # port
        window.port_label = tk.Label(tab, text="Port:")
        window.port_label.grid(row=0, column=2, sticky="e")
        window.port_text = tk.Entry(tab)
        window.port_text.grid(row=0, column=3, sticky="w")
        # button & feedback label
        window.connect_button = tk.Button(
            tab, text="Connect", command=window.connect_to_server
        )
        window.connect_button.grid(row=1, column=3)
        window.connect_feedback_label = tk.Label(tab, text="")
        window.connect_feedback_label.grid(row=2, column=0, columnspan=4)

    @classmethod
    def setup_tab_tactical(self, window, tab):
        test_txt = "I saw a blind man in Amsterdam\nWith a box around his neck"
        test_txt2 = "I saw a blind man in Amsterdam With a box around his neck"

        # ================== WORDS input ==================
        # frame
        window.words_input_labelframe = ttk.LabelFrame(
            tab, text="Words Input", height=400
        )
        input_frame = window.words_input_labelframe
        input_frame.grid(row=0, column=0)
        # WORD select
        validate_command = (input_frame.register(self.validate_word_input), "%P")
        window.words_input_word_label = tk.Label(input_frame, text="Word:")
        window.words_input_word_label.grid(row=0, column=0, sticky="w")
        window.words_input_word_entry = tk.Entry(
            input_frame, width=2, validate="key", validatecommand=validate_command
        )
        window.words_input_word_entry.grid(row=0, column=1, sticky="w")
        # WORD text
        window.words_input_text = tk.Text(input_frame, width=30, height=5)
        window.words_input_text.grid(row=1, column=0, columnspan=2)

        # ================== WORDS seperator ==================
        window.words_seperator = ttk.Separator(tab)
        window.words_seperator.grid(row=0, column=1, padx=5, sticky="ns")
        # ================== WORDS table ==================
        # frame
        window.words_treeFrame = ttk.LabelFrame(tab, text="Words")
        tree_frame = window.words_treeFrame
        tree_frame.grid(row=0, column=2)
        # scrollbar init
        treeScroll = ttk.Scrollbar(tree_frame, orient="vertical")
        treeScroll.pack(side="right", fill="y")
        # treeview & scrollbar config
        cols = ("WORD", "Content")
        window.words_treeview = ttk.Treeview(
            tree_frame,
            columns=cols,
            show="headings",
            height=8,
            yscrollcommand=treeScroll.set,
        )
        window.words_treeview.pack()
        treeScroll.config(command=window.words_treeview.yview)
        # set column width
        window.words_treeview.column("WORD", width=5, anchor="center")
        window.words_treeview.column("Content", width=400, anchor="w")
        # set column names
        for col in cols:
            window.words_treeview.heading(col, text=col)

    @classmethod
    def validate_word_input(self, result):
        # https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter/4140988#4140988

        # WORD can only be a single letter ("" also allowed to let user delete)
        # Couldn't find a way to call widget within a validatecommand
        if (result == "" or result.isalpha()) and len(result) <= 1:
            return True
        else:
            return False
