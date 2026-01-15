import serial, click, time, logging
from threading import Thread, Event
from os import system

READ_SIZE = 1024

def setup_logger(output: str | None):
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] [%(asctime)s] %(message)s", datefmt="%H:%M:%S", filename=output if output else None)

class Uartmon:
    def __init__(self, port: str, baud: int, output: str | None):
        self.serial = serial.Serial(port, baudrate=baud, timeout=0.1)
        self.stop_event = Event()
        setup_logger(output)

    def start(self, not_clear):
        if not not_clear: system("clear")
        self.rx_thread = Thread(target=self._read_loop)
        self.tx_thread = Thread(target=self._write_loop)
        self.rx_thread.start()
        self.tx_thread.start()

    def stop(self):
        self.stop_event.set()
        self.serial.close()

    def _write_loop(self):
        while not self.stop_event.is_set():
            try:
                data = input("uartmon > ")
                self.serial.write(data.encode())
            except EOFError: break

    def _read_loop(self):
        while not self.stop_event.is_set():
            data = self.serial.read(READ_SIZE)
            if not data: continue

            decoded = data.decode()
            logging.info("[RX] hex=%s | text=%s", data.hex(), decoded.strip())

@click.command()
@click.option("--port", default="/dev/ttyUSB0", help="Your custom port.")
@click.option("--baud", default=115200, help="Your custom baudrate.")
@click.option("--output", default=None, help="Your log file")
@click.option("--not_clear", is_flag=True, help="Dont clear screen.")
def main(port, baud, output, not_clear):
    try:
        monitor = Uartmon(port, baud, output)
    except serial.SerialException as e:
        print(f"[error] failed to open serial: {e}")
        return

    monitor.start(not_clear)

    try:
        while True: time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nExiting...")
        monitor.stop()

if __name__ == "__main__": main()
