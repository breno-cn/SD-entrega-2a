import grpc

from Server_pb2_grpc import ServerServicer, ServerStub, add_ServerServicer_to_server
from Server_pb2 import Request, Response
from Hashtable import Hashtable

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
    print(address)
    try:
        channel = grpc.insecure_channel(address)
        stub = ServerStub(channel)
        stub.ping(Request())
        response = True
    except Exception as e:
        print(e)
        response = False
    finally:
        channel.close()
        return response

class Server(ServerServicer):
    
    def __init__(self, id: int, host: str, maxServers: int, maxId: int) -> None:
        super().__init__()
        self.id = id
        self.host = host
        self.hashtable = Hashtable()
        self.maxServers = maxServers
        self.maxId = maxId
        # self.fingerTable = [self.succ(self.id + (2 ** (i - 1))) for i in range(self.maxServers)]

        # print(self.fingerTable)
        print(self.succ(self.id))


    def shouldIProcess(self, key: str) -> bool:
        result = getHash(key) % self.maxId
        
        return (result - self.maxServers) < result < (result + self.maxServers)

    def succ(self, addr: int):
        currentAddr = addr + 1
        while True:
            if ping(f'localhost:{currentAddr}'):
                return currentAddr
            currentAddr += 1

    def ping(self, request, context):
        return Response()

server = Server(300, 'localhost', 5, 455)
