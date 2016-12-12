import socket
import struct
import sys
import readFile
 
#sudo modprobe vcan
#Create a vcan network interface with a specific name
#sudo ip link add dev vcan0 type vcan
#sudo ip link set vcan0 up
#python3.5 send.py redes1.csv


# CAN frame packing/unpacking (see `struct can_frame` in <linux/can.h>)
can_frame_fmt = "=IB3x8s"
 
 
send = readFile.SendManager()
send.initiate(sys.argv[1])
# create a raw socket and bind it to the given CAN interface
s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
s.bind(('vcan0',))
 
packets = send.get_packet()
while packets != False:
        try:
                if packets[0] != None:
                        s.send(packets[0])
                if packets[1] != None:
                        s.send(packets[1])
                if packets[2] != None:
                        s.send(packets[2])
                if packets[3] != None:
                        s.send(packets[3])
        except socket.error:
                print('Error sending CAN frame')

        packets = send.get_packet()

print("Operation Finished")
