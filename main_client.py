#################################
# Sockets Client 
# by Rohan Varma and Kyle Chin
# adapted and modified by Shu You
#################################

import socket
import threading
from queue import Queue
from base64 import *

HOST = "127.0.0.1" # IP address
PORT = 50013

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

server.connect((HOST,PORT))
print("connected to server")

def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += b64decode(server.recv(1024)).decode()
        
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverMsg.put(readyMsg)
            command = msg.split("\n")

# events-example0.py from 15-112 website
# adapted and modified by Shu You

from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import Image
from PIL import ImageTk
from PIL import ImageFile
import random, time
import speech_recognition as sr

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.LOAD_TRUNCATED_IMAGES = True
ImageTk.LOAD_TRUNCATED_IMAGES = True

#################################
# event based animation
#################################

def init(data):

    # init users
    data.myPID = "ME"
    
    # init main screen objects' property 
    data.buttonColor="#F0F0F0"
    data.sendColor = "black"
    data.lineColor = "black"
    data.buttonWidth = data.width/8 + 30
    data.buttonHeight = 40
    data.buttonX = data.width3-10
    data.buttonY = data.height3 - 5
    data.message = dict()
    data.message["myself"] = []
    data.message["group"] = []    
    data.wordLength = 34
    data.scrollSpeed = 50
    data.fontSize = 12
    data.font = "Noto Mono"    
    data.margin = 20
    data.offset = dict()
    data.offset["group"] = 40
    data.inputBar = 70
    data.currentPage = 0
    data.selectColor = "#0077FF"
    data.currentUser = "myself"
    data.checkedGrid = set()  
    data.imageIcon = "" 
    data.voiceIcon = ""
    data.buttonIcon = ""
    data.voiceIconSource = "img/microphone.png"
    data.listenIconSource = "img/microphone.png"
    data.imageIconSource = "img/imgMsg.png"
    data.voiceInputScreenOn = False
    data.recording = False
    data.voiceWidgetBuffer = 0

    # init user related info
    data.newPosition = dict()
    data.newPosition["group"] = 0
    data.sumPosition = dict() 
    data.sumPosition["group"] = 0   
    data.contactList = [["group","Group",True]]
    data.rMe = 35
    data.gridNum = -1
    data.bgUser = set()
    data.currentProfile = "" 
    data.displayName = ""
    data.profilePic = ""   
    data.selectProfileColor = "#F0F0F0" 
    data.check = 0
    data.warning = False

#################################
# control group 
#################################

def mousePressed(event, entry, data, nameEntry, welcome):
    
    msg = ""
    # event x and y handling cited from https://stackoverflow.com/
    # questions/22925599/
    # mouse-position-python-tkinter
    x = event.x_root-data.root.winfo_rootx()
    y = event.y_root-data.root.winfo_rooty()
    
    if (x>=data.width-10-data.buttonWidth and x<=data.width-10
        and y>=data.height-5-data.buttonHeight and y<=data.height-5):
            if entry.get() != "":
                data.buttonColor = "#4070f5" #click blue        

    # choose user
    if x >= 0 and x <= 100 and y >= 100:        
        totalGrids = len(data.contactList)
        currentGrid = y // 100
        if (currentGrid <= totalGrids and currentGrid != data.currentPage and 
            data.contactList[currentGrid-1][1] != ""):
            data.gridNum = currentGrid
            data.currentPage = data.gridNum
            entry.delete(0, END)            

            # request profile picture option
            if (data.message[data.contactList[currentGrid-1][0]] == [] and
                currentGrid not in data.checkedGrid):
                if currentGrid != 1:
                    targetuser = data.contactList[currentGrid-1][0] 
                    msg = "requestImg %s %s\n" % (targetuser, "requestImg")
                    data.server.send(b64encode(msg.encode("utf-8")))
                    data.checkedGrid.add(currentGrid)
        else:
            data.gridNum = -1
    else:
        data.gridNum = -1

    if x >= 0 and x <= 100 and y <= 100:
        if data.currentPage != 0:
            data.currentPage = 0
            entry.delete(0, END)
    else:
        data.gridNum = -1

    if event.widget == nameEntry:
        nameEntry.delete(0, "end")
        nameEntry.config(fg="black")

    # click on profile picture
    if (x >= data.width//2-110 and y >= data.height*2//5-110 and 
        x <= data.width//2+110 and y <= data.height*2//5+110 and
        event.widget == welcome and data.warning == False):
        filename = askopenfilename(initialdir = "/",title = "Select Profile",
                filetypes = (("png files","*.png"),("jpeg files","*.jpg")))
        if filename != "":
            data.profilePic = filename 

def mouseReleased(event, entry, data, welcome):
    msg = ""
    # event x and y handling cited from https://stackoverflow.com/
    # questions/22925599/
    # mouse-position-python-tkinter
    x = event.x_root-data.root.winfo_rootx()
    y = event.y_root-data.root.winfo_rooty()    

    if (x>=data.width-10-data.buttonWidth and x<=data.width-10
        and y>=data.height-5-data.buttonHeight and y<=data.height-5 and 
        event.widget != welcome):
        if entry.get() != "":      
            message = entry.get().strip()
            data.message[data.currentUser].append([message,data.displayName])
            newLabel = drawScratchLabel(data, message)            
            calcLabelSize(newLabel, data, data.currentUser)            
            addPosition(data, data.currentUser)            
            if data.currentUser != "group":          
                msg = "userSaid %s %s\n" % (data.currentUser,message) 
            else:
                msg = "userSaidGroup %s\n" % message
            entry.delete(0, END)
            data.buttonColor = "#F0F0F0"
            data.sendColor = "black"  

    if data.currentPage == 0:
        data.buttonColor = "white"
        data.sendColor = "white"
        data.lineColor = "white"
        entry.lower()
    elif data.currentPage != 0:
        if data.buttonColor == "white":
            data.buttonColor = "#F0F0F0"
            data.sendColor = "black"
            data.lineColor = "black"
            entry.lift()

    # handle voice input screen
    if (event.widget != data.voiceWidget and data.voiceInputScreenOn == True):
        data.voiceWidgetBuffer = 0
        data.voiceInputScreenOn = False
        
    # click on voice input icon
    if (x>=data.width-10-data.buttonWidth-50 and x<=data.width-data.buttonWidth
        -20 and y>=data.height-5-data.buttonHeight and y<=data.height-5 and 
        event.widget != welcome and data.voiceInputScreenOn == False):
        data.voiceInputScreenOn = True
        data.voiceIconSource = "img/microphone.png" 
        data.voiceWidgetBuffer += 1  

    # click on image message
    if (x>=105 and x<=140
        and y>=data.height-5-data.buttonHeight and y<=data.height-5 and 
        event.widget != welcome and data.voiceInputScreenOn == False):
        file = askopenfilename(initialdir = "/",title = "Select Profile",
                filetypes = (("png files","*.png"),))  
        filename = nameGenerator() 
        item = readImg(file)
        writeImg(item, filename)

        data.message[data.currentUser].append([filename,data.displayName,"img"])
        calcImgSize("imgMsg/"+filename, data, data.currentUser)
        addPosition(data, data.currentUser)        
        data.imageIconSource = "img/imgMsg.png"
        if data.currentUser != "group":          
            msg = "imgMsg %s %s %s\n" % (data.currentUser, 
                                    readImg("imgMsg/"+filename), filename) 
        else:
            msg = "imgMsgGroup %s %s\n" % (readImg("imgMsg/"+filename),filename)

    # send the message to other players!
    if (msg != ""):
        if not (msg.split(" ")[0] == "imgMsg" or 
                msg.split(" ")[0] == "imgMsgGroup"):
            print ("sending: ", msg,)
        data.server.send(b64encode(msg.encode("utf-8")))

