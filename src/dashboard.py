import asyncio
from typing import List
from nicegui import ui, context
from nicegui.events import ValueChangeEventArguments
from src.Agent.AgentAction import AgentAction
from src.utils import StylingHelper, media_path
import json
import time
import ast
# Objects
from src.Messages.message import Message, MessageLog, PlaceboManager, PlaceboOption
from src.websocket import Websocket
import src.utils as utils


class DashboardSettings:
    """This class represents the dashboard settings, you can add additional settings here that you want to configure."""

    def __init__(self):
        self.stream_webcam: bool = True
        self.webcam_size = (640, 320) #The size of the webcam preview
        
        #Agent mode - Boolean states
        self.agent_mode = "Reactive" # The starting state. If you change the boolean values, make sure to this string to the correct value
        self.reactive_agent  : bool = True
        self.proactive_agent : bool = False
        self.placebo_agent   : bool = False
        self.woz_mode        : bool = False
        

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
        self.user_icon = f"https://robohash.org/{current_time}?set=set5" # You can change the icons here, using any image url
        self.robot_icon = f"https://robohash.org/{current_time}?set=set3" # You can change the icons here, using any image url

        # Message logs
        self.message_log = MessageLog()
        self.text_input = ""

        # Dashboard Settings
        self.dashboard_settings = DashboardSettings()

        # Dialogs
        self.settings_opened = False
        
        #Agent Actions
        self.auto_accept = False
        self.agent_actions : List[AgentAction] = []
        
        #Placebo log
        self.placebo_log = PlaceboManager()

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

        self.draw_logs()
    # endregion
    
    # region - Dialogs (Cards)

    def setup_dialogs(self):
        """Sets up the dialogs, so they can be opened by buttons or other actions.
            This is where the style and look of the cards are defined.
        """

        # Settings
        self.settings_dialog = ui.dialog()

        # Settings Dialog
        with self.settings_dialog, ui.card().classes(f"{self.sh.app_settings_dialog_color} rounded w-3/4").style("max-width: none"):
            ui.label("App Settings").classes("text-3xl")
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
    def draw_webcam_preview(self):
        """Draws the webcam preview, using the image defined
        """
        
        with ui.column().classes(" items-center").style("width:30%"):
            ui.label("Webcam Preview").classes("text-3xl")
            self.webcam_image = ui.interactive_image("/media/placeholder.png").classes(f"rounded {self.sh.border_color} border-solid {self.sh.border_thickness}").style(f"max-width:{self.dashboard_settings.webcam_size[0]}px;max-height:{self.dashboard_settings.webcam_size[1]}px;width:auto;height:auto;")  # Webcam element

            with ui.column().classes("w-full items-center"):
                self.draw_ws_status()
                self.draw_webcam_status()

    @ui.refreshable
    def draw_ws_status(self):
        """Draws the websocket status for the comms websocket
        """
        
        with ui.row():
            ui.label("Comms WebSocket Status:").classes("text-2xl")
            if self.comms_ws_connected:
                ui.icon(name="check_circle", color="green").props("size=md")
            else:
                ui.icon(name="cancel", color="red").props("size=md")
    
    
    @ui.refreshable
    def draw_webcam_status(self):
        """Draws the webcam websocket status
        """
        
        with ui.row():
            ui.label("Webcam Stream Status:").classes("text-2xl")
            if self.webcam_ws_connected:
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
            ui.label("Chatbox").classes("text-3xl ")
            with ui.scroll_area().classes(f"rounded {self.sh.border_color} {self.sh.chat_color} border-solid {self.sh.border_thickness}").style("height:450px;") as scroll:
                scroll.scroll_to(percent=1)
                self.draw_messages()
            ui.input(label="Type here").bind_value(self, "text_input").on("keydown.enter", self.submit_message).classes(f"{self.sh.chat_color} rounded {self.sh.border_color} border-solid {self.sh.border_thickness} px-2 py-1").style(
                "width:100%; margin-top:-15px;"
            )

    @ui.refreshable
    def draw_messages(self):
        """Draws the messages, on the left we display messages from the user, on the right messages sent by the server
        """
        
        for message in self.message_log.get_all_messages():
            with ui.row().style("width:100%;"):
                if message.sender.lower() == "server":
                    ui.chat_message(text=message.get_content(), name=message.get_sender().upper(), stamp=message.get_timestamp(), avatar=self.robot_icon, sent=True).props(f"{self.sh.sent_message_color}").style("width:100%;")
                elif message.sender.lower() == "user":
                    ui.chat_message(text=message.get_content(), name=message.get_sender().upper(), stamp=message.get_timestamp(), avatar=self.user_icon, sent=False).props(f"{self.sh.received_message_color}")

    # endregion
    
    # region - Actions
    @ui.refreshable
    def draw_control_actions(self):
        """Draws the control actions / the action buttons
        """
        
        with ui.row().classes("justify-center").style("width:30%"):
            with ui.column().classes("w-full").style("align-items: anchor-center;"):
                
                ui.label("Change App Settings").classes('text-3xl')
                with ui.button(text="App Settings",on_click=self.open_app_settings,color=self.sh.button_main_color).classes("text-white"): #To add a tooltip to a button, use the with: keyword
                    ui.tooltip('Configure the app')
                 
    @ui.refreshable
    def draw_dashboard_options(self):
        """Draws the dashboard options panel, containing the settings of the dashboard
        """
        with ui.row().classes(f"bg-{self.sh.button_main_color}  rounded items-center").style("width:auto; padding-left:10px;"):
            ui.label("Stream Webcam: ").classes("text-white text-weight-bold lg").style("display: contents !important;")
            ui.checkbox().bind_value(self.dashboard_settings,"stream_webcam").classes("text-weight-bold lg").props('color=blue-9 label-color=white input-class=text-white').style("display: contents !important;")

        ui.separator().classes("bg-black w-full")
        ui.label('Agent Mode').classes('text-2xl ')
        ui.toggle(["Reactive","Proactive","Placebo","WoZ"]).bind_value(self.dashboard_settings,"agent_mode").on_value_change(self.process_dashboard_mode_change).classes("text-weight-bold lg").props('color=blue-9 label-color=white input-class=text-white').style("display: contents !important;")
    
    def process_dashboard_mode_change(self, event : ValueChangeEventArguments):
    
        self.notify_safe(f"Dashboard is in mode: {event.value}")
        self.dashboard_settings.agent_mode = event.value
        
        if(event.value == "Reactive"):
            self.dashboard_settings.reactive_agent=True
            self.dashboard_settings.proactive_agent=False
            self.dashboard_settings.placebo_agent = False
            self.dashboard_settings.woz_mode=False
            
        if(event.value == "Proactive"):
            self.dashboard_settings.reactive_agent=False
            self.dashboard_settings.proactive_agent=True
            self.dashboard_settings.placebo_agent = False
            self.dashboard_settings.woz_mode=False
            
        if(event.value == "Placebo"):
            self.dashboard_settings.reactive_agent=False
            self.dashboard_settings.proactive_agent=False
            self.dashboard_settings.placebo_agent = True
            self.dashboard_settings.woz_mode=False
            
        if(event.value == "WoZ"):
            self.dashboard_settings.reactive_agent=False
            self.dashboard_settings.proactive_agent=False
            self.dashboard_settings.placebo_agent = False
            self.dashboard_settings.woz_mode=True
        
        self.app.swap_agent_type(self.dashboard_settings.agent_mode)
        self.auto_accept = False
        self.settings_opened = False
        self.settings_opened = False
        self.draw_logs.refresh() # type: ignore
        self.draw_dialogs.refresh() # type: ignore
    
    #endregion
    
    # region - Image
    
    async def set_webcam_image(self, image_data):
        """Sets the webcam image source to the newly provided image data

        Args:
            image_data (bytes): The image data to display
        """
        if not self.has_modal_open() and hasattr(self, "webcam_image"):  # Stop image refresh when you have a modal open, for performance's sake

            self.webcam_image.set_source(image_data)

    def set_no_image(self):
        """Resets the webcam image to the placeholder
        """
        
        if hasattr(self, "webcam_image"):
            
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
        self.draw_chatbox.refresh() # type: ignore

    def save_system_message(self, msgContent: str):
        self.message_log.add_message(Message("system", content=msgContent))
        self.draw_chatbox.refresh()

    async def submit_message(self):
        msg = Message(content=self.text_input, sender="server")
        
        self.save_message(msg)
        
        #Log the message, under the WoZ handle
        # To log actions that are not agent actions, we create a dummy AgentAction object and use that to log the message
        action = AgentAction("MSG",self.send_agent_message,{"msg" : msg.content},"Sends a message to the user.") 
        self.logger.write_woz_action(action)

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
    
    #Agent messages
    def send_agent_message(self, msg : str):
        with self.client:
            new_msg = Message(content=msg,user="server")
            self.save_message(new_msg)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.send_message(new_msg))
            except:
                # If we're not in a running event loop, run a task manually (blocking)
                asyncio.run(self.send_message(new_msg))

    # endregion
    
    # region - Button actions 
    # Define your button actions here for organization's sake

    def open_app_settings(self):
        """Opens the dialog/card that contains the app settings
        """
        self.settings_opened = True
        self.redraw()

    # endregion

    # region - Generic

    def has_modal_open(self):
        """
        Check if any settings modal is currently open. This function is useful if you want to hold out on executing a function if the user is busy
        with a modal/card/dialog open.

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
        self.create_dashboard.refresh() # type: ignore

        if message != "":
            self.notify_safe(message)

    def set_ws_active(self):
        """Sets the comms socket as active
        """
        self.comms_ws_connected = True
        self.draw_ws_status.refresh()

    def set_webcam_ws_active(self):
        """Sets the webcam socket as active
        """
        self.webcam_ws_connected = True
        self.draw_webcam_status.refresh()

    def set_ws_inactive(self):
        """Sets the comms socket as inactive
        """
        # print("Comms down")
        self.comms_ws_connected = False
        self.draw_ws_status.refresh()

    def set_webcam_ws_inactive(self):
        """Sets the webcam socket as inactive
        """
        # print("Webcam down")
        self.webcam_ws_connected = False
        self.draw_webcam_status.refresh()

    # endregion
    
    # region - Agent actions
    
    def add_agent_action(self, action : AgentAction):
        with self.client:
            self.agent_actions.append(action)
            
            if(self.auto_accept):
                self.activate_action(action, True)
            
            self.draw_agent_log.refresh()

    #endregion
    
    #region - Agent Log
    
    @ui.refreshable
    def draw_logs(self):
        with ui.row().classes('w-full mt-4'):
            #In WoZ mode we don't need the agent log
            if(self.dashboard_settings.placebo_agent):
                self.draw_placebo_log()
            elif(self.dashboard_settings.proactive_agent or self.dashboard_settings.reactive_agent):
                self.draw_agent_log()
    
    @ui.refreshable
    def draw_agent_log(self):
        
        with ui.row().classes('w-full justify-center '):
            with ui.column().classes('w-full ').style('align-items: anchor-center; '):
                
                with ui.row().classes("w-full items-center justify-center"):
                    ui.button(icon="delete",on_click=self.clear_log).props('size=sm color=red').classes('custom-cursor').style("width:25px;height:25px;")
                    ui.label("Agent Log (Reversed)").classes('text-3xl ')
                    ui.switch("Allow All",value=self.auto_accept).bind_value(self,"auto_accept").classes('text-xl  ').props("color='blue' keep-color").on_value_change(self.try_and_accept_all_actions)
                    
                if(len(self.agent_actions) != 0):
                    with ui.row().classes("w-full border rounded py-2 px-2 justify-between items-center"):
                        for action in self.agent_actions.__reversed__():
                            
                            bg_color = action.get_color()
                            
                            with ui.row().classes(f"{bg_color} rounded py-2 px-10 justify-between items-center").style("width:100%;"):
                                
                                ui.label(action.get_action_notification()).tooltip(action.description).classes("text-lg").style("width:85%;")
                                
                                ui.space()
                                if(not action.executed and not action.disabled):
                                    ui.button(text="",icon="edit",color="#d2de4a",on_click=  lambda a = action: self.edit_action(a)) # type: ignore
                                    ui.button(text="",icon="check",color="#4ade80",on_click= lambda a = action: self.activate_action(a)) # type: ignore
                                    ui.button(text="",icon="close",color="#ef4444",on_click= lambda a = action: self.remove_action(a)) # type: ignore
                                else:
                                    ui.button(text="",icon="check",color="#4ade80").classes("disabled")
                                    ui.button(text="",icon="close",color="#ef4444").classes("disabled")
                              
    @ui.refreshable
    def draw_placebo_log(self):
        with ui.column().classes('w-full ').style('align-items: anchor-center; '):
            with ui.row().classes('w-full justify-center '):
                ui.label("Placebo Log (Reversed)").classes('text-3xl ')
                
            
            with ui.row().classes('w-full justify-center'):
                colors = ["#4E7E40","#92864F","#446377"]
                color_index = 0
                last_index = -1
                for option in self.placebo_log.options:
                    if(last_index != -1 and option.index != last_index):
                        color_index += 1 if color_index != 2 else -2
                        
                    ui.button(option.text, color=colors[color_index]).classes('justify-center text-lg py-10 text-white text-center rounded border-white border-solid border-2 ').style("width:48%;").on_click(lambda choice = option : self.choose_placebo_option(choice)) # type: ignore
                    
                    last_index = option.index
    
    def clear_log(self):
        for action in self.agent_actions.copy():
            if(action.executed or action.disabled):
                self.agent_actions.remove(action)
                
                
        self.draw_agent_log.refresh() # type: ignore
    
    def activate_action(self, action : AgentAction , refresh = True):
        try:
            action.activate()
            if refresh:
                self.draw_agent_log.refresh()
            self.logger.write_agent_action(action) #Rewrite the action, now that it's executed
            
        except Exception as ex:
            ui.notify(f"ERROR: Could not execute function! {ex}")
            print(f"ERROR: Could not execute function! {ex}")
        finally:
            if(refresh):self.draw_agent_log.refresh()

    def try_and_accept_all_actions(self, event : ValueChangeEventArguments):
        if(self.auto_accept):
            for action in self.agent_actions:
                if(not action.executed):
                    self.activate_action(action,False)
            
            self.draw_agent_log.refresh()

    def remove_action(self, action : AgentAction):
        action.disable()
        self.logger.write_agent_action(action) #Rewrite the action, now that it's executed
        self.draw_agent_log.refresh()
        
    def edit_action(self, action : AgentAction):
        self.edited_action = action
        self.action_editor_opened = True
        self.draw_dialogs.refresh()
        
    def draw_action_editor(self):
        if(self.edited_action is not None and type(self.edited_action.args) == dict):
            
            changes = {}
            
            for arg in self.edited_action.args.items():
                print(arg)
                arg_name = arg[0]
                arg_value = arg[1]
                changes[arg_name] = f"{arg_value!r}"
                
                with ui.row().classes("bg-neutral-500 rounded items-center").style("width:80%; padding-left:10px; padding-right:10px; padding-bottom:10px"):
                    ui.label(f"{arg_name} ({type(arg_value)})").classes("text-white text-weight-bold lg").style("display: contents !important;")
                    ui.input(value=f"{arg_value!r}").bind_value(changes,arg_name).classes("text-weight-bold lg").props('color=blue-9 label-color=white input-class=text-white').style("display: contents !important;")

            #Button to save changes, or try to.
            with ui.button(text="Save Changes", on_click=lambda c = changes: self.save_action_changes(c)).props('size=md color=green').classes('custom-cursor'):
                    ui.tooltip("If UNITY is running, saves and sends the changes made to the levels")
    
    def save_action_changes(self,changes):
        """Saves the changes done to a given action

        Args:
            changes (dict): Dictionary containing the changes made to a given action

        """
        for name, val_str in changes.items():
            try:
                # Safely parse basic Python literals like True, 42, 'text', etc.
                parsed_val = ast.literal_eval(val_str)
            except Exception:
                # fallback if literal_eval fails (e.g., malformed input)
                parsed_val = val_str
            
        changes[name] = parsed_val
        
        self.notify_safe("[EDIT] Saved action changes!")
        self.edited_action.args = changes
        self.action_editor_opened = False
        self.draw_dialogs.refresh()
        self.draw_agent_log.refresh()
        
    def choose_placebo_option(self, msg : PlaceboOption):
        self.send_agent_message(msg.text)
        self.free_up_agent()
        action = AgentAction("SYNC",self.app.send_agent_state,{'ready' : True},"Tells unity the agent is ready to communicate again")
        action.executed = True
        self.logger.write_agent_action(action)
        
        #Log action
        action = AgentAction("MSG",self.send_agent_message,{'msg':msg.text},"")
        action.executed = True
        self.logger.write_agent_action(action)
        
        #Reset placebo log for next turn
        self.placebo_log.clear_placebo_options(msg.index)
        self.draw_placebo_log.refresh()
        
    def free_up_agent(self):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.ws.send_content(utils.MessageTypes.AGENT_READY,""))
        except RuntimeError:
            # If we're not in a running event loop, run a task manually (blocking)
            asyncio.run(self.ws.send_content(utils.MessageTypes.AGENT_READY,""))
    #endregion