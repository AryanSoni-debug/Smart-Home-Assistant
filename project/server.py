# server.py — NEO Multi Device Smart Home
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import re

app = Flask(__name__)
app.config["SECRET_KEY"] = "neo!"
socketio = SocketIO(app, cors_allowed_origins="*")

# DEVICE STATES
state = {
    "bulb":   {"power": "OFF", "brightness": 100},
    "fan":    {"power": "OFF", "speed": 0},
    "ac":     {"power": "OFF", "temp": 24},
    "tv":     {"power": "OFF"},
    "lamp":   {"power": "OFF", "brightness": 100},
    "speaker":{"power": "OFF", "volume": 30}
}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def connect():
    emit("state_update", state)


# ---------------- DEVICE ACTIONS -----------------

@socketio.on("toggle_device")
def toggle_device(device):
    if state[device]["power"] == "ON":
        state[device]["power"] = "OFF"
    else:
        state[device]["power"] = "ON"

    emit("state_update", state, broadcast=True)


@socketio.on("increase")
def increase(device):
    if device == "fan":
        state["fan"]["speed"] = min(5, state["fan"]["speed"] + 1)

    elif device == "ac":
        state["ac"]["temp"] = min(30, state["ac"]["temp"] + 1)

    elif device == "speaker":
        state["speaker"]["volume"] = min(100, state["speaker"]["volume"] + 5)

    emit("state_update", state, broadcast=True)


@socketio.on("decrease")
def decrease(device):
    if device == "fan":
        state["fan"]["speed"] = max(0, state["fan"]["speed"] - 1)

    elif device == "ac":
        state["ac"]["temp"] = max(16, state["ac"]["temp"] - 1)

    elif device == "speaker":
        state["speaker"]["volume"] = max(0, state["speaker"]["volume"] - 5)

    emit("state_update", state, broadcast=True)


@socketio.on("set_brightness")
def set_brightness(data):
    dev = data["id"]
    val = data["value"]
    state[dev]["brightness"] = val

    emit("state_update", state, broadcast=True)


@socketio.on("set_volume")
def set_volume(val):
    state["speaker"]["volume"] = val
    emit("state_update", state, broadcast=True)


# ---------------- VOICE ENGINE -----------------

@socketio.on("voice_command")
def voice(text):
    text = text.lower()
    print("NEO heard:", text)

    # ON/OFF ACTIONS
    for d in state.keys():
        if f"turn on {d}" in text or f"{d} on" in text:
            state[d]["power"] = "ON"

        if f"turn off {d}" in text or f"{d} off" in text:
            state[d]["power"] = "OFF"

    # Brightness
    if "brightness" in text or "light" in text:
        m = re.search(r"(\d+)", text)
        if m:
            val = min(100, max(0, int(m.group(1))))
            state["bulb"]["brightness"] = val
            state["lamp"]["brightness"] = val

    # Speaker volume
    if "volume" in text:
        m = re.search(r"(\d+)", text)
        if m:
            state["speaker"]["volume"] = int(m.group(1))

    # Fan speed
    if "speed" in text and "fan" in text:
        m = re.search(r"(\d+)", text)
        if m:
            state["fan"]["speed"] = min(5, max(0, int(m.group(1))))

    # AC temp
    if "temperature" in text or "temp" in text:
        m = re.search(r"(\d+)", text)
        if m:
            state["ac"]["temp"] = min(30, max(16, int(m.group(1))))

    emit("state_update", state, broadcast=True)


# ---------------- RUN SERVER -----------------

if __name__ == "__main__":
    print("NEO Multi Device Server running at http://127.0.0.1:5050")
    socketio.run(app, host="127.0.0.1", port=5050)