def mouseMotion(event, data, welcome):    
    # event x and y handling cited from https://stackoverflow.com/
    # questions/22925599/
    # mouse-position-python-tkinter
    x = event.x_root-data.root.winfo_rootx()
    y = event.y_root-data.root.winfo_rooty()   

    if x >= 0 and x <= 100 and y > 100:        
        totalGrids = len(data.contactList)
        currentGrid = y // 100
        if (currentGrid <= totalGrids and currentGrid != data.currentPage and 
            data.contactList[currentGrid-1][1] != ""):
            data.gridNum = currentGrid
        else:
            data.gridNum = -1
    elif x >= 0 and x <= 100 and y <= 100:
        if data.currentPage != 0:
            data.gridNum = 0
        else:
            data.gridNum = -1
    else:
        data.gridNum = -1

    if (x >= data.width//2-110 and y >= data.height*2//5-110 and 
        x <= data.width//2+110 and y <= data.height*2//5+110 and
        event.widget == welcome and data.profilePic == ""):
        data.selectProfileColor = "#dddddd"
    else:
        data.selectProfileColor = "#F0F0F0"

    # hover over voice input button   
    if (x>=data.width-10-data.buttonWidth-50 and x<=data.width-data.buttonWidth
        -20 and y>=data.height-5-data.buttonHeight and y<=data.height-5 and 
        event.widget != welcome and data.voiceInputScreenOn == False):
        data.voiceIconSource = "img/microphone1.png"
    else:
        data.voiceIconSource = "img/microphone.png"

    # hover over image message button
    if (x>=105 and x<=140
        and y>=data.height-5-data.buttonHeight and y<=data.height-5 and 
        event.widget != welcome and data.voiceInputScreenOn == False):
        data.imageIconSource = "img/imgMsg1.png"
    else:
        data.imageIconSource = "img/imgMsg.png"

def mouseWheel(event, data):   

    user = data.currentUser
    if data.warning == True or data.welcomeDestroy == False:
        return

    if event.delta < 0:
        if data.sumPosition[user] > (data.height-data.inputBar):
            dy = (data.sumPosition[user] + data.offset[user] - 
                 (data.height-data.inputBar))
            if dy > data.scrollSpeed:
                data.offset[user] -= data.scrollSpeed
            elif dy >= 0:
                data.offset[user] -= dy
            else:
                return 

    if event.delta > 0:
        if data.offset[user] < 40:
            temp = data.offset[user]
            if temp + data.scrollSpeed > 0:
                data.offset[user] = 40
            else:
                data.offset[user] += data.scrollSpeed

def keyPressed(event, entry, data, nameEntry):    
    msg = ""
    user = data.currentUser   

    if entry.get() != "":
        data.buttonColor = "#4086F5"
        data.sendColor = "white"
    else:
        if data.buttonColor != "white":
            data.buttonColor = "#F0F0F0"
            data.sendColor = "black"

    if (event.keysym == "Return") and (event.widget==entry):        
        if entry.get() != "":
            message = entry.get().strip()
            data.message[data.currentUser].append([message,data.displayName])
            newLabel = drawScratchLabel(data, message)            
            calcLabelSize(newLabel, data, data.currentUser)            
            addPosition(data, data.currentUser)  
            if data.currentUser != "group":          
                msg = "userSaid %s %s\n" % (data.currentUser,message) 
            else:
                msg = "userSaidGroup %s\n" % message
            entry.delete(0, END)
            data.buttonColor = "#F0F0F0"
            data.sendColor = "black"
            data.server.send(b64encode(msg.encode("utf-8")))
            print ("sending: ", msg,)

    if (event.widget == nameEntry):
        data.displayName = nameEntry.get()

    if (event.widget == nameEntry) and (event.keysym == "Return"):        
        if isLegalName(data):                       
            data.displayName = nameEntry.get()
            nameEntry.destroy()
            data.warning = True   
            msg = "ready %s\n" % data.myPID       
            data.server.send(b64encode(msg.encode("utf-8")))
        else:
            return

    if (event.keysym == "F5" and data.warning == True):
        data.check += 1
        if data.check == 1:
            data.welcomeDestroy = True

    if event.keysym == "F5":
        # send user name to the server
        msg = "userOnline %s\n" % data.myPID       
        data.server.send(b64encode(msg.encode("utf-8"))) 
        msg = "newName %s\n" % data.displayName
        data.server.send(b64encode(msg.encode("utf-8")))          

    if (event.keysym == "Down" and data.warning == False 
        and data.welcomeDestroy == True):        
        if data.sumPosition[user] > (data.height-data.inputBar):
            dy = (data.sumPosition[user] + data.offset[user] - 
                 (data.height-data.inputBar))
            if dy > data.scrollSpeed:
                data.offset[user] -= data.scrollSpeed
            elif dy >= 0:
                data.offset[user] -= dy
            else:
                return 

    if (event.keysym == "Up" and data.warning == False 
        and data.welcomeDestroy == True): 
        if data.offset[user] < 40:
            temp = data.offset[user]
            if temp + data.scrollSpeed > 0:
                data.offset[user] = 40
            else:
                data.offset[user] += data.scrollSpeed
            
