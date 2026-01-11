import serial, click, os, time, sys
from threading import Thread

running = True
output_file = ""

def log_info(msg):
	ts = time.time()
	info_msg = f"[info] [{ts:.6f}] {msg}"
	if output_file:
		print(info_msg, file=output_file)
		return
	print(info_msg)

def log_err(msg): 
	ts = time.time()
	err_msg = f"[error] [{ts:.6f}] {msg}"
	if output_file:
		print(err_msg, file=output_file)
		return
	print(err_msg)

def read_data(port): 
	global running
	size_read_data = 1024

	while running:
		data = port.read(size=size_read_data)
		if not data: continue
		log_info(f"RX {data.hex()}")

def write_data(port):
	global running

	while running:
		data = input("uartmon > ")
		port.write(data.encode())

def create_serial(port, baud): return serial.Serial(port=port, baudrate=baud, timeout=0.1)

@click.command()
@click.option("--port", default="/dev/ttyUSB0", help="Your serial port.")
@click.option("--read", "only_read", help="Only read uart.", default=False)
@click.option("--baud", default=115200, help="Your custom baudrate.")
@click.option("--output", default="", help="Your file for logs.")
def main(port, only_read, baud, output):
	global running
	global output_file
   	
	if len(output) > 0:
		try:
			output_file = open(output, "w", encoding="utf-8")
		except Exception as e:
			log_err(f"failed to open output file, error: {e}")
			return

	try:
		ser = create_serial(port, baud)
	except Exception as e:
		log_err(f"failed to create serial port, error: {e}.")
		return

	os.system("clear")
	
	read_thread = Thread(target=read_data, args=(ser,), daemon=True)
	
	if not only_read:
		write_thread = Thread(target=write_data, args=(ser,), daemon=True)
		write_thread.start()
	
	read_thread.start()

	try:
		while running:
			time.sleep(0.2)
	except KeyboardInterrupt:
		running = False
		output_file.close()

if __name__ == "__main__": 
    main()
