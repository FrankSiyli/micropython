from dfplayer import Player
from time import sleep

music = Player(pin_TX=17, pin_RX=16)

print("set volume")
music.volume(10)

# Loop through tracks and play each for 30 seconds
for track_id in range(1, 255):  # Assuming maximum number of tracks is 255
    print("Playing track:", track_id)
    music.play(track_id)
    sleep(30)  # Play each track for 30 seconds

music.stop()
print("All tracks played.")
