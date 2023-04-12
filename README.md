# bike_safe_hardware
Repository for all code for the microcontroller(s) for the bike safe project.

The Adafruit Feather microcontroller and Bluefruit nRF52 bluetooth module are configured here. We use CircuitPython to utilize the bluetooth module for recieving from the android app. The ADXL343 IMU is also configured here. The Adafruit feather communicates with the ADXL343 via I2C to read accelerometer data.

The Raspberry Pi and SIM7600 system code are configured here. We use Python to allow the Raspberry PI to send/receive AT commands to the GPS/SMS module.

The files `code.py` and `motor_control.py` should be uploaded to the Adafruit feather (which should be loaded with CircuitPython) and you should copy the Adafruit bluefruit module to the lib folder on the Feather. You can download the bluefruit module as part of the [Adafruit CircuitPython Library Bundle](https://circuitpython.org/libraries) Additionally,`sim7600.py` should be saved onto the Raspberry Pi and configured to run at startup.
![image](https://user-images.githubusercontent.com/58480140/227580137-ba8b6314-44e6-488d-ac7f-6507bbde0c08.png)

