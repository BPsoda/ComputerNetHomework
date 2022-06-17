from peerhandler import PeerHandler
import threading
"""
(a) --|link1|-- (b) --|link2|-- (c)
"""
a=PeerHandler("a")
b=PeerHandler("b")
c=PeerHandler("c")
link1=[(a.ip(),8001),(b.ip(),8002)]
link2=[(b.ip(),8003),(c.ip(),8004)]
a.addpeer(link1[0][1],link1[1])
b.addpeer(link1[1][1],link1[0])
b.addpeer(link2[0][1],link2[1])
c.addpeer(link2[1][1],link2[0])
t_a=threading.Thread(target=a.run)
t_a.setDaemon(True)
t_a.start()
t_b=threading.Thread(target=b.run)
t_b.setDaemon(True)
t_b.start()
t_c=threading.Thread(target=c.run)
t_c.setDaemon(True)
t_c.start()

c.send("Hello guys!",None)
# PeerHandler.me_event 为用于回复的事件响应函数
input()