General:
ADD UNIT TESTS
able to hook errors and log before raised? must ignore try-excepts
add colours to logger


Server:
send connected user updates

Client:
add a "recall" and "undo" button to client (get input from last send; reverse action of last send to server)
add 'Enter' functionality
add users and chat tab (multiple channels? DMs?)
add 'favourites' to connect - allow to save IPs
add ATOs tab (needs planning prior to implementation)


Very rarely, server sends auth successful, client recieves start, but never considers to have recieved 'full' message?
- haven't had this recently, may have been an issue whilst auth was still WIP

add linter
reinitialising client queue on connect (= None on disconnect)
- will processing thread get stuck on old "none" queue due to blocking?
sort word treeview by iid (A->Z)
sort user treeview by iid (socket fileno)
broadcast new user callsigns

Feedback:
- add ATOs
- add sound
- add replay
- transcription of SRS?