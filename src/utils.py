import socket
import os
from pathlib import Path
import time

#Ports to use
WEBSOCKET_WEBCAM_PORT = 5000
WEBSOCKET_COMMS_PORT = 5001
WEBSOCKET_MSG_SIZE = 4 * 1024 * 1024

#Directories, assumes everything is local ./
script_dir = ""
media_path = script_dir + "/Media"
log_path = script_dir + "/WebappLogs"
media_path_graphs = script_dir + "/Media/graphs"



# ! Message types, 8 bits maximum.
## Messaging
class MessageTypes:
    """To add new message types simply add a new entry here. They can have a maximum of 8 characters in length.
    """
    
    MESSAGE_TYPE = "M" #Represents a text message
    MESSAGE_SYNC = "MSG_SYNC" #Represents a message sync, where unity and the dashboard exchange the message logs


class StylingHelper():
    """This styling helper can help define the styling for the dashboard UI elements. You can define additional colors and variables here.
    """
    def __init__(self):
        
        self.bg_color = "#e6e6e6"

def generate_padding(len : int):
    return '#'*len

def get_ip():
    """Returns your current IP address to use in the hosting address for nicegui

    Returns:
        str: Your current local public IP address
    """
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class Logger():
    """A logger that automatically runs on each websocket connection.
    """
    
    def __init__(self):
        self.log_file = None   
    
    def create_new_log(self):
        self.current_time = f"{get_current_date_formatted()}--{get_current_time_formatted()}"
        self.open_file()
        
    def close_logs(self):
        if(self.log_file is not None):
            self.log_file.close()
            self.log_file = None

    
    def open_file(self):
        if(Path(log_path).exists()):
            self.log_file = open(f"{log_path}/{self.current_time}.csv",'x')
        else:
            os.mkdir(log_path)
            self.log_file = open(f"{log_path}/{self.current_time}.csv",'x')
        
        # ! Write the header of your log file here
        # self.log_file.write("turn;action;author;timestamp;function_name;execution_state\n")
        
        
    
    def write_to_file(self,content : str):
        """Writes a string to the log file, assuming it is already opened.

        Args:
            content (str): The content to write to the log file.
        """
        if(self.log_file is None):
            return
        
        self.log_file.write(f"{content}\n")
        self.log_file.flush()
        
        
def get_current_time_formatted():
    return time.strftime("%Hh-%Mm-%Ss", time.localtime())

def get_current_date_formatted():
    return time.strftime("%Y-%m-%d", time.localtime())

