import threading

TIMEOUT = 5  #secondi di attesa per le risposte OK

#Avvia l'elezione
def avvia_elezione(nodo):
    nodo.stato = "eleggendo"
    print(f"[Nodo {nodo.id}] avvia l'elezione...")
    
    #peer = pari, passa nodo per nodo in base a quale è attivo. Ci riesce perché ogni nodo ha una lista di peer.
    superiori = [peer for peer in nodo.peers if peer > nodo.id]
    if not superiori:
        proclama_leader(nodo)
        return

    #Invia il messaggio per l'elezione se non ci sono risposte
    nodo.risposte_ok = False
    for peer_id in superiori:
        nodo.invia_messaggio("elezione", peer_id)

    #Avvia un timer per attendere risposte OK
    timer = threading.Timer(TIMEOUT, verifica_risposte, args=(nodo,))
    timer.start()

#Controlla se c'è la risposta OK
def gestisci_risposta_ok(nodo, mittente_id):
    print(f"[Nodo {nodo.id}] riceve l'OK da {mittente_id}")
    nodo.risposte_ok = True

#Verifica le risposte per il coordinatore
def verifica_risposte(nodo):
    if not nodo.risposte_ok:
        proclama_leader(nodo)
    else:
        print(f"[Nodo {nodo.id}] attende coordinatore...")

#Ora il nodo da normale diventa leader
def proclama_leader(nodo):
    if nodo.leader is None:
        nodo.stato = "leader"
        nodo.leader = nodo.id
        print(f"[Nodo {nodo.id}] si proclama leader.")
        for peer_id in nodo.peers:
            if peer_id != nodo.id:
                nodo.invia_messaggio("coordinatore", peer_id)


#Ricevuta coordinatore perché riconosce il leader
def ricevi_coordinatore(nodo, nuovo_leader_id):
    nodo.stato = "normale"
    nodo.leader = nuovo_leader_id
    print(f"[Nodo {nodo.id}] riconosce {nuovo_leader_id} come leader.")