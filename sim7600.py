import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial("/dev/ttyS0",115200)
ser.flushInput()
phone_number = '9542583115'
text_message = 'Message received!'
power_key = 6
rec_buff = ''
rec_buff2 = ''
time_count = 0
received_msg = ''

# Supporting functions
def send_at(command,back,timeout):
	rec_buff = ''
	ser.write((command+'\r\n').encode())
	time.sleep(timeout)
	if ser.inWaiting():
		time.sleep(0.01 )
		rec_buff = ser.read(ser.inWaiting())
	if back not in rec_buff.decode():
		print(command + ' ERROR')
		print(command + ' back:\t' + rec_buff.decode())
		return 0
	else:
		print(rec_buff.decode())
		return 1

def send_at_GPS(command,back,timeout):
	rec_buff = ''
	ser.write((command+'\r\n').encode())
	time.sleep(timeout)
	if ser.inWaiting():
		time.sleep(0.01 )
		rec_buff = ser.read(ser.inWaiting())
	if rec_buff != '':
		if back not in rec_buff.decode():
			print(command + ' ERROR')
			print(command + ' back:\t' + rec_buff.decode())
			return 0
		else:
			print(rec_buff.decode())
			return 1
	else:
		print('GPS is not ready')
		return 0

def ReceiveShortMessage():
	rec_buff = ''
	print('Setting SMS mode...')
	send_at('AT+CMGF=1','OK',1)
	send_at('AT+CSCS="GSM"','OK',1)
	send_at('AT+CNMI=2,1','OK',1)
	# Read all unread messages
	answer = send_at('AT+CMGL="REC UNREAD"', 'OK', 5)
	
	if 1 == answer:
		answer = 0
		if 'OK' in rec_buff:
			answer = 1
			print(rec_buff)
	else:
		print('error%d'%answer)
		return False
	return True
    
def SendShortMessage(phone_number,text_message):
	
	print("Setting SMS mode...")
	send_at("AT+CMGF=1","OK",1)
	print("Sending Short Message")
	answer = send_at("AT+CMGS=\""+phone_number+"\"",">",2)
	if 1 == answer:
		ser.write(text_message.encode())
		ser.write(b'\x1A')
		answer = send_at('','OK',20)
		if 1 == answer:
			print('send successfully')
		else:
			print('error')
	else:
		print('error%d'%answer)


def get_gps_position():
	rec_null = True
	answer = 0
	print('Start GPS session...')
	rec_buff = ''
	send_at_GPS('AT+CGPS=1,1','OK',1)
	time.sleep(2)
	while rec_null:
		answer = send_at_GPS('AT+CGPSINFO','+CGPSINFO: ',1)
		if 1 == answer:
			answer = 0
			if ',,,,,,' in rec_buff:
				print('GPS is not ready')
				rec_null = False
				time.sleep(1)
		else:
			print('error %d'%answer)
			rec_buff = ''
			send_at_GPS('AT+CGPS=0','OK',1)
			return False
		time.sleep(1.5)

def power_on(power_key):
	print('SIM7600X is starting:')
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(power_key,GPIO.OUT)
	time.sleep(0.1)
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(2)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(20)
	ser.flushInput()
	print('SIM7600X is ready')

def power_down(power_key):
	print('SIM7600X is logging off:')
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(3)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(18)
	print('Good bye')


# Main function
try:
	power_on(power_key)
	
	# Clear the SMS cache
	#send_at('AT+CMGD=,2',"OK",1)
	# Receive a text from a phone
	ReceiveShortMessage()
	
	# Reply to that phone
	SendShortMessage(phone_number,text_message)
	
	# Get GPS location
	get_gps_position()
	
	power_down(power_key)
except :
	if ser != None:
		ser.close()
	GPIO.cleanup()
