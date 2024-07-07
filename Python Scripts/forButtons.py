import socket
from pymodbus.client import ModbusTcpClient
import time
from threading import Thread  # Import Thread from threading module
from flask import Flask, jsonify, render_template_string, request

# Network settings
UDP_PORT = 4210
SLAVE_ID = 1
BROADCAST_IP = '255.255.255.255'
MODBUS_PORT = 502

# Flask app setup
app = Flask(__name__)
register_values = [0, 0, 0, 0]  # Placeholder for register values
holding_register_values = [0, 0]  # Placeholder for values to be written to registers 5 and 6

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

# Read input registers
def read_input_registers(client):
    global register_values
    try:
        result = client.read_input_registers(1, 4, unit=1)  # Read 4 registers
        if result.isError():
            print(f"Error reading input registers: {result}")
        else:
            register_values = result.registers
            print(f"Input Registers: {register_values}")
    except Exception as e:
        print(f"Exception in Modbus read loop: {e}")

# Write values to holding registers
def write_holding_registers(client):
    global holding_register_values
    try:
        for i, value in enumerate(holding_register_values):
            register = 5 + i
            result = client.write_register(register, value, unit=1)  # Write to specified register
            if result.isError():
                print(f"Error writing to holding register {register}: {result}")
            else:
                print(f"Holding register {register} set to {value}")
    except Exception as e:
        print(f"Exception while writing to holding register: {e}")

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
                document.getElementById('reg1').innerText = data.input_registers[0];
                document.getElementById('reg2').innerText = data.input_registers[1];
                document.getElementById('reg3').innerText = data.input_registers[2];
                document.getElementById('reg4').innerText = data.input_registers[3];
              });
          }

          function updateRegisters() {
            let value5 = document.getElementById('value5').value;
            let value6 = document.getElementById('value6').value;
            fetch('/update', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ values: [value5, value6] }),
            });
          }

          setInterval(fetchData, 1000); // Refresh every second
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
          <input type="number" id="value5" placeholder="Value for Register 5" />
          <input type="number" id="value6" placeholder="Value for Register 6" />
          <button onclick="updateRegisters()">Update Registers</button>
        </div>
      </body>
    </html>
    '''
    return render_template_string(template)

# Flask route to return register values as JSON
@app.route('/data')
def data():
    global register_values
    return jsonify({'input_registers': register_values})

# Flask route to handle register update
@app.route('/update', methods=['POST'])
def update():
    global holding_register_values
    data = request.get_json()
    holding_register_values = [int(value) for value in data['values']]
    return '', 204

# Main function
def main():
    slave_ip = discover_slave()
    if not slave_ip:
        print("Could not discover slave, exiting.")
        return
    
    client = ModbusTcpClient(slave_ip, port=MODBUS_PORT)

    while True:
        if not client.is_socket_open():
            client.connect()
        
        read_input_registers(client)
        write_holding_registers(client)
        
        time.sleep(1)

if __name__ == "__main__":
    # Start Flask server in a separate thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False))
    flask_thread.start()
    
    # Run the main loop
    main()