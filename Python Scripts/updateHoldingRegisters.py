import socket
from pymodbus.client import ModbusTcpClient
import time
from threading import Thread
from flask import Flask, jsonify, render_template_string, request

UDP_PORT = 4210
SLAVE_ID = 1
BROADCAST_IP = '255.255.255.255'
MODBUS_PORT = 502

app = Flask(__name__)
register_values = [0, 0, 0, 0] 
holding_register_values = [0, 0]

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

def read_input_registers(client):
    global register_values
    try:
        result = client.read_input_registers(1, 4, unit=1)
        if result.isError():
            print(f"Error reading input registers: {result}")
        else:
            register_values = result.registers
            print(f"Input Registers: {register_values}")
    except Exception as e:
        print(f"Exception in Modbus read loop: {e}")

def write_holding_registers(client):
    global holding_register_values
    try:
        for i, value in enumerate(holding_register_values):
            register = 5 + i
            result = client.write_register(register, value, unit=1)
            if result.isError():
                print(f"Error writing to holding register {register}: {result}")
            else:
                print(f"Holding register {register} set to {value}")
    except Exception as e:
        print(f"Exception while writing to holding register: {e}")

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
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
      body, html {
        height: 100%;
        margin: 0;
        font-family: 'Roboto', sans-serif;
      }
      .bgimg {
        background-image: url('https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?q=80&w=2835&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
        min-height: 100%;
        background-position: center;
        background-size: cover;
        display: flex;
        justify-content: center;
        align-items: center;
      }
      .container {
        max-width: 600px;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        text-align: center;
        color: #03045e;
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
    <div class="bgimg">
      <div class="container">
        <h1>Modbus Data Dashboard</h1>
        <p class="lead">Displaying the values of 4 input registers:</p>
        <ul>
          <li>Register 1: <span id="reg1">0</span></li>
          <li>Register 2: <span id="reg2">0</span></li>
          <li>Register 3: <span id="reg3">0</span></li>
          <li>Register 4: <span id="reg4">0</span></li>
        </ul>
        <div class="input-container">
          <input type="number" id="value5" placeholder="Value for Register 5" />
          <input type="number" id="value6" placeholder="Value for Register 6" />
        </div>
        <button onclick="updateRegisters()">Update Registers</button>
      </div>
    </div>
  </body>
</html>

    
    '''
    return render_template_string(template)

@app.route('/data')
def data():
    global register_values
    return jsonify({'input_registers': register_values})

@app.route('/update', methods=['POST'])
def update():
    global holding_register_values
    data = request.get_json()
    holding_register_values = [int(value) for value in data['values']]
    return '', 204

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
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False))
    flask_thread.start()
    
    main()