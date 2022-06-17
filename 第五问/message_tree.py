import json
import time
from anti_fraud import *
import os

class Node:
    def __init__(self, pkt:dict) -> None:
        '''用dict创建一个新的节点，如果不指定id, time, signature，则自动生成'''
        self.level = pkt['level']
        self.parentId = pkt['parent']
        self.content = pkt['content']
        if 'time' in pkt.keys():
            self.time = pkt['time']
        else:
            self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if 'id' in pkt.keys():
            self.id = pkt['id']
        else:
            self.id = self.generateId()
        if 'signature' in pkt.keys():
            self.signature = pkt['signature']
        else:
            self.signature = self.generateSign()
        self.parent = None
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
        with open('rsa_private_key.pem', 'rb')as f:
            private_key = f.read()
        with open('rsa_public_key.pem', 'rb')as f:
            public_key = f.read()
        data = json.dumps({'id': self.id, 'level': self.level, 'parent': self.parentId, 'content': self.content, 'time': self.time})
        return {'sign': sign(private_key, data), 'pub': public_key}

    def verification(self) -> bool:
        # check id
        msg = json.dumps({'level': self.level, 'parent': self.parentId, 'content': self.content, 'time': self.time})
        if not check_msg_id(self.id, msg):
            return False
        data = json.dumps({'id': self.id, 'level': self.level, 'parent': self.parentId, 'content': self.content, 'time': self.time})
        return check_sign(self.signature['pub'], data, self.signature['sign'])


class messageTree:
    def __init__(self) -> None:
        self.root = None
        self.nodeList = []

    def constructTree(self):
        '''从本地保存的文件中读取节点并组成一棵树'''
        fileList = os.listdir('messages/')
        if (len(fileList) == 0):
            return
        for fileName in fileList:
            with open(fileName, 'r') as f:
                data = json.load(f)
            self.nodeList.append(Node(data['body']))

        self.nodeList.sort(key=lambda x: x.time)    # 按时间排序
        self.root = self.nodeList[0]
        for i in range(1, len(self.nodeList)):
            # 检查真伪
            if not self.nodeList[i].verification():
                self.nodeList.remove(self.nodeList[i])
                i -= 1
                continue
            parentId = self.nodeList[i].parentId
            # 插入树中
            for j in range(i):
                if self.nodeList[j].id == parentId:
                    self.nodeList[i].parent = self.nodeList[j]
                    if self.nodeList[i].level == self.nodeList[j].level:
                        self.nodeList[j].sibling = self.nodeList[i]
                    else:
                        self.nodeList[j].firstSon = self.nodeList[i]
                    break


    def insert(self, n: dict) -> None:
        '''插入一个新节点'''
        self.nodeList.append(Node(n))
        # 插入树中
        for i in range(-1, -len(self.nodeList), -1):
            if self.nodeList[i].id == self.nodeList[-1].parentId:
                self.nodeList[-1].parent = self.nodeList[i]
                if self.nodeList[i].level == self.nodeList[-1].level:
                    self.nodeList[i].sibling = self.nodeList[-1]
                else:
                    self.nodeList[i].firstSon = self.nodeList[-1]

    def getNode(self, id) -> Node:
        for n in self.nodeList:
            if n.id == id:
                return n

    def getSubtree(self, id) -> dict:
        '''以一个字典形式，返回以对应id为根节点的包含其children和grandchildren的子树'''
        subtree = dict()
        for n in self.nodeList:
            if n.id == id:
                subtree = {
                    'id': n.id,
                    'level': n.level,
                    'parent': n.parentId,
                    'content': n.content,
                    'time': n.time,
                    'signature': n.signature,
                    'children': self.getSubtree()
                }

    def _getChildren(self, n: Node) -> dict:
        children = []
        p = n.firstSon
        while p is not None:
            children.append(p)
            p = p.sibling
        return {
            'id': n.id,
            'level': n.level,
            'parent': n.parentId,
            'content': n.content,
            'time': n.time,
            'signature': n.signature,
            'children': list(self._getChildren(x) for x in children)
        }
