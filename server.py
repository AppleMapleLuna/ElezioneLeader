from flask import Flask, request, jsonify
from Nodo import get_local_ip

app = Flask(__name__)
nodi = {}

@app.route("/register", methods=["POST"])
def register():
    id = int(request.form["id"])
    ip = request.form["ip"]
    port = int(request.form["port"])
    if id in nodi:
        return f"Errore: ID {id} già registrato", 400
    nodi[id] = (ip, port)
    print(f"Registrato nodo {id} → {ip}:{port}")
    return "OK"


@app.route("/peers", methods=["GET"])
def get_peers():
    return jsonify(nodi)

@app.route("/remove", methods=["POST"])
def remove():
    id = int(request.form["id"])
    if id in nodi:
        del nodi[id]
        print(f"Nodo {id} rimosso dal registro.")
    return "OK"


if __name__ == "__main__":
    ip_server = get_local_ip()
    print(f"Server avviato su {ip_server}:8000")
    app.run(host=ip_server, port=8000)

leader_id = None

@app.route("/leader", methods=["GET"])
def get_leader():
    return jsonify({"leader": leader_id})

@app.route("/set_leader", methods=["POST"])
def set_leader():
    global leader_id
    leader_id = int(request.form["id"])
    print(f"Leader impostato: Nodo {leader_id}")
    return "OK"
