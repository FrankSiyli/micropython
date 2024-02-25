import utime
from machine import UART

class Player:
    def __init__(self, pin_TX, pin_RX):
        self.uart = UART(1, 9600, tx=pin_TX, rx=pin_RX)
        self.cmd(0x3F)  # send initialization parameters

        self._volume = 15
        self._max_volume = 15

    def cmd(self, command, parameter=0x00):
        query = bytes([0x7E, 0xFF, 0x06, command, 0x00, 0x00, parameter, 0xEF])
        self.uart.write(query)

    def play(self, track_id=False):
        if not track_id:
            self.resume()
        elif track_id == 'next':
            self.cmd(0x01)
        elif track_id == 'prev':
            self.cmd(0x02)
        elif isinstance(track_id, int):
            self.cmd(0x03, track_id)

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

    def volume_up(self):
        self._volume += 1
        self.cmd(0x04)

    def volume_down(self):
        self._volume -= 1
        self.cmd(0x05)

    def volume(self, volume=False):
        if volume:
            self._volume = int(sorted([0, volume, self._max_volume])[1])
            print("volume", self._volume)
            self.cmd(0x06, self._volume)
        
        return self._volume

    def module_sleep(self):
        self.cmd(0x0A)

    def module_wake(self):
        self.cmd(0x0B)

    def module_reset(self):
        self.cmd(0x0C)
