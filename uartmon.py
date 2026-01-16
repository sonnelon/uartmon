import serial, click, time, logging
from threading import Thread, Event
from os import system

def setup_logger(output: str | None):
	logging.basicConfig(level=logging.INFO,
		format="[%(levelname)s] [%(asctime)s] %(message)s",
		datefmt="%H:%M:%S",
		filename=output if output else None
	)

class Uartmon:
    _write_mode = False

    def __init__(self, port: str, baud: int, output: str | None, write: bool, timeout: int):
        self.serial = serial.Serial(port, baudrate=baud, timeout=timeout)
        self.stop_event = Event()
        setup_logger(output)
        if write: self._write_mode = True

    def start(self, not_clear: bool, read_size: int):
        if not not_clear: system("clear")

        if self._write_mode:
            self.tx_thread = Thread(target=self._write_loop, daemon=True)
            self.tx_thread.start()

        self.rx_thread = Thread(target=self._read_loop, args=(read_size,), daemon=True)
        self.rx_thread.start()

    def stop(self):
        self.stop_event.set()
        self.serial.close()

    def _write_loop(self):
        while not self.stop_event.is_set():
            try:
                data = input("uartmon > ")
                encoded_data = data.encode()
                self.serial.write(encoded_data)
                logging.info("[TX] [hex=%s] [text=%s]", encoded_data.hex(), data.rstrip())
            except EOFError: break

    def _read_loop(self, read_size: int):
        while not self.stop_event.is_set():
            data = self.serial.read(read_size)
            if not data: continue

            decoded = data.decode("utf-8", errors="replace")
            logging.info("[RX] [hex=%s] [text=%s]", data.hex(), decoded.rstrip())

@click.command()
@click.option("--port", default="/dev/ttyUSB0", help="Your custom port.")
@click.option("--baud", default=115200, help="Your custom baudrate.")
@click.option("--output", default=None, help="Your log file.")
@click.option("--not_clear", is_flag=True, help="Dont clear screen.")
@click.option("--write", is_flag=True, help="Set write mode.")
@click.option("--read_size", defaul=1024, help="Size read rx block.")
@click.option("--timeout", default=0.1, help="Your custom timeout for rx line.")
def main(port, baud, output, not_clear, write, read_size, timeout):
    create_err_msg = lambda msg: f"[error] {msg}"
    if write and not output:
        print(create_err_msg("for write mode, output file does not be empty"))
        return

    try:
        monitor = Uartmon(port, baud, output, write, timeout)
    except serial.SerialException as e:
        print(create_err_msg(f"failed to open serial: {e}"))
        return
	
    monitor.start(not_clear, read_size)

    try:
        while True: time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nExiting...")
        monitor.stop()

if __name__ == "__main__": main()
