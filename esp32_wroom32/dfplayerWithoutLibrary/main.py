import machine
import utime



DFPLAYER_UART = machine.UART(1, baudrate=9600, tx=17, rx=16)
DFPLAYER_BUSY = machine.Pin(5, machine.Pin.IN)

def send_command(command, parameter=0):
    query = bytes([0x7E, 0xFF, 0x06, command, 0x00, 0x00, parameter, 0xEF])
    DFPLAYER_UART.write(query)



def play_mp3(track_id):
    send_command(0x03, track_id)  
    

def main():
    track_id = 1 
    play_mp3(track_id)

if __name__ == "__main__":
    main()