def timerFired(data, entry):
    # timerFired receives instructions and executes them

    # init speech recognition
    if data.voiceWidgetBuffer == 2 and data.recording == False:
        data.recording = True
        content = speechRecognition(data)
        if content != None:
            words = content.split()
            if words[0] in ["how","what","why","where","who","can","could",
                "is","am","are"]:
                entry.insert(END, "%s%s? "%(content[0].upper(), content[1:]))
            else:
                entry.insert(END, "%s%s. "%(content[0].upper(), content[1:]))
        data.voiceWidgetBuffer = 0
        data.voiceInputScreenOn = False
        data.recording = False

    if data.currentUser in data.bgUser:
        data.bgUser.remove(data.currentUser)    
    if data.currentPage != 0:
        data.currentUser = data.contactList[data.currentPage-1][0]
    else:
        data.currentUser = "myself"

    if (serverMsg.qsize() > 0):
        msg = serverMsg.get(False)
        try:
            msg = msg.split(" ", 2)
            command = msg[0]
            if not (command == "newProfile" or command == "imgMsg" 
                    or command == "imgMsgGroup"):
                print("received: ", msg, "\n")
        
            if (command == "myIDis"):
                myPID = msg[1]
                data.myPID = myPID

            if (command == "newPlayer"):  
                pass

            if (command == "ready"):  
                msg = "userOnline %s\n" % data.myPID       
                data.server.send(b64encode(msg.encode("utf-8"))) 
                msg = "newName %s\n" % data.displayName
                data.server.send(b64encode(msg.encode("utf-8")))

            if (command == "requestImg"):
                PID = msg[1]
                if data.profilePic != "":
                    msg = "newProfile %s %s\n" % (PID, readImg(data.profilePic))
                    data.server.send(b64encode(msg.encode("utf-8")))

            if (command == "userOnline"):
                PID = msg[1]             
                if isIdDuplicate(data, PID) == False:
                    data.contactList.append([PID,""])
                if PID not in data.message.keys():
                    data.message[PID] = []
                if PID not in data.newPosition.keys():
                    data.newPosition[PID] = 0
                if PID not in data.sumPosition.keys():
                    data.sumPosition[PID] = 0
                if PID not in data.offset.keys():
                    data.offset[PID] = 40        

            if (command == "newName"):
                PID = msg[1]
                item = msg[2]
                addDisplayName(data, PID, item)

            if (command == "newProfile"):
                PID = msg[1]
                item = msg[2]
                writeProfileImg(item, PID)
                addProfilePic(data,PID)            

            if (command == "userSaid"):
                PID = msg[1]                
                item = msg[2]     
                data.message[PID].append([item,"you"])
                newLabel = drawScratchLabel(data, item)
                calcLabelSize(newLabel, data, PID)
                addPosition(data, PID) 
                if data.currentUser != PID:
                    data.bgUser.add(PID)  

            if (command == "imgMsg"):
                PID = msg[1]
                file = msg[2].split(" ")[0]
                filename = nameGenerator()
                writeImg(file, filename, False)
                data.message[PID].append([filename,"you","img"])
                calcImgSize("imgMsg/"+filename, data, PID)
                addPosition(data, PID) 
                if data.currentUser != PID:
                    data.bgUser.add(PID)  

            if (command == "userSaidGroup"):
                PID = "group" 
                userID = msg[1]              
                item = msg[2]     
                data.message[PID].append([item,userID])
                newLabel = drawScratchLabel(data, item)
                calcLabelSize(newLabel, data, PID)
                addPosition(data, PID) 
                if data.currentUser != PID:
                    data.bgUser.add(PID)

            if (command == "imgMsgGroup"):
                PID = "group"
                userID = msg[1]
                file = msg[2].split(" ")[0]
                filename = nameGenerator()
                writeImg(file, filename, False)
                data.message[PID].append([filename,userID,"img"])
                calcImgSize("imgMsg/"+filename, data, PID)
                addPosition(data, PID)
                if data.currentUser != PID:
                    data.bgUser.add(PID) 

        except:
            print("failed") 

        serverMsg.task_done()

#################################
# helper functions group 
# general calculation and handling
#################################

def changePID(data, PID):
    pass

def calcLabelSize(label, data, user):
    # calculate the dimension of the label
    # modify offset and position if necessary 
    temp = data.scratch.create_window(0,0,window=label)
    labelHeight = data.scratch.bbox(temp)[3] - data.scratch.bbox(temp)[1]
    data.newPosition[user] = data.sumPosition[user] + labelHeight + data.margin
    data.sumPosition[user] = data.newPosition[user]
    if ((data.sumPosition[user] + data.offset[user]) > 
       (data.height2 - data.margin)):
        data.offset[user] -= ((data.sumPosition[user] + data.offset[user]) - 
                       (data.height2 - data.margin))

def calcImgSize(filename, data, user):
    im1 = Image.open(filename)
    imgMsg = ImageTk.PhotoImage(im1)
    label = Label(image=imgMsg)
    label.image = imgMsg
    imgWidth = imgMsg.width()
    imgHeight = imgMsg.height()

    data.newPosition[user] = data.sumPosition[user] + imgHeight + data.margin
    data.sumPosition[user] = data.newPosition[user]
    if ((data.sumPosition[user] + data.offset[user]) > 
       (data.height2 - data.margin)):
        data.offset[user] -= ((data.sumPosition[user] + data.offset[user]) - 
                       (data.height2 - data.margin))   

def addPosition(data, PID):  
    data.message[PID][-1].insert(2, data.newPosition[PID]) 

def addNewLabel(data, PID, label):
    data.message[PID][-1].append(label)

def isLegalName(data):
    if (len(data.displayName) < 2 or len(data.displayName) > 14): 
        return False    
    return True

def isIdDuplicate(data,id):
    # check duplicate user names in contactlist
    for ids in data.contactList:
        if id == ids[0]:
            return True
    return False
        
def addDisplayName(data, PID, displayName):
    # add displace to contactlist which contains system id
    for ids in data.contactList:
        if PID == ids[0] and len(ids) == 2:
            ids.insert(1, displayName)

def addProfilePic(data, PID):
    for ids in data.contactList:
        if PID == ids[0] and len(ids) == 3:
            ids[2] = True

def hasProfile(data, userName):
    for ids in data.contactList:
        if ids[0] == userName:
            return ids[2] != ""

def findDisplayName(data, PID):
    for ids in data.contactList:
        if ids[0] == PID:
            return ids[1]

def readImg(path):        
    with open(path, "rb") as f:
        file = b64encode(f.read())
    return str(file)            

def writeImg(item, filename, compress=True):
    fp = open("imgMsg/%s" % filename,"wb")    
    content = item.split("'")[1]
    fp.write(b64decode(bytes(content, encoding="utf-8")))

    if compress == True:
        foo = Image.open("imgMsg/%s" % filename)
        img = ImageTk.PhotoImage(foo)
        scaleWidth = img.width()//(img.width()//200 + 1)
        scaleHeight = img.height()//(img.width()//200 + 1)

        foo = foo.resize((scaleWidth,scaleHeight),Image.ANTIALIAS)
        foo.save("imgMsg/%s" % filename,quality=85)       

