import time
import threading

TIMEOUT = 5  # secondi di attesa per le risposte OK

def avvia_elezione(nodo):
    nodo.stato = "leggendo"
    print(f"[Nodo {nodo.id}] Avvio elezione...")

    