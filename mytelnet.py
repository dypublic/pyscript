'''
Created on Mar 19, 2013

@author: daiyue
'''
#import getpass
import sys, os , time , random
import telnetlib
import multiprocessing
import Queue
from multiprocessing import Process, Lock
import threading
from threading import Thread
import Tkinter as tk


'''defaulttext = ["sounder 2215 pssIntervalFast 1 on",
               "sounder 2215 pssIntervalMiddle 1 on",
               "sounder 2215 pssIntervalSlow 1 on",
               "sounder 2215 pssClick 1 on",
               "sounder 2215 pssClick 1 off"]'''
defaulttext = ["userinterface 10800 SetSounders on pssTemplate 1",
               "userinterface 10800 SetSounders on pssClick 1",
               "userinterface 10800 SetSounders on pssOneBeep 1",
               "userinterface 10800 SetSounders on pssTwoBeeps 1",
               "userinterface 10800 SetSounders on pssThreeBeeps 1",
               
               ]

"""defaulttext = ["keyboard 10800 SetLED 3 on 4",
               "keyboard 10800 SetLED 4 on 5",
               "keyboard 10800 SetLED 3 on 11",
               "keyboard 10800 SetLED 4 on 12",
               "keyboard 10800 SetLED 5 on lsLedAlternateRed"]
           """    
#defaulttext = ["led 1 1 0",
#               "led 1 1 1",
#               "led 1 1 2",
#               "led 1 0 1",
#               "led 0 1 0"]
#a = {"a":4, "ahfkja":3.3,"fff":defaulttext}



    
# def inputUpdate(ent,text):
#     ent.delete(0, tk.END)
#     ent.insert(0,text)
    
# def textUp(text,recvq,stop):
#     while(not stop.is_set()):
#         #print("in textup\n")
#         try:
#             getstr = recvq.get(True,1)
#         except Queue.Empty:
#             continue
#         text.addtext(getstr)

class ScrolledText(tk.Frame):
    def __init__(self, parent=None, text=''):
        tk.Frame.__init__(self, parent)
        self.pack(expand=tk.YES, fill=tk.BOTH)
        # make me expandable
        self.makewidgets()
        self.settext(text)
    def makewidgets(self):
        sbar = tk.Scrollbar(self)
        text = tk.Text(self, relief=tk.SUNKEN)
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)
        text.config(height=20, width = 80 ,font=('times', 14))
        sbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        
        self.text = text

    def settext(self, text=''): # delete current text

        self.text.delete('1.0', tk.END) # save user a click
        self.text.insert('1.0', text) 
        #self.text.mark_set(tk.INSERT, '1.0') 
        #self.text.focus() 
    def addtext(self, text=''): # delete current text

        #self.text.delete('1.0', tk.END) # save user a click
        #print(list(text))
        self.text.insert(tk.END, text) 
        self.text.see(tk.END)
        #self.text.mark_set(tk.INSERT, tk.END) 


           
def makeinput(root,callback,defaulttext):
    row = tk.Frame(root)
    row.pack(fill=tk.X)

    entry = tk.Entry(row) # set text
    entry.config(width=70)
    entry.insert(0, defaulttext) # grow horiz
    entry.pack(side=tk.LEFT, fill=tk.X) 
    #entry.grid()
    entry.focus()
    entry.bind('<Return>', (lambda:callback(entry)))
    
    btn = tk.Button(row, text='OK', command= (lambda:callback(entry)))
    btn.pack(side=tk.RIGHT)
    
def console_sender(stdin,sender):
    nonerecv = 0
    while(1):
        getcmd =  stdin.readline()
        if not getcmd:
            nonerecv += 1
            if nonerecv == 100: break
        nonerecv = 0
        print getcmd
        sender(getcmd)
#recv from telenet and trans to recvqueue
# def receiver(teln, recvq):
#     nonerecv = 0
#     while(1):
#         #getstr = read_eager()
#         #getstr = teln.read_very_lazy()
#         #getstr = teln.read_all()
#         if teln:
#             getstr = teln.read_some()
#         else:
#             time.sleep(1)
#             continue
#         if not getstr:
#             nonerecv += 1
#             if nonerecv == 100: 
#                 print ('recv too much null char\n')
#                 break
#             continue
#         nonerecv = 0
#         recvq.put(getstr)
#         print ('recv:'+getstr)
#get string form sender queue then send out and updata GUI
# def telnetsender(senderq,telenet,textgui,stop):
#     while(not stop.is_set()):
#         #print("in textup\n")
#         try:
#             getstr = senderq.get(True,1)
#         except Queue.Empty:
#             continue
#         if telenet:
#             telenet.write(getstr+'\n')
#             textgui.addtext(getstr+'\n');
#         else:
#             print("none telent")
#         



