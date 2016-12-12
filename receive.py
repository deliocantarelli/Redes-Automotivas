import socket
import struct
import sys
import readFile
import serial
import cryp
 
# CAN frame packing/unpacking (see `struct can_frame` in <linux/can.h>)
can_frame_fmt = "=IB3x8s"
 
send = readFile.SendManager()
send.initiate(sys.argv[1])
# create a raw socket and bind it to the given CAN interface
s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
s.bind(('vcan0',))
"""
while True:
        try:
                ser = serial.Serial('/dev/ttyUSB0', 9600)
                break
        except: pass
        try:
                ser = serial.Serial('/dev/ttyUSB1', 9600)
                break
        except: pass
        try:
                ser = serial.Serial('/dev/ttyUSB2', 9600)
                break
        except: pass
        try:
                ser = serial.Serial('/dev/ttyUSB3', 9600)
                break
        except: pass

        ser = serial.Serial('/dev/ttyUSB4', 9600)
        break
"""
#rpm = 00 | motor_temp = 01 | air_temp = 10 | speed = 11
 
while True:
        cf, addr = s.recvfrom(16)


        can_id, can_dlc, data = send.dissect_can_frame(cf)
        data = cryp.decrypt_byte(data)
        data = data[:data[0]]
        information = send.get_information_data(data)
        print()
        print('Received: can_id=%x, can_dlc=%x, data=%s', (can_id, can_dlc, data))
        print ("vehicle data")
        if(information.type_info == "rpm"):
                print("RPM: " + str(information.rpm))
                rest = information.rpm - int(information.rpm)
                rest = rest / 0.25
                byte = int(str(11111111), 2).to_bytes(1, byteorder='big') + int(str(00), 2).to_bytes(1, byteorder='big') + int(information.rpm).to_bytes(2, byteorder='big') + int(rest).to_bytes(1, byteorder='big')
                #ser.write(byte)
        elif(information.type_info == "motor_temp"):
                print("Engine coolant temperature: " + str(information.motor_temp))
                byte = int(str(11111111), 2).to_bytes(1, byteorder='big') + int('01', 2).to_bytes(1, byteorder='big') + information.motor_temp.to_bytes(2, byteorder='big') + int(0).to_bytes(1, byteorder='big')
                #ser.write(byte)
        elif(information.type_info == "air_temp"):
                print("Intake Air Temperature: " + str(information.air_temp))
                byte = int(str(11111111), 2).to_bytes(1, byteorder='big') + int(str(10), 2).to_bytes(1, byteorder='big') + information.air_temp.to_bytes(2, byteorder='big') + int(0).to_bytes(1, byteorder='big')
                #ser.write(byte)
        elif(information.type_info == "speed"):
                print("Speed: " + str(information.speed))
                byte = int(str(11111111), 2).to_bytes(1, byteorder='big') + int(str(11), 2).to_bytes(1, byteorder='big') + information.speed.to_bytes(2, byteorder='big') + int(0).to_bytes(1, byteorder='big')
                #ser.write(byte)
