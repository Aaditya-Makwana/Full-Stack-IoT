# Full-Stack-IoT

This project includes the development of an IoT system. Initial configurations include the understanding of ModBus protocol. We will be writing ModBus codes which will allows us to communicate between two ESP-WROOM-32 controllers.

The basic description of code files will be updated in the ReadMe.
Thank you!

# Table of Contents

1. MODBUS RTU
2. MODBUS TCP
3. PYTHON SCRIPTS

# MODBUS RTU

## Writing into a single holding register
[writeSingleHoldingRegisterMaster.ino](./ModBusRTU/Write%20Single%20Holding%20Register/writeSingleHoldingRegisterMaster/writeSingleHoldingRegisterMaster.ino), 
[writeSingleHoldingRegisterSlave.ino](./ModBusRTU/Write%20Single%20Holding%20Register/writeSingleHoldingRegisterSlave/writeSingleHoldingRegisterSlave.ino)

Header files used :
1. ModbusRTU.h

This code allows you to write a value into a single holding register in the slave. The protocol used is ModBus RTU, which uses the serial commuincation on the Serial2 line.

Please note that the Tx and Rx pins are 12 and 13 respectively on both the master and slave. These pins are specified in the Serial2.begin() function. The Tx pin of master is connected to the Rx pin of the slave, and vice versa.

## Reading input registers and writing holding registers
[readAndWriteMaster.ino](./ModBusRTU/Read%20and%20Write/readAndWriteMaster/readAndWriteMaster.ino), 
[readAndWriteSlave.ino](./ModBusRTU/Read%20and%20Write/readAndWriteSlave/readAndWriteSlave.ino)

Header files used :
1. ModbusRTU.h

This code allows me to read 4 input registers from the slave as well as write into 2 holding registers conditionally. The conditions as well as the number of registers are due to the project requirements and can be changed accordingly.

Please note that:
1. Due to asynchornous nature of the ModBusRTU, it was essential to create boolean variables which allow us to know if the task was completed. A callback function changes the state of the boolean variable from true to false. Please refer to the code.
2. The logic for writing into the holding registers is specific to our project demonstration and can be changed according to personal needs.
3. The pin definitions (except the Tx and Rx pins) in the slave code are for input from sensors. We have set these pins to fulfill our input requirements. They are NOT mandatory to the modbus operation.

# MODBUS TCP

## Writing holding registers
[writeHoldingRegistersMaster.ino](./ModBusTCP/writeHoldingRegisters/writeHoldingRegistersMaster/writeHoldingRegistersMaster.ino), 
[writeHoldingRegistersSlave.ino](./ModBusTCP/writeHoldingRegisters/writeHoldingRegistersSlave/writeHoldingRegistersSlave.ino)

Header files used : 
1. WiFi.h
2. ModbusIP_ESP8266.h

The master and the slave communicate via Modbus TCP. Please ensure the following steps have been taken :
1. Replace the "ssid" and "password" variables of both the master and slave codes. We have used the ssid and password of mobile hotspot to achieve the communication.
2. Make sure to run the slave code once to determine it's IP Address. Once found, replace the IP Address in the master code with the slave IP address.

## Reading input registers with dynamic slave IP address
[readWithDynamicIPMaster.ino](./ModBusTCP/readWithDynamicIP/readWithDynamicIPMaster/readWithDynamicIPMaster.ino), 
[readWithDynamicIPSlave.ino](./ModBusTCP/readWithDynamicIP/readWithDynamicIPSlave/readWithDynamicIPSlave.ino)

Header files used : 
1. WiFi.h
2. ModbusIP_ESP8266.h
3. WiFiUdp.h

The problem with the previous code (Writing holding registers) is that we need to figure out the slave IP address first and then give it to the master manually. This is a very inefficient process. 

This problem can easily be eliminated using Slave IDs, just like ModBusRTU. We follow the given steps :
1. Set a Slave ID (say 1) in both the master and the slave
2. The master will send a broadcast, which includes the slave ID
3. The slave will be coded in such a way that it will only respond if the broadcast contains that Slave ID
4. Upon receiving broadcast containing the Slave ID, the slave will transmit it's IP Address to the master
5. The master will now know which IP Address the slave with the particular Slave ID sits at

