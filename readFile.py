import datetime
from datetime import timedelta
import re
import inspect
import binascii
import struct
import cryp
 
# CAN frame packing/unpacking (see `struct can_frame` in <linux/can.h>)
can_frame_fmt = "=IB3x8s"
CONSTANT_PID_RPM = 0x0C
CONSTANT_PID_INTAKE_AIR = 0x0F
CONSTANT_PID_ENGINE_COOLANT = 0x05
CONSTANT_PID_VEHICLE_SPEED = 0x0D

def getTimeMil(date_time):
	time = datetime.datetime(1900, 1, 1, 0,0,0)
	time_delta = date_time - time
	return time_delta.total_seconds() * 1000.0


class Information:
	time = datetime.datetime.now()	#1
	type_info = None
	motor_temp = 0		#5
	rpm = 0				#9
	speed = 0			#10
	air_temp = 0		#12


class SendManager:
	fileName = ''
	f = None

	start = getTimeMil(datetime.datetime.now())
	start_file = getTimeMil(datetime.datetime(1900, 1, 1, 0,0,0))

	def setFileStart(self, date_time):
		start_file = getTimeMil(date_time)

	def initiate(self, name):
		self.fileName = name
		self.f = open(name, 'r')
		
		p = re.compile('\,')
		line = self.f.readline()
		line = self.f.readline()
		array = p.split(line)
		time_str = array[0]
		time = datetime.datetime.strptime(time_str, "%H:%M:%S.%f")
		self.start_file = getTimeMil(time)
		print(time, self.start_file)


	def readFile(self):

		p = re.compile('\,')

		line = self.f.readline()
		if line != '':
			array = p.split(line)

			information = Information()


			time_str = array[0]
			time = datetime.datetime.strptime(time_str, "%H:%M:%S.%f")

			motor_temp = array[4].strip("\"")
			rpm = array[8].strip("\"")
			speed = array[9].strip("\"")
			air_temp = array[11].strip("\"")



			if motor_temp != '' or rpm != '' or speed != '' or air_temp != '':

				information.time = time
				information.motor_temp = motor_temp
				information.rpm = rpm
				information.speed = speed
				information.air_temp = air_temp



				print (time, getTimeMil(time), self.start_file)
				return information
			return False
		else:
			return True

	def canSendNext(self, file_time):
		now = getTimeMil(datetime.datetime.now())
		now = now - self.start

		next_time = getTimeMil(file_time)
		next = next_time - self.start_file

		#print (next_time, self.start_file)

		if now >= next:
			return True
		else:
			return False


#1- engine coolant temperature
#2- engine rpm
#3- vehicle speed
#4- intake air temperature
#4 7E80641010007E100	01 intake air
#1 7E80341057F			05 engine coolant
#2 7E804410C0EFE		0C RPM
#3 7E803410D00			0D vehicle speed


