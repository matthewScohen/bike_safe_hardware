import time
import board
import digitalio
import busio
import array as arr

#define constants
I2C_ADDR = 0x53
DEVID_REG = 0x00
PWR_CTRL_REG = 0x2D
DATAX0_REG = 0x32
DATAX1_REG = 0x33
DATAY0_REG = 0x34
DATAY1_REG = 0x35
DATAZ0_REG = 0x36
DATAZ1_REG = 0x37
DEVID = 0xE5
SENSITIVITY_2G = 1.0 / 256
EARTH_GRAVITY = 9.80665

#function definitions
def read_reg(i2c,reg):
    i2c.writeto(I2C_ADDR, bytes([reg]))
    result = bytearray(1)
    i2c.readfrom_into(I2C_ADDR, result)
    return result

def write_reg(i2c,reg,value):
    i2c.writeto(I2C_ADDR,bytes([reg,value]))
    print("bytes:", int.from_bytes(bytes([reg,value]),"big"))

def imu_setup(i2c):
    print("starting imu")

    while not i2c.try_lock():
        pass

    print("I2C addresses found:",[hex(device_address) for device_address in i2c.scan()])

    #read devid
    data = read_reg(i2c,DEVID_REG)
    print("device id:",int.from_bytes(data,"big"))

    #read pwr control
    data = read_reg(i2c,PWR_CTRL_REG)
    pwr_data = int.from_bytes(data,"big")
    print("power control:",pwr_data)

    #change measure bit
    measure_set = pwr_data | (1 << 3)
    write_reg(i2c,PWR_CTRL_REG,measure_set)

    #read pwr control again
    data = read_reg(i2c,PWR_CTRL_REG)
    pwr_data = int.from_bytes(data,"big")
    print("new power control:",pwr_data)

    time.sleep(2)


def read_coordinate(i2c,reg1,reg0):
    data0 = read_reg(i2c,reg0)
    data1 = read_reg(i2c,reg1)
    data = data1 + data0
    return int.from_bytes(data,"big")

def read_xyz(i2c):
    x = read_coordinate(i2c,DATAX1_REG,DATAX0_REG)
    y = read_coordinate(i2c,DATAY1_REG,DATAY0_REG)
    z = read_coordinate(i2c,DATAZ1_REG,DATAZ0_REG)
    print("x: ",x,"y: ",y,"z: ",z)
    a = arr.array('i',[x,y,z])
    return a

def sig_move(a1,a2):
    if abs(a2[2]- a1[2]) > 30 and abs(a2[1]- a1[1]) > 30 and abs(a2[0] - a1[0]) > 30:
        return True
    else:
        return False    
