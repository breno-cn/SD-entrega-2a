import sys
import os
import signal
import grpc

from Server_pb2_grpc import ServerServicer, ServerStub, add_ServerServicer_to_server
from Server_pb2 import Request, Response
from Hashtable import Hashtable

from concurrent import futures

print(f'server pid: {os.getpid()}')

def calculateFingerTable(_signum, _frame):
    global serverServicer

    print(f'Calculating finger table of server {serverServicer.n}...')

    serverServicer.calculateFingerTable()

signal.signal(signal.SIGUSR1, calculateFingerTable)

def getHash(key: str):
    keyBytes = bytes(key, 'ascii')
    p = 31
    i = 0
    sum = 0

    for byte in keyBytes:
        sum += byte * (p ** i)
        i += 1

    return sum

def ping(address: str) -> bool:
    response = None
    try:
        channel = grpc.insecure_channel(address)
        stub = ServerStub(channel)
        stub.ping(Request())
        response = True
    except Exception as e:
        response = False
    finally:
        channel.close()
        return response

class Server(ServerServicer):
    
    def __init__(self, n: int, host: str, m: int) -> None:
        super().__init__()
        self.n = n
        self.host = host
        self.hashtable = Hashtable()
        self.m = m                      # ammount of bits used by the hash function, also determinate the max network size
        self.fingerTable = [0] * self.m
        self.maxNodes = (2 ** self.m) + 1

    def succ(self, addr: int):
        currentAddr = addr + 1
        while True:
            if ping(f'localhost:{currentAddr}'):
                return currentAddr
            currentAddr = (currentAddr + 1) % self.maxNodes

    def ping(self, request, context):
        return Response()

    def calculateFingerTable(self):
        for i in range(self.m):
            self.fingerTable[i] = self.succ(((self.n + (2 ** (i))) % self.maxNodes))

        print(f'process {self.n} finger table: {self.fingerTable}')

n = int(sys.argv[1])
m = int(sys.argv[2])
serverServicer = Server(n, 'localhost', m)
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

add_ServerServicer_to_server(serverServicer, server)

server.add_insecure_port(f'[::]:{n}')
server.start()

server.wait_for_termination()
