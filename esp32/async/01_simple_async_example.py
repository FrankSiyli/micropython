from machine import Pin
import uasyncio

led = Pin(25, Pin.OUT)
btn = Pin(27, Pin.IN, Pin.PULL_UP)

led_state = False


async def blink(delay):
    global led_state
    while True:
        led_state = not led_state
        led.value(led_state)
        await uasyncio.sleep(delay)


async def wait_button():
    btn_prev = btn.value()
    while (btn.value() == 1) or (btn.value() == btn_prev):
        btn_prev = btn.value()
        await uasyncio.sleep(0.2)


async def main():
    uasyncio.create_task(blink(0.5))

    while True:
        await wait_button()
        print("yeha")


uasyncio.run(main())
