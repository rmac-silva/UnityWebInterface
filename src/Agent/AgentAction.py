from typing import Callable, Union

class AgentAction:
    
    def __init__(self, type : str, function : Callable, args : Union[list, tuple, dict],  description : str ):
        self.type = type
        self.args = args
        self.function = function
        self.description = description
        self.executed = False
        self.disabled = False
        
    def activate(self):
        """Executes the function, with the stored arguments

        Raises:
            TypeError: If the function can't be executed due to the arguments not being one of the supported types

        Returns:
            Any: The result of the function call
        """
        
        self.executed = True 
        
        if isinstance(self.args, dict):
            #print("Dict")
            return self.function(**self.args)
        
        elif isinstance(self.args, (list)):
            #print("List")
            return self.function([*self.args])
        
        elif isinstance(self.args, (tuple)):
            #print("Tuple")
            return self.function(*self.args)
        
        elif isinstance(self.args, object):
            #print("Object")
            return self.function(*self.args)
        
        else:
            raise TypeError("Unsupported argument type for 'args' in AgentAction. Supported types are: list, tuple, dict, object.")
        
    def get_action_notification(self):
        """Returns the "label" for the agent action, for easy formatting in the agent log in the dashboard.

        Returns:
            _type_: _description_
        """
        
        return f"[{self.type}] Agent wants to execute {self.function.__name__} with args: {self.print_args()}"
    
    def get_state(self):
        """Returns the state of the agent action (EXECUTED, DENIED, PENDING)

        Returns:
            str: The current state
        """
        
        if(self.executed):
            return "EXECUTED"
        elif(self.disabled):
            return "DENIED"
        else:
            return "PENDING"
    
    def print_args(self, limit = True):
        """Returns the arguments of the action as a string

        Args:
            limit (bool, optional): Whether to limit the output. Defaults to True.

        Returns:
            str: The arguments of the action as a string.
        """
        
        args_str = ""
        if isinstance(self.args, dict):
            # Keyword arguments
            args_str = ', '.join(f"{k}={v!r}" for k, v in self.args.items())
        elif isinstance(self.args, list):
            # Positional arguments
            for arg in self.args:
                if(isinstance(arg,object)):
                    args_str += f"{self._get_object_attributes(arg, limit)} | \n"
                else:
                    args_str = ', '.join(f"{arg}")
        elif isinstance(self.args, object):
            args_str = self._get_object_attributes(self.args, limit)
        else:
            # Fallback
            args_str = repr(self.args)
        if(len(args_str) == 0 ):
            return "NO_ARGS"
        
        return args_str
    
    def _get_object_attributes(self, obj, limit = True):
        # Iterate over the object's attributes
        try:
            attributes = vars(obj)
            # Create a string of attributes and values
            attributes_str = ', '.join(f"{key}={value!r}" for key, value in attributes.items())
            attributes_str.replace('"',"'")
            return f"<{type(obj).__name__}( {attributes_str} )>"
        except:
            try:
                return obj if len(obj) < 100 or not limit else obj[0:99] 
            except:
                return obj
    
    def disable(self):
        """Disable an action that was pending
        """
        self.disabled = True
        
    def get_color(self):
        """Returns a color based on the action type. 

        Returns:
            str: TailwindCSS Color
        """
        match(self.type):
            
            case "CONTEXT":
                return "bg-green-200" if (self.executed or self.disabled) else "bg-green-400"
            case "MSG":
                return "bg-orange-200" if (self.executed or self.disabled) else "bg-orange-400"
            case "SYNC":
                return "bg-amber-200" if (self.executed or self.disabled) else "bg-amber-400"
            case _:
                return "bg-violet-200" if (self.executed or self.disabled) else "bg-violet-400"
    