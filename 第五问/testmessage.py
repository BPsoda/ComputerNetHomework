from message_tree import *

parentId = 0
for i in range(5):
    print('Message {}'.format(i))
    pkt = {
        'level': int(input('Please input level')),
        'parent': parentId,
        'content': input('Please input content'),
    }
    n = Node(pkt)
    with open('{}.json'.format(n.id), 'w') as f:
        f.write(n.makepkt())
    parentId = n.id
