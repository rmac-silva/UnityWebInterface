# Unity Web Interface Addon

This project provides a web interface for Unity applications, allowing developers to set up communication between a Unity app and a web server. By default, it includes a live webcam stream from unity to the web server and a text chat between Unity and the web server.

## Features
- Live webcam streaming from Unity to a web server.
- Text chat functionality between Unity and the web server.
- WebSockets automatically generate a configuration file, making the connection between Unity and the web server easy.
- Expandable architecture for WebSockets, allowing developers to add more features and exchange different information.

## Setup Instructions

### Web Server Setup
1. Clone the repository to your local machine; 
2. Run main.py to start the web server;
3. Copy the newly generated config.cfg file to your Unity persistent data path (%Appdata%/LocalLow/YourCompanyName/YourProjectName/config.cfg);

### Unity Setup
1. Import the Unity package into your Unity project;
2. Add the "Networking" prefab to your scene;
3. Ensure you have copied the config.cfg file to the persistent data path as mentioned above;
4. Run your Unity application.

### Testing the Setup
Run both the web server (main.py) and your Unity scene:
- Your web server should indicate a successful connection with Unity beneath the webcam feed.
- Your Unity console should log a successful connection message as well.
You can now exchange information between Unity and the web server.

By now you should also see a live webcam feed in your Unity scene, as well as a live webcam feed in your web server interface.
You can swap which webcam you want to use through the dropdown menu in the top right corner of your Unity application. 

Finally you can test the text chat functionality by sending messages from either Unity or the web server interface. Messages should appear in both interfaces.

## Requirements

### Unity
- NativeWebSocket package (included in the Unity package);
- TMPro package (included in the Unity package);

### Python
- nicegui == 2.12.1
- pillow == 10.4.0
- websockets == 15.0.1

# Expanding the WebSocket Functionality
To add more features and exchange different information between Unity and the web server, you need to create new message types:

1. **Define a New Message Type**: In both Unity and the web server, define a new message type. In Python, under `utils.py` add a new constant under `MessageTypes`. In Unity under RequestFramework.cs, add a new constant under `MessageType` ensuring it matches the Python constant.
2. **Handle the New Message Type**: In both Unity and the web server, implement the logic to handle the new message type. This involves adding new cases in the message processing functions to handle sending and receiving messages of the new type.

In Python this is done under main.py in the `process_input` function. Simply add a new if statement checking for your new message type and implement the desired functionality.

In Unity this is done under RequestFramework.cs in the `InterpretMessage` function. Simply add a new case in the switch statement checking for your new message type, and implement the desired functionality.

3. **JSONifying Messages**: If your new message type involves sending complex data, consider using JSON to structure the data. In Python, you can use the `json` module to serialize and deserialize data. In Unity, you can use `JsonUtility` for similar functionality. The pre-existing JSON classes used in Unity are under the JsonClasses.cs file. In Python these are under the Messages/message.py file.

# Using Conversational Agents
If you wish to use conversational agents in your project, please download the code from the conversational-agents branch instead.
