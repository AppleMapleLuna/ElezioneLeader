from Nodo import Nodo, get_local_ip
import sys

def chiedi_id(peers):
    if len(sys.argv) >= 2:
        try:
            id = int(sys.argv[1])
            if id in peers:
                return id
            else:
                print(f"ID {id} non valido. Deve essere uno tra: {list(peers.keys())}")
        except ValueError:
            print("L'ID passato da terminale non è un numero valido.")

    while True:
        try:
            id = int(input(f"Inserisci l'ID del nodo ({list(peers.keys())}): "))
            if id in peers:
                return id
            else:
                print("ID non valido. Riprova.")
        except ValueError:
            print("Input non numerico. Riprova.")

def crea_nodo():
    ip = get_local_ip()
    peers = {
        1: (ip, 50001),
        2: (ip, 50002),
        3: (ip, 50003)
    }
    id = chiedi_id(peers)
    nodo = Nodo(id, peers)
    nodo.start()
    return nodo

if __name__ == "__main__":
    nodo = crea_nodo()
    if nodo.attendi_rete():
        nodo.start_election()