#FORMAT
# 07E0 (SIZE) 41
	def fillWithZero(self, string, size):
		return string.rjust(size, '0')

	def strBi_to_intDec(self, string):
		string = int(string, 2)
		return string

	def strHex_to_intDec(self, string):
		string = binascii.hexlify(string)
		string = string.decode(encoding='UTF-8')
		string = int(string, 16)
		return string


	def mountPackage(self, size):
		#CAN identifier response (07E0 + 8)
		code = 0x7E8
		code = str("0"+'{:X}').format(code)
		#number of bytes
		size = size
		size = str("0"+'{:X}').format(size)
		#response mode (1 + 40)
		response_mode = 0x41
		response_mode = str('{:X}').format(response_mode)

		return code + size + response_mode

	def mountEngineCoolant(self, value):
		package = self.mountPackage(3)
		value = int(value)

		pid = str("0"+'{:X}').format(CONSTANT_PID_ENGINE_COOLANT)

		#we are mounting, so it's the oposite
		value = value + 40

		#format to hex
		value = str('{:X}').format(value)

		#fill the string with zeros
		value = self.fillWithZero(value, 2)

		#mount package
		package_string = package + pid + value

		return binascii.unhexlify(package_string)


	def mountRPM(self, value):
		package = self.mountPackage(4)
		value = float(value)

		pid = str("0"+'{:X}').format(CONSTANT_PID_RPM)

		#we are mounting, so we have to make a few steps
		#this steps needs clarification
		rest = value - (int(value))
		rest_bytes = ""
		if rest == 0.75:
			rest_bytes = "11"
		elif rest == 0.5:
			rest_bytes = "10"
		elif rest == 0.25:
			rest_bytes = "01"
		elif rest == 0.0:
			rest_bytes = "00"

		#mount the bytes from value
		B = (int(value) % 64)
		B = str('{:b}').format(B)
		B = self.fillWithZero(B, 6)
		B = B + rest_bytes
		B = int(B, 2)

		A = int(int(value) / 64)
		A = str('{:b}').format(A)
		A = self.fillWithZero(A, 8)
		A = int(A, 2)

		#format to hex
		value = str('{:X}{:X}').format(A, B)
		value = value

		#fill the string with zeros
		value = self.fillWithZero(value, 4)

		#mount package
		package_string = package + pid + value
		return binascii.unhexlify(package_string)

	def mountVehicleSpeed(self, value):
		package = self.mountPackage(3)
		value = int(value)

		pid = str("0"+'{:X}').format(CONSTANT_PID_VEHICLE_SPEED)

		#this one does not need to modify the value
		value = str('{:X}').format(value)

		#fill the string with zeros
		value = self.fillWithZero(value, 2)

		#mount package
		package_string = package + pid + value
		return binascii.unhexlify(package_string)

	def mountIntakeAirTemperature(self, value):
		package = self.mountPackage(3)
		value = int(value)

		pid = str("0"+'{:X}').format(CONSTANT_PID_INTAKE_AIR)

		#the temperature is stored as 40 more
		value = value + 40

		#format to hex
		value = str('{:X}').format(value)

		#fill the string with zeros
		value = self.fillWithZero(value, 2)

		#mount package
		package_string = package + pid + value
		return binascii.unhexlify(package_string)


	class Package:
		can_id = ""
		size = 0
		mode = ""
		pid = 0x0
		value = ""

	def unmountPackage(self, package):
		pack = self.Package()

		pack.can_id = package[:4]

		#get in hex
		size = package[4:6]
		size = int(size, 16)

		pack.mode = package[6:8]

		pid = package[8:10]
		pack.pid = int(pid, 16)

		pack.value = package[10:]

		return pack

	def getValueRPM(self, value):
		A = value[0]

		B = value[1]

		result = (A*256 + B) / 4
		return result


	def getValueIntakeAirTemperature(self, value):
		#subtract 40 from the value
		value = value[0] - 40
		return value

	def getValueEngineCoolant(self, value):
		#subtract 40 from the value
		value = value[0] - 40
		return value

	def getValueVehicleSpeed(self, value):
		#as simple as that, there is no need to change anything
		return value[0]

	def createPacketFromInformation(self, information):
		packets = [{}, {}, {}, {}]
		if information.motor_temp != "":
			packets[0] = self.mountEngineCoolant(information.motor_temp)
		else:
			packets[0] = None
		if information.rpm != "":
			packets[1] = self.mountRPM(information.rpm)
		else:
			packets[1] = None
		if information.speed != "":
			packets[2] = self.mountVehicleSpeed(information.speed)
		else:
			packets[2] = None
		if information.air_temp != "":
			packets[3] = self.mountIntakeAirTemperature(information.air_temp)
		else:
			packets[3] = None

		return packets

	def build_can_frame(self, packet):
		can_id = self.strHex_to_intDec(packet[:2])
		can_dlc = int(packet[2])
		data = packet[3:]
		#data = data.ljust(8, b'\x00')
		return struct.pack(can_frame_fmt, can_id, can_dlc, data)

	def dissect_can_frame(self, frame):
		can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
		data = data[:can_dlc]
		return (can_id, can_dlc, data)

	def get_information_data(self, data):
		information = Information()
		mode = data[0]
		pid = data[1]
		value = data[2:]
		data_list = []
		for ch in value:
			data_list.append(ch)
		value = data_list
		if pid == CONSTANT_PID_RPM:
			value = self.getValueRPM(value)
			information.rpm = value;
			information.type_info = "rpm"
		elif pid == CONSTANT_PID_INTAKE_AIR:
			value = self.getValueIntakeAirTemperature(value)
			information.air_temp = value;
			information.type_info = "air_temp"
		elif pid == CONSTANT_PID_ENGINE_COOLANT:
			value = self.getValueEngineCoolant(value)
			information.motor_temp = value
			information.type_info = "motor_temp"
		elif pid == CONSTANT_PID_VEHICLE_SPEED:
			value = self.getValueVehicleSpeed(value)
			information.speed = value
			information.type_info = "speed"

		return information

#code
	def get_packet(self):
		information = self.readFile()
		while information != True:
			if isinstance(information, Information):
				while not self.canSendNext(information.time): pass

				#after we can send...
				packets = self.createPacketFromInformation(information)
				if packets[0] != None:
					packet = cryp.crypt_byte(packets[0][3], packets[0])
					packets[0] = self.build_can_frame(packet)
				if packets[1] != None:
					packet = cryp.crypt_byte(packets[1][3], packets[1])
					packets[1] = self.build_can_frame(packet)
				if packets[2] != None:
					packet = cryp.crypt_byte(packets[2][3], packets[2])
					packets[2] = self.build_can_frame(packet)
				if packets[3] != None:
					packet = cryp.crypt_byte(packets[3][3], packets[3])
					packets[3] = self.build_can_frame(packet)
				
				return packets
			information = self.readFile()
		return False
