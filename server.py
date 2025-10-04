from flask import Flask, request, jsonify
from Nodo import get_local_ip

app = Flask(__name__)
nodi = {}

@app.route("/register", methods=["POST"])
def register():
    id = int(request.form["id"])
    ip = request.form["ip"]
    port = int(request.form["port"])
    nodi[id] = (ip, port)
    print(f"Registrato nodo {id} → {ip}:{port}")
    return "OK"

@app.route("/peers", methods=["GET"])
def get_peers():
    return jsonify(nodi)

if __name__ == "__main__":
    ip_server = get_local_ip()
    print(f"Server avviato su {ip_server}:8000")
    app.run(host=ip_server, port=8000)