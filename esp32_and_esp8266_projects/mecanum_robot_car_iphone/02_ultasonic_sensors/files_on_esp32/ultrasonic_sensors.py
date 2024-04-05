from machine import Pin
import time

TRIG_PIN_NUM = 15
ECHO_PIN_NUM = 13

trig_pin = Pin(TRIG_PIN_NUM, Pin.OUT)
echo_pin = Pin(ECHO_PIN_NUM, Pin.IN)

def get_distance_cm():
    trig_pin.value(0)
    time.sleep_us(5)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)
    duration = time_pulse_us(echo_pin, 1)
    distance_cm = duration / 58
    return int(distance_cm)
