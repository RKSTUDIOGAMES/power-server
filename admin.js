// 🔥 Same-origin calls (PC + Mobile compatible)

async function loadPlayers() {
  try {
    const res = await fetch("/players");
    const players = await res.json();

    const container = document.getElementById("buttons");
    container.innerHTML = "";

    const ids = Object.keys(players);

    if (ids.length === 0) {
      container.innerText = "No players registered yet";
      return;
    }

    ids.forEach(id => {
      const name = players[id];

      const btn = document.createElement("button");
      btn.innerText = `${name} (${id}) POWER`;
      btn.style.display = "block";
      btn.style.margin = "10px 0";
      btn.style.padding = "10px";
      btn.style.fontSize = "16px";

      btn.onclick = () => givePower(id);
      container.appendChild(btn);
    });

  } catch (e) {
    console.error(e);
    document.getElementById("buttons").innerText =
      "❌ Server not reachable";
  }
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

loadPlayers();
setInterval(loadPlayers, 3000);
