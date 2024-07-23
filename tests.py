

from pynng import Pair0

server = Pair0()
server.listen('tcp://127.0.0.1:1014')


while True:
    print(server.recv())


