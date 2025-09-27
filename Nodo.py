import socket
import threading
import time

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
        self.ok_event = threading.Event()
        self.listener_thread = threading.thread(target=self._listener, deamon=True)

    def start(self):
        self.listener_thread.start()

    def _listener(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            msg = data.decode()
            self._handle_message(msg)

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
        if typ == "ELECTION":
            if sender < self.id:
                self.send_to(sender, f"OK:{self.id}")
                self.start_election()
        elif typ == "OK":
            self.ok_event.set()
        elif typ == "COORD":
            with self.lock:
                self.leader = sender
                self.state = "normale"
