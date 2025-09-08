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


class App:
    """The Flask application class, responsible for managing the Flask server & agent interactions"""

    def __init__(self, ws: Websocket):
        # Setup agent with access to the main app

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
            self.dashboard.sync_information()  # Syncs information between dashboard and game
            self.logger.create_new_log()  # Opens a new log, on each connection of the websocket

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

        header = data[0:8].decode("utf-8")

        print(f"Received communication: {header}")
        if header == utils.MessageTypes.MESSAGE_TYPE:  # User Message/Prompt
            received_msg_str = self.dashboard.save_message_json(data[8:])  # Returns the received message string

            # If you wish to perform any other operations with the message, you can do them here

        if header == utils.MessageTypes.MESSAGE_SYNC:  # Message Log

            # By default, the dashboard loads all messages from unity, meaning the game's message log replaces the dashboard message log
            self.dashboard.replace_message_log(data[8:])

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



if __name__ in {"__main__", "__mp_main__"}:
    ws = Websocket()

    main_app = App(ws=ws)
    main_app.run_app()

@ui.page("/dashboard")
def create_dashboard_page():
    main_app.dashboard.create_dashboard()