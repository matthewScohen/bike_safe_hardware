import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial("/dev/ttyS0",115200)
ser.flushInput()
phone_number = '9542583115'
power_key = 6
rec_buff = ''
time_count = 0

# Supporting functions
def send_at(command,back,timeout):
    global rec_buff
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
    global rec_buff
    rec_buff = ''
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01)
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
    global rec_buff
    global phone_number
    rec_buff = ''
    print('Setting SMS mode...')
    send_at('AT+CMGF=1','OK',1)
    send_at('AT+CSCS="GSM"','OK',1)
    send_at('AT+CNMI=2,1','OK',1)
    # Read all unread messages
    answer = send_at('AT+CMGL="REC UNREAD"', 'OK', 5)
    response = rec_buff.decode()
    if 1 == answer:
        answer = 0
        if 'OK' in response:
            # Get phone number and message
            answer = 1
            try:
                phone_number = response.split('\n')[1].split(',')[2].strip('"')
                rec_message = response.split('\n')[2].strip('\r')
                print("Printing phone number: ")
                print(phone_number)
                print("Printing message: ")
                print(rec_message)
                return rec_message
            except:
                return True
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
    global rec_buff
    answer = 0
    print('Start GPS session...')
    rec_buff = ''
    send_at_GPS('AT+CGPS=1,1','OK',1)
    time.sleep(2)
    while rec_null:
        answer = send_at_GPS('AT+CGPSINFO','+CGPSINFO: ',1)
        response = rec_buff.decode()
        if 1 == answer:
            answer = 0
            #Get the location from the GPS
            lat = response.split('\n')[1].split(',')[0].strip('+CGPSINFO: ')
            long = response.split('\n')[1].split(',')[2]
            return lat, long
        
            if ',,,,,,' in rec_buff:
                print('GPS is not ready')
                rec_null = False
                time.sleep(1)
        else:
            print('error %d'%answer)
            rec_buff = ''
            send_at_GPS('AT+CGPS=0','OK',1)
            return False
        time.sleep(0.5)

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
    
    while True:
        # Clear the SMS cache
        #send_at('AT+CMGD=,2',"OK",1)
        # Receive a text from a phone to set the phone number for alerts
        msg = ReceiveShortMessage()
        
        if msg == 'Set phone number':   
            # Reply to that phone to confirm
            text_message = 'Phone number set!'
            SendShortMessage(phone_number,text_message)
            
        if msg == 'Find my bike': 
            # Get GPS location
            gps_loc = get_gps_position()
            latitude = gps_loc[0]
            longitude = gps_loc[1]
            text_message = 'Bike is located at: \n' + 'Latitude: ' + latitude + '\nLongitude: ' + longitude
            # Receive a text from a phone to request location
            msg = ReceiveShortMessage()
            # Text location to phone when requested
            SendShortMessage(phone_number,text_message)
        if msg == 'Power off':
            text_message = 'Turning off device...'
            SendShortMessage(phone_number,text_message)
            power_down(power_key)
            break
            
except :
    if ser != None:
        ser.close()
    GPIO.cleanup()


