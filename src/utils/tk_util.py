from tkinter import END


def get_tk_entry_text(tk_entry):
    return tk_entry.get()


def set_tk_entry_text(tk_entry, text: str, remove_old_text=True):
    if remove_old_text:
        tk_entry.delete(0, END)
    tk_entry.insert(0, text)


def get_tk_text_text(tk_text):
    return tk_text.get("1.0", "end-1c")


def set_tk_text_text(tk_text, text: str, remove_old_text=True):
    if remove_old_text:
        tk_text.delete("1.0", END)
    tk_text.insert("1.0", text)
