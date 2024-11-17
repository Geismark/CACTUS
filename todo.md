from logger import logger as log -> init log in logger.py and just import from there

# BUGS
- any errors in server/client are not caught by logger
  - able to hook errors and log before raised? must ignore try-excepts
- have treeview rows expand with multiple lines (text-overflow)
  - https://stackoverflow.com/questions/51131812/wrap-text-inside-row-in-tkinter-treeview
- *client freezes on delayed connect/server response*
# Features
## General:
1. ADD UNIT TESTS (ongoing)
- add colours to logger
- make executables for server and client
- add linter

## Client:
1. add 'Enter' button functionality
2. add audio and visual alerts when receiving updates
3. sort treeview: https://stackoverflow.com/questions/22032152/python-ttk-treeview-sort-numbers
  - sort word treeview by iid (A->Z)
  - sort user treeview by iid (socket fileno)
- add a "recall" and "undo" button to client (get input from last send; reverse action of last send to server)
- add 'favourites' to connect - allow to save IPs
- add ATOs tab (needs planning prior to implementation)
- add check for sending chat message that client is actually connected (currently throws error)
- add check for treeview double click that anything is in the treeview (client connected)
- add client settings
  - 'favourites' to connect
  - keybindings (e.g. 'Enter' functionality, select tab)


## Feedback:
- add ATOs
- add sound
- add replay
- transcription of SRS?



## Notes / Future Reference
### Notebook editing
- self.window.notebook.bind("<<NotebookTabChanged>>", None)
- self.notebook.hide(self.tab_words)
- self.notebook.tab(self.tab_words, state="disabled")

### Initial tutorials used as reference:
- Python server multi-client chatroom using sockets: https://www.youtube.com/watch?v=tDxc4NHgflY
- Python Sockets:
  - https://realpython.com/python-sockets/#application-client-and-server
  - https://docs.python.org/3/howto/sockets.html
- Tkinter:
  - tkinter tabs: https://www.youtube.com/watch?v=4en9gSwmn5g
  - tkinter menus: https://www.youtube.com/watch?v=aODNQnc4Ebc
  - tkinter treeview w/ data entry: https://www.youtube.com/watch?v=8m4uDS_nyCk