from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

players = {}
current_power = None


@app.route("/")
def home():
    return "POWER SERVER RUNNING"


# 🔥 ADMIN PANEL
@app.route("/admin")
def admin():
    return render_template("admin.html")


# 🔹 Unity → register player
@app.route("/register_player", methods=["POST"])
def register_player():
    data = request.json
    pid = data["playerId"]
    pname = data["playerName"]

    players[pid] = pname
    print("PLAYER REGISTERED:", players)

    return jsonify({"status": "registered"})


# 🔹 Admin → list players
@app.route("/players")
def get_players():
    return jsonify(players)


# 🔹 Admin → give power
@app.route("/give_power", methods=["POST"])
def give_power():
    global current_power
    current_power = request.json
    print("POWER RECEIVED:", current_power)
    return jsonify({"status": "power_set"})


# 🔹 Unity → get power
@app.route("/get_power")
def get_power():
    global current_power
    if current_power:
        temp = current_power
        current_power = None
        return jsonify(temp)
    return jsonify({"power": None})



# 🔥 NEW ROUND RESET API
@app.route("/reset_round", methods=["POST"])
def reset_round():
    global players, current_power
    players = {}
    current_power = None
    print("🔄 ROUND RESET — players cleared")
    return jsonify({"status": "round_reset"})




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
