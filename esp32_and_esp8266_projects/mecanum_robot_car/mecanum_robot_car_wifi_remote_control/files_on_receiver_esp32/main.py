from robot_car import RobotCar
import network
import espnow
from machine import Pin

# A WLAN interface must be active to send/recv
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()  # For ESP8266

# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

# Wifi Robot Car Configuration
MAX_POWER_LEVEL = 65535        # 100%
MEDIUM_POWER_LEVEL = 49151     # 75%
MIN_POWER_LEVEL = 32767        # 50%

front_enable_pins = [23, 22]
front_motor_pins = [19, 21, 25, 33]

rear_enable_pins = [26, 27]
rear_motor_pins = [16, 17, 12, 14]

robot_car = RobotCar(front_enable_pins, rear_enable_pins, front_motor_pins, rear_motor_pins, MAX_POWER_LEVEL)

# Mapping received car commands to robot_car methods
car_commands = {
    b"forward": robot_car.forward,
    b"reverse": robot_car.reverse,
    b"left": robot_car.left,
    b"right": robot_car.right,
    b"spinLeft": robot_car.spinLeft,
    b"spinRight": robot_car.spinRight,
    b"stop": robot_car.stop
}


while True:
    _, msg = esp.recv()
    if msg:  # msg == None if timeout in recv()
        if msg in car_commands:
            car_commands[msg]()
            print(msg)
        else:
            print("Unknown message!")
