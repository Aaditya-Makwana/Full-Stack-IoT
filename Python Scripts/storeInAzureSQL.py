import socket
from pymodbus.client import ModbusTcpClient
import pyodbc
import time

UDP_PORT = 4210
SLAVE_ID = 1
BROADCAST_IP = '255.255.255.255'
MODBUS_PORT = 502

server = 'your_database_server_name.database.windows.net'
database = 'your_database_name'
username = 'your_username'
password = 'your_password'
driver= '{ODBC Driver 18 for SQL Server}'

def connect_to_database():
    try:
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        print("Successfully connected to the database")
        return conn
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return None

# Create table if not exists
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InputRegisters' and xtype='U')
    CREATE TABLE InputRegisters (
        ID INT PRIMARY KEY IDENTITY,
        Register1 INT,
        Register2 INT,
        Register3 INT,
        Register4 INT,
        Timestamp DATETIME DEFAULT GETDATE()
    )
    """)
    conn.commit()

def insert_data(conn, registers):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO InputRegisters (Register1, Register2, Register3, Register4) VALUES (?, ?, ?, ?)", 
                   registers[0], registers[1], registers[2], registers[3])
    conn.commit()
    print("Data inserted into the database")

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

def read_modbus_data(slave_ip, conn):
    client = ModbusTcpClient(slave_ip, port=MODBUS_PORT)
    client.connect()

    try:
        while True:
            result = client.read_input_registers(1, 4, unit=1)
            if result.isError():
                print("Error reading input registers")
            else:
                print(f"Input Registers: {result.registers}")
                insert_data(conn, result.registers)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Stopping Modbus read loop.")
    finally:
        client.close()

def main():
    slave_ip = discover_slave()
    if slave_ip:
        conn = connect_to_database()
        if conn:
            create_table(conn)
            read_modbus_data(slave_ip, conn)
            conn.close()

if __name__ == "__main__":
    main()
