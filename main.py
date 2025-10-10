from Nodo import Nodo, get_local_ip, BASE_PORT
import sys
import requests

def scarica_peers(server_ip):
    try:
        r = requests.get(f"http://{server_ip}:8000/peers")
        peers_raw = r.json()
        peers = {int(pid): tuple(peers_raw[pid]) for pid in peers_raw}
        return peers
    except Exception as e:
        print(f"Errore nel download dei peer: {e}")
        return {}


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
    id = int(input("Inserisci l'ID del nodo: "))
    ip = get_local_ip()
    port = BASE_PORT + id
    registra_nodo(id, ip, port, server_ip)
    peers = scarica_peers(server_ip)
    nodo = Nodo(id, peers, server_ip)
    nodo.start(server_ip)
    return nodo

def rimuovi_nodo(id, server_ip):
    try:
        requests.post(f"http://{server_ip}:8000/remove", data={"id": id})
        print(f"Nodo {id} rimosso dal server.")
    except Exception as e:
        print(f"Errore nella rimozione: {e}")


def verifica_leader(server_ip):
    try:
        r = requests.get(f"http://{server_ip}:8000/leader")
        data = r.json()
        return data.get("leader")
    except:
        return None


if __name__ == "__main__":
    SERVER_IP = input("Inserisci l'IP del server: ")
    nodo = crea_nodo(SERVER_IP)

    leader = verifica_leader(SERVER_IP)
    if leader is None:
        nodo.start_election()
    else:
        nodo.leader = leader
        print(f"[Nodo {nodo.id}] riconosce il leader esistente: Nodo {leader}")
    
    while True:
        try:
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
                target_input = input("ID del nodo destinatario: ").strip()
                if not target_input.isdigit():
                    print("ID non valido.")
                    continue
                target = int(target_input)

                nodo.invia_messaggio("ok", target)

            elif scelta == "8":
                target = int(input("ID del nodo destinatario: "))
                nodo.invia_messaggio("coordinatore", target)
        
            elif scelta == "0":
                rimuovi_nodo(nodo.id, SERVER_IP)
                nodo.stop()
                print("Nodo rimosso e arrestato.")
                print("Uscita...")
                break

            else:
                print("Scelta non valida.")
        except Exception as e:
            print(f"Errore durante l'esecuzione: {e}")