from Nodo import Nodo
import time

def crea_rete():
    nodi = {}
    peers = {1: 50001, 2: 50002, 3: 50003}
    for id in peers:
        nodi[id] = Nodo(id, peers)
        nodi[id].start()
    return nodi

if __name__ == "__main__":
    nodi = crea_rete()
    time.sleep(2)
    # print("Simulo guasto del leader...")
    # nodi[3].stop()
    time.sleep(1)
    nodi[1].start_election()  # Nodo 1 avvia elezione
