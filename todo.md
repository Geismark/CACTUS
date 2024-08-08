from logger import logger as log -> init log in logger.py and just import from there


General:
ADD UNIT TESTS
able to hook errors and log before raised? must ignore try-excepts
add colours to logger
have treeview rows expand with multiple lines
make executables for server and client

Client:
add a "recall" and "undo" button to client (get input from last send; reverse action of last send to server)
add 'Enter' button functionality
add 'favourites' to connect - allow to save IPs
add ATOs tab (needs planning prior to implementation)
add audio and visual alerts when receiving updates
double click both treeview; also grab existing data to edit if edit is empty
client freezes on delayed connect/server response


add client settings
- 'favourites' to connect
- keybindings (e.g. 'Enter' functionality, select tab)
sort treeview: https://stackoverflow.com/questions/22032152/python-ttk-treeview-sort-numbers
add linter
sort word treeview by iid (A->Z)
sort user treeview by iid (socket fileno)


tidy up
make smaller functions (many in class is fine)
clear up comments
remove unused code


Feedback:
- add ATOs
- add sound
- add replay
- transcription of SRS?


self.window.notebook.bind("<<NotebookTabChanged>>", None)
self.notebook.hide(self.tab_words)
self.notebook.tab(self.tab_words, state="disabled")


Python server multi-client chatroom using sockets: https://www.youtube.com/watch?v=tDxc4NHgflY

Python Sockets:
- https://realpython.com/python-sockets/#application-client-and-server
- https://docs.python.org/3/howto/sockets.html

tkinter tabs: https://www.youtube.com/watch?v=4en9gSwmn5g

tkinter menus: https://www.youtube.com/watch?v=aODNQnc4Ebc

tkinter treeview w/ data entry: https://www.youtube.com/watch?v=8m4uDS_nyCk