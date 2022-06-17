import json
import time
from anti_fraud import *

class Node:
    def __init__(self, pkt:dict) -> None:
        '''用dict创建一个新的节点，如果不指定id，则自动生成'''
        self.level = pkt['level']
        self.parentId = pkt['parent']
        self.content = pkt['content']
        if 'time' in pkt.keys():
            self.time = pkt['time']
        else:
            self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.signature = pkt['signature']
        if 'id' in pkt.keys():
            self.id = pkt['id']
        else:
            self.id = self.generateId()
        self.firstSon = None
        self.sibling = None
        self.conflict = None

    def makepkt(self) -> str:
        '''
        {
            type: 'message'// 数据类型
            destination:  // 数据目标，不写表示广播
            time:  // 数据创建时间
            body:{ // 数据具体内容
                id: // 数据包id，使用SHA-256生成
                level: 1  // 1代表楼， 2代表帖，3代表评论，以此类推
                parent: // 父节点id
                content:  // 消息内容
                time:  // 发帖时间
                signature:  // 签名，包含发帖者的标识与验证信息
            }
        }'''
        pkt = {
            'type': 'message',
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'body': {'id':self.id,
                'level': self.level,
                'parent': self.parentId,
                'content': self.content,
                'time': self.time,
                'signature': self.generateSign()
            }
        }
        return json.dumps(pkt)

    def generateId(self) -> str:
        msg = json.dumps({'level': self.level, 'parent': self.parentId, 'content': self.content, 'time': self.time})
        return generate_msg_id(msg)

    def generateSign(self) -> str:
        with open('rsa_private_key.pem', 'wb')as f:
            private_key = f.read()
        data = json.dumps({'id': self.id, 'level': self.level, 'parent': self.parentId, 'content': self.content, 'time': self.time})
        return sign(private_key, data)


class messageTree:
    def __init__(self) -> None:
        self.root = None
        self.nodeList = []

    def constructTree(self):
        '''从本地保存的文件中读取节点并组成一棵树'''
        pass

    def insert(self, n: Node) -> None:
        '''插入一个新节点'''