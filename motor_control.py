import board
import microcontroller
import pwmio

def setup_motor_pins():
    motor1 = pwmio.PWMOut(board.A0, frequency=5000, duty_cycle=0)
    motor2 = pwmio.PWMOut(board.A1, frequency=5000, duty_cycle=0)
    return motor1, motor2

def vibrate_motor(motor, strength):
    """
    side: The pin object the motor is connected to
    strength: A float describing the strength at which to vibrate the motor
    """
    if strength == 0:
        motor.duty_cycle = 0
    else:
        strength = strength / 2 + 50
        motor.duty_cycle = int(strength/100 * 65535 -1)
    print(f"{strength}=")
    print(f"{motor.duty_cycle=}")
    



