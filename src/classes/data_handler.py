from src.logger.logger import get_logger
import traceback, re

# get_logger(__name__)


class DataHandler:
    def __init__(self, conn, output_queue):
        self.conn = conn
        self.buffer = b""
        self.expected_length = None
        self.output_queue = output_queue

    # "†‡"
    def process_data(self, data):
        # no prior message/header:
        if self.expected_length == None:
            # could just search for encoded header and decode only that, instead of entire message?
            temp_hold = data.decode("utf-8")
            if temp_hold[0] != "†":
                raise ValueError(
                    f"Expected header indicator † not found: {temp_hold[0]=}"
                )
            self.expected_length = re.search(r"†(\d+)‡", temp_hold).group(1)
            self.buffer += temp_hold.split("‡")[1].encode("utf-8")
        # ongoing message stream
        else:
            pass


if __name__ == "__main__":
    inp = "†123‡I saw a blind man in amsterdam"
    testb = re.search(r"†(\d+)‡", inp).group(1)
    print(testb)
