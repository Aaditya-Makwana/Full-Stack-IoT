import socket
from pymodbus.client import ModbusTcpClient
import time

UDP_PORT = 4210
SLAVE_ID = 1
BROADCAST_IP = '255.255.255.255'
MODBUS_PORT = 502

# Discover the slave IP using UDP broadcast
def discover_slave():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)
    
    message = bytes([SLAVE_ID])
    sock.sendto(message, (BROADCAST_IP, UDP_PORT))
    
    try:
        data, addr = sock.recvfrom(1024)
        slave_ip = addr[0]
        print(f"Slave discovered at IP: {slave_ip}")
        return slave_ip
    except socket.timeout:
        print("Slave discovery timed out.")
        return None
    finally:
        sock.close()


def read_modbus_data(slave_ip):
    client = ModbusTcpClient(slave_ip, port=MODBUS_PORT)
    client.connect()

    try:
        while True:
            result = client.read_input_registers(1, 4, unit=1)
            if result.isError():
                print("Error reading input registers")
            else:
                print(f"Input Registers: {result.registers}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping Modbus read loop.")
    finally:
        client.close()


def main():
    slave_ip = discover_slave()
    if slave_ip:
        read_modbus_data(slave_ip)

if __name__ == "__main__":
    main()