def writeProfileImg(item, user):
    filename = "profilePic/%s.png" % user
    fp = open(filename,"wb")
    content = item.split("'")[1]
    fp.write(b64decode(bytes(content, encoding="utf-8")))
    # image compression
    # cited from https://stackoverflow.com/questions/
    # 10607468/how-to-reduce-the-image-file-size-using-pil
    foo = Image.open(filename)
    foo = foo.resize((250,250),Image.ANTIALIAS)
    foo.save(filename,quality=85)

def speechRecognition(data):
    # method cited from https://pythonspot.com/en/
    # speech-recognition-using-google-speech-api/
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:        
        print("You said: " + r.recognize_google(audio))
        return r.recognize_google(audio)

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print('''Could not request results from Google Speech Recognition 
                 service; {0}'''.format(e))

def nameGenerator(n=""):
    # generate a random file name 
    if len(n) > 10:
        return n+".png"
    else:
        seq = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f",
        "g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x",
        "y","z"]
        n += random.choice(seq)
        return nameGenerator(n)   

#################################
# draw/view group 
#################################

def drawScratchLabel(data, message):
    # draw a temporary label on scratch paper for dimension calculation
    if len(message) <= data.wordLength:
        boxWidth = len(message)
    else:
        boxWidth = data.wordLength
    if len(message) % data.wordLength == 0:
        boxHeight = len(message)//data.wordLength
    else:
        boxHeight = len(message)//data.wordLength + 1
    newLabel = Text(data.scratch, wrap=WORD)
    newLabel.config(font=(data.font, data.fontSize),width=boxWidth, 
                    height=boxHeight)
    newLabel.insert(INSERT, message)
    newLabel.config(state=DISABLED)
    return newLabel

def drawTextInput(data, frame2):
    # handle conversation bubble
    user = data.currentUser
    if user == "group":
        return
    for i in range(len(data.message[user])):                
        message = data.message[user][i][0]        
        if len(message) <= data.wordLength:
            boxWidth = len(message)
        else:
            boxWidth = data.wordLength
        if len(message) % data.wordLength == 0:
            boxHeight = len(message)//data.wordLength
        else:
            boxHeight = len(message)//data.wordLength + 1
        if data.message[user][i][1] == data.displayName:
            if len(data.message[user][i]) == 3:        
                newLabel = Text(frame2,font=(data.font, data.fontSize),
                                width=boxWidth, height=boxHeight,bg="#0084FF",
                                fg="white",relief=FLAT,padx=10,pady=5,wrap=WORD)
                newLabel.insert(INSERT, message)
                newLabel.config(state=DISABLED)        
                newLabel.place(x=data.width2-10,y=data.message[user][i][2]+
                               data.offset[user],anchor=SE) 
            else:
                # draw image msg
                try:
                    im1 = Image.open("imgMsg/"+message)
                    imgMsg = ImageTk.PhotoImage(im1)
                    label = Label(frame2, image=imgMsg)
                    label.image = imgMsg
                    label.place(x=data.width2-10,y=data.message[user][i][2]+
                                   data.offset[user]-6,anchor=SE)
                except:
                    im1 = Image.open("img/loading.png")
                    imgMsg = ImageTk.PhotoImage(im1)
                    label = Label(frame2, image=imgMsg)
                    label.image = imgMsg
                    label.place(x=data.width2-10,y=data.message[user][i][2]+
                                   data.offset[user]-6,anchor=SE)

        else:
            if len(data.message[user][i]) == 3:
                newLabel = Text(frame2,font=(data.font, data.fontSize),
                                width=boxWidth, height=boxHeight,bg="#F0F0F0",
                                fg="black",relief=FLAT,padx=10,pady=5,wrap=WORD)
                newLabel.insert(INSERT, message)
                newLabel.config(state=DISABLED)
                newLabel.place(x=10,y=data.message[user][i][2]+data.offset[user]
                               ,anchor=SW) 
            else:
                # draw image msg
                try:
                    im1 = Image.open("imgMsg/"+message)
                    imgMsg = ImageTk.PhotoImage(im1)
                    label = Label(frame2, image=imgMsg)
                    label.image = imgMsg
                    label.place(x=10,y=data.message[user][i][2]+
                                   data.offset[user]-6,anchor=SW)
                except:
                    im1 = Image.open("img/loading.png")
                    imgMsg = ImageTk.PhotoImage(im1)
                    label = Label(frame2, image=imgMsg)
                    label.image = imgMsg
                    label.place(x=10,y=data.message[user][i][2]+
                                   data.offset[user]-6,anchor=SW)

