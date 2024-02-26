import utime
from machine import UART
from machine import Pin


class Player:

    def __init__(self, pin_TX, pin_RX, pin_busy, button_volume_up, button_volume_down):
        self.uart = UART(1, 9600, tx=pin_TX, rx=pin_RX)
        self.pin_busy = Pin( pin_busy, Pin.IN)

        self.cmd(0x3F)  

        self._volume = 15
        self._max_volume = 15
        
        self.button_volume_up = Pin(button_volume_up, Pin.IN, Pin.PULL_UP)
        self.button_volume_down = Pin(button_volume_down, Pin.IN, Pin.PULL_UP)

        self.button_volume_up.irq(trigger=Pin.IRQ_FALLING, handler=self.volume_up)
        self.button_volume_down.irq(trigger=Pin.IRQ_FALLING, handler=self.volume_down)
        
        self.last_volume_up_press = 0
        self.last_volume_down_press = 0
        self.debounce_delay = 500
        
    def volume(self, volume=False):
        if volume:
            self._volume = int(sorted([0, volume, self._max_volume])[1])
            print("volume", self._volume)
            self.cmd(0x06, self._volume)

        return self._volume    

    def volume_up(self, pin):
        current_time = utime.ticks_ms()
        if current_time - self.last_volume_up_press > self.debounce_delay:
            self.last_volume_up_press = current_time
            self._volume = min(self._volume + 1, self._max_volume)
            self.cmd(0x04)

    def volume_down(self, pin):
        current_time = utime.ticks_ms()
        if current_time - self.last_volume_down_press > self.debounce_delay:
            self.last_volume_down_press = current_time
            self._volume = max(self._volume - 1, 0)
            self.cmd(0x05) 

    def cmd(self, command, parameter=0x00):
        query = bytes([0x7E, 0xFF, 0x06, command, 0x00, 0x00, parameter, 0xEF])
        self.uart.write(query)

    def play(self, track_id=1):
        if not track_id:
            self.resume()
        elif track_id == 'next':
            self.cmd(0x01)
        elif track_id == 'prev':
            self.cmd(0x02)
        elif isinstance(track_id, int):
            self.cmd(0x03, track_id)
            
    def is_busy(self):
        return self.pin_busy.value() == 0      

    def pause(self):
        self.cmd(0x0E)

    def resume(self):
        self.cmd(0x0D)

    def stop(self):
        self.cmd(0x16)

    def loop_track(self, track_id):
        self.cmd(0x08, track_id)

    def loop(self):
        self.cmd(0x19)

    def loop_disable(self):
        self.cmd(0x19, 0x01)

    def module_sleep(self):
        self.cmd(0x0A)

    def module_wake(self):
        self.cmd(0x0B)

    def module_reset(self):
        self.cmd(0x0C)
