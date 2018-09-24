# Project Name 
MessageLite
# Description
MessageLite is a message app built with python3. It utilizes python socket to enable connections between clients. main_server.py is the server which receives information from clients and forwards information to clients. main_client.py is user client which handles user inputs. User not only can do basic navigations between tabs locally, but also can send messages and pictures to selected users. Images are encoded/decoded using base64 encoding/decoding so the images are in a string format and could be transferred between server and clients. A speech to text feature can convert user's speech to text. This feature utilizes Google Speech API. It records user's speech and sends the speech to Google for speech recognition, and Google sends back a string of recognized text. GUI mainly utilizes tkinter. It takes user's inputs including key press, mouse press, mouse release, mouse hover and mouse wheel, and trigger actions accordingly. Actions include modifying objects on the main screen and sending/receiving information to/from the server. The screen will refresh(redraw) constantly to update the objects displayed on the screen. 

# Components
1. main_client.py
2. main_server.py
3. img
4. imgMsg
5. profilePic

# Working environment
1. Windows OS
2. Python 3

# Modules required to be installed
## 1. PIL

### How to install PIL
  Open cmd, type in ```pip install pillow```
## 2. PyAudio and SpeechRecognition
### How to install 
  Open cmd, type in 
  ```pip install pyaudio
     pip install SpeechRecognition
  ```

# How to run?
1. copy two files and three folders to the same directory
two files: main_client.py main_server.py
three folders: img imgMsg profilePic
2. open cmd and change to the directory containing above files 
3. type in cmd ```python3 main_server.py``` to initialize the server 
4. for each new user, type in cmd ```python3 main_client.py``` to initialize GUI 
5. follow the instructions of the program and enjoy!


