import socket,threading,time,queue,json,os,sys,random
##################################################################
def json_load(fname:str):
    with open("messages/"+fname,"r") as f:
        return json.load(f)
##################################################################
def make_message(source_name:str,destination_name:str,_id:str,level:int,parent:str,content:str,signature:str):
    return json.dumps({
        "type": 'message',
        "source": source_name,
        "destination": destination_name,
        "time":time.time(),
        "body":{
            "id": _id,
            "level": level,
            "parent": parent,
            "content": content,
            "time":  time.time(),
            "signature":  signature
        }
    })
##################################################################
def port_avaliable(port:int):
    """判断端口是否可用"""
    if port<32768 or 65535<port:return False
    if 'win32'==sys.platform: cmd='netstat -aon|findstr ":%s "'%port
    elif 'linux'==sys.platform: cmd='netstat -aon|grep ":%s "'%port
    else: raise NotImplementedError('Unsupported system type %s'%sys.platform)
    with os.popen(cmd, 'r') as f:
        if ''!=f.read():return False
        else:return True
##################################################################
def get_avaliable_ports(n:int=1):
    """返回 n 个可用端口"""
    ret=[]
    for port in range(random.randint(5000,8000),65536):
        if len(ret)>=n:break
        if port_avaliable(port):ret.append(port)
    return ret[:n]
##################################################################
def makepkt(msg:str,s_name:str,t_name:str):
    return json.dumps({
        "s_name":s_name,
        "t_name":t_name,
        "time":time.time(),
        "content":msg
    })
##################################################################
def listen(port:int,ip:str,recv_buffer:queue.Queue):
    server = socket.socket()
    server.bind((socket.gethostbyname(socket.gethostname()),port))
    server.listen(4)
    serObj,address=server.accept()
    while True:
        re_data = serObj.recv(32768).decode('utf-8')
        if re_data=="QUIT":break
        recv_buffer.put(re_data)
        serObj.send("ok".encode('utf-8'))
    serObj.close()
    server.close()
###################################################################
def send(peer:tuple,sender_buffer:queue.Queue):
    client = socket.socket()
    client.connect(peer)
    while True:
        if sender_buffer.empty():
            time.sleep(0.05)
            continue
        send_data=sender_buffer.get()
        client.send(send_data.encode('utf-8'))
        if send_data == 'QUIT':break
        print,("reply: ",client.recv(32768).decode('utf-8'))
    client.close()
###################################################################
class PeerHandler:
    def __init__(self,name:str,self_ip:str,connection_port:int,on_receive_message):
        if not os.path.exists("messages"):
            os.makedirs("messages")
        self.name=name
        self.listening_ports=set()
        """主机标识"""
        self.peers={}
        """{(ip,port):(recv_buffer,sender_buffer)}"""
        self.storage=set()
        """见过的消息的hash值"""
        self.msg=queue.Queue()
        """待发送信息"""
        self.living=True
        self.connection_port=connection_port
        self.ip=self_ip

        self.t=threading.Thread(target=self.connection_module,args=(connection_port,))
        self.t.setDaemon(True)
        self.t.start()

        self.t=threading.Thread(target=self.run)
        self.t.setDaemon(True)
        self.t.start()

        self.request_done=False
        self.request_all()

        self.dead_peers=queue.Queue()

        self.tracker=None

    def request_all(self):
        """请求全部数据包"""
        self.send(json.dumps({"type":"request","source":self.name,"time":time.time()}),None)

    def addpeer(self,port:int,peer:list):
        print(self.name,"addpeer",port,peer)
        self.listening_ports.add(port)
        """添加 peer 
        参数 peer 的格式：[ip,port]
        """
        self.peers[peer]=(queue.Queue(),queue.Queue()) # (recv_buffer,sender_buffer)
        t_listen=threading.Thread(target=listen,args=(port,self.ip,self.peers[peer][0]))
        t_listen.setDaemon(True)
        t_listen.start()
        t_send=threading.Thread(target=send,args=(peer,self.peers[peer][1]))
        t_send.setDaemon(True)
        t_send.start()
        return self.peers[peer]

    def send(self,msg:str,t_name:str):
        """对 t_name 发送 msg\n
        t_name为None表示广播"""
        self.msg.put(makepkt(msg,self.name,t_name))

    def me_event(self,pkt:str):
        """收到发给自己或广播的消息时触发"""
        print(self.name+" received:"+pkt+"\n\n",end='')
        data=json.loads(json.loads(pkt)["content"])
        print(data)
        if not self.request_done and type(data)==list:# 接收返回的所有数据包
            for i in data:
                with open("messages/{}.json".format(i["body"]["id"]),"w") as f:
                    json.dump(i,f)
            self.request_done=True
        elif data["type"]=="request":# 发送所有数据包
            self.send(json.dumps([json_load(i) for i in os.listdir("messages")]),data["source"])############所有包中加入source##############
        elif data["type"]=="message":# 接收正常的消息包
            with open("messages/{}.json","w") as f:
                json.dump(data,f)
            """同时插入到内存里："""
            self.on_receive_message(data)
        elif data["type"]=="quit":# 邻居退出
            for port in data["ports"]:
                if (_:=(data["ip"],port)) in self.peers:#########################在quit包中加入自己的ip和ports##########################
                    # self.peers.pop(_)
                    self.dead_peers.put(_)
        
        # if data["content"]=="Hello guys!":
        #     self.send("Hi, {}".format(data["s_name"]),data["s_name"])
    def quit(self):
        """自己退出并告诉邻居和tracker"""
        self.send(json.dumps({"type":"quit","ip":self.ip,"ports":list(self.listening_ports),"time":time.time()}),None)
        client = socket.socket()
        client.connect(self.tracker)

        send_data=json.dumps([
            self.name,
        ])
        client.send(send_data.encode('utf-8'))
        recv_data=client.recv(32768).decode('utf-8')
        client.close()

    def run(self):
        """消息接收及转发等"""
        while True:
            for p in self.peers:
                if self.peers[p][0].empty():continue
                _=self.peers[p][0].get()
                if hash(_) in self.storage:continue
                self.storage.add(hash(_))
                __=json.loads(_)
                s_name,t_name=__["s_name"],__["t_name"]
                if t_name==self.name or (t_name==None and s_name!=self.name):self.me_event(_)
                if t_name!=self.name:self.msg.put(_)
            if self.msg.empty():
                time.sleep(0.05)
                continue
            while not self.dead_peers.empty():
                self.peers.pop(self.dead_peers.get())
            while not self.msg.empty():
                tmp=self.msg.get()
                for p in self.peers:
                    self.peers[p][1].put(tmp)

    def __del__(self):
        self.living=False

    def connection_module(self,port:int):
        server = socket.socket()
        server.bind((self.ip,port))
        server.listen(4)
        while self.living:
            serObj,address=server.accept()
            re_data = json.loads(serObj.recv(32768).decode('utf-8'))

            if re_data["type"]=="PORTS":
                send_data=get_avaliable_ports(re_data["value"])
            elif re_data["type"]=="ADD":
                self.addpeer(re_data["value"]["port"],tuple(re_data["value"]["peer"]))
                send_data=None

            serObj.send(json.dumps(send_data).encode('utf-8'))

            serObj.close()
        server.close()
    
    def login(self,tracker:tuple):
        client = socket.socket()
        client.connect(tracker)
        self.tracker=tracker

        send_data=json.dumps([
            self.name,
            self.ip,
            self.connection_port,
            get_avaliable_ports(10)
        ])
        client.send(send_data.encode('utf-8'))
        recv_data=client.recv(32768).decode('utf-8')
        client.close()
        return self