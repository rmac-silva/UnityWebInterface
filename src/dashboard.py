from nicegui import ui, context
from src.utils import StylingHelper, media_path
import json
import time
# Objects
from src.Messages.message import Message, MessageLog
from src.websocket import Websocket
import src.utils as utils


class DashboardSettings:
    """This class represents the dashboard settings, you can add additional settings here that you want to configure."""

    def __init__(self):
        self.stream_webcam: bool = True


class Dashboard:

    def __init__(self, ws: Websocket, logger: utils.Logger, app):
        self.sh = StylingHelper()

        self.app = app
        self.logger = logger
        self.client = context.client

        # WS
        self.ws = ws
        self.comms_ws_connected = False
        self.webcam_ws_connected = False

        # Chat Icons
        current_time = time.time()
        self.user_icon = f"https://robohash.org/{current_time}?set=set5"
        self.robot_icon = f"https://robohash.org/{current_time}?set=set3"

        # Message logs
        self.message_log = MessageLog()
        self.text_input = ""

        # Dashboard Settings
        self.dashboard_settings = DashboardSettings()

        # Dialogs
        self.settings_opened = False

    # region - UI functions
    @ui.refreshable
    def create_dashboard(self):
        """Main function that draws the dashboard interface
        """
        
        self.client = context.client # Fetches the current client from the app context
        
        ui.page_title("Dashboard")

        ui.add_head_html("<style>body {background-color:" + self.sh.bg_color + ";}</style>") #Background color
        
        self.draw_dialogs() 

        with ui.row().classes("w-full mt-4"):

            # Webcam Preview
            self.draw_webcam_preview()

            # Chatbox
            self.draw_chatbox()

            # WoZ Actions
            self.draw_control_actions()
    # endregion
    
    # region -Dialogs (Cards)

    def setup_dialogs(self):
        """Sets up the dialogs, so they can be opened by buttons or other actions.
        """

        # Settings
        self.settings_dialog = ui.dialog()

        # Settings Dialog
        with self.settings_dialog, ui.card().classes("bg-grey-9 rounded w-3/4").style("max-width: none"):
            ui.label("App Settings").classes("text-2xl text-white")
            with ui.column().style("width:100%;"):
                self.draw_dashboard_options()

    @ui.refreshable
    def draw_dialogs(self):
        """Draws the currently open dialogs.
        """
        
        self.setup_dialogs()

        if self.settings_opened:
            self.settings_dialog.open()
            self.settings_dialog.on("hide", lambda: setattr(self, "settings_opened", False))

    # endregion

    
    # region - Webcam
    @ui.refreshable
    def draw_webcam_status(self):
        """Draws the webcam websocket status
        """
        
        with ui.row():
            ui.label("Webcam Stream Status:").classes("text-2xl text-white")
            if self.webcam_ws_connected:
                ui.icon(name="check_circle", color="green").props("size=md")
            else:
                ui.icon(name="cancel", color="red").props("size=md")

    @ui.refreshable
    def draw_webcam_preview(self):
        """Draws the webcam preview, using the image defined
        """
        
        with ui.column().classes(" items-center").style("width:30%"):
            ui.label("Webcam Preview").classes("text-2xl text-white")
            self.webcam_image = ui.interactive_image("/media/placeholder.png").classes("rounded border-white border-solid border-2").style("max-width:640px;width:auto;height:auto;")  # Webcam element

            with ui.column().classes("w-full items-center"):
                self.draw_ws_status()
                self.draw_webcam_status()

    @ui.refreshable
    def draw_ws_status(self):
        """Draws the websocket status for the comms websocket
        """
        
        with ui.row():
            ui.label("Comms WebSocket Status:").classes("text-2xl text-white")
            if self.comms_ws_connected:
                ui.icon(name="check_circle", color="green").props("size=md")
            else:
                ui.icon(name="cancel", color="red").props("size=md")
    
    # endregion
    # region - Chatbox
    @ui.refreshable
    def draw_chatbox(self):
        """Draws the chatbox, containing the messages exchanged between user and server
        """
        
        with ui.row().classes("justify-center").style("width:35%"):
            ui.label("Chatbox").classes("text-2xl text-white")
            with ui.scroll_area().classes("rounded border-white border-solid border-2 bg-neutral-600").style("height:450px;") as scroll:
                scroll.scroll_to(percent=1)
                self.draw_messages()
            ui.input(label="Type here").bind_value(self, "text_input").on("keydown.enter", self.submit_message).classes("bg-neutral-600 rounded border-white border-solid border-2 px-2 py-1").style(
                "width:100%; margin-top:-15px;"
            )

    @ui.refreshable
    def draw_messages(self):
        """Draws the messages, on the left we display messages from the user, on the right messages sent by the server
        """
        
        for message in self.message_log.get_all_messages():
            with ui.row().style("width:100%;"):
                if message.sender.lower() == "server":
                    ui.chat_message(text=message.get_content(), name=message.get_sender().upper(), stamp=message.get_timestamp(), avatar=self.robot_icon, sent=True).style("width:100%;")
                elif message.sender.lower() == "user":
                    ui.chat_message(text=message.get_content(), name=message.get_sender().upper(), stamp=message.get_timestamp(), avatar=self.user_icon, sent=False)

    # endregion
    # region - Actions
    @ui.refreshable
    def draw_control_actions(self):
        """Draws the control actions / the action buttons
        """
        
        with ui.row().classes("justify-center").style("width:30%"):
            with ui.column().classes("w-full").style("align-items: anchor-center;"):
                
                ui.label("Change App Settings").classes('text-2xl text-white')
                with ui.button(text="App Settings",on_click=self.open_app_settings):
                    ui.tooltip('Configure the app')
                    
    @ui.refreshable
    def draw_dashboard_options(self):
        """Draws the dashboard options panel, containing the settings of the dashboard
        """
        with ui.row().classes("bg-neutral-500  rounded items-center").style("width:auto; padding-left:10px;"):
            ui.label("Stream Webcam: ").classes("text-white text-weight-bold lg").style("display: contents !important;")
            ui.checkbox().bind_value(self.dashboard_settings,"stream_webcam").classes("text-weight-bold lg").props('color=blue-9 label-color=white input-class=text-white').style("display: contents !important;")

    # region - Image
    

    async def set_webcam_image(self, image_data):
        """Sets the webcam image source to the newly provided image data

        Args:
            image_data (bytes): The image data to display
        """
        if not self.has_modal_open() and hasattr(self, "image_element"):  # Stop image refresh when you have a modal open, for performance's sake
            self.webcam_image.set_source(image_data)

    def set_no_image(self):
        """Resets the webcam image to the placeholder
        """
        
        if hasattr(self, "image_element"):
            
            self.webcam_image.set_source(media_path + "/placeholder.png")
            

    # endregion
    # region - Message
    def save_message_json(self, message_data) -> str:
        """Saves a received message in json format, converting it to Message and returning its contents

        Args:
            message_data (Message): The incoming message

        Returns:
            str: The JSON representation of the message
        """
        
        data_json = message_data.decode("utf-8")
        data_dict = json.loads(data_json)
        
        message = Message(data_dict["sender"], data_dict["content"])

        self.message_log.add_message(message)
        self.draw_messages.refresh()
        self.notify_safe("[SYNC] Received a new message.")
        return message.content

    def replace_message_log(self, message_log):
        """Replaces the dashboard message log with the provided one

        Args:
            message_log (MessageLog): The new message log to replace the old one.
        """
        
        data_json = message_log.decode("utf-8")
        data = json.loads(data_json)
        self.message_log.replace_message_log(data)  # Replace our message log with the received one
        self.draw_chatbox.refresh()
        self.notify_safe("[SYNC] Synchronized the chat logs.")

    def save_message(self, message: Message):
        """Saves a message to the chat log

        Args:
            message (Message): message to save
        """
        self.message_log.add_message(message)
        self.draw_chatbox.refresh()

    def save_system_message(self, msgContent: str):
        self.message_log.add_message(Message("system", content=msgContent))
        self.draw_chatbox.refresh()

    async def submit_message(self):
        msg = Message(content=self.text_input, user="server")
        
        self.save_message(msg)

        await self.send_message(msg)
        
        self.text_input = ""

    async def send_message(self, msg: Message):
        content = msg.__jsonify__()
        type = utils.MessageTypes.MESSAGE_TYPE
        await self.ws.send_content(type, content)

    def sync_information(self):
        """Use this function to sync information between the dashboard and the game on new websocket connections.
        This function will be called in each websocket connection. It can be useful to either send or receive information,
        to get both sides in sync
        """
        return

    # endregion
    
    # region - Button actions

    def open_app_settings(self):
        self.settings_opened = True
        self.redraw()

    # endregion

    # region - Generic

    def has_modal_open(self):
        """
        Check if any settings modal is currently open.

        Returns:
            bool: True if any settings modal is open, False otherwise.
        """
        return self.settings_opened
    
    def notify_safe(self, message: str):
        """Occasionaly when calling ui.notify from other classes, such as the app or websocket, nicegui failed to create said notifications.
        This is a workaround to ensure notifications are displayed 100% of the time.

        Args:
            message (str): The message to display in the notification.
        """
        with self.client:
            ui.notify(message)

    def redraw(self, message=""):
        """Redraws the whole interface, performance heavy if there are a lot of elements

        Args:
            message (str, optional): The message to display in the notification. Defaults to "".
        """
        self.create_dashboard.refresh()

        if message != "":
            self.notify_safe(message)

    def set_ws_active(self):
        self.comms_ws_connected = True
        self.draw_ws_status.refresh()

    def set_webcam_ws_active(self):
        self.webcam_ws_connected = True
        self.draw_webcam_status.refresh()

    def set_ws_inactive(self):
        # print("Comms down")
        self.comms_ws_connected = False
        self.draw_ws_status.refresh()

    def set_webcam_ws_inactive(self):
        # print("Webcam down")
        self.webcam_ws_connected = False
        self.draw_webcam_status.refresh()

    # endregion
