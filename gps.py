import digitalio
import busio
import usb_cdc
import storage
import time
import board

""" add to boot.py file
    usb_cdc.enable(console=True, data=True) """

#ser = serial.Serial('COM8',115200)
ser = usb_cdc.data
ser.flush()

power_key = digitalio.DigitalInOut(board.D6)  # change pin for feather?
rec_buff = ''
rec_buff2 = ''
time_count = 0

def send_at(command,back,timeout):
	rec_buff = ''
	ser.write((command+'\r\n').encode())
	time.sleep(timeout)
	if ser.in_waiting():
		time.sleep(0.01 )
		rec_buff = ser.read(ser.in_waiting())
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

def get_gps_position():
	rec_null = True
	answer = 0
	print('Start GPS session...')
	rec_buff = ''
	send_at('AT+CGPS=1,1','OK',1)
	time.sleep(2)
	while rec_null:
		answer = send_at('AT+CGPSINFO','+CGPSINFO: ',1)
		if 1 == answer:
			answer = 0
			if ',,,,,,' in rec_buff:
				print('GPS is not ready')
				rec_null = False
				time.sleep(1)
		else:
			print('error %d'%answer)
			rec_buff = ''
			send_at('AT+CGPS=0','OK',1)
			return False
		time.sleep(1.5)

def power_on(power_key):
	print('SIM7600X is starting:')
    power_key.direction = digitalio.Direction.OUTPUT
    power_key.pull = digitalio.Pull.UP
    time.sleep(0.1)
	ser.flush()
	print('SIM7600X is ready')

def power_down(power_key):
	print('SIM7600X is longing off:')
	power_key.value = true
	time.sleep(3)
	power_key.value = false
	time.sleep(18)
	print('Good bye')

def gps_position_check():
    try:
        power_on(power_key)
        get_gps_position()
        power_down(power_key)
    except:
        if ser != None:
            ser.close()
        power_down(power_key)
        GPIO.cleanup()
    if ser != None:
        ser.close()
        GPIO.cleanup()	
