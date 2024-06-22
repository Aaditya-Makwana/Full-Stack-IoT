# Full-Stack-IoT

This project includes the development of an IoT system. Initial configurations include the understanding of ModBus protocol. We will be writing ModBus codes which will allows us to communicate between two ESP-WROOM-32 controllers.

The basic description of code files will be updated in the ReadMe.
Thank you!

## Writing into a single holding register (Modbus RTU)
[writeSingleHoldingRegisterMaster.ino](./ModBusRTU/Write%20Single%20Holding%20Register/writeSingleHoldingRegisterMaster/writeSingleHoldingRegisterMaster.ino), 
[writeSingleHoldingRegisterSlave.ino](./ModBusRTU/Write%20Single%20Holding%20Register/writeSingleHoldingRegisterSlave/writeSingleHoldingRegisterSlave.ino)

Header files used :
1. ModbusRTU.h

This code allows you to write a value into a single holding register in the slave. The protocol used is ModBus RTU, which uses the serial commuincation on the Serial2 line.

Please note that the Tx and Rx pins are 12 and 13 respectively on both the master and slave. These pins are specified in the Serial2.begin() function. The Tx pin of master is connected to the Rx pin of the slave, and vice versa.

## Reading input registers and writing holding registers (Modbus RTU)
[readAndWriteMaster.ino](./ModBusRTU/Read%20and%20Write/readAndWriteMaster/readAndWriteMaster.ino), 
[readAndWriteSlave.ino](./ModBusRTU/Read%20and%20Write/readAndWriteSlave/readAndWriteSlave.ino)

Header files used :
1. ModbusRTU.h

This code allows me to read 4 input registers from the slave as well as write into 2 holding registers conditionally. The conditions as well as the number of registers are due to the project requirements and can be changed accordingly.

Please note that:
1. Due to asynchornous nature of the ModBusRTU, it was essential to create boolean variables which allow us to know if the task was completed. A callback function changes the state of the boolean variable from true to false. Please refer to the code.
2. The logic for writing into the holding registers is specific to our project demonstration and can be changed according to personal needs.
3. The pin definitions (except the Tx and Rx pins) in the slave code are for input from sensors. We have set these pins to fulfill our input requirements. They are NOT mandatory to the modbus operation.

## Writing holding registers (Modbus TCP)
[writeHoldingRegistersMaster.ino](./ModBusTCP/writeHoldingRegisters/writeHoldingRegistersMaster/writeHoldingRegistersMaster.ino), 
[writeHoldingRegistersSlave.ino](./ModBusTCP/writeHoldingRegisters/writeHoldingRegistersSlave/writeHoldingRegistersSlave.ino)

Header files used : 
1. WiFi.h
2. ModbusIP_ESP8266.h

The master and the slave communicate via Modbus TCP. Please ensure the following steps have been taken :
1. Replace the "ssid" and "password" variables of both the master and slave codes. We have used the ssid and password of mobile hotspot to achieve the communication.
2. Make sure to run the slave code once to determine it's IP Address. Once found, replace the IP Address in the master code with the slave IP address.

## Reading input registers with dynamic slave IP address (Modbus TCP)
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