def drawTextInputGroup(data, frame2):
    user = data.currentUser  
    canvas2 = Canvas(frame2,width=data.width2,height=data.height2,
                     bg="white")
    canvas2.place(x=-2,y=-1,anchor=NW)
    for i in range(len(data.message[user])):

        message = data.message[user][i][0] 
        userName = data.message[user][i][1]     
        if len(message) <= data.wordLength:
            boxWidth = len(message)
        else:
            boxWidth = data.wordLength

        if len(message) % data.wordLength == 0:
            boxHeight = len(message)//data.wordLength
        else:
            boxHeight = len(message)//data.wordLength + 1

        if data.message[user][i][1] == data.displayName:
            if len(data.message[user][i]) == 3:      

                newLabel = Text(frame2,font=(data.font, data.fontSize),
                                width=boxWidth, height=boxHeight,bg="#0084FF",
                                fg="white",relief=FLAT,padx=10,pady=5,wrap=WORD)
                newLabel.insert(INSERT, message)
                newLabel.config(state=DISABLED)        
                newLabel.place(x=data.width2-10-45,y=data.message[user][i][2]+
                               data.offset[user],anchor=SE) 
            else:
                # draw image msg
                try:
                    im1 = Image.open("imgMsg/"+message)
                    imgMsg = ImageTk.PhotoImage(im1)
                    label = Label(frame2, image=imgMsg)
                    label.image = imgMsg
                    label.place(x=data.width2-10-45+2,y=data.message[user][i][2]
                                +data.offset[user]-6,anchor=SE)
                except:
                    im1 = Image.open("img/loading.png")
                    imgMsg = ImageTk.PhotoImage(im1)
                    label = Label(frame2, image=imgMsg)
                    label.image = imgMsg
                    label.place(x=data.width2-10-45+2,y=data.message[user][i][2]
                                +data.offset[user]-6,anchor=SE)

            if data.profilePic != "":
                try:
                    im1 = Image.open("profilePic/%s.png" % data.myPID)
                    im1.resize((36,36),Image.ANTIALIAS)
                    im1.thumbnail((36,36),Image.ANTIALIAS)
                    profile = ImageTk.PhotoImage(im1)
                    label = Label(image=profile,bg="white")
                    label.image = profile
                    if i == 0:
                        canvas2.create_image(690,13+
                                    data.offset[user],image=profile,anchor=NE)
                    else:
                        canvas2.create_image(690,(data.message[user][i][2]+
                                data.offset[user])-(data.message[user][i][2]
                                -data.message[user][i-1][2])+data.margin/2+3,
                                image=profile,anchor=NE)  
                except:
                    if i == 0: 
                        canvas2.create_rectangle(654, 13+
                                    data.offset[user], 690, 49+
                                    data.offset[user], width = 0, 
                                                 fill="gray")
                        canvas2.create_text(672,31+data.offset[user],
                                text="%s%s"% (userName[0].upper(),
                                userName[-1].upper()),font=(data.font, "12"))
                    else:    
                        canvas2.create_rectangle(654, (data.message[user][i][2]+
                                    data.offset[user])-(data.message[user][i][2]
                                    -data.message[user][i-1][2])+data.margin/2
                                    +3,690, (data.message[user][i][2]+
                                    data.offset[user])-(data.message[user][i][2]
                                    -data.message[user][i-1][2])+data.margin/2
                                    +39,width = 0,fill="gray")  
                        canvas2.create_text(672, (data.message[user][i][2]+
                                    data.offset[user])-(data.message[user][i][2]
                                    -data.message[user][i-1][2])+data.margin/2
                                    +21, text="%s%s"%
                                    (userName[0].upper(),userName[-1].upper()),
                                    font=(data.font, "12"))
            elif i == 0: 
                canvas2.create_rectangle(654, 13+
                            data.offset[user], 690, 49+
                            data.offset[user], width = 0, 
                                         fill="gray")
                canvas2.create_text(672,31+data.offset[user],
                        text="%s%s"% (userName[0].upper(),
                        userName[-1].upper()),font=(data.font, "12"))
            else:    
                canvas2.create_rectangle(654, (data.message[user][i][2]+
                            data.offset[user])-(data.message[user][i][2]
                            -data.message[user][i-1][2])+data.margin/2
                            +3,690, (data.message[user][i][2]+
                            data.offset[user])-(data.message[user][i][2]
                            -data.message[user][i-1][2])+data.margin/2
                            +39,width = 0,fill="gray")  
                canvas2.create_text(672, (data.message[user][i][2]+
                            data.offset[user])-(data.message[user][i][2]
                            -data.message[user][i-1][2])+data.margin/2
                            +21, text="%s%s"%
                            (userName[0].upper(),userName[-1].upper()),
                            font=(data.font, "12")) 
        else:
            if len(data.message[user][i]) == 3:
                newLabel = Text(frame2,font=(data.font, data.fontSize),
                                width=boxWidth, height=boxHeight,bg="#F0F0F0",
                                fg="black",relief=FLAT,padx=10,pady=5,wrap=WORD)
                newLabel.insert(INSERT, message)
                newLabel.config(state=DISABLED)
                newLabel.place(x=10+45-5, y=data.message[user][i][2]+
                               data.offset[user], anchor=SW)
            else:
                # draw image msg
                try:
                    im1 = Image.open("imgMsg/"+message)
                    imgMsg = ImageTk.PhotoImage(im1)
                    label = Label(frame2, image=imgMsg)
                    label.image = imgMsg   
                    label.place(x=10+45-7, y=data.message[user][i][2]+
                                   data.offset[user]-6, anchor=SW)
                except:
                    im1 = Image.open("img/loading.png")
                    imgMsg = ImageTk.PhotoImage(im1)
                    label = Label(frame2, image=imgMsg)
                    label.image = imgMsg   
                    label.place(x=10+45-7, y=data.message[user][i][2]+
                                   data.offset[user]-6, anchor=SW)

            displayName = findDisplayName(data, userName)

            if hasProfile(data, userName):
                try:
                    im1 = Image.open("profilePic/%s.png" % userName)
                    im1.resize((36,36),Image.ANTIALIAS)
                    im1.thumbnail((36,36),Image.ANTIALIAS)
                    profile1 = ImageTk.PhotoImage(im1)
                    label = Label(image=profile1,bg="white")
                    label.image = profile1 
                    if i == 0:                         
                        canvas2.create_image(10,13+
                                    data.offset[user],image=profile1,anchor=NW)
                    else:  
                        canvas2.create_image(10,(data.message[user][i][2]+
                                data.offset[user])-(data.message[user][i][2]
                                -data.message[user][i-1][2])+data.margin/2+3,
                                image=profile1,anchor=NW) 
                except:
                    if i == 0: 
                        canvas2.create_rectangle(10, 13+data.offset[user], 46, 
                                                 49+data.offset[user], width=0, 
                                                 fill="gray")
                        canvas2.create_text(28,31+data.offset[user],text="%s%s"%
                            (displayName[0].upper(),displayName[-1].upper()),
                            font=(data.font, "12"))
                    else:    
                        canvas2.create_rectangle(10, (data.message[user][i]
                            [2]+data.offset[user])-(data.message[user][i][2]
                            -data.message[user][i-1][2])+data.margin/2
                            +3,46, (data.message[user][i][2]+
                            data.offset[user])-(data.message[user][i][2]
                            -data.message[user][i-1][2])+data.margin/2
                            +39,width = 0,fill="gray")  
                        canvas2.create_text(28, (data.message[user][i][2]+
                            data.offset[user])-(data.message[user][i][2]
                            -data.message[user][i-1][2])+data.margin/2
                            +21, text="%s%s"%
                            (displayName[0].upper(),displayName[-1].upper()),
                            font=(data.font, "12")) 
          
            elif i == 0: 
                canvas2.create_rectangle(10, 13+data.offset[user], 46, 
                                         49+data.offset[user], width=0, 
                                         fill="gray")
                canvas2.create_text(28,31+data.offset[user],text="%s%s"%
                    (displayName[0].upper(),displayName[-1].upper()),
                    font=(data.font, "12"))
            else:    
                canvas2.create_rectangle(10, (data.message[user][i]
                    [2]+data.offset[user])-(data.message[user][i][2]
                    -data.message[user][i-1][2])+data.margin/2
                    +3,46, (data.message[user][i][2]+
                    data.offset[user])-(data.message[user][i][2]
                    -data.message[user][i-1][2])+data.margin/2
                    +39,width = 0,fill="gray")  
                canvas2.create_text(28, (data.message[user][i][2]+
                    data.offset[user])-(data.message[user][i][2]
                    -data.message[user][i-1][2])+data.margin/2
                    +21, text="%s%s"%
                    (displayName[0].upper(),displayName[-1].upper()),
                    font=(data.font, "12")) 

