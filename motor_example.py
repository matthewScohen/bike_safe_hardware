import board
import microcontroller
import time
import asyncio

from digitalio import DigitalInOut, Direction
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_airlift.esp32 import ESP32

from motor_control import setup_motor_pins, vibrate_motor

motor1, motor2 = setup_motor_pins()
vibrate_motor(motor1, 50)
vibrate_motor(motor2, 25)

while True:
    pass