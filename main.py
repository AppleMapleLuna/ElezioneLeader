from Nodo import Nodo, get_local_ip
import sys
import requests

def registra_nodo(id, ip, port, server_ip):
    try:
        requests.post(f"http://{server_ip}:8000/register", data={
            "id": id,
            "ip": ip,
            "port": port
        })
        print(f"Nodo {id} registrato sul server.")
    except Exception as e:
        print(f"Errore nella registrazione: {e}")

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

def crea_nodo(server_ip):
    ip = get_local_ip()
    peers = {
        1: (ip, 50001),
        2: (ip, 50002),
        3: (ip, 50003)
    }
    id = chiedi_id(peers)
    registra_nodo(id, ip, 50000 + id, server_ip)
    nodo = Nodo(id, peers)
    nodo.start()
    return nodo


if __name__ == "__main__":
    SERVER_IP = input("Inserisci l'IP del server: ")
    nodo = crea_nodo(SERVER_IP)

    if nodo.attendi_rete():
        nodo.start_election()

    while True:
        print("\n--- Menù Nodo", nodo.id, "---")
        print("1. Avvia elezione")
        print("2. Ping agli altri nodi")
        print("3. Mostra stato")
        print("4. Simula guasto")
        print("5. Invia messaggio 'elezione'")
        print("6. Invia messaggio 'OK'")
        print("7. Invia messaggio 'coordinatore'")
        print("0. Esci")   
        scelta = input("Scegli un'opzione: ")

        if scelta == "1":
            nodo.start_election()
        elif scelta == "2":
            nodo.invia_ping()
            nodo.broadcast(f"ping:{nodo.id}")
        elif scelta == "3":
            print(f"Stato: {nodo.stato}, Leader: {nodo.leader}")
        elif scelta == "4":
            nodo.stop()
            print("Nodo arrestato.")
        elif scelta == "6":
            target = int(input("ID del nodo destinatario: "))
            nodo.invia_messaggio("elezione", target)

        elif scelta == "7":
            target = int(input("ID del nodo destinatario: "))
            nodo.invia_messaggio("ok", target)

        elif scelta == "8":
            target = int(input("ID del nodo destinatario: "))
            nodo.invia_messaggio("coordinatore", target)
    
        elif scelta == "0":
            nodo.stop()
            print("Uscita...")
            break

        else:
            print("Scelta non valida.")
