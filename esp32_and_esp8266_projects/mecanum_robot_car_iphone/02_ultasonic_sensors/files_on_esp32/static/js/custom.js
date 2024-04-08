var targetUrl = `ws://${location.host}/ws`;
var websocket;

function initializeSocket() {
  console.log("Opening WebSocket connection to ESP32 MicroPython Server...");
  websocket = new WebSocket(targetUrl);
  websocket.onopen = onOpen;
  websocket.onclose = onClose;
  websocket.onmessage = onMessage;
}

function onLoad() {
  initializeSocket();
  setDefaultSpeed();
    //  setInterval(updateDistanceValue, 1000);

}

function onOpen(event) {
  console.log("Starting connection to WebSocket server..");
}

function onClose(event) {
  console.log("Closing connection to server..");
  setTimeout(initializeSocket, 2000);
}

function onMessage(event) {
  console.log("WebSocket message received:", event);
  var data = JSON.parse(event.data);
  if (data.distance !== undefined) {
    document.getElementById(
      "distance-value"
    ).innerText = `Distance: ${data.distance} cm`;
  }
}

function updateDistanceValue() {
  // Send a message to request the distance value from the server
  websocket.send("request_distance");

}

function sendMessage(message) {
  websocket.send(message);
}

// Speed Settings Handler
var speedSettings = document.querySelectorAll(
  'input[type=radio][name="speed-settings"]'
);
speedSettings.forEach((radio) =>
  radio.addEventListener("change", () => {
    var speedSettings = radio.value;
    console.log("Speed Settings :: " + speedSettings);
    sendMessage(speedSettings);
  })
);

function setDefaultSpeed() {
  console.log("Setting default speed to normal..");
  let normalOption = document.getElementById("option-2");
  normalOption.checked = true;
}

// O-Pad/ D-Pad Controller and Javascript Code
document.body.addEventListener("click", function (e) {
  if (e.target && e.target.nodeName == "A") {
    e.preventDefault();
  }
});

function touchStartHandler(event) {
  var direction = event.target.dataset.direction;
  console.log("Touch Start :: " + direction);
  sendMessage("car-" + direction);
}

function touchEndHandler(event) {
  const stop_command = "car-stop";
  var direction = event.target.dataset.direction;
  console.log("Touch End :: " + direction);
  sendMessage(stop_command);
}

document.querySelectorAll(".control").forEach((item) => {
  item.addEventListener("touchstart", touchStartHandler);
});

document.querySelectorAll(".control").forEach((item) => {
  item.addEventListener("touchend", touchEndHandler);
});

// Call onLoad function when the window loads
window.addEventListener("load", onLoad);
