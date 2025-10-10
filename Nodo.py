import socket
import threading
from Elezione import avvia_elezione, gestisci_risposta_ok, ricevi_coordinatore
import time
import requests

BASE_PORT = 50000

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # Google DNS
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

class Nodo:
    def __init__(self,id, peers, server_ip):
        # info nodi
        self.ip = get_local_ip()
        self.id = id
        self.server_ip = server_ip
        self.peers = peers
        self.port = BASE_PORT + id
        print(f"[Nodo {self.id}] in ascolto su {self.ip}:{self.port}")

        # risposte
        self.risposte_ok = False
        self.stato = "normale"
        self.leader = None
        # sock e thread
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # serve a far in modo che i nodi comunicano sullo stesso dispositivo
        self.sock.bind((self.ip, self.port))
        self.lock = threading.Lock()
        self.listener_thread = threading.Thread(target=self._listener, daemon=True)
        # flag e counter
        self.attivo = True
        self.pong_ricevuti = 0
        self.coordinatore_ricevuto = False

    def monitor_leader(self, intervallo=5):
        def ciclo():
            while self.attivo:
                if self.leader and self.leader != self.id:
                    self.pong_ricevuti = 0
                    self.send_to(self.leader, f"ping:{self.id}")
                    time.sleep(intervallo)
                    if self.pong_ricevuti == 0:
                        print(f"[Nodo {self.id}] leader {self.leader} non risponde, avvio elezione.")
                        self.leader = None
                        self.start_election()
                else:
                    time.sleep(intervallo)
        threading.Thread(target=ciclo, daemon=True).start()

    def aggiorna_peers(self, server_ip, intervallo=10):
        def ciclo():
            while self.attivo:
                try:
                    r = requests.get(f"http://{server_ip}:8000/peers")
                    peers_raw = r.json()
                    with self.lock:
                        self.peers = {int(pid): tuple(peers_raw[pid]) for pid in peers_raw}
                except:
                    pass
                time.sleep(intervallo)
        time.sleep(1)
        threading.Thread(target=ciclo, daemon=True).start()


    def start(self,server_ip):
        self.aggiorna_peers(server_ip)
        self.listener_thread.start()
        self.monitor_leader()
    
    def _listener(self):
        while self.attivo:
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = data.decode()
                self._handle_message(msg)
                print(f"[Nodo {self.id}] ha ricevuto: {msg}")
            except OSError:
                break  # Socket chiuso


    def attendi_rete(self, soglia=2, timeout=10):
        self.broadcast(f"ping:{self.id}")
        inizio = time.time()
        while time.time() - inizio < timeout:
            if self.pong_ricevuti >= soglia:
                print(f"[Nodo {self.id}] ha ricevuto abbastanza pong, avvia elezione.")
                return True
            time.sleep(0.5)
        print(f"[Nodo {self.id}] non ha ricevuto abbastanza pong, elezione rimandata.")
        return False


    def send_to(self, target_id, msg):
        ip, port = self.peers[target_id]
        self.sock.sendto(msg.encode(), (ip, port))


    def broadcast(self, msg):
        print(f"[Nodo {self.id}] peers attuali: {self.peers}")
        for pid in self.peers:
            if pid == self.id:
                continue
            self.send_to(pid, msg)

    def invia_ping(self):
        self.pong_ricevuti = 0  # resetta il conteggio
        self.broadcast(f"ping:{self.id}")
        print(f"[Nodo {self.id}] invia PING a tutti i peer.")


    def _handle_message(self, msg):
        parts = msg.split(':')
        if len(parts) < 2:
            print(f"[Nodo {self.id}] messaggio malformato: {msg}")
            return
        typ = parts[0]
        try:
            sender = int(parts[1])
            if sender not in self.peers:
                print(f"[Nodo {self.id}] ha ricevuto messaggio da nodo sconosciuto: {sender}")
                return
        except ValueError:
            print(f"[Nodo {self.id}] mittente non valido: {parts[1]}")
            return
        # tipi previsti dall'algoritmo dei bulli
        if typ == "elezione":
            if sender < self.id:
                self.send_to(sender, f"OK:{self.id}")
                if self.stato == "normale":
                    self.start_election()
        elif typ == "ok":
            gestisci_risposta_ok(self, sender)
        elif typ == "coordinatore":
            with self.lock:
                if sender != self.id:
                    self.leader = sender
                    self.stato = "normale"
                    self.coordinatore_ricevuto = True
                    print(f"[Nodo {self.id}] riceve COORDINATORE da {sender}")

        # ping e pong
        elif typ == "ping":
            self.send_to(sender, f"pong:{self.id}")

        elif typ == "pong":
            self.pong_ricevuti += 1
            print(f"[Nodo {self.id}] riceve PONG da {sender}")

    def start_election(self):
        if self.stato == "leader" or self.stato == "eleggendo":
            return
        self.stato = "eleggendo"
        avvia_elezione(self)

    def invia_messaggio(self, tipo, target_id):
        self.send_to(target_id, f"{tipo}:{self.id}")

    def stop(self):
        self.attivo = False
        self.sock.close()
