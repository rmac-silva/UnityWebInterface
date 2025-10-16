import asyncio
from nicegui import app, ui
from PIL import Image
import io
import os

# Endpoints
from src.dashboard import Dashboard

# Objects
import src.utils as utils
from src.websocket import Websocket
from src.Agent.AgentManager import AgentManager
from src.Agent.AgentAction import AgentAction


# Default LLM
LLM_DEFAULT = "gpt-4o"

class App:
    """The Flask application class, responsible for managing the Flask server & agent interactions"""

    def __init__(self, ws: Websocket):
        # Setup agent with access to the main app
        self.agent = AgentManager(LLM_DEFAULT,"Reactive",self,True) #Change this to True if you want console prints from the agent!

        self.ws = ws

        # Logger
        self.logger = utils.Logger()

        # WebServer
        self.dashboard = Dashboard(ws=ws, logger=self.logger, app=self)

        # Clear old session & setup media
        self.setup_media()

        app.on_startup(ws.start_websocket_server)

        # Setup websocket with access to main app
        ws.setup_application(self)

        # Webcam stream buffer
        self.received_bytes = False

        # self.send_message_to_user("Test message from agent!")

    def get_dashboard(self) -> Dashboard:
        """Returns the dashboard component

        Returns:
            Dashboard: the webapp dashboard
        """
        return self.dashboard

    def create_dashboard_notification(self, content : str):
        self.dashboard.notify_safe(content)
    
    def run_app(self):
        """Runs the webapp"""

        self.create_ui()

        ui.run(host=utils.get_ip(), port=8080, show=False, show_welcome_message=False)

        print(f"\nDashboard is ready under http://{utils.get_ip()}:8080/dashboard\n")

    def create_ui(self):
        """Creates the main webpage, linking to the dashboard page. You can add other pages here"""
        with ui.row():
            ui.button("Dashboard", on_click=lambda: ui.navigate.to(target="/dashboard"))

    def handle_websocket_open(self, websocket_type):
        """Handles when websockets open and connect

        Args:
            type (str): the type of websocket that connected
        """
        if websocket_type == "webcam":
            self.dashboard.set_webcam_ws_active()
        elif websocket_type == "comms":
            self.dashboard.set_ws_active()
            self.dashboard.message_log.clear_messages()  # Clears messages on new connection
            self.dashboard.sync_information()  # Syncs information between dashboard and game
            self.logger.create_new_log()  # Opens a new log, on each connection of the websocket
            self.dashboard.redraw()  # Redraws the dashboard to ensure everything is up to date
            self.enable_agent(bypass=True)
            

        else:
            print(f"Error handling websocket open for type: {websocket_type}!")

    def handle_websocket_close(self, websocket_type):
        """Handles when websockets close or lose connection.

        Args:
            type (str): the type of websocket that failed, webcam or comms
        """
        if websocket_type == "webcam":
            self.dashboard.set_no_image()
            self.dashboard.set_webcam_ws_inactive()

        elif websocket_type == "comms":
            self.dashboard.set_ws_inactive()
            self.logger.close_logs()

        else:
            print(f"Error handling websocket close for type: {websocket_type}!")

    async def save_frame(self, image_data):
        """Saves an image frame

        Args:
            image_data (byte[]): The image data in raw form
        """

        if not self.dashboard.dashboard_settings.stream_webcam:
            return
        
        try:
            loop = asyncio.get_event_loop()
            image = Image.open(io.BytesIO(image_data))
            image.resize(self.dashboard.dashboard_settings.webcam_size)
            loop.create_task(self.dashboard.set_webcam_image(image))  # Once loaded, sets the image
        except RuntimeError:
            # If we're not in a running event loop, run the task manually (blocking)
            image = Image.open(io.BytesIO(image_data))
            image.resize(self.dashboard.dashboard_settings.webcam_size)
            asyncio.run(self.dashboard.set_webcam_image(image))  # Once loaded, sets the image

    async def process_input(self, data):
        """This is the main method for handling incoming messages.

        Args:
            data (byte[]): The incoming data as a byte array
        """

        header = data[0:utils.HEADER_LENGTH].decode("utf-8").replace("#","") #First 8 bytes are the header
        print(f"Received communication: {header}")
        
        if header == utils.MessageTypes.MESSAGE_TYPE:  # User Message/Prompt
            received_msg_str = self.dashboard.save_message_json(data[utils.HEADER_LENGTH:])  # Returns the received message string

            # If you wish to perform any other operations with the message, you can do them here
            # For example, let's prompt the agent with this message
            await self.prompt_agent(received_msg_str)

        if header == utils.MessageTypes.MESSAGE_SYNC:  # Message Log

            # By default, the dashboard loads all messages from unity, meaning the game's message log replaces the dashboard message log
            self.dashboard.replace_message_log(data[utils.HEADER_LENGTH:])

    async def process_webcam_data(self, data):
        """Processes webcam data

        Args:
            data (byte[]): byte array containing image information
        """
        asyncio.create_task(self.save_frame(data[1:]))

    def setup_media(self):

        # Create media folders if needed
        if not os.path.isdir(utils.media_path):
            os.mkdir(utils.media_path)

        # Create logs folder if it doesn't exist
        logs_path = utils.script_dir + "./WebappLogs"
        if not os.path.isdir(logs_path):
            os.mkdir(logs_path)


        # Add static files to the dashboard, meaning files placed in the utils.media_path will be usable by the nicegui application
        app.add_static_files("/media", utils.media_path)

    #region - Agent Interactions
    async def prompt_agent(self, prompt : str):
        """Sends a prompt to the current agent

        Args:
            prompt (str): The user prompt
        """
        self.logger.write_user_message(prompt) # Log the user prompt
        await self.agent.prompt_agent(prompt)
        
    def send_message_to_user(self, message : str):
        
        action = AgentAction("MSG",self.dashboard.send_agent_message,{"msg" : message},"Sends a message to the user.")
        self.logger.write_agent_action(action)
        self.add_agent_action(action)
        
    def swap_agent_type(self, agent_type : str):
        """Swaps the current agent type from Reactive to Proactive for example

        Args:
            agent_type (str): The agent type
        """
        
        self.agent.swap_config(agent_type,LLM_DEFAULT)

    def add_agent_action(self, action : AgentAction):
        """Adds an agent action to the pending action list.

        Args:
            action (AgentAction): the action the system intends on doing
        """
        self.dashboard.add_agent_action(action)
        
    def enable_agent(self, bypass = False):
        if(bypass):
            self.send_agent_state(True)
        else:
            action = AgentAction("SYNC",self.send_agent_state,{'ready' : True},"Tells unity the agent is ready to communicate again")
            self.logger.write_agent_action(action)
            self.add_agent_action(action)
    
    def disable_agent(self):
        action = AgentAction("SYNC",self.send_agent_state,{'ready' : False},"Tells unity the agent is ready to communicate again")
        action.executed = True
        self.logger.write_agent_action(action)
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.ws.send_content(utils.MessageTypes.AGENT_BUSY ,""))
        except RuntimeError:
            # If we're not in a running event loop, run a task manually (blocking)
            asyncio.run(self.ws.send_content(utils.MessageTypes.AGENT_BUSY,""))

    def send_agent_state(self, ready : bool):
        print("Sending agent state: " + ("READY" if ready else "BUSY"))
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.ws.send_content(utils.MessageTypes.AGENT_READY if ready else utils.MessageTypes.AGENT_BUSY ,""))
        except RuntimeError:
            # If we're not in a running event loop, run a task manually (blocking)
            asyncio.run(self.ws.send_content(utils.MessageTypes.AGENT_READY if ready else utils.MessageTypes.AGENT_BUSY,""))

if __name__ in {"__main__", "__mp_main__"}:
    ws = Websocket()

    main_app = App(ws=ws)
    main_app.run_app()

@ui.page("/dashboard")
def create_dashboard_page():
    main_app.dashboard.create_dashboard()