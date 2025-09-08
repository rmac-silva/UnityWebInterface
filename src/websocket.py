#Websockets
import asyncio
from typing import Set
import src.utils as utils
from pathlib import Path
import websockets
from websockets.server import WebSocketServerProtocol # type: ignore

class Websocket():
    """This class represents the websocket connections for the application. It has two websockets, one for communication between the game 
    and the server. And the other websocket for sending webcam images so it doesn't clog the communication channel.
    """
    
    
    def __init__(self):
        self.WEBCAM_CONNECTIONS: Set[WebSocketServerProtocol] = set()
        self.COMMUNICATION_CONNECTIONS: Set[WebSocketServerProtocol] = set()
    
    def setup_application(self, app):
        """Configures the application.

        Args:
            app (Application): The application you are building / using
        """
        self.app = app
        
    def get_connection(self, type : str) -> WebSocketServerProtocol | int: 
        """Returns a websocket connection

        Args:
            type (str): The type of websocket connection to retrieve ("webcam" or "comms")

        Returns:
            WebSocketServerProtocol | int: The websocket connection or -1 if not available
        """
        connections = self.WEBCAM_CONNECTIONS if type == "webcam" else self.COMMUNICATION_CONNECTIONS
        if(len(connections) > 0):
            conn = connections.pop()
            connections.add(conn)
            return conn
        else:
            return -1
    
    #region - Websocket Setup
    async def start_websocket_server(self):
        """Starts the websocket server
        """
        ws_address = f"{utils.get_ip()}"
        print(f"\nWebsocket configured at: {ws_address}")
        
        self.save_websocket_config(ws_address)
        
        await asyncio.gather(
            websockets.serve(self.handle_connect_comm, ws_address, utils.WEBSOCKET_COMMS_PORT,ping_timeout=5,ping_interval=5),
            websockets.serve(self.handle_connect_webcam, ws_address, utils.WEBSOCKET_WEBCAM_PORT, max_size=utils.WEBSOCKET_MSG_SIZE,ping_timeout=5,ping_interval=5)
        )

    async def handle_connect_webcam(self, websocket: WebSocketServerProtocol):
        """Registers the new websocket connections, handles incoming messages and remove the connection when it is closed."""
        try:
            print("\n****WEBCAM CONNECTED****\n")
            self.WEBCAM_CONNECTIONS.add(websocket)
            self.app.handle_websocket_open("webcam")
            
            async for data in websocket:
                # Processes webcam data, converting it back into an image
                await self.app.process_webcam_data(data)
                
        finally:
            print("\n****WEBCAM DISCONNECTED****\n")
            self.WEBCAM_CONNECTIONS.remove(websocket)
            self.app.handle_websocket_close("webcam")
            
    async def handle_connect_comm(self, websocket: WebSocketServerProtocol):
        """Registers the new websocket connections, handles incoming messages and remove the connection when it is closed."""
        try:
            print("\n****COMMS CONNECTED****\n")
            self.COMMUNICATION_CONNECTIONS.add(websocket)
            self.app.handle_websocket_open("comms")
            
            async for data in websocket:
                await self.app.process_input(data)
                
        finally:
            print("\n****COMMS DISCONNECTED****\n")
            self.COMMUNICATION_CONNECTIONS.remove(websocket)
            self.app.handle_websocket_close("comms")
            
    #endregion
    
    #region - Sending Content
    
        
    async def send_content(self, header : str, content : str):
        """Sends a given message to unity through the communications websocket.
        """
        
        conn = self.get_connection("comms")
        if(len(header) > 8):
            print(f"\n Error! Message header: {header} is longer than 8 characters!\n")

            return "ERROR: Message header is longer than 8 characters"
        
        if(len(header) < 8):
            #Pads the message with #s so it becomes 8 in length
            header = utils.generate_padding(8-len(header)) + header

        if conn != -1 and type(conn) is not int:
            try:

                self.app.create_dashboard_notification(f"[WS] Sending: {header} | {content if len(content) < 20 else content[0:20]}")
                await conn.send(header+content)
            except Exception as e:
                print(f"Error sending websocket data: {e}")
                self.COMMUNICATION_CONNECTIONS.discard(conn)
        else:
            self.app.create_dashboard_notification("[WS] Error: No active websocket.")
            return "ERROR: No active websocket..."
    

    #endregion
    
    #region - Config
    
    def save_websocket_config(self, address):
        """Saves the websocket address to a config file, to be loaded by unity afterwards.

        Args:
            address (str): websocket address
        """

        config_path = Path("./config.cfg")

        if(not config_path.exists()):
            #Create the config file
            file = open(config_path,'x')
            file.close()
            
        #Write to the config file
        file = open(config_path,'w')
        file.write("# Place the config file under the appdata folder for your unity project!\n")
        file.write(f"WS_ADDRESS = ws://{address}\n")
        file.write(f"COMMS_PORT = {utils.WEBSOCKET_COMMS_PORT}\n")
        file.write(f"WEBCAM_PORT = {utils.WEBSOCKET_WEBCAM_PORT}\n")
        file.close()
        
        
        
    
    #endregion
            


    