def drawMainScreen(canvas3, data):
    # draw button and entry widget
    if data.currentPage != 0:
        canvas3.create_rectangle(data.buttonX-data.buttonWidth,
                                data.buttonY-data.buttonHeight,
                                data.buttonX,data.buttonY,width=0,
                                fill=data.buttonColor)
        canvas3.create_text(data.buttonX-data.buttonWidth/2,
                           data.buttonY-data.buttonHeight/2,text="Send",
                           font=(data.font, 12),fill=data.sendColor)
        canvas3.create_line(55,data.height3-5,data.width3-data.buttonWidth-15,
                            data.height3-5, fill=data.lineColor)

        # draw voice input button 
        # img from http://pixsector.com/icon/microphone-icon-png-vector/599
            
        im1 = Image.open(data.voiceIconSource)
        im1.resize((40,40),Image.ANTIALIAS)
        im1.thumbnail((40,40),Image.ANTIALIAS)
        voiceIcon = ImageTk.PhotoImage(im1)
        data.voiceIcon = Label(canvas3, image=voiceIcon, bg="white")
        data.voiceIcon.image = voiceIcon    
        data.voiceIcon.place(x=data.buttonX-data.buttonWidth-45,
            y=data.buttonY-data.buttonHeight-4,anchor=NW)

        # draw image message button
        # img from https://pixabay.com/zh/照片-图像-景观-图标-1103595/
        im2 = Image.open(data.imageIconSource)
        im2.resize((40,40),Image.ANTIALIAS)
        im2.thumbnail((40,40),Image.ANTIALIAS)
        imageIcon = ImageTk.PhotoImage(im2)
        data.imageIcon = Label(canvas3, image=imageIcon, bg="white")
        data.imageIcon.image = imageIcon    
        data.imageIcon.place(x=5,y=data.buttonY,anchor=SW)
   
    else:
        for child in canvas3.winfo_children():
            child.destroy()
        canvas3.delete(ALL)
    
def drawProfile(canvas, data):
    # draw my profile
    canvas.create_rectangle(50-data.rMe,50-data.rMe,52+data.rMe,52+data.rMe, 
                              fill="#F0F0F0",width=0)
    if data.displayName != "" and data.profilePic == "":
        canvas.create_text(51,51,text="%s%s"%(data.displayName[0].upper(),
                       data.displayName[-1].upper()),fill="black",
                       font=(data.font, 20))
    elif (data.displayName != "" and data.profilePic != "" and 
        data.welcomeDestroy == True):
        try:
            filename = "profilePic/%s.png" % data.myPID
            im1 = Image.open(filename)
            im1.thumbnail((72,72),Image.ANTIALIAS)
            profile = ImageTk.PhotoImage(im1)
            label = Label(image=profile)
            label.image = profile
            canvas.create_image(51,51,image=profile)
        except:
            canvas.create_text(51,51,text="%s%s"%(data.displayName[0].upper(),
                       data.displayName[-1].upper()),fill="black",
                       font=(data.font, 20))

def drawContact(canvas, data):
    # draw contacts on the side bar
    gridNum = 1
    margin = 15    
    r = 35
  
    for people in data.contactList:
        if people[1] == "":
            continue
        else:
            # notification 
            for bgUsers in data.bgUser:
                if bgUsers == people[0]:
                    canvas.create_line(-1,100*gridNum+5,-1,
                                   100*gridNum+100-5, 
                                   fill="#34A853",width=20) 
            if people[0] == "group":
                fillColor = "white"
            else:
                fillColor = "gray"               
            canvas.create_rectangle(51-r,100*gridNum + margin,52-r+2*r,
                               100*gridNum+margin+2*r, 
                               fill=fillColor,width=0)   

            if people[2] != "" and people[0] != "group":    
                try:            
                    filename = "profilePic/%s.png" % people[0]
                    im1 = Image.open(filename)
                    im1.resize((71,71),Image.ANTIALIAS)
                    im1.thumbnail((71,71),Image.ANTIALIAS)
                    profile = ImageTk.PhotoImage(im1)
                    label = Label(image=profile)
                    label.image = profile
                    canvas.create_image(51,100*gridNum + margin+r,image=profile)
                except:
                    canvas.create_text(51,100*gridNum+margin+r,
                       font=(data.font,20),
                       text="%s%s"%(people[1][0].upper(),people[1][-1].upper()),
                       fill="black")
            elif people[0] == "group":                
                # img downloaded from http://www.faidamarketlink.or.tz/faidamal
                # imis/plugins/ionicons-2.0.1/png/512/android-contacts.png
                filename = "img/group.png" 
                im1 = Image.open(filename)
                im1.resize((71,71),Image.ANTIALIAS)
                im1.thumbnail((71,71),Image.ANTIALIAS)
                profile = ImageTk.PhotoImage(im1)
                label = Label(image=profile)
                label.image = profile
                canvas.create_image(51,100*gridNum + margin+r,image=profile)
            else:
                canvas.create_text(51,100*gridNum+margin+r,
                       font=(data.font,20),
                       text="%s%s"%(people[1][0].upper(),people[1][-1].upper()),
                       fill="black")
            gridNum += 1    
  
