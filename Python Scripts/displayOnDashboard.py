import socket
from pymodbus.client import ModbusTcpClient
import time
from threading import Thread
from flask import Flask, jsonify, render_template_string

UDP_PORT = 4210
SLAVE_ID = 1
BROADCAST_IP = '255.255.255.255'
MODBUS_PORT = 502

app = Flask(__name__)
register_values = [0, 0, 0, 0] 

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
    global register_values
    client = ModbusTcpClient(slave_ip, port=MODBUS_PORT)
    client.connect()

    try:
        while True:
            result = client.read_input_registers(1, 4, unit=1)
            if result.isError():
                print("Error reading input registers")
            else:
                register_values = result.registers
                #print(f"Input Registers: {register_values}")
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Stopping Modbus read loop.")
    finally:
        client.close()

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
        color: #03045e;
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
    </style>
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
      setInterval(fetchData, 500); // Refresh every 0.5 second
    </script>
  </head>
  <body>
    <div class="bgimg">
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
    </div>
  </body>
</html>

    '''
    return render_template_string(template)

@app.route('/data')
def data():
    global register_values
    return jsonify(register_values)

def main():
    slave_ip = discover_slave()
    if slave_ip:
        modbus_thread = Thread(target=read_modbus_data, args=(slave_ip,))
        modbus_thread.start()

        app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()