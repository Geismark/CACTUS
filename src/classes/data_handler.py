from src.logger.logger import get_logger
import traceback, re, json, time
from errno import ENOTSOCK
from src.utils.socket_util import get_socket_id
from src.utils.words_util import int_to_phonetic


class DataHandler:
    log = get_logger("DataHandler")
    log.trace("DataHandler class loaded")

    def __init__(self, client_socket, output_dict_queue):
        """Obj/init should only be used in peer-peer listen threads for recv functions.\n
        Send functions can be run from class, object is not required."""
        self.client_socket = client_socket
        self.output_dict_queue = output_dict_queue
        self.client_ip = client_socket.getpeername()
        self.socket_id = get_socket_id(client_socket)
        self.message_buffer = None
        self.enc_message_buffer = b""
        self.expected_length = None

    # # "†‡" \xe2\x80\xa0   \xe2\x80\xa1
    def process_recv_data(self, data):
        if not data:
            DataHandler.log.warning(f"Empty data received from {self.socket_id}")
            return
        DataHandler.log.detail(f"New data received from {self.socket_id}")
        self.enc_message_buffer += data
        self._check_message_buffer()

    def _check_message_buffer(self):
        if self.expected_length == None:
            self._search_for_message_header()
            if self.expected_length == None:
                DataHandler.log.debug(f"Waiting on header: {self.enc_message_buffer=}")
                return
        if len(self.enc_message_buffer) >= self.expected_length:
            data_dict = self._get_data_dict_from_buffer()
            self.output_dict_queue.put([self.client_socket, data_dict])
            if self.enc_message_buffer:
                self._check_message_buffer()

    def _search_for_message_header(self):
        data = self.enc_message_buffer
        if not data or len(data) < 8:
            return
        if not data.startswith(b"\xe2\x80\xa0"):
            DataHandler.log.error(
                f"Expected header indicator † not found: {data=}\n\t{data.decoded('utf-8')=}"
            )
            raise ValueError(
                f"Expected header indicator † not found: {data=}\n\t{data.decoded('utf-8')=}"
            )
        self.expected_length = int(
            re.search(b"\xe2\x80\xa0(\\d+)\xe2\x80\xa1", data).group(1).decode("utf-8")
        )
        self.enc_message_buffer = data.split(b"\xe2\x80\xa1", 1)[1]
        DataHandler.log.debug(
            f"New header found, expected length: {self.expected_length}, {self.socket_id}"
        )
        return

    def _get_data_dict_from_buffer(self):
        message = self.enc_message_buffer[: self.expected_length]
        self.enc_message_buffer = self.enc_message_buffer[self.expected_length :]
        data_dict = json.loads(message.decode("utf-8"))
        DataHandler.log.debug(
            f"Full message received from {self.client_ip} - length: {self.expected_length}\n\t{data_dict = }"
        )
        self.expected_length = None
        return data_dict

    @classmethod
    def _send_data(self, conn, data):
        try:
            conn.sendall(data)
        except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
            DataHandler.log.warning(f"Failed to send message, disconnected: {conn=}")
        except Exception as e:
            if e.errno == ENOTSOCK:
                DataHandler.log.warning(
                    f"Failed to send message, socket closed [10038] {conn=}"
                )
            else:
                DataHandler.log.error(f"Error sending data: {conn=}\n\t{data=}\n\t{e=}")
                DataHandler.log.error(traceback.format_exc())
                raise e

    @classmethod
    def _process_send_data(self, data):
        # data must be checked for header indicators BEFORE being passed to this method
        enc_data = data.encode("utf-8")
        header = f"†{len(enc_data)}‡".encode("utf-8")
        data_to_send = header + enc_data
        return data_to_send

    @classmethod
    def send_dict_message_to_sockets(self, sockets: list, message_dict: dict) -> None:
        if not sockets:
            DataHandler.log.warning("No sockets to broadcast to")
            return
        message_dict["time"] = time.time()
        json_plain = json.dumps(message_dict)
        json_bytes_to_send = self._process_send_data(json_plain)
        DataHandler.log.info(
            f"Sending message (in log.debug) to {len(sockets)} sockets - bytes length: {len(json_bytes_to_send)}"
        )
        DataHandler.log.debug(f"Message: {message_dict}")
        for conn in sockets:
            DataHandler.log.debug(f"Broadcasting to: {conn.fileno()}")
            self._send_data(conn, json_bytes_to_send)
        pass
