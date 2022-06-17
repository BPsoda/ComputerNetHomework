import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as msgbox
from tkinter import scrolledtext  
from message_tree import *
def 发帖():
    title=e1.get()
    description=e2.get(0.0,tk.END)
    ################################
    print([title,description])
    ################################
    msgbox.showinfo('信息', '发帖成功')
    e1.delete(0,tk.END)
    e2.delete(0.0,tk.END)
    tabControl.select(tab2)
viewing=None
def 回帖():
    content=text_input.get(0.0,tk.END)
    text_input.delete(0.0,tk.END)
    ###############################
    
    ###############################
mt=messageTree()
mt.constructTree()


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

for node in mt.nodeList:
    tree.insert(node.parentId if node.parent!=None else '',tk.END,text="Node",iid=node.id,values=node.id,open=False)
tree.grid(row=0, column=0,ipady=80,rowspan=2)
def select_tree():
    for item in tree.selection():
        id=tree.item(item, "values")[0]
        viewing=id
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