import socket
from pymodbus.client import ModbusTcpClient
import time
from threading import Thread
from flask import Flask, jsonify, render_template_string

# Network settings
UDP_PORT = 4210
SLAVE_ID = 1
BROADCAST_IP = '255.255.255.255'
MODBUS_PORT = 502

# Flask app setup
app = Flask(__name__)
register_values = [0, 0, 0, 0]  # Placeholder for register values

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

# Connect to the Modbus slave and read input registers
def read_modbus_data(slave_ip):
    global register_values
    client = ModbusTcpClient(slave_ip, port=MODBUS_PORT)
    client.connect()

    try:
        while True:
            result = client.read_input_registers(1, 4, unit=1)  # Read 4 registers
            if result.isError():
                print("Error reading input registers")
            else:
                register_values = result.registers
                #print(f"Input Registers: {register_values}")
            time.sleep(0.01)  # Reduced delay to 0.1 seconds
    except KeyboardInterrupt:
        print("Stopping Modbus read loop.")
    finally:
        client.close()

# Flask route to display the values
@app.route('/')
def index():
    global register_values
    template = '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Modbus Data Dashboard</title>
        <script>
          function fetchData() {
            fetch('/data')
              .then(response => response.json())
              .then(data => {
                document.getElementById('reg1').innerText = data[0];
                document.getElementById('reg2').innerText = data[1];
                document.getElementById('reg3').innerText = data[2];
                document.getElementById('reg4').innerText = data[3];
              });
          }
          setInterval(fetchData, 100); // Refresh every 0.5 second
        </script>
      </head>
      <body>
        <div class="container">
          <h1 class="mt-5">Modbus Data Dashboard</h1>
          <p class="lead">Displaying the values of 4 input registers:</p>
          <ul>
            <li>Register 1: <span id="reg1">0</span></li>
            <li>Register 2: <span id="reg2">0</span></li>
            <li>Register 3: <span id="reg3">0</span></li>
            <li>Register 4: <span id="reg4">0</span></li>
          </ul>
        </div>
      </body>
    </html>
    '''
    return render_template_string(template)

# Flask route to return register values as JSON
@app.route('/data')
def data():
    global register_values
    return jsonify(register_values)

# Main function
def main():
    slave_ip = discover_slave()
    if slave_ip:
        # Start Modbus data reading in a separate thread
        modbus_thread = Thread(target=read_modbus_data, args=(slave_ip,))
        modbus_thread.start()

        # Start Flask server
        app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()