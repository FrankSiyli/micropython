from dfplayer import Player
from time import sleep

music = Player(pin_TX=17, pin_RX=16, pin_busy=5, button_volume_up=13, button_volume_down=15 , button_song_start=2)


for track_id in range(1, 255):
    music.volume(15)

    music.play(track_id)

    while music.is_busy():
        sleep(1)

    music.play('next')

    while music.is_busy():
        sleep(1)

music.stop()
