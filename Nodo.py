import socket
import threading
from Elezione import avvia_elezione


BASE_PORT = 50000

class Nodo:
    def __init__(self,id, peers):
        self.id = id
        self.peers = peers
        self.port = BASE_PORT + id
        self.state = "normale"
        self.leader = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.port))
        self.lock = threading.Lock()
        self.listener_thread = threading.Thread(target=self._listener, daemon=True)
        self.attivo = True


    def start(self):
        self.listener_thread.start()

    def _listener(self):
        while self.attivo:
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = data.decode()
                self._handle_message(msg)
            except OSError:
                break  # Socket chiuso


    def send_to(self, target_id, msg):
        port = self.peers[target_id]
        self.sock.sendto(msg.encode(), ('127.0.0.1', port))

    def broadcast(self, msg):
        for pid in self.peers:
            if pid == self.id:
                continue
            self.send_to(pid, msg)

    def _handle_message(self, msg):
        parts = msg.split(':')
        typ = parts[0]
        sender = int(parts[1])
        if typ == "elezione":
            if sender < self.id:
                self.send_to(sender, f"OK:{self.id}")
                if self.state != "leader" and self.state!="eleggendo":
                    self.start_election()

        elif typ == "ok":
            self.risposte_ok = True
        elif typ == "coordinatore":
            with self.lock:
                if sender != self.id:
                    self.leader = sender
                    self.state = "normale"
                    print(f"[Nodo {self.id}] riceve COORDINATORE da {sender}")



    def start_election(self):
        if self.state == "leader" or self.state == "eleggendo":
            return
        avvia_elezione(self)

    def invia_messaggio(self, tipo, target_id):
        self.send_to(target_id, f"{tipo}:{self.id}")

    def stop(self):
        self.attivo = False
        self.sock.close()
