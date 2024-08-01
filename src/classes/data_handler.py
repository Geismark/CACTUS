from src.logger.logger import get_logger
import traceback, re, json, time


class DataHandler:
    log = get_logger(__name__)
    log.trace("DataHandler class loaded")

    def __init__(self, client_socket, output_dict_queue):
        """Obj/init should only be used in peer-peer listen threads for recv functions.\n
        Send functions can be run from class, object is not required."""
        self.client_socket = client_socket
        self.output_dict_queue = output_dict_queue
        self.client_ip = client_socket.getpeername()
        self.message_buffer = None
        self.expected_length = None

    # "†‡"
    def process_recv_data(self, data):
        # no prior message/header:
        if self.expected_length == None:
            # could just search for encoded header and decode only that, instead of entire message?
            DataHandler.log.debug(f"New message started from {self.client_ip}")
            temp_hold = data.decode("utf-8")
            if temp_hold[0] != "†":
                raise ValueError(
                    f"Expected header indicator † not found: {temp_hold[0]=}\n\t{temp_hold=}"
                )
            self.expected_length = re.search(r"†(\d+)‡", temp_hold).group(1)
            self.message_buffer = temp_hold.split("‡", 1)[1].encode("utf-8")
            DataHandler.log.detail(f"Expected length: {self.expected_length}")
        # ongoing message stream
        else:
            DataHandler.log.debug(f"Message continues from {self.client_ip}")
            self.message_buffer += data.decode("utf-8")
        # check is entire message has been received
        if len(self.message_buffer) == int(self.expected_length):
            data_dict_output = json.loads(self.message_buffer)
            DataHandler.log.debug(
                f"Full message received, length: {self.expected_length}, from {self.client_ip}"
            )
            self.output_dict_queue.put([self.client_socket, data_dict_output])
            self.expected_length = None
            self.message_buffer = None

    @classmethod
    def _send_data(self, conn, data):
        try:
            conn.sendall(data)
        except Exception as e:
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

    def json_test(self, client_socket):
        dict_to_send = {
            "time": time.time(),
            "Meta": {"Test": True},
            "Init": {"Username": "Red Crown", "Password": "1234"},
            "WORDS": {"ADD": {"A": "WORDS Alpha in effect"}},
        }
        json_plain = json.dumps(dict_to_send)
        json_bytes_to_send = self._process_send_data(json_plain)
        print(f"{len(json_bytes_to_send)=}")
        self._send_data(client_socket, json_bytes_to_send)

    @classmethod
    def send_dict_message_to_server(self, conn, message_dict):
        """Takes a formatted dictionary from the client and sends it to the server as JSON.\n
        "time" should not be added to the dictionary before calling this method.\n
        Header indicators should be filtered prior to calling this method.\n
        See: /src/utils/example.json for protocol documentation."""
        message_dict["time"] = time.time()
        DataHandler.log.debug(f"Sending message - dict length: {len(message_dict)}")
        DataHandler.log.detail(f"{message_dict=}")
        json_plain = json.dumps(message_dict)
        json_bytes_to_send = self._process_send_data(json_plain)
        self._send_data(conn, json_bytes_to_send)
