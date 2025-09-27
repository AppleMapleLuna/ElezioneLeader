import socket
class Nodo:
    def __init__(self,id,slisten,saccept,stato):
        self.id = id
        self.slisten= slisten
        self.saccept = saccept
        self.stato = stato

    def getId(self):
        return self.id
    def getSocketListen(self):
        return self.slisten
    def getSocketAccept(self):
        return self.saccept
    def getStato(self):
        return self.stato
