import socket
import json
import time

HEADER_REQUEST = 'Connect me'
HEADER_READY = 'Ready to connect'
HEADER_GREET = 'Hello peer'

class connector:
    def __init__(self, tracker_name, tracker_port, port) -> None:
        self.tracker_name = tracker_name
        self.tracker_port = tracker_port
        self.port = port
        self.sockets = []

    def run(self):
        # connect to tracker
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        peer_socket.bind(('', self.port))
        #peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peer_socket.sendto(HEADER_REQUEST.encode(), (self.tracker_name, self.tracker_port))
        state = 'w1'
        print('Ready to connect')

        while True:
            if state == 'w1':
                try:
                    rcvpkt = peer_socket.recv(1024)
                    rcvpkt = json.loads(rcvpkt.decode())
                    print(rcvpkt)
                    # if no other peer exists
                    if not 'name' in rcvpkt:
                        state = 'w0'
                        continue
                    # ready to connect
                    state = 'c2'
                except BlockingIOError:
                    print('Waiting for tracker to respond.')
                    time.sleep(1)
                    continue

            if state == 'c2':
                print('Sending greet to peer.')
                peer_socket.sendto(self.make_pkg(HEADER_GREET, None).encode(), (rcvpkt['name'], rcvpkt['port']))
                time.sleep(0.5)
                peer_socket.sendto(self.make_pkg(HEADER_READY, None).encode(), (self.tracker_name, self.tracker_port))
                peer_socket.sendto(self.make_pkg(HEADER_GREET, None).encode(), (rcvpkt['name'], rcvpkt['port']))
                state = 'w2'

            if state == 'w2':
                try:
                    rcvpkt, address = peer_socket.recvfrom(1024)
                    rcvpkt = json.loads(rcvpkt.decode())
                    print(rcvpkt)
                    print('Connection success')
                    peer_socket.sendto(self.make_pkg(HEADER_GREET, None).encode(), address)
                    self.sockets.append(peer_socket)
                    time.sleep(0.1)
                    return
                except BlockingIOError:
                    print('Waiting for peer to connect')
                    time.sleep(1)
                    continue

            if state == 'w0':
                try:
                    # receive target peer from tracker
                    rcvpkt = peer_socket.recv(1024)
                    rcvpkt = json.loads(rcvpkt.decode())
                    print(rcvpkt)
                    peer_name = rcvpkt['name']
                    peer_port = rcvpkt['port']
                    # ready to connect
                    state = 'c3'
                except BlockingIOError:
                    print('Waiting for new peers.')
                    time.sleep(1)
                    continue
            
            if state == 'c3':
                print('Sending greet to peer.')
                peer_socket.sendto(self.make_pkg(HEADER_GREET, None).encode(), (peer_name, peer_port))
                state = 'w2'

    def make_pkg(self, header, address):
        pkg = {}
        pkg['header'] = header
        if not address is None:
            pkg['name'] = address[0]
            pkg['port'] = address[1]
        return json.dumps(pkg)


if __name__ == '__main__':
    c = connector('10.0.0.1', 12000, 50000)
    c.run()