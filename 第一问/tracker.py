import socket,threading,time,queue,json,os,sys,random

port=5000
if len(sys.argv)==2:
    port=int(sys.argv[1])
elif len(sys.argv)>2:
    print("[Usage]: \"python tracker.py <port|default:5000>\"")
    exit()

hosts={}

def add_send(tar_peer:tuple,tar_port:int,other_peer:tuple):
    client = socket.socket()
    client.connect(tar_peer)
    send_data=json.dumps({
        "type":"ADD",
        "value":{
            "port":tar_port,
            "peer":other_peer
        }
    })
    client.send(send_data.encode('utf-8'))
    recv_data=client.recv(1024).decode('utf-8')
    client.close()
    return recv_data
def get_ports(tar_peer:tuple,n:int=1):
    client = socket.socket()
    client.connect(tar_peer)
    send_data=json.dumps({
        "type":"PORTS",
        "value":n
    })
    client.send(send_data.encode('utf-8'))
    recv_data=json.loads(client.recv(1024).decode('utf-8'))
    client.close()
    return recv_data

server = socket.socket()
server.bind((socket.gethostbyname(socket.gethostname()),port))
server.listen(4)
while 1:
    print(hosts)
    serObj,address=server.accept()
    re_data = serObj.recv(1024).decode('utf-8')

    data=json.loads(re_data)
    hosts[data[0]]=(data[1],data[2])

    peers=[hosts[i] for i in random.sample(hosts.keys(),min(len(hosts),len(data[3]))) if i!=data[0]]
    for port,peer in zip(data[3],peers):
        peer_port=get_ports(peer,1)[0]
        add_send(peer,peer_port,(data[1],port))
        add_send((data[1],data[2]),port,(peer[0],peer_port))

    serObj.send("ok".encode('utf-8'))

    serObj.close()
server.close()