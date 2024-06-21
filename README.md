# Full-Stack-IoT

This project includes the development of an IoT system. Initial configurations include the understanding of ModBus protocol. We will be writing ModBus codes which will allows us to communicate between two ESP-WROOM-32 controllers.

## Writing into a single holding register
[writeSingleHoldingRegisterMaster.ino](./ModBusRTU/Write%20Single%20Holding%20Register/writeSingleHoldingRegisterMaster/writeSingleHoldingRegisterMaster.ino)
[writeSingleHoldingRegisterSlave.ino](./ModBusRTU/Write%20Single%20Holding%20Register/writeSingleHoldingRegisterSlave/writeSingleHoldingRegisterSlave.ino)

This code allows you to write a value into a single holding register in the slave. The protocol used is ModBus RTU, which uses the serial commuincation on the Serial2 line.

Please note that the Tx and Rx pins are 12 and 13 respectively on both the master and slave. These pins are specified in the Serial2.begin() function. The Tx pin of master is connected to the Rx pin of the slave, and vice versa.

The basic description of code files will be updated in the ReadMe.
Thank you!