class telnet:
    def __init__(self,host = None,text = None):
        self.__text = text
        self.__telnet = None
        self.__host = host
        self.__recvtelq = multiprocessing.Queue()
        #self.__sendtelq = multiprocessing.Queue()
        self.__lock = Lock()
        self.__stop= threading.Event()
        self.__recvthread = Thread(target=self.__recvtelenet)
        self.__recvthread.daemon = True
    def set(self,host):
        self.__host = host
    def start(self):
        if self.__host:
            self.__telnet = telnetlib.Telnet(*self.__host)
            self.__recvthread.start()
        else:
            print("no ip addr")
    def stop(self):
        self.__telnet.close()
        self.__stop.set()
    def send(self,msg):
        with self.__lock:
            if self.__telnet:
                self.__telnet.write(msg + '\n');
            if self.__text:
                self.__text(msg + '\n')

    def __recvtelenet(self):
        nonerecv = 0
        while(not self.__stop.is_set()):
            if self.__telnet:

            #getstr = read_eager()
            #getstr = teln.read_very_lazy()
            #getstr = teln.read_all()
                msg = self.__telnet.read_some()
                #print msg
            else:
                time.sleep(1)
                continue
            if not msg:
                nonerecv += 1
                if nonerecv == 1000: 
                    print ('recv too much null char\n')
                    break
                continue
            nonerecv = 0
            #print msg
            self.__recvtelq.put(msg)
            print msg
            self.__text(msg+'\n')
    def recv(self,timeout = None):
        return self.__recvtelq.get(True, timeout)

            
def sendout(sender):
    def entrysender(entry):
        instr = entry.get()
        sender(instr)
    return entrysender
def setIP(telnetIPseter):
    def IPset(entry):
        instr = entry.get()
        host = instr.splite(':')
        telnetIPseter(host[0], int(host[1]))
    return IPset
def cmd(sender):
    cmds=["userinterface 10800 SetSounders on pssTemplate 1",
           "userinterface 10800 SetSounders on pssClick 1",
           "userinterface 10800 SetSounders on pssOneBeep 1",
           "userinterface 10800 SetSounders on pssTwoBeeps 1",
           "userinterface 10800 SetSounders on pssThreeBeeps 1",
           "userinterface 10800 SetSounders on pssIntervalFast 1",
           "userinterface 10800 SetSounders on pssStatic 1"]
    while(1):
        i = random.randrange(0, len(cmds))
        #for i in cmds:
        sender(cmds[i]+'\n');
        timelen = random.random()
        time.sleep(timelen)
        print i, timelen
        
    
def main():
    HOST = ("192.168.1.102",12346)
    useConsoleInput = False
    testscrip = True
    #HOST = ("127.0.0.1",22)
    #mytelnet = None
    
    
    #recvtelq = multiprocessing.Queue()
    #sendtelq = multiprocessing.Queue()
    
    root = tk.Tk()
    makeinput(root,setIP,HOST[0]+':'+str(HOST[1]))
    textwigdet = ScrolledText(root)
    
    mytelnet = telnet(HOST,textwigdet.addtext)
        
    for i in range(len(defaulttext)):
        makeinput(root,sendout(mytelnet.send),defaulttext[i])
    if testscrip:
        testcmd = Thread(target=cmd,args=(mytelnet.send,))
        testcmd.daemon = True
        testcmd.start()
        


    #pRecv = Process(target=receiver, args=(telnet,recvtelq))
    #pRecv.start()
    #teGuiUpdata_stop= threading.Event()
    #updata text area from a queue
    #tGuiUpdata = Thread(target=textUp, args=(textwigdet,recvtelq,teGuiUpdata_stop))
    #tGuiUpdata.start()
    
    
    if useConsoleInput:
        newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
        try: 
            pGetCMD = Process(target=console_sender, args=(newstdin,mytelnet.send))
            pGetCMD.start()    
        finally:
            newstdin.close()

    mytelnet.start()
    tk.mainloop()
    print("after mainloop\n")
    
    mytelnet.stop()
#    teGuiUpdata_stop.set()
#    pRecv.terminate()
    if useConsoleInput:
        pGetCMD.terminate()
#    telnet.close()
    #pRecv.join()
    #pGetCMD.join()


#print telnet.read_all()
if __name__ == '__main__':
    main()