def drawLogo(data, frame2):
    # draw start page logo
    # logo downloaded from https://medium.com/@leocavalcante/
    # lets-chat-with-ratchet-siler-react-8cb749f69fc0
    # resize method cited from https://stackoverflow.com/questions/273946/
    # how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
    # image from https://medium.com/@leocavalcante/
    # lets-chat-with-ratchet-siler-react-8cb749f69fc0
    logo = Canvas(frame2,width=300,height=300,bg="white",highlightthickness=0)
    logo.place(x=data.width2//2,y=data.height2//2,anchor=CENTER)
    im1 = Image.open("img/logo.png")
    im1.resize((250,250),Image.ANTIALIAS)
    im1.thumbnail((250,250),Image.ANTIALIAS)
    myLogo = ImageTk.PhotoImage(im1)
    label = Label(image=myLogo, bg="white")
    label.image = myLogo    
    logo.create_image(150,140,image=myLogo)      
    logo.create_text(110,300,text="Message",font=(data.font,20),
                     fill="black",anchor=S)
    logo.create_text(220,300,text="Lite",font=(data.font,20),
                     fill="#0084FF",anchor=S)
            
def drawWelcome(data, welcome):
    # draw profile and username on welcome screen     
    welcome.create_text(510,490,text="%d/14"%len(data.displayName),
                        font=("Dengxian",14),fill="light gray")
    welcome.create_rectangle(0,560,802,602,width=0,fill="#0084FF")
    welcome.create_line(400-130,450+22,400+130,450+22,width=2)
    welcome.create_text(400-60,60,text="Message",font=(data.font,36))
    welcome.create_text(400+140,60,text="Lite",font=(data.font,36),
                        fill = "#0084FF")

    if data.profilePic == "" and data.displayName == "":
        welcome.create_rectangle(data.width//2-110,data.height*2//5-110,
                            data.width//2+110,data.height*2//5+110,
                            fill=data.selectProfileColor,width=0) 
        welcome.create_oval(data.width//2-40,data.height*2//5-60,
                            data.width//2+40,data.height*2//5+20,
                            fill="#a5a5a5",width=0) 
        welcome.create_rectangle(data.width//2-65,data.height*2//5+40,
                            data.width//2+65,data.height*2//5+110,
                            fill="#a5a5a5",width=0) 

    elif data.profilePic == "" and data.displayName != "": 
        welcome.create_rectangle(data.width//2-110,data.height*2//5-110,
                            data.width//2+110,data.height*2//5+110,
                            fill=data.selectProfileColor,width=0) 
        
        if isLegalName(data):
            welcome.create_text(data.width//2,data.height*2//5+160,
                                text="Valid Name!",fill="#34A853")             
            welcome.create_text(data.width//2,data.height//2-55,
                            text="%s%s"%(data.displayName[0].upper(),
                            data.displayName[-1].upper()),fill="black",
                            font=(data.font, 70))
        else:
            welcome.create_text(data.width//2,data.height*2//5+160,
                                text="Invalid Name!",fill="red")
            welcome.create_oval(data.width//2-40,data.height*2//5-60,
                            data.width//2+40,data.height*2//5+20,
                            fill="light gray",width=0) 
            welcome.create_rectangle(data.width//2-65,data.height*2//5+40,
                            data.width//2+65,data.height*2//5+110,
                            fill="light gray",width=0)

    elif data.profilePic != "" and data.displayName == "": 
        if data.buffer != data.profilePic:        
            writeProfileImg(readImg(data.profilePic),data.myPID)
            data.buffer = data.profilePic
                   
        filename = "profilePic/%s.png" % data.myPID
        im1 = Image.open(filename)
        im1.resize((220,220),Image.ANTIALIAS)
        im1.thumbnail((220,220),Image.ANTIALIAS)
        profile = ImageTk.PhotoImage(im1)
        label = Label(image=profile)
        label.image = profile
        welcome.create_image(data.width//2,data.height*2//5,
                             image=profile)

    else:
        if data.buffer != data.profilePic:
            writeProfileImg(readImg(data.profilePic),data.myPID)
            data.buffer = data.profilePic
            
        filename = "profilePic/%s.png" % data.myPID
        im1 = Image.open(filename)
        im1.resize((220,220),Image.ANTIALIAS)
        im1.thumbnail((220,220),Image.ANTIALIAS)
        profile = ImageTk.PhotoImage(im1)
        label = Label(image=profile)
        label.image = profile
        welcome.create_image(data.width//2,data.height*2//5,
                             image=profile)        
        if isLegalName(data):
            welcome.create_text(data.width//2,data.height*2//5+160,
                                text="Valid Name!",fill="#34A853")
        else:      
            welcome.create_text(data.width//2,data.height*2//5+160,
                                text="Invalid Name!",fill="red") 

def drawWarning(data, welcome):    
    # img download from https://www.ddscalorimeters.com/keyboard-functionality/
    welcome.create_text(data.width//2,data.height//2-40, font=(data.font, 20),
                        text="Please click on new contacts")
    welcome.create_text(data.width//2,data.height//2, font=(data.font, 20),
                        text="to update their profile pictures when")
    welcome.create_text(data.width//2,data.height//2+40, font=(data.font, 20),
                        text="new contacts are added!")
    welcome.create_text(data.width//2,data.height-40, font=(data.font, 12),
                        text="Press F5 to continue...",fill="gray")

    im1 = Image.open("img/f5.jpg")
    im1.thumbnail((80,80),Image.ANTIALIAS)
    key = ImageTk.PhotoImage(im1)
    label = Label(image=key)
    label.image = key    
    welcome.create_image(400,450,image=key)


def drawTitleBar(canvas4, data):
    if data.currentPage != 0: 
        if data.currentPage == 1:
            name = "Group(%d)" % (len(data.contactList)) 
        else:
            name = data.contactList[data.currentPage-1][1]
        canvas4.create_text(data.width4//2,data.height4//2-6,
                            text=name, font=(data.font, "16"))
        canvas4.create_line(data.width4//2-len(name)*20/2,data.height4-8,
                            data.width4//2+len(name)*20/2,data.height4-8,
                            width=2, fill="light gray")
   
def redrawAll(canvas, entry, data, frame2, canvas3, welcome, canvas4):

    # UI modification
    if entry.get() != "":
        data.buttonColor = "#4086F5"
        data.sendColor = "white"
    else:
        if data.buttonColor != "white":
            data.buttonColor = "#F0F0F0"
            data.sendColor = "black"

    # profile background
    canvas.create_rectangle(0,0,data.width1+2,data.width1,width=0,
                            fill="gray")
    # draw start page logo
    if data.currentPage == 0:
        drawLogo(data, frame2)        
    else:   
        # draw selected grid background
        if data.contactList[data.currentPage-1][1] != "":
            canvas.create_rectangle(0,data.currentPage*100,data.width1+2,
                            data.currentPage*100+data.width1,width=0,
                            fill="white")
    # draw select grid background when mouse hover over
    if data.gridNum != 0:
        canvas.create_rectangle(0,data.gridNum*100,data.width1+2,
                            (data.gridNum+1)*100, width=0,
                            fill=data.selectColor)
    drawMainScreen(canvas3, data)    
    drawTextInput(data, frame2)
    if data.currentUser == "group":
        drawTextInputGroup(data, frame2)
    drawContact(canvas, data)
    drawTitleBar(canvas4, data)

    # handle welcome screen

    if data.warning == True:        
        try:
            drawWarning(data, welcome)
        except:
            data.warning = True    

    if data.welcomeDestroy == True:
        data.warning = False
        try:
            welcome.destroy()
        except:
            data.welcomeDestroy = True
    else:
        if data.warning == False:
            drawWelcome(data, welcome)

    # draw user profile
    drawProfile(canvas, data)

    # handle voice screen
    if data.voiceInputScreenOn == True and data.voiceWidgetBuffer == 1: 
        data.voiceWidgetBuffer = 2       
        data.voiceWidget.lift(frame2)
    else:
        data.voiceWidget.lower(frame2)

#################################
# run
#################################

def run(width=800, height=600, serverMsg=None, server=None):
    def redrawAllWrapper(canvas, entry, data, frame2, canvas3, welcome, 
                         canvas4):
        canvas.delete(ALL)
        
        canvas4.delete(ALL)
        data.scratch.delete(ALL)
        try:
            welcome.delete(ALL)
        except:
            data.welcomeDestroy = True
        # clear screen method cited from https://stackoverflow.com/questions/
        # 15995783/python-tkinter-how-to-delete-all-children-elements
        for child in frame2.winfo_children():
            child.destroy()
        redrawAll(canvas, entry, data, frame2, canvas3, welcome, canvas4)
        frame2.update()
        canvas.update()

        canvas4.update() 
        data.scratch.update()
        try:
            welcome.update()
        except:
            data.welcomeDestroy = True 

    def mousePressedWrapper(event, entry, data, nameEntry, welcome):
        mousePressed(event, entry, data, nameEntry, welcome)
        redrawAllWrapper(canvas, entry, data, frame2, canvas3, welcome, canvas4)

    def mouseReleasedWrapper(event, entry, data, welcome):
        mouseReleased(event, entry, data, welcome)
        redrawAllWrapper(canvas, entry, data, frame2, canvas3, welcome, canvas4)

    def mouseMotionWrapper(event, data, welcome):
        mouseMotion(event, data, welcome)
        redrawAllWrapper(canvas, entry, data, frame2, canvas3, welcome, canvas4)

    def mouseWheelWrapper(event, data):
        mouseWheel(event, data)
        redrawAllWrapper(canvas, entry, data, frame2, canvas3, welcome, canvas4)

    def keyPressedWrapper(event, entry, data, nameEntry):
        keyPressed(event, entry, data, nameEntry)
        redrawAllWrapper(canvas, entry, data, frame2, canvas3, welcome, canvas4)

    def timerFiredWrapper(data, entry):
        timerFired(data, entry)
        redrawAllWrapper(canvas, entry, data, frame2, canvas3, welcome, canvas4)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, data, entry)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.server = server
    data.serverMsg = serverMsg

    # init window properties
    data.width = width
    data.height = height    
    data.width1 = 100
    data.height1 = 600
    data.width2 = 700
    data.height2 = 545
    data.width3 = data.width - 100
    data.height3 = 55
    data.width4 = data.width3
    data.height4 = 40
    data.width5 = 180
    data.height5 = 180
    data.welcomeDestroy = False     
    data.buffer = ""

    data.timerDelay = 100 # milliseconds

    init(data)
    # create the root and the canvas
    data.root = Tk()
    data.root.title("MessageLite")    
    data.root.iconbitmap("img/logo.ico")
    data.root.geometry("800x600")
    data.root.resizable(width=False, height=False)
    
    # init scratch paper to calculate message bubble dimension
    data.scratch = Canvas(data.root)
    data.scratch.pack()

