from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import time
import pytchat
import threading
VIDEO_ID ="iwvRNaR6hhM"
power_requests = {}

def read_chat():

    try:

        chat = pytchat.create(video_id=VIDEO_ID)

        while chat.is_alive():

            for c in chat.get().sync_items():

                username = c.author.channelId
                message = c.message.lower().strip()

                if message == "power" and username in players:

                    # prevent duplicate spam
                    if not power_requests.get(username):

                        power_requests[username] = True

                        print("⚡ POWER REQUEST:", username)

            time.sleep(1)

    except Exception as e:

        print("CHAT ERROR:", e)
app = Flask(__name__)
CORS(app)

players = {}
current_power = None

# 🔐 Password from Render Environment (not visible on GitHub)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")
SESSION_TOKEN = "RK_ADMIN_LOGGED_IN"


# 🟢 Server Check
@app.route("/")
def home():
    return "POWER SERVER RUNNING"


# 🔐 LOGIN API (one time)
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"error": "wrong password"}), 403

    res = make_response({"status": "ok"})
    res.set_cookie("session", SESSION_TOKEN, max_age=86400)  # 1 day
    return res


# 🔥 ADMIN PANEL (same UI + login added)
@app.route("/admin")
def admin():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>POWER CONTROL PANEL</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body style="background:#111;color:white;font-family:Arial;padding:20px">

<h2>🔥 POWER CONTROL PANEL</h2>

<div id="loginBox">
  <input id="pass" type="password" placeholder="Enter Password">
  <button onclick="login()">Login</button>
</div>

<div id="panel" style="display:none">
  <div id="buttons">Loading players...</div>
  <p id="status"></p>
</div>

<script>

function getCookie(name){
  return document.cookie.split('; ')
    .find(row => row.startsWith(name+'='))
    ?.split('=')[1];
}

// auto login if already authenticated
if(getCookie("session")==="RK_ADMIN_LOGGED_IN"){
  openPanel();
}

function login(){
  fetch("/login",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
      password: document.getElementById("pass").value
    })
  }).then(r=>{
    if(r.ok) openPanel();
    else alert("Wrong password");
  });
}

function openPanel(){
  document.getElementById("loginBox").style.display="none";
  document.getElementById("panel").style.display="block";
  loadPlayers();
  setInterval(loadPlayers, 3000);
}

async function loadPlayers() {

  const res = await fetch("/players_full");
  const data = await res.json();

  const container = document.getElementById("buttons");
  container.innerHTML = "";

  const ids = Object.keys(data);

  if (ids.length === 0) {
    container.innerText = "No players registered yet";
    return;
  }

  ids.forEach(id => {

    const player = data[id];

    const btn = document.createElement("button");

    let label = player.name;

    if(player.power){
      label += " ⚡POWER";
    }

    btn.innerText = label;

    btn.style.display = "block";
    btn.style.margin = "10px 0";
    btn.style.padding = "10px";
    btn.style.fontSize = "16px";

    btn.onclick = () => givePower(id);

    container.appendChild(btn);

  });
}

function givePower(playerId) {
  fetch("/give_power", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      playerId: playerId,
      value: 1
    })
  }).then(() => {
    document.getElementById("status").innerText =
      "⚡ POWER SENT TO " + playerId;
  });
}

</script>

</body>
</html>
"""


# 🔐 Session check
def is_logged_in():
    return request.cookies.get("session") == SESSION_TOKEN


# 🔹 Unity → Register Player
@app.route("/register_player", methods=["POST"])
def register_player():
    data = request.json
    pid = data.get("playerId")
    pname = data.get("playerName")

    if not pid or not pname:
        return jsonify({"error": "Missing data"}), 400

    players[pid] = pname
    print("PLAYER REGISTERED:", players)

    return jsonify({"status": "registered"})


@app.route("/request_power", methods=["POST"])
def request_power():

    data = request.json
    pid = data.get("playerId")

    if pid not in players:
        return jsonify({"error": "player not registered"}), 400

    power_requests[pid] = True

    print("POWER REQUEST:", pid)

    return jsonify({"status": "power_requested"})

# 🔹 Admin → List Players (protected)
@app.route("/players")
def get_players():
    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(players)

@app.route("/players_full")
def players_full():

    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 403

    result = {}

    for pid, name in players.items():

        result[pid] = {
            "name": name,
            "power": power_requests.get(pid, False)
        }

    return jsonify(result)


# 🔹 Admin → Give Power (protected)
@app.route("/give_power", methods=["POST"])
def give_power():
    global current_power

    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 403

    data = request.json
    pid = data.get("playerId")

    current_power = data

    # remove power indicator after use
    power_requests.pop(pid, None)

    print("POWER RECEIVED:", current_power)

    return jsonify({"status": "power_set"})


# 🔹 Unity → Get Power
@app.route("/get_power")
def get_power():
    global current_power

    if current_power:
        temp = current_power
        current_power = None
        return jsonify(temp)

    return jsonify({"power": None})


# 🔥 Round Reset
@app.route("/reset_round", methods=["POST"])
def reset_round():
    global players, current_power
    players = {}
    current_power = None
    return jsonify({"status": "round_reset"})


# 🟢 Local run
if __name__ == "__main__":
    threading.Thread(target=read_chat, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



