import board
import microcontroller

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


print(f"Saved phone number : {microcontroller.nvm[0:10]}") # https://docs.circuitpython.org/en/latest/shared-bindings/nvm/index.html
while True:
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
            else:
                print(f"Saving phone number")
                microcontroller.nvm[0:10] = input_byte_array