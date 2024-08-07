def get_socket_id(client_socket):
    addr_ip = client_socket.getpeername()
    return f"{client_socket.fileno()}-{addr_ip[0]}:{addr_ip[1]}"
