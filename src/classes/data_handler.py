from src.logger.logger import get_logger
import traceback, re, json, time
from errno import ENOTSOCK
from src.utils.socket_util import get_socket_id
from src.utils.words_util import int_to_phonetic


class DataHandler:
	log = get_logger(__name__)
	log.trace("DataHandler class loaded")

	def __init__(self, client_socket, output_dict_queue):
		"""Obj/init should only be used in peer-peer listen threads for recv functions.\n
		Send functions can be run from class, object is not required."""
		self.client_socket = client_socket
		self.output_dict_queue = output_dict_queue
		self.client_ip = client_socket.getpeername()
		self.socket_id = get_socket_id(client_socket)
		self.message_buffer = None
		self.expected_length = None

	# "†‡" \xe2\x80\xa0   \xe2\x80\xa1
	def process_recv_data(self, data):
		# TODO what happens if data contains end of message and start of another???
		# no prior message/header:
		if self.expected_length == None:
			# could just search for encoded header and decode only that, instead of entire message?
			DataHandler.log.trace(f"New message started from {self.socket_id}")
			# temp_data_decoded = data.decode("utf-8")
			if not data.startswith(b"\xe2\x80\xa0"):  # startswith("†")
				raise ValueError(
					f"Expected header indicator † not found: {data=}\n\t{data.decoded("utf-8")=}"
				)
			
			self.expected_length = re.search(b"\xe2\x80\xa0(\\d+)\xe2\x80\xa1", data).group(1).decode("utf-8")
			self.message_buffer = data.split(b"\xe2\x80\xa1", 1)[1]
			DataHandler.log.debug(f"New message {self.socket_id} expected length: {self.expected_length}")
		# ongoing message stream
		else:
			DataHandler.log.detail(f"Message continues from {self.socket_id}")
			self.message_buffer += data
		# check is entire message has been received
		if len(self.message_buffer) == int(self.expected_length):
			decoded_message = self.message_buffer.decode("utf-8")
			data_dict_output = json.loads(decoded_message)
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
		except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
			DataHandler.log.warning(f"Failed to send message, disconnected: {conn=}")
		except Exception as e:
			if e.errno == ENOTSOCK:
				DataHandler.log.warning(f"Failed to send message, socket closed [10038] {conn=}")
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
	def send_dict_message_to_sockets(self,sockets:list,message_dict:dict)->None:
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
