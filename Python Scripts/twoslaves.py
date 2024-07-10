
import socket
from pymodbus.client import ModbusTcpClient
import time
from threading import Thread
from flask import Flask, jsonify, render_template_string, request

# Network settings
UDP_PORT = 4210
SLAVE_ID_1 = 1
SLAVE_ID_2 = 2
BROADCAST_IP = '255.255.255.255'
MODBUS_PORT = 502

# Flask app setup
app = Flask(__name__)
register_values_1 = [0, 0, 0, 0]  # Placeholder for register values of Slave ID 1
register_values_2 = [0, 0, 0, 0]  # Placeholder for register values of Slave ID 2
holding_register_values = [0, 0]  # Placeholder for values to be written to registers 5 and 6 for Slave ID 1

# Discover the slave IP using UDP broadcast
def discover_slave(slave_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)
    
    message = bytes([slave_id])
    sock.sendto(message, (BROADCAST_IP, UDP_PORT))
    
    try:
        data, addr = sock.recvfrom(1024)
        slave_ip = addr[0]
        print(f"Slave {slave_id} discovered at IP: {slave_ip}")
        return slave_ip
    except socket.timeout:
        print(f"Slave {slave_id} discovery timed out.")
        return None
    finally:
        sock.close()

# Read input registers for a specific slave
def read_input_registers(client, slave_id):
    global register_values_1, register_values_2
    try:
        if slave_id == SLAVE_ID_1:
            result = client.read_input_registers(1, 4, unit=1)  # Read 4 registers for Slave ID 1
            register_values_1 = result.registers
            print(f"Input Registers for Slave ID 1: {register_values_1}")
        elif slave_id == SLAVE_ID_2:
            result = client.read_input_registers(1, 4, unit=2)  # Read 4 registers for Slave ID 2
            register_values_2 = result.registers
            print(f"Input Registers for Slave ID 2: {register_values_2}")
        else:
            print(f"Invalid slave ID: {slave_id}")
    except Exception as e:
        print(f"Exception in Modbus read loop for Slave ID {slave_id}: {e}")

# Write values to holding registers for Slave ID 1
def write_holding_registers(client):
    global holding_register_values
    try:
        for i, value in enumerate(holding_register_values):
            register = 5 + i
            result = client.write_register(register, value, unit=1)  # Write to specified register for Slave ID 1
            if result.isError():
                print(f"Error writing to holding register {register}: {result}")
            else:
                print(f"Holding register {register} set to {value}")
    except Exception as e:
        print(f"Exception while writing to holding register for Slave ID 1: {e}")

# Flask route to display the values
@app.route('/')
def index():
    template = '''
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Modbus Data Dashboard</title>
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Raleway">
    <style>
      body,h1 {font-family: "Raleway", sans-serif}
      body, html {height: 100%; margin: 0;}
      .bgimg {
        background-image: url('https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?q=80&w=2835&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
        min-height: 100%;
        background-position: center;
        background-size: cover;
      }
      .container {
        max-width: 600px;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        text-align: center;
        color: #03045e;
        margin: 20% auto;
      }
      h1 {
        font-size: 2.5rem;
        margin-bottom: 20px;
        animation: shine 2s infinite;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
      }
      @keyframes shine {
        0% { color: #03045e; }
        50% { color: #007bff; }
        100% { color: #03045e; }
      }
      .lead {
        font-size: 1.25rem;
        margin-bottom: 20px;
      }
      ul {
        list-style: none;
        padding: 0;
      }
      ul li {
        padding: 10px;
        background-color: #e9ecef;
        margin-bottom: 10px;
        border-radius: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1rem;
      }
      ul li span {
        font-weight: bold;
      }
      .input-container {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
      }
      input[type="number"] {
        flex: 1;
        padding: 10px;
        border: 1px solid #ced4da;
        border-radius: 5px;
        transition: border-color 0.3s;
      }
      input[type="number"]:focus {
        border-color: #007bff;
        outline: none;
      }
      button {
        display: block;
        width: 100%;
        padding: 10px;
        background-color: #03045e;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1rem;
        transition: background-color 0.3s;
      }
      button:hover {
        background-color: #007bff;
      }
    </style>
    <script>
      function fetchData() {
        fetch('/data')
          .then(response => response.json())
          .then(data => {
            document.getElementById('reg1').innerText = data.input_registers_1[0];
            document.getElementById('reg2').innerText = data.input_registers_1[1];
            document.getElementById('reg3').innerText = data.input_registers_1[2];
            document.getElementById('reg4').innerText = data.input_registers_1[3];

            document.getElementById('reg5').innerText = data.input_registers_2[0];
            document.getElementById('reg6').innerText = data.input_registers_2[1];
            document.getElementById('reg7').innerText = data.input_registers_2[2];
            document.getElementById('reg8').innerText = data.input_registers_2[3];
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
    <div class="bgimg w3-display-container w3-animate-opacity">
      <div class="container w3-display-middle">
        <h1 class="mt-5">Modbus Data Dashboard</h1>
        <p class="lead">Displaying the values of 4 input registers for Slave ID 1:</p>
        <ul>
          <li>Register 1: <span id="reg1">0</span></li>
          <li>Register 2: <span id="reg2">0</span></li>
          <li>Register 3: <span id="reg3">0</span></li>
          <li>Register 4: <span id="reg4">0</span></li>
        </ul>
        <p class="lead">Displaying the values of 4 input registers for Slave ID 2:</p>
        <ul>
          <li>Register 1: <span id="reg5">0</span></li>
          <li>Register 2: <span id="reg6">0</span></li>
          <li>Register 3: <span id="reg7">0</span></li>
          <li>Register 4: <span id="reg8">0</span></li>
        </ul>
        <div class="input-container">
          <input type="number" id="value5" placeholder="Value for Register 5" />
          <input type="number" id="value6" placeholder="Value for Register 6" />
        </div>
        <button onclick="updateRegisters()">Update Registers for Slave ID 1</button>
      </div>
    </div>
  </body>
</html>

    '''
    return render_template_string(template, input_registers_1=register_values_1, input_registers_2=register_values_2)

# Flask route to return register values as JSON
@app.route('/data')
def data():
    global register_values_1, register_values_2
    return jsonify({'input_registers_1': register_values_1, 'input_registers_2': register_values_2})

# Flask route to handle register update for Slave ID 1
@app.route('/update', methods=['POST'])
def update():
    global holding_register_values
    data = request.get_json()
    holding_register_values = [int(value) for value in data['values']]
    return '', 204

# Main function
def main():
    slave_ip_1 = discover_slave(SLAVE_ID_1)
    if not slave_ip_1:
        print(f"Could not discover Slave ID {SLAVE_ID_1}, exiting.")
        return
    
    slave_ip_2 = discover_slave(SLAVE_ID_2)
    if not slave_ip_2:
        print(f"Could not discover Slave ID {SLAVE_ID_2}, exiting.")
        return

    client_1 = ModbusTcpClient(slave_ip_1, port=MODBUS_PORT)
    client_2 = ModbusTcpClient(slave_ip_2, port=MODBUS_PORT)

    while True:
        if not client_1.is_socket_open():
            client_1.connect()
        
        if not client_2.is_socket_open():
            client_2.connect()
        
        read_input_registers(client_1, SLAVE_ID_1)
        read_input_registers(client_2, SLAVE_ID_2)
        
        write_holding_registers(client_1)  # Only write to holding registers for Slave ID 1
        
        time.sleep(1)

if __name__ == "__main__":
    # Start Flask server in a separate thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False))
    flask_thread.start()
    
    # Run the main loop
    main()