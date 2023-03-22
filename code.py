import board
import microcontroller
import time
import board
import digitalio
import busio
import array as arr
import imu as imu

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_airlift.esp32 import ESP32

from motor_control import setup_motor_pins, vibrate_motor

motor1, motor2 = setup_motor_pins()
esp32 = ESP32(  
    reset=board.D12,
    gpio0=board.D10,
    busy=board.D11,
    chip_select=board.D13,
    tx=board.TX,
    rx=board.RX,
)
adapter = esp32.start_bluetooth()
ble = BLERadio(adapter)
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

lock_mode = False
alert = False

#setup gpio pin to inform raspi
movement = digitalio.DigitalInOut(board.D5)
movement.direction = digitalio.Direction.OUTPUT
movement.value = False

# To use default I2C bus (most boards)
i2c = busio.I2C(board.SCL, board.SDA)

imu.imu_setup(i2c)


print(f"Saved phone number : {microcontroller.nvm[0:10]}") # https://docs.circuitpython.org/en/latest/shared-bindings/nvm/index.html
while True:
    lock_mode = False
    ble.start_advertising(advertisement)
    print("waiting to connect")
    while not ble.connected:
        pass
    print("connected: trying to read input")
    while ble.connected:
        # Returns b'' if nothing was read.
        input_byte_array = uart.read(10)
        input_string = input_byte_array.decode() 
        if(len(input_string) == 10):
            if input_string[3:10] == "5550000":
                strength = int(input_string[0:3])
                print(f"Turn on left motor at strength: {strength}")
                vibrate_motor(motor1, strength)
            elif input_string[3:10] == "5551111":
                strength = int(input_string[0:3])
                print(f"Turn on right motor at strength: {strength}")
                vibrate_motor(motor2, strength)
            elif input_string[] == "55550001":
                lock_mode = True
                print("Set lock mode")
                alert = False
            else:
                print(f"Saving phone number")
                microcontroller.nvm[0:10] = input_byte_array
    while lock_mode and not alert and not ble.connected:  #end lock mode when phone comes back in range
        #first reading
        a1 = imu.read_xyz(i2c)
        time.sleep(1)
        #second reading
        a2 = imu.read_xyz(i2c)
        if imu.sig_move(a1,a2):
            print("1st MOVEMENT")
            time.sleep(120)  #wait 2 minutes (120seconds) and see if it's still being moved
            a3 = imu.read_xyz(i2c)
            if imu.sig_move(a2,a3):
                print("2nd MOVEMENT")
                movement.value = True
                time.sleep(1)  #one second gpio pulse
                movement.value = False
                alert = True #notify user of alert only once until new lock mode is initiated
        time.sleep(1)
    #tell app lock mode is no longer set? (in case of mistakenly coming back in range)
