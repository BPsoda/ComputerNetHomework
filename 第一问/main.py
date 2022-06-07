from peerhandler import PeerHandler
import threading,time,json
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

c.send("Hello guys!",None)
# PeerHandler.me_event 为用于回复的事件响应函数
input()