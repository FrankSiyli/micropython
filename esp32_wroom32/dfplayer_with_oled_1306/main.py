import machine
from machine import Pin, I2C
import utime
from utime import sleep
import json
import ssd1306

i2c = I2C(0, sda=Pin(4), scl=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


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

def update_display():
    oled.fill(0)  
    oled.text("Volume: {}".format(volume), 0, 0)
    oled.text("Track: {}".format(track_id), 0, 20)
    oled.show()

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
        update_display() 

def volume_down(pin):
    global volume, last_volume_down_press
    current_time = utime.ticks_ms()
    if current_time - last_volume_down_press > debounce_delay:
        last_volume_down_press = current_time
        volume = max(volume - 1, 0)
        send_command(0x05)
        save_volume(volume)
        update_display()

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
        with open("track_id.json", 'w') as f:
            json.dump({'track_id': track_id}, f)
    except Exception as e:
        pass
            
def load_track_id():
    try:
        with open("track_id.json", 'r') as f:
            data = json.load(f)
            track_id = data.get('track_id', 1)
            if isinstance(track_id, int):
                return track_id
            else:
                return 1  
    except Exception as e:
        return 1  

def save_volume(volume):
    try:
        with open("volume.json", 'w') as f:
            json.dump({'volume': volume}, f)
    except Exception as e:
        pass

def load_volume():
    try:
        with open("volume.json", 'r') as f:
            data = json.load(f)
            volume = data.get('volume', 15) 
            if isinstance(volume, int): 
                return volume
            else:
                return 15
    except Exception as e:
        return 15  
    
def main():
    global volume, track_id
    volume = load_volume()
    send_command(0x06, volume)
    track_id = load_track_id()
    play_mp3(track_id)
    
    update_display()
   
    start_time = utime.time()
    while utime.time() - start_time < 30:
        pass
    
    send_command(0x16)  #stop playback
    oled.fill(0)  
    oled.show()

# Initialize pins and interrupts
button_volume_up.irq(trigger=Pin.IRQ_FALLING, handler=volume_up)
button_volume_down.irq(trigger=Pin.IRQ_FALLING, handler=volume_down)
button_next_song.irq(trigger=Pin.IRQ_FALLING, handler=next_song)

if __name__ == "__main__":
    main()