This process can also be used for multiple slaves. We will be attempting to achieve the same (alongwith using our PC as the master instead of ESP-32) in upcoming examples.

## Dashboard display with dynamic slave IP address
[Master](./ModBusTCP/dashboardDisplay/dashboardDisplayMaster/dashboardDisplayMaster.ino), 
[Slave](./ModBusTCP/dashboardDisplay/dashboardDisplaySlave/dashboardDisplaySlave.ino)

Header files used : 
1. WiFi.h
2. ModbusIP_ESP8266.h
3. WiFiUdp.h
4. WebServer.h

Alongwith dynamic slave IP as seen in previous code, we now host a server on the master to display the data on a dashboard. It includes writing a simple html code and then hosting the server on master.

In order to view the dashboard on your PC, follow the steps given below : 
1. Connect your pc to the same network as the master and the slave
2. Note down the master IP address on startup (The master will print it's IP address on serial monitor)
3. Open your browser and type in the IP address of master. You should see the data from the slave being displayed

Auto update is yet to be implemented.

# Python Scripts

The python scripts are for the purpose of having your pc act as a master instead of an ESP32 controller. The description for each of the files is given below.

## Displaying input registers on your terminal
[printOnTerminal.py](./Python%20Scripts/printOnTerminal.py)

Imports Used:
1. socket
2. pymodbus
3. time

This code serves the same functionality as [Master](./ModBusTCP/readWithDynamicIP/readWithDynamicIPMaster/readWithDynamicIPMaster.ino). Make sure that your PC is connected to the SAME network as the ESP32 slave.

In order to implement the slave, you can use [Slave](./ModBusTCP/readWithDynamicIP/readWithDynamicIPSlave/readWithDynamicIPSlave.ino) as an example.

## Displaying input registers on a dashboard
[displayOnDashboard.py](./Python%20Scripts/displayOnDashboard.py)

Imports Used:
1. socket
2. pymodbus
3. time
4. threading
5. flask

An extension on the previous code, where in this case we display the input registers on a dashboard hosted on your local network using Flask.

## Updating holding registers using dashboard
[updateHoldingRegisters.py](./Python%20Scripts/updateHoldingRegisters.py)

Imports Used:
1. socket
2. pymodbus
3. time
4. threading
5. flask

In order to implement write functionality via dashboard, we deploy input fields and an update button. The register addresses and count are project specific and can be changed accordinly. In order to implement the slave, please use [Slave](./ModBusTCP/writeHoldingRegisters/writeHoldingRegistersSlave/writeHoldingRegistersSlave.ino) as a reference.

## Storing the register data in SQL
[storeInAzureSQL.py](./Python%20Scripts/storeInAzureSQL.py)

This script allows us to connect to Azure SQL Server, create a table, and store the register data. Make sure that your Azure SQL Server and your Azure SQL Database are setup correctly. Also make sure that your PC IP Address is configured to have access to the Azure SQL Database.

Here are a few queries which we executed as examples : 

### Viewing the table
<img src="https://github.com/Aaditya-Makwana/Full-Stack-IoT/blob/main/ScreenShots/SQL/viewtable.jpg" alt="View Table" width="1000" height="400">

### View the table with a single constraint
<img src="https://github.com/Aaditya-Makwana/Full-Stack-IoT/blob/main/ScreenShots/SQL/viewtablewithconstraint1.jpg" alt="View Table" width="1000" height="400">

### View the table with multiple constraints
<img src="https://github.com/Aaditya-Makwana/Full-Stack-IoT/blob/main/ScreenShots/SQL/viewtablewithconstraint2.jpg" alt="View Table" width="1000" height="400">

### View the table with timestamp constraints
<img src="https://github.com/Aaditya-Makwana/Full-Stack-IoT/blob/main/ScreenShots/SQL/querywithtimestamp.jpg" alt="View Table" width="1000" height="400">