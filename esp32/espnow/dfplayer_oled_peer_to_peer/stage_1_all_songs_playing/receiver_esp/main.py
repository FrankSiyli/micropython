import network
import espnow
import machine
from machine import Pin
import utime
from utime import sleep

DFPLAYER_UART = machine.UART(1, baudrate=9600, tx=17, rx=16)


sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()

esp = espnow.ESPNow()
esp.active(True)


def send_command(command, parameter=0):
    query = bytes([0x7E, 0xFF, 0x06, command, 0x00, 0x00, parameter, 0xEF])
    DFPLAYER_UART.write(query)


def main():
    send_command(0x0D)
    send_command(0x16)


while True:
    _, msg = esp.recv()
    if msg:
        if msg == b"makeItHappen":
            print("Message received:", msg)
            main()
        else:
            print("Unknown message!")


if __name__ == "__main__":
    main()


# my ESPs:
# sender    08:3A:8D:9A:41:D0 b'\x08:\x8d\x9aA\xd0'
# receiver  08:3A:8D:9A:48:30 b'\x08:\x8d\x9aH0'