#################################
# frames init
#################################

    frame1 = Frame(data.root, width=data.width1,height=data.height1)
    frame1.place(x=0,y=0,anchor=NW)

    data.voiceWidget = Frame(data.root,width=data.width5,height=data.height5)
    data.voiceWidget.place(x=data.width//2+50,y=data.height//2,anchor=CENTER)

    im1 = Image.open(data.listenIconSource)
    im1.resize((180,180),Image.ANTIALIAS)
    im1.thumbnail((180,180),Image.ANTIALIAS)
    listenIcon = ImageTk.PhotoImage(im1)
    label = Label(data.voiceWidget,image=listenIcon)
    label.image = listenIcon
    label.place(x=0,y=0,anchor=NW)     

    frame2 = Frame(data.root, width=data.width2,height=data.height2,
                   bg="white")
    frame2.place(x=100,y=0,anchor=NW)

    frame3= Frame(data.root,width=700,height=60,bg="red")
    frame3.place(x=100,y=545,anchor=NW)

    frame4 = Frame(data.root,width=700,height=40,bg="white")
    frame4.place(x=100,y=-1,anchor=NW)

#################################
# frame1 widgets init
#################################

    canvas = Canvas(frame1,width=100,height=600,bg="#0084FF")
    canvas.place(x=-2,y=-2,anchor=NW)

#################################
# frame2 widgets init
#################################
  

#################################
# frame3 widgets init
#################################
    def callback1(sv1):
        # entry character limit
        # method cited from https://stackoverflow.com/questions/11491161/
        # limiting-entry-on-a-tk-widget
        c = sv1.get()[0:280]
        sv1.set(c)
    
    sv1 = StringVar()
    sv1.trace("w", lambda name, index, mode, sv1=sv1: callback1(sv1))

    canvas3 = Canvas(frame3, width=data.width3, height=data.height3, 
                    bg="white")
    canvas3.place(x=-2,y=-2,anchor=NW)    

    entry = Entry(frame3,relief=FLAT,font=(data.font, 18),bg="white",
                  width=25, textvariable=sv1)
    entry.place(x=55,y=(data.height3-8),anchor=SW) 

#################################
# frame4 widgets init
#################################

    canvas4 = Canvas(frame4,width=700,height=40,bg="white")
    canvas4.place(x=-1,y=-1,anchor=NW)

#################################
# welcome screen init
#################################
    def callback(sv):
        # entry character limit
        # method cited from https://stackoverflow.com/questions/11491161/
        # limiting-entry-on-a-tk-widget
        c = sv.get()[0:14]
        sv.set(c)
    
    sv = StringVar()
    sv.trace("w", lambda name, index, mode, sv=sv: callback(sv))
    
    welcome = Canvas(data.root,width=800,height=600,bg="white")
    welcome.place(x=data.width//2,y=data.height//2,anchor=CENTER)
    nameEntry = Entry(welcome,width=14,relief=FLAT,bg="white",textvariable=sv,
                      font=("Dengxian", 18),justify=CENTER,fg="light gray")
    nameEntry.insert(0, 'Your Name...')
    nameEntry.place(x=400,y=450,anchor=CENTER)

#################################
# set up events
#################################

    # extra key bindings learned from http://effbot.org/tkinterbook/
    data.root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, entry, data, nameEntry,
                                                welcome))
    data.root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, entry, data, nameEntry))
    data.root.bind("<Motion>", lambda event:
                            mouseMotionWrapper(event, data, welcome))
    data.root.bind("<ButtonRelease-1>", lambda event:
                            mouseReleasedWrapper(event, entry, data, welcome))
    data.root.bind("<MouseWheel>", lambda event:
                            mouseWheelWrapper(event, data))    
    timerFiredWrapper(data, entry)
    # and launch the app
    data.root.mainloop()  # blocks until window is closed
    print("bye!")

serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()

run(800, 600, serverMsg, server)