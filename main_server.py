################################
# Sockets Server 
# by Rohan Varma and Kyle Chin
# adapted and modified by Shu You 
#################################

import socket
import threading
import random
from queue import Queue
from base64 import *

HOST = "127.0.0.1" # IP address
PORT = 50013
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(BACKLOG)
print("looking for connection")

def handleClient(client, serverChannel, cID, clientele):
    client.setblocking(1)
    msg = ""
    while True:
        try:
            msg += b64decode(client.recv(8192)).decode()
            
            command = msg.split("\n")
            while (len(command) > 1):
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                serverChannel.put(str(cID) + " " + readyMsg)
                command = msg.split("\n")
        except:
            # we failed
            return

def serverThread(clientele, serverChannel):
    while True:
        msg = serverChannel.get(True, None)
        temp = msg.split()                      

        if ((temp[1] == "userSaid") or (temp[1] == "requestImg") or 
            (temp[1] == "newProfile") or (temp[1] == "imgMsg")): 
            # send messages to selected user
            if (temp[1] != "newProfile" and temp[1] != "imgMsg"):
                print("msg recv: ", msg)            
            msgList = msg.split(" ")
            senderID = msgList[0]
            instruction = msgList[1]            
            receiverID = msgList[2]
            details = " ".join(msgList[3:])            
            if (details != ""):                
                cID = receiverID
                if cID != senderID:                    
                    sendMsg = (instruction + " " + senderID + " " + details + 
                              "\n")
                    print(sendMsg)
                    clientele[cID].send(b64encode(sendMsg.encode("utf8")))
                    if (temp[1] != "newProfile" and temp[1] != "imgMsg"):
                        print("> sent to %s:" % cID, sendMsg[:-1])
            if (temp[1] != "newProfile" and temp[1] != "imgMsg"):                        
                print()

        else: 
            # forward messages to all users
            if temp[1] != "imgMsgGroup":
                print("msg recv: ", msg)                      
            msgList = msg.split(" ")
            senderID = msgList[0]
            instruction = msgList[1]
            details = " ".join(msgList[2:])            
            if (details != ""):
                for cID in clientele:               
                    if cID != senderID:
                        sendMsg = (instruction + " " + senderID + " " + details 
                                  + "\n")
                        clientele[cID].send(b64encode(sendMsg.encode("utf8")))
                        if temp[1] != "imgMsgGroup":
                            print("> sent to %s:" % cID, sendMsg[:-1])
            if temp[1] != "imgMsgGroup":
                print()
        serverChannel.task_done()

clientele = dict()
playerNum = 0

serverChannel = Queue(100)
threading.Thread(target=serverThread, args=(clientele, serverChannel)).start()

names = ["Player1", "Player2", "Player3", "Player4"]


while True:
    client, address = server.accept()
    # myID is the key to the client in the clientele dictionary
    myID = names[playerNum]
    print(myID, playerNum)    
    for cID in clientele:
        print (repr(cID), repr(playerNum))
        clientele[cID].send(b64encode(("newPlayer %s\n"%myID).encode("utf8")))
        client.send(b64encode(("newPlayer %s\n" % cID).encode("utf8")))
    clientele[myID] = client
    #client.send(("myIDis %s \n" % myID).encode())
    client.send(b64encode(("myIDis %s \n" % myID).encode("utf8")))
    print("connection recieved from %s" % myID)
    threading.Thread(target = handleClient, args = 
                        (client ,serverChannel, myID, clientele)).start()
    playerNum += 1
