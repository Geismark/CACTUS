import re
import tkinter as tk
from tkinter import ttk, scrolledtext
from src.logger.logger import get_logger
from src.utils.words_util import int_to_phonetic
from src.utils.chat_utils import message_data_list_to_str


class ClientGUI:

    @classmethod
    def gui_setup(self, window: tk.Tk):
        self.log = get_logger("ClientGUI")

        self.log.trace("Starting ClientGUI setup")
        self.window = window
        window.geometry("795x265")
        window.resizable(False, False)
        self.setup_notebook_and_tabs()
        self.setup_tab_connect(window, window.tab_connect)
        self.setup_tab_words(window, window.tab_words)
        self.setup_tab_users(window, window.tab_users)
        self.setup_tab_chat(window, window.tab_chat)
        self.log.trace("ClientGUI setup complete")

    @classmethod
    def setup_notebook_and_tabs(self):
        self.window.notebook = ttk.Notebook(self.window)
        # --- Connect ---
        self.window.tab_connect = ttk.Frame(self.window.notebook)
        self.window.notebook.add(self.window.tab_connect, text="Connect")
        # --- Words ---
        self.window.tab_words = ttk.Frame(self.window.notebook)
        self.window.notebook.add(self.window.tab_words, text="WORDS")
        # --- Chat ---
        self.window.tab_chat = ttk.Frame(self.window.notebook)
        self.window.notebook.add(self.window.tab_chat, text="Chat")
        # --- Users ---
        self.window.tab_users = ttk.Frame(self.window.notebook)
        self.window.notebook.add(self.window.tab_users, text="Users")
        # --- Pack ---
        self.window.notebook.pack()

    @classmethod
    def setup_tab_connect(self, window, tab):
        # --- Address ---
        window.address_label = tk.Label(tab, text="Address:")
        window.address_label.grid(row=0, column=0, sticky="e")
        window.address_text = tk.Entry(tab)
        window.address_text.grid(row=0, column=1, sticky="w")
        # --- Port ---
        window.port_label = tk.Label(tab, text="Port:")
        window.port_label.grid(row=0, column=2, sticky="e")
        window.port_text = tk.Entry(tab)
        window.port_text.grid(row=0, column=3, sticky="w")
        # --- Callsign ---
        window.callsign_label = tk.Label(tab, text="Callsign:")
        window.callsign_label.grid(row=1, column=0, sticky="e")
        window.callsign_text = tk.Entry(tab)
        window.callsign_text.grid(row=1, column=1, sticky="w")
        # --- Password ---
        window.password_label = tk.Label(tab, text="Password:")
        window.password_label.grid(row=1, column=2, sticky="e")
        window.password_text = tk.Entry(tab, show="*")
        window.password_text.grid(row=1, column=3, sticky="w")
        # --- Button ---
        window.connect_button = tk.Button(
            tab, text="Connect", command=window.connect_to_server
        )
        window.connect_button.grid(row=2, column=3, sticky="e")
        # --- Feedback ---
        window.connect_feedback_label = tk.Label(tab, text="")
        window.connect_feedback_label.grid(row=2, column=0, columnspan=3)

    @classmethod
    def setup_tab_words(self, window, tab):
        self.setup_words_treeview(window, tab)
        self.setup_words_input(window, tab)
        self.setup_words_seperator(window, tab)

    @classmethod
    def setup_words_input(self, window, tab):
        # --- Frame ---
        window.words_input_labelframe = ttk.LabelFrame(
            tab, text="Words Input", height=400
        )
        input_frame = window.words_input_labelframe
        input_frame.grid(row=0, column=0)
        # --- Select WORD ---
        validate_command = (
            input_frame.register(self._validate_word_select_input),
            "%P",
        )
        window.words_input_word_label = tk.Label(input_frame, text="Word:")
        window.words_input_word_label.grid(row=0, column=0, sticky="w")
        window.words_input_word_entry = tk.Entry(
            input_frame, width=2, validate="key", validatecommand=validate_command
        )
        window.words_input_word_entry.grid(row=0, column=1, sticky="w")
        # --- Remove ---
        window.words_input_remove_label = tk.Label(input_frame, text="Remove:")
        window.words_input_remove_label.grid(row=0, column=2, sticky="w")
        window.words_input_remove = ttk.Checkbutton(
            input_frame, command=self.toggle_words_input_text
        )
        # alternate is default state for ttk.Checkbutton, make button unselected
        window.words_input_remove.state(["!alternate"])
        window.words_input_remove.grid(row=0, column=3, sticky="w")
        # --- Text ---
        window.words_input_text = tk.Text(input_frame, width=30, height=5)
        window.words_input_text.grid(row=1, column=0, columnspan=3)
        # --- Feedback ---
        window.words_input_feedback_label = tk.Label(input_frame, text="")
        window.words_input_feedback_label.grid(row=2, column=0, columnspan=2)
        # --- Button ---
        window.words_input_update_button = tk.Button(
            input_frame, text="Update", command=window.update_words
        )
        window.words_input_update_button.grid(row=2, column=3, sticky="e")

    @classmethod
    def setup_words_seperator(self, window, tab):
        window.words_seperator = ttk.Separator(tab)
        window.words_seperator.grid(row=0, column=1, padx=5, sticky="ns")

    @classmethod
    def setup_words_treeview(self, window, tab):
        # --- Frame ---
        window.words_treeFrame = ttk.LabelFrame(tab, text="Words")
        tree_frame = window.words_treeFrame
        tree_frame.grid(row=0, column=2)
        # --- Scrollbar ---
        treeScroll = ttk.Scrollbar(tree_frame, orient="vertical")
        treeScroll.pack(side="right", fill="y")
        # --- Treeview ---
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
        window.words_treeview.column("WORD", width=44, minwidth=20, anchor="center")
        window.words_treeview.column("Content", width=400, anchor="w")
        for col in cols:
            window.words_treeview.heading(col, text=col)

    @classmethod
    def setup_tab_users(self, window, tab):
        self.setup_users_treeview(window, tab)
        self.setup_users_input(window, tab)
        self.setup_users_seperator(window, tab)

    @classmethod
    def setup_users_treeview(self, window, tab):
        # --- Frame ---
        window.users_treeFrame = ttk.LabelFrame(tab, text="Users")
        tree_frame = window.users_treeFrame
        tree_frame.grid(row=0, column=2)
        # --- Scrollbar ---
        treeScroll = ttk.Scrollbar(tree_frame, orient="vertical")
        treeScroll.pack(side="right", fill="y")
        # --- Treeview ---
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
        window.users_treeview.column("IID", width=30, anchor="w")
        window.users_treeview.column("Users", width=80, anchor="center")
        window.users_treeview.column("Notes", width=380, anchor="w")
        for col in cols:
            window.users_treeview.heading(col, text=col)
        window.users_treeview.bind(
            "<Double-1>", self._user_treeview_double_click_select_user_combobox
        )

    @classmethod
    def setup_users_input(self, window, tab):
        self.users_dropdown_var = tk.StringVar()
        # --- Frame ---
        window.users_input_labelframe = ttk.LabelFrame(
            tab, text="Edit User Notes", height=400
        )
        input_frame = window.users_input_labelframe
        input_frame.grid(row=0, column=0)
        # --- Dropdown (Combobox) ---
        window.users_input_user_label = tk.Label(input_frame, text="User:")
        window.users_input_user_label.grid(row=0, column=0, sticky="w")
        window.users_select_user_combobox = ttk.Combobox(
            input_frame,
            width=10,
            textvariable=self.users_dropdown_var,
            postcommand=self._update_user_dropdown_options,
        )
        window.users_select_user_combobox.grid(row=0, column=1, sticky="w")
        # --- Text ---
        window.users_input_edit_text = tk.Text(input_frame, width=30, height=5)
        window.users_input_edit_text.grid(row=1, column=0, columnspan=2)
        # --- Feedback ---
        window.users_input_feedback_label = tk.Label(input_frame, text="")
        window.users_input_feedback_label.grid(row=2, column=0)
        # --- Button ---
        window.users_input_update_button = tk.Button(
            input_frame, text="Update", command=window.update_users
        )
        window.users_input_update_button.grid(row=2, column=1, sticky="e")

    @classmethod
    def setup_users_seperator(self, window, tab):
        window.users_seperator = ttk.Separator(tab)
        window.users_seperator.grid(row=0, column=1, padx=5, sticky="ns")

    @classmethod
    def setup_tab_chat(self, window, tab):
        # --- Chat ---
        window.chat_scrolled_text = scrolledtext.ScrolledText(tab, width=90, height=13)
        window.chat_scrolled_text.pack()
        window.chat_scrolled_text.config(state="disabled")
        # --- Input ---
        window.chat_input_entry = tk.Entry(tab, width=90)
        window.chat_input_entry.pack(side="left", fill="x", expand=True)
        # --- Button ---
        window.chat_send_button = tk.Button(
            tab, text="Send", command=window.send_chat_message
        )
        window.chat_send_button.pack(side="right")

    @classmethod
    def _validate_word_select_input(self, result):
        """Takes the value of the text entry if an edit were to be allowed and returns if it is a valid WORD character"""
        if (result == "" or result.isalpha()) and len(result) <= 1:
            self.log.trace(f"Input is valid WORD character: {result}")
            return True
        else:
            self.log.trace(f"Attempting to input invalid WORD character: {result}")
            return False

    @classmethod
    def toggle_words_input_text(self):
        """Runs when the remove checkbox is toggled; toggles whether the text input is disabled based on if the checkbox is selected."""
        remove_state = self.window.words_input_remove.instate(["selected"])
        if remove_state:
            self.window.words_input_text.config(state="disable")
        else:
            self.window.words_input_text.config(state="normal")

    @classmethod
    def reset_treeview(self, treeview):
        """Takes a treeview object and deletes all rows"""
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
    def edit_words_treeview_row(self, treeview, iid, context):
        treeview.set(iid, "Content", context)

    @classmethod
    def edit_users_treeview_row(self, treeview, iid, user_note_list):
        user_note_list.insert(0, iid)
        treeview.item(iid, values=user_note_list)

    @classmethod
    def remove_treeview_row(self, treeview, iid):
        treeview.delete(iid)

    @staticmethod
    def get_values_list_from_treeview(treeview: ttk.Treeview) -> list[list]:
        """Takes a treeview and returns a list of values for each row"""
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
        for value in values:
            if str(value[0]) == str(iid):
                return value
        return False

    @classmethod
    def _update_user_dropdown_options(self):
        users_list = self.get_user_strings_for_dropdown()
        self.window.users_select_user_combobox["values"] = users_list

    @classmethod
    def reset_gui(self):
        self.reset_treeview(self.window.words_treeview)
        self.reset_treeview(self.window.users_treeview)

    @classmethod
    def _user_treeview_double_click_select_user_combobox(self, event):
        _selected = self.window.users_treeview.selection()
        values = self.window.users_treeview.item(_selected)["values"]
        iid = self.window.users_treeview.focus()
        values_list = self.get_values_list_from_treeview(self.window.users_treeview)
        for v_list in values_list:
            if v_list[0] == iid:
                values = v_list
        self.users_dropdown_var.set(f"[{values[0]}] {values[1]}")

    @classmethod
    def add_chat_message(self, message):
        message_str = message_data_list_to_str(message, show_timestamp=True)
        self.window.chat_scrolled_text.config(state="normal")
        self.window.chat_scrolled_text.insert("end", message_str)
        self.window.chat_scrolled_text.config(state="disabled")
