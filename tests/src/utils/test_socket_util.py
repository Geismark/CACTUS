from src.utils.socket_util import get_socket_id
import socket, pytest, errno


def test_get_socket_id_gives_correct_response():
    class MockSocket:
        def getpeername(self):
            return ("192.168.0.17", 8080)

        def fileno(self):
            return 419

    socket = MockSocket()
    assert get_socket_id(socket) == "419-192.168.0.17:8080"


def test_get_socket_id_raises_error():
    with pytest.raises(AttributeError):
        get_socket_id("not a socket")
        get_socket_id(1234)
        get_socket_id(None)


def test_get_socket_id_unbound_socket():
    try:
        get_socket_id(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    except OSError as e:
        assert e.errno == errno.ENOTCONN
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("www.google.com", 80))
    except OSError as e:
        assert e.errno == errno.ENOTCONN
        print(e)


def test_get_socket_id_disconnected_socket():
    # TODO how to mock a server // disconnected socket?
    # will it require threading?
    pass
