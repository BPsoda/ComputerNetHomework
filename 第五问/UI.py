from ast import arg
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as msgbox
from tkinter import scrolledtext  
from message_tree import *
from peerhandler import PeerHandler

this_ip,this_port=None
tracker_ip,tracker_port="10.162.8.133",5000

if not os.path.exists("rsa_private_key.pem") or not os.path.exists("rsa_public_key.pem"):
    generate_keypair()
with open("rsa_public_key.pem","r") as f:
    name=f.read().split("\n")[1][:8]

mt=messageTree()
mt.constructTree()
this_peer=PeerHandler(name,this_ip,this_port,on_receive)
this_peer.login((tracker_ip,tracker_port))

def 发帖():
    title=e1.get()
    description=e2.get(0.0,tk.END)
    ################################
    ret=Node({
        "level":1,
        "parent":0,################################################################### parentId 
        "content":title+"\n\n"+description,
        "source":name,
        "destination":None
    })
    with open("messages/{}.json".format(ret.id),"w") as f:
        f.write(_:=ret.makepkt())
    this_peer.send(_,None)
    # level 1
    ################################
    msgbox.showinfo('信息', '发帖成功')
    e1.delete(0,tk.END)
    e2.delete(0.0,tk.END)
    tabControl.select(tab2)
viewing_id=None
def 回帖(*args):
    content=text_input.get(0.0,tk.END)
    node=mt.getNode(viewing_id)
    ###############################
    # print(content)
    ret=Node({
        "level":node.level+1,
        "parent":node.parentId,
        "content":content,
        "source":name,
        "destination":None
    })
    with open("messages/{}.json".format(ret.id),"w") as f:
        f.write(_:=ret.makepkt())
    this_peer.send(_,None)
    ###############################
    text_input.delete(0.0,tk.END)

root =tk.Tk()
root.title(string = "title") 
tabControl = ttk.Notebook(root)  
tab1 = tk.Frame(tabControl) 
tabControl.add(tab1, text='发帖')  
tk.Label(tab1, text="标题：").grid(row=0,column=0)
tk.Label(tab1, text="正文：").grid(row=1,column=0)
e1 = tk.Entry(tab1)
e2 = tk.Text(tab1)
e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
publish=tk.Button(tab1,text="发布",command=发帖)
publish.grid(row=1, column=2)

tab2 = tk.Frame(tabControl)
tabControl.add(tab2, text='看帖')
tree = ttk.Treeview(tab2)

def addnode(x:list,f=1):
    for i in x:
        tree.insert(i["parent"] if f==0 else '',tk.END,text=i["content"],iid=i["id"],values=i["id"],open=False)
        addnode(i["children"],0)
addnode(mt.getWholeTree())

tree.grid(row=0, column=0,ipady=80,rowspan=2)
def select_tree():
    global viewing_id
    for item in tree.selection():
        id=tree.item(item, "values")[0]
        viewing_id=id
        node=mt.getNode(id)
        view.config(state='normal')
        view.delete(0.0,tk.END)
        view.insert(tk.END,node.content)
        view.config(state='disabled')
        break


tree.bind("<<TreeviewSelect>>", lambda event: select_tree())
view=scrolledtext.ScrolledText(tab2)
view.config(state='disabled')
view.grid(row=0,column=1,padx=10)

text_input=scrolledtext.ScrolledText(tab2,height=5)
text_input.grid(row=1,column=1,padx=10)
text_input.bind("<Control-Return>",回帖)
tabControl.pack(expand=1, fill="both")
tabControl.select(tab1) 
root.mainloop()