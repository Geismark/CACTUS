import re
import tkinter as tk
from tkinter import ttk
from src.logger.logger import get_logger
from src.classes.data_handler import DataHandler
from src.utils.words_util import int_to_phonetic


class ClientGUI:

    @classmethod
    def gui_setup(self, window: tk.Tk):
        self.log = get_logger("ClientGUI")

        self.log.trace("Starting ClientGUI setup")
        self.window = window
        # window.geometry("795x235") # BELOW IS TESTING SIZE
        window.geometry("795x265")
        # window.resizable(False, False)
        # Notebook & tabs
        window.notebook = ttk.Notebook(window)
        window.tab_connect = ttk.Frame(window.notebook)
        window.notebook.add(window.tab_connect, text="Connect")
        window.tab_tactical = ttk.Frame(window.notebook)
        window.notebook.add(window.tab_tactical, text="Tactical")
        window.tab_users = ttk.Frame(window.notebook)
        window.notebook.add(window.tab_users, text="Users")
        window.notebook.pack()
        window.notebook.bind("<<NotebookTabChanged>>", None)
        # reminder on how to hide/disable tabs for later
        # self.notebook.hide(self.tab_tactical)
        # self.notebook.tab(self.tab_tactical, state="disabled")
        self.setup_tab_connect(window, window.tab_connect)
        self.setup_tab_tactical(window, window.tab_tactical)
        self.setup_tab_users(window, window.tab_users)
        self.log.trace("ClientGUI setup complete")

    @classmethod
    def setup_tab_connect(self, window, tab):
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
        # Callsign
        window.callsign_label = tk.Label(tab, text="Callsign:")
        window.callsign_label.grid(row=1, column=0, sticky="e")
        window.callsign_text = tk.Entry(tab)
        window.callsign_text.grid(row=1, column=1, sticky="w")
        # password
        window.password_label = tk.Label(tab, text="Password:")
        window.password_label.grid(row=1, column=2, sticky="e")
        window.password_text = tk.Entry(tab, show="*")
        window.password_text.grid(row=1, column=3, sticky="w")
        # button & feedback label
        window.connect_button = tk.Button(
            tab, text="Connect", command=window.connect_to_server
        )
        window.connect_button.grid(row=2, column=3, sticky="e")
        window.connect_feedback_label = tk.Label(tab, text="")
        window.connect_feedback_label.grid(row=2, column=0, columnspan=3)

    @classmethod
    def setup_tab_tactical(self, window, tab):
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
        # Remove toggle (disables words_input_text)
        window.words_input_remove_label = tk.Label(input_frame, text="Remove:")
        window.words_input_remove_label.grid(row=0, column=2, sticky="w")
        window.words_input_remove = ttk.Checkbutton(
            input_frame, command=self.toggle_words_input_text
        )
        #   alternate is default for ttk.Checkbutton, make button unselected
        window.words_input_remove.state(["!alternate"])
        #   window.words_input_remove.state(["!selected"]) # not needed(?)
        window.words_input_remove.grid(row=0, column=3, sticky="w")
        # WORD text
        window.words_input_text = tk.Text(input_frame, width=30, height=5)
        window.words_input_text.grid(row=1, column=0, columnspan=3)
        # WORDS feedback
        window.words_input_feedback_label = tk.Label(input_frame, text="")
        window.words_input_feedback_label.grid(row=2, column=0, columnspan=2)
        # WORDS update button
        window.words_input_update_button = tk.Button(
            input_frame, text="Update", command=window.update_words
        )
        window.words_input_update_button.grid(row=2, column=3, sticky="e")

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
        window.words_treeview.column("WORD", width=44, minwidth=20, anchor="center")
        window.words_treeview.column("Content", width=400, anchor="w")
        # set column names
        for col in cols:
            window.words_treeview.heading(col, text=col)

    @classmethod
    def setup_tab_users(self, window, tab):
        self.setup_users_treeview(window, tab)
        self.setup_users_input(window, tab)
        self.setup_users_seperator(window, tab)

    @classmethod
    def setup_users_treeview(self, window, tab):
        # frame
        window.users_treeFrame = ttk.LabelFrame(tab, text="Users")
        tree_frame = window.users_treeFrame
        tree_frame.grid(row=0, column=2)
        # scrollbar init
        treeScroll = ttk.Scrollbar(tree_frame, orient="vertical")
        treeScroll.pack(side="right", fill="y")
        # treeview & scrollbar config
        cols = ("IID", "Users", "Notes")
        window.users_treeview = ttk.Treeview(
            tree_frame,
            columns=cols,
            show="headings",
            height=8,
            yscrollcommand=treeScroll.set,
        )
        window.users_treeview.pack()
        treeScroll.config(command=window.users_treeview.yview)
        # set column width
        window.users_treeview.column("IID", width=30, anchor="w")
        window.users_treeview.column("Users", width=80, anchor="center")
        window.users_treeview.column("Notes", width=380, anchor="w")
        # set column names
        for col in cols:
            window.users_treeview.heading(col, text=col)
        window.users_treeview.bind(
            "<Double-1>", self.user_treeview_double_click_select_user_combobox
        )

    @classmethod
    def setup_users_input(self, window, tab):
        self.users_dropdown_var = tk.StringVar()
        # frame
        window.users_input_labelframe = ttk.LabelFrame(
            tab, text="Edit User Notes", height=400
        )
        input_frame = window.users_input_labelframe
        input_frame.grid(row=0, column=0)

        # User select dropdown (combobox)
        window.users_input_user_label = tk.Label(input_frame, text="User:")
        window.users_input_user_label.grid(row=0, column=0, sticky="w")
        window.users_select_user_combobox = ttk.Combobox(
            input_frame,
            width=10,
            textvariable=self.users_dropdown_var,
            postcommand=self.update_user_dropdown_options,
        )
        window.users_select_user_combobox.grid(row=0, column=1, sticky="w")

        # User edit text
        window.users_input_edit_text = tk.Text(input_frame, width=30, height=5)
        window.users_input_edit_text.grid(row=1, column=0, columnspan=2)
        # Users feedback
        window.users_input_feedback_label = tk.Label(input_frame, text="")
        window.users_input_feedback_label.grid(row=2, column=0)
        # Users update button
        window.users_input_update_button = tk.Button(
            input_frame, text="Update", command=window.update_users
        )
        window.users_input_update_button.grid(row=2, column=1, sticky="e")

    @classmethod
    def setup_users_seperator(self, window, tab):
        window.users_seperator = ttk.Separator(tab)
        window.users_seperator.grid(row=0, column=1, padx=5, sticky="ns")

    @classmethod
    def validate_word_input(self, result):
        # https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter/4140988#4140988

        # WORD can only be a single letter ("" also allowed to let user delete)
        # Couldn't find a way to call widget within a validatecommand
        if (result == "" or result.isalpha()) and len(result) <= 1:
            self.log.trace(f"Input is valid WORD character: {result}")
            return True
        else:
            self.log.trace(f"Attempting to input invalid WORD character: {result}")
            return False

    @classmethod
    def toggle_words_input_text(self):
        remove_state = self.window.words_input_remove.instate(["selected"])
        if remove_state:
            self.window.words_input_text.config(state="disable")
        else:
            self.window.words_input_text.config(state="normal")

    @classmethod
    def reset_treeview(self, treeview):
        children = treeview.get_children()
        treeview.delete(*children)

    @classmethod
    def add_words_treeview_row(self, treeview, iid, context):
        treeview.insert("", "end", values=(int_to_phonetic(iid), context), iid=iid)

    @classmethod
    def add_users_treeview_row(self, treeview, iid, user_note_list):
        user_note_list.insert(0, iid)
        treeview.insert("", "end", values=user_note_list, iid=iid)

    @classmethod
    def edit_treeview_row(self, treeview, iid, context):
        treeview.set(iid, "Content", context)

    @classmethod
    def edit_users_treeview_row(self, treeview, iid, user_note_list):
        user_note_list.insert(0, iid)
        treeview.item(iid, values=user_note_list)

    @classmethod
    def remove_treeview_row(self, treeview, iid):
        treeview.delete(iid)

    @staticmethod
    def get_values_list_from_treeview(treeview):
        users = []
        iids = treeview.get_children()
        for iid in iids:
            users.append(treeview.item(iid)["values"])
        return users

    @classmethod
    def get_user_strings_for_dropdown(self):
        users = self.get_values_list_from_treeview(self.window.users_treeview)
        user_strings = [f"[{user[0]}] {user[1]}" for user in users]
        return user_strings

    @classmethod
    def get_user_values_from_user_str(self, user_str):
        values = self.get_values_list_from_treeview(self.window.users_treeview)
        iid = re.search(r"\[(\d+)\]", user_str).group(1)
        print(f"============= {iid=} {values=}")
        for value in values:
            if str(value[0]) == str(iid):
                return value
        return False

    @classmethod
    def update_user_dropdown_options(self):
        users_list = self.get_user_strings_for_dropdown()
        self.window.users_select_user_combobox["values"] = users_list

    @classmethod
    def reset_gui(self):
        self.reset_treeview(self.window.words_treeview)
        self.reset_treeview(self.window.users_treeview)

    @classmethod
    def user_treeview_double_click_select_user_combobox(self, event):
        children = self.window.users_treeview.get_children()
        print(f"============= {children=}")
        _selected = self.window.users_treeview.selection()
        values = self.window.users_treeview.item(_selected)["values"]
        iid = self.window.users_treeview.focus()
        values_list = self.get_values_list_from_treeview(self.window.users_treeview)
        for v_list in values_list:
            if v_list[0] == iid:
                values = v_list
        self.users_dropdown_var.set(f"[{values[0]}] {values[1]}")


# TODO sort treeview: https://stackoverflow.com/questions/22032152/python-ttk-treeview-sort-numbers
