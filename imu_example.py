import time
import board
import digitalio
import busio
import array as arr
import imu as imu

lock_mode = True
alert = False

#setup gpio pin to inform raspi
movement = digitalio.DigitalInOut(board.D5)
movement.direction = digitalio.Direction.OUTPUT
movement.value = False

# To use default I2C bus (most boards)
i2c = busio.I2C(board.SCL, board.SDA)

imu.imu_setup(i2c)

while(1):
    if lock_mode and not alert:
        #first reading
        a1 = imu.read_xyz(i2c)
        time.sleep(1)
        #second reading
        a2 = imu.read_xyz(i2c)
        if imu.sig_move(a1,a2):
            print("1st MOVEMENT")
            time.sleep(2)  #wait 2 minutes (120seconds) and see if it's still being moved
            a3 = imu.read_xyz(i2c)
            if imu.sig_move(a2,a3):
                print("2nd MOVEMENT")
                movement.value = True
                alert = True #notify user of alert only once until new lock mode is initiated
        time.sleep(1)



