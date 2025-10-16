# Unity Web Interface Addon

This project provides a web interface for Unity applications, allowing developers to set up communication between a Unity app and a web server. By default, it includes a live webcam stream from unity to the web server and a text chat between Unity and the web server. This branch of the project also includes the integration of a conversational agent that can interact with the Unity application.

## Features
- Live webcam streaming from Unity to a web server.
- Text chat functionality between Unity and the web server.
- WebSockets automatically generate a configuration file, making the connection between Unity and the web server easy.
- Expandable architecture for WebSockets, allowing developers to add more features and exchange different information.
- Integration of a conversational agent that can interact with the Unity application.
- Multiple agent configurations (Reactive, Proactive, Placebo, WoZ) to suit different interaction styles.
- A Wizard-in-the-Loop (WoZ) mode, allowing a human operator to approve or modify agent actions before they are executed.

## Setup Instructions

### Web Server Setup
1. Clone the repository to your local machine; 
2. Create a .env file in the root directory of the project and add your OpenAI API key with the layout: OPENAI_API_KEY = {key};
3. Run main.py to start the web server;
4. Copy the newly generated config.cfg file to your Unity persistent data path (%Appdata%/LocalLow/YourCompanyName/YourProjectName/config.cfg);

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

Finally, you can test the text chat functionality by sending messages from either Unity or the web server interface. Messages should appear in both interfaces.
Additionally, the message should prompt the agent to respond, making the agent reply through the talk tool if you have it defined to do so.

## Requirements

### Unity
- NativeWebSocket package (included in the Unity package);

### Python
Check the requirements.txt file for the necessary packages. You can install them using pip:
```pip install -r requirements.txt
```

# Expanding the WebSocket Functionality
To add more features and exchange different information between Unity and the web server, you need to create new message types:

1. **Define a New Message Type**: In both Unity and the web server, define a new message type. In Python, under `utils.py` add a new constant under `MessageTypes`. In Unity under RequestFramework.cs, add a new constant under `MessageType` ensuring it matches the Python constant.
2. **Handle the New Message Type**: In both Unity and the web server, implement the logic to handle the new message type. This involves adding new cases in the message processing functions to handle sending and receiving messages of the new type.

In Python this is done under main.py in the `process_input` function. Simply add a new if statement checking for your new message type and implement the desired functionality.

In Unity this is done under RequestFramework.cs in the `InterpretMessage` function. Simply add a new case in the switch statement checking for your new message type, and implement the desired functionality.

3. **JSONifying Messages**: If your new message type involves sending complex data, consider using JSON to structure the data. In Python, you can use the `json` module to serialize and deserialize data. In Unity, you can use `JsonUtility` for similar functionality. The pre-existing JSON classes used in Unity are under the JsonClasses.cs file. In Python these are under the Messages/message.py file.

# Expanding the Agent Functionality
This branch adds a conversational agent to the web server, allowing it to interact with the Unity application. The agent can perform actions based on its configuration, which can be set to Reactive, Proactive, Placebo, or WoZ (Wizard of Oz) modes by default.

Each agent action will be logged in the web server interface, and added to the agent log. This agent log allows the wizard to allow, deny or modify individual actions performed by the agent before they are executed.

## Adding a new Agent Configuration (Agent Prompt)
To change the existing configurations or system prompts, you can modify the files under the `src/Agent/Configs` directory. Each configuration file defines a different behavior for the agent. You can also add new configurations by creating new classes that inherit from `BaseAgentConfig`.

If you define additional agent types, you must include them in the agent manager located in `src/Agent/AgentManager.py`. This involves changing the `__init__` and `swap_config` methods to account for the new agent types, 
adding a new `elif` statement checking for your new agent type and initializing it accordingly.

## Adding new Tools
The agent can be extended with new tools that it can use to interact with the Unity application. To add a new tool, you need to create a new entry 
in the AgentManager's  `setup_handler` method. This involves creating a new AgentAction entry, and linking it with your own python function you defined.
Just ensure the python function returns a string providing feedback to the agent about the action it just performed.

By default, the tools that come pre-defined are first sent to the agent log for approval by the wizard before they are executed. If you wish to do the same, simply create an AgentAction with your own function
and add it to the dashboard through the `add_agent_action` method.

## Adding new LLMs
To change the OpenAI model used by the agent, you can modify the `__init__` and `swap_config` methods in the `AgentManager` class located in `src/Agent/AgentManager.py`. 
By adding your model name to the `elif` statements, you can add a new OpenAI model for the agent to use.

To use Claude, import and instantiate the Claude model from src/Agent/LLMs/Claude.py, providing your API key through the .env file with the layout: ANTHROPIC_API_KEY = {key}