import socket
import json

HEADER_CONNECT = 'Connect now'
HEADER_PEERLIST = 'Peer List'

class tracker:
    def __init__(self, port) -> None:
        self.server_port = port

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('', self.server_port))
        state = 'w0'
        peer_list = []
        print('Ready to serve.')

        while True:
            if state == 'w0':
                rcvpkt, address = server_socket.recvfrom(1024)
                rcvpkt = rcvpkt.decode()
                print(address, rcvpkt, '\n')
                if len(peer_list) < 1:
                    print('Only one peer, waiting for others to join.')
                    server_socket.sendto(self.make_pkg(HEADER_PEERLIST, None).encode(), address)
                else:
                    server_socket.sendto(self.make_pkg(HEADER_PEERLIST, peer_list[0]).encode(), address)
                    state = 'c1'
                peer_list.append(address)

            if state == 'c1':
                rcvpkt, address = server_socket.recvfrom(1024)
                print(address)
                rcvpkt = rcvpkt.decode()
                rcvpkt = json.dumps(rcvpkt)
                server_socket.sendto(self.make_pkg(HEADER_CONNECT, address).encode(), peer_list[0])
                state = 'w0'

    def make_pkg(self, header, address):
        pkg = {}
        pkg['header'] = header
        if not address is None:
            pkg['name'] = address[0]
            pkg['port'] = address[1]
        return json.dumps(pkg)
        
if __name__ == '__main__':
    t = tracker(12000)
    t.run()