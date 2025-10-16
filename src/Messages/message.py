from typing import List
import json
import time
import copy


class Message():
    """Represents a message, saving information about who sent it, 
    """
    
    def __init__(self,sender,content):
        self.sender = sender
        self.content = content
        self.stamp = ""
        
    def __jsonify__(self):
        return json.dumps({"sender" : self.sender, "content" : self.content})
        
    def get_content(self):
        return self.content
    
    def get_sender(self) -> str:
        return self.sender
    
    def get_timestamp(self):
        return self.stamp

class MessageLog():
    
    def __init__(self, messages = []):
        self.messages : List[Message] = messages
        
    def __jsonify__(self):
        return {"messages" : self.messages}
        
    def get_last_message(self):
        return self.messages[-1]
    
    def get_last_message_json(self):
        return self.messages[-1].__jsonify__()
    
    def get_all_messages(self):
        return self.messages
    
    def get_all_messages_json(self):
        # Convert the messages to a list of dictionaries
        messages_dict = [message.__jsonify__() for message in self.messages]
        return {"messages": messages_dict}
    
    def clear_messages(self):
        self.messages.clear()
    
    def replace_message_log(self,data):
        self.clear_messages()
        
        for entry in data["messages"]:
            # print(entry)
            self.messages.append(Message(entry["sender"],entry["content"]))
    
    def add_message(self, message : Message):
        message.stamp = self.get_timestamp()
        self.messages.append(message)
    
    def get_timestamp(self):
        now = time.time()
        return time.strftime("%H:%M:%S",time.localtime(now))

class PlaceboOption():
    
    def __init__(self, text, index):
        self.text = text
        self.index = index

class PlaceboManager():
    def __init__(self):
        self.options : List[PlaceboOption] = []
        self.msg_index = 0
        
    def add_placebo_options(self,message_pair : tuple[str,str]):
        self.msg_index += 1
        self.options.append(PlaceboOption(message_pair[0],self.msg_index))
        self.options.append(PlaceboOption(message_pair[1],self.msg_index))
        
    def clear_placebo_options(self, index):
        options_copy = copy.copy(self.options)
        for option in options_copy:
            if(option.index == index):
                self.options.remove(option)
        
    def get_message_from_option(self, message : PlaceboOption):
        try:
            return Message("agent",message.text)
        except ValueError:
            return Message("","")
        
