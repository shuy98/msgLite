# MessageLite
This is the term project for course 15112 during the fall of 2017. Check out my demo from this YouTube video: https://youtu.be/5aZwagMfCyw.

# Description
MessageLite is a message app built with python3. It utilizes python socket to enable connections between clients. main_server.py is the server which receives information from clients and forwards information to clients. main_client.py is user client which handles user inputs. User not only can do basic navigations between tabs locally, but also can send messages and pictures to selected users. Images are encoded/decoded using base64 encoding/decoding so the images are in a string format and could be transferred between server and clients. A speech to text feature can convert user's speech to text. This feature utilizes Google Speech API. It records user's speech and sends the speech to Google for speech recognition, and Google sends back a string of recognized text. GUI mainly utilizes tkinter. It takes user's inputs including key press, mouse press, mouse release, mouse hover and mouse wheel, and trigger actions accordingly. Actions include modifying objects on the main screen and sending/receiving information to/from the server. The screen will refresh(redraw) constantly to update the objects displayed on the screen. 

# Components
- main_client.py
- main_server.py
- img
- imgMsg
- profilePic

# Working environment
- Windows OS
- Python 3

# Modules required to be installed
## 1. PIL
  Open cmd, type in 
  ```
  pip install pillow
  ```
## 2. PyAudio and SpeechRecognition
  Open cmd, type in 
  ```
     pip install pyaudio
     pip install SpeechRecognition
  ```

# How to run?
1. download and unzip this file
2. copy two files and three folders to the same directory
two files: main_client.py main_server.py
three folders: img imgMsg profilePic
3. open cmd and change to the directory containing above files 
4. type in cmd ```python3 main_server.py``` to initialize the server 
5. for each new user, type in cmd ```python3 main_client.py``` to initialize GUI 
6. follow the instructions of the program and enjoy!


