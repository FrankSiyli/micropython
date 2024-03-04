import machine
from machine import Pin, I2C, ADC
import utime
from utime import sleep
import json
import ssd1306

i2c = I2C(0, sda=Pin(4), scl=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

adc = ADC(Pin(34))

DFPLAYER_UART = machine.UART(1, baudrate=9600, tx=17, rx=16)
DFPLAYER_BUSY = machine.Pin(5, machine.Pin.IN)

max_volume = 30
volume = 0

button_volume_up = Pin(13, Pin.IN, Pin.PULL_UP)
button_volume_down = Pin(15, Pin.IN, Pin.PULL_UP)
button_next_song = Pin(2, Pin.IN, Pin.PULL_UP)

last_volume_up_press = 0
last_volume_down_press = 0
last_next_song_press = 0
debounce_delay = 200


def update_display(volume, track_id, voltage):
    oled.fill(0)
    oled.text("Volume: {}".format(volume), 0, 20)
    oled.text("Track: {}".format(track_id), 0, 40)
    if voltage >= 3.3:
        oled.fill_rect(105, 0, 25, 10, 1)
        oled.fill_rect(105, 0, 1, 10, 1)
        oled.fill_rect(101, 3, 4, 4, 1)
    elif voltage >= 3.1:
        oled.fill_rect(117, 0, 15, 10, 1)
        oled.fill_rect(105, 0, 25, 1, 1)
        oled.fill_rect(105, 10, 25, 1, 1)
        oled.fill_rect(105, 0, 1, 10, 1)
        oled.fill_rect(101, 3, 4, 4, 1)
    else:
        oled.fill_rect(127, 0, 1, 10, 1)
        oled.fill_rect(105, 0, 25, 1, 1)
        oled.fill_rect(105, 10, 25, 1, 1)
        oled.fill_rect(105, 0, 1, 10, 1)
        oled.fill_rect(101, 3, 4, 4, 1)

    oled.show()


def read_battery_voltage():
    adc.read()
    utime.sleep_ms(50)
    adc_value = adc.read()
    voltage = adc_value * (3.3 / 4095)
    return voltage


def send_command(command, parameter=0):
    query = bytes([0x7E, 0xFF, 0x06, command, 0x00, 0x00, parameter, 0xEF])
    DFPLAYER_UART.write(query)


def play_mp3(track_id):
    send_command(0x12, track_id)


def volume_up(pin):
    global volume, last_volume_up_press
    current_time = utime.ticks_ms()
    if current_time - last_volume_up_press > debounce_delay:
        last_volume_up_press = current_time
        volume = min(volume + 1, max_volume)
        send_command(0x04)
        save_volume(volume)
        update_display(volume, track_id, battery_voltage)


def volume_down(pin):
    global volume, last_volume_down_press
    current_time = utime.ticks_ms()
    if current_time - last_volume_down_press > debounce_delay:
        last_volume_down_press = current_time
        volume = max(volume - 1, 0)
        send_command(0x05)
        save_volume(volume)
        update_display(volume, track_id, battery_voltage)


def next_song(pin):
    global last_next_song_press, track_id
    current_time = utime.ticks_ms()
    if current_time - last_next_song_press > debounce_delay:
        last_next_song_press = current_time
        next_track_id = track_id + 1
        if next_track_id > 10:
            next_track_id = 1
        save_track_id(next_track_id)
        send_command(0x16)
        utime.sleep_ms(100)
        machine.reset()


def save_track_id(track_id):
    try:
        with open("track_id.json", "w") as f:
            json.dump({"track_id": track_id}, f)
    except Exception as e:
        pass


def load_track_id():
    try:
        with open("track_id.json", "r") as f:
            data = json.load(f)
            track_id = data.get("track_id", 1)
            if isinstance(track_id, int):
                return track_id
            else:
                return 1
    except Exception as e:
        return 1


def save_volume(volume):
    try:
        with open("volume.json", "w") as f:
            json.dump({"volume": volume}, f)
    except Exception as e:
        pass


def load_volume():
    try:
        with open("volume.json", "r") as f:
            data = json.load(f)
            volume = data.get("volume", 15)
            if isinstance(volume, int):
                return volume
            else:
                return 15
    except Exception as e:
        return 15


def main():
    global volume, track_id, battery_voltage
    battery_voltage = read_battery_voltage()
    volume = load_volume()
    send_command(0x06, volume)
    track_id = load_track_id()
    play_mp3(track_id)
    update_display(volume, track_id, battery_voltage)
    start_time = utime.time()  # Move the start_time initialization outside the loop
    while True:  # Keep running until stopped externally
        if utime.time() - start_time >= 20:  # Check if 20 seconds have elapsed
            break  # Exit the loop if 20 seconds have elapsed
        utime.sleep(1)  # Sleep for 1 second before checking again

    send_command(0x16)  # stop playback
    oled.fill(0)
    oled.show()


# Initialize pins and interrupts
button_volume_up.irq(trigger=Pin.IRQ_FALLING, handler=volume_up)
button_volume_down.irq(trigger=Pin.IRQ_FALLING, handler=volume_down)
button_next_song.irq(trigger=Pin.IRQ_FALLING, handler=next_song)

if __name__ == "__main__":
    main()
