from microdot_asyncio import Microdot, Response, send_file
from microdot_asyncio_websocket import with_websocket
from microdot_utemplate import render_template
from robot_car import RobotCar
from machine import Pin
from machine import time_pulse_us
import time
import ujson  # Import ujson for JSON serialization

app = Microdot()
Response.default_content_type = "text/html"

# Wifi Robot Car Configuration
MAX_POWER_LEVEL = 65535  # 100%
MEDIUM_POWER_LEVEL = 49151  # 75%
MIN_POWER_LEVEL = 32767  # 50%

front_enable_pins = [23, 22]
front_motor_pins = [19, 21, 25, 33]

rear_enable_pins = [26, 27]
rear_motor_pins = [16, 17, 12, 14]

robot_car = RobotCar(
    front_enable_pins,
    rear_enable_pins,
    front_motor_pins,
    rear_motor_pins,
    MEDIUM_POWER_LEVEL,
)

car_commands = {
    "forward": robot_car.forward,
    "reverse": robot_car.reverse,
    "left": robot_car.left,
    "right": robot_car.right,
    "spinLeft": robot_car.spinLeft,
    "spinRight": robot_car.spinRight,
    "stop": robot_car.stop,
}

speed_commands = {
    "slow-speed": MIN_POWER_LEVEL,
    "normal-speed": MEDIUM_POWER_LEVEL,
    "fast-speed": MAX_POWER_LEVEL,
}

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


# App Route
@app.route("/")
async def index(request):
    return render_template("index.html")


@app.route("/ws")
@with_websocket
async def executeCarCommands(request, ws):
    while True:
        websocket_message = await ws.receive()
        print(f"receive websocket message : {websocket_message}")

        if "speed" in websocket_message:
            new_speed = speed_commands.get(websocket_message)
            robot_car.set_speed(new_speed)
        else:
            command = car_commands.get(websocket_message)
            command()

        # Send ultrasonic sensor data to the WebSocket client
        distance = get_distance_cm()
        await ws.send(
            ujson.dumps({"distance": distance})
        )  # Serialize distance data to JSON


@app.route("/shutdown")
async def shutdown(request):
    request.app.shutdown()
    return "The server is shutting down..."


@app.route("/static/<path:path>")
def static(request, path):
    if ".." in path:
        # directory traversal is not allowed
        return "Not found", 404
    return send_file("static/" + path)


if __name__ == "__main__":
    try:
        app.run()
    except KeyboardInterrupt:
        robot_car.cleanUp()
