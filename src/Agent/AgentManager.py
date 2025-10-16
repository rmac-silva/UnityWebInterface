import asyncio

from src.Agent.Agent import Agent
from src.Agent.ActionHandler import ActionHandler
from src.Agent.AgentAction import AgentAction
from src.Agent.LLMs.GPT import GPT

from src.Agent.Agents.ReactiveAgent import ReactiveAgent
from src.Agent.Agents.ProactiveAgent import ProactiveAgent
from src.Agent.Agents.PlaceboAgent import PlaceboAgent

from src.Agent.Configs.ReactiveConfig import ReactiveAgentConfig
from src.Agent.Configs.ProactiveConfig import ProactiveAgentConfig
from src.Agent.Configs.PlaceboConfig import PlaceboAgentConfig

# Color codes for terminal output
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = "\033[0m" # Reset to default color


class MultiTurnState():
    """
    This class is used to manage the single turn prompt state of the command line interface.
    """
    def __init__(self, agent : Agent): # type: ignore
        self.agent = agent
        self.user_prompt = f"{YELLOW}Your message to {agent.name}{RESET}:"

    def enter_state(self) -> None:
        print(f"{YELLOW}You are in multi turn mode.{RESET}")

    def process_command(self, command, image = None) -> 'MultiTurnState':
        
        if image is not None:
            print(f"{BLUE}{self.agent.plan_and_execute_with_images(command,[image])['content']}{RESET}")
        else:
            print(f"{BLUE}{self.agent.plan_and_execute(command)['content']}{RESET}")
        return self



class Message:
    """
    This class is used to manage the message history of the command line interface.
    """
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def __str__(self):
        return f"{self.role}: {self.content}"


class AgentManager():
    
    def __init__(self, llm : str, agent_type : str, app, debug = True):
        
        #State
        
        self.busy = False
        self.debug = debug
        self.type = agent_type
        #App
        self.app = app
        
        #LLM - Add other LLM models here
        if(llm.lower() == "gpt-4o-mini"):
            self.llm = GPT(model_name="gpt-4o-mini")
        elif(llm.lower() == "gpt-4o"):
            self.llm = GPT(model_name="gpt-4o")
            
        
        #Function handler
        self.setup_handler()
        
        #Agent Type
        if(self.type.upper() == "REACTIVE"):
            config = ReactiveAgentConfig()
            self.agent = ReactiveAgent(llm=self.llm, handler=self.handler, config=config, debug=self.debug) # Reactive agent
        elif(self.type.upper() == "PROACTIVE"):
            config = ProactiveAgentConfig()
            self.agent = ProactiveAgent(llm=self.llm, handler=self.handler, config=config, debug=self.debug) # Proactive Agent
            pass
        elif(self.type.upper() == "PLACEBO"):
            config = PlaceboAgentConfig()
            self.agent = PlaceboAgent(llm=self.llm, handler=self.handler, config=config, debug=self.debug) # Placebo Agent
            pass
        else:
            print(f"\n[AgentManager.py] ERROR Initializing agent, invalid type:{agent_type.upper()}, use either [REACTIVE, PROACTIVE, PLACEBO]\n")
        
        self.current_state = MultiTurnState(self.agent)
         
        
    def swap_config(self, type, llm):
        #Agent Type
        
        if(llm.lower() == "gpt-4o-mini"):
            self.llm = GPT(model_name="gpt-4o-mini")
        elif(llm.lower() == "gpt-4o"):
            self.llm = GPT(model_name="gpt-4o")
        
        if(type.upper() == "REACTIVE"):
            config = ReactiveAgentConfig()
            self.agent = ReactiveAgent(llm=self.llm, handler=self.handler, config=config, debug=self.debug) # Reactive agent
        elif(type.upper() == "PROACTIVE"):
            config = ProactiveAgentConfig()
            self.agent = ProactiveAgent(llm=self.llm, handler=self.handler, config=config, debug=self.debug) # Proactive Agent
            pass
        elif(type.upper() == "PLACEBO"):
            config = PlaceboAgentConfig()
            self.agent = PlaceboAgent(llm=self.llm, handler=self.handler, config=config, debug=self.debug) # Placebo Agent
            pass
        else:
            print(f"\n[AgentManager.py] ERROR Initializing agent, invalid type:{type.upper()}, use either [REACTIVE, PROACTIVE]\n")


        self.current_state = MultiTurnState(self.agent)
        
        
    
    def setup_handler(self):
        """This function will setup the tools that the agent can use. It is here where you can define additional tools for the agent 
        to call. With each entry, you will have to provide a real python function to be executed, what arguments are expected and 
        a short description of what the tool does.
        
        The information for each tool will later be extracted from the AgentAction object.
        """
        
        
        self.handler = ActionHandler(actions=[
        
        # COMMUNICATION TOOLS
        AgentAction(type="COMMUNICATION", function=self.stop, args=[], description="Stop and wait for the user to talk."),

        ])
        
        if(self.type.upper() == "PLACEBO"):
            # The placebo talk function takes two arguments, the two possible responses the wizard can choose from
            self.handler.actions.append(
                AgentAction(type="COMMUNICATION", function=self.talk_p, args=["response1","response2"], description="Talk to the user, providing two possible answers")
            )
        else:
            # Other agent types use the normal talk function, which takes one argument, the message to send to the user
            self.handler.actions.append(
                AgentAction(type="COMMUNICATION", function=self.talk, args=["message"], description="Talk to the user")
            )

    # COMMUNICATION TOOLS
    def talk(self, message):
        """
        This function is called when the agent wants to send a message to the user.
        """
        if(self.debug):print(f"{BLUE}[TALK] Agent: {message} {RESET}")
        
        self.app.send_message_to_user(message) # Call the function equivalent in your main application.
            
        return 'Message sent successfully' 
    
    def talk_p(self, response1, response2):
        """
        This function is called when the PLACEBO agent wants to send a message to the user.
        """
        if(self.debug):print(f"{BLUE}[PLACEBO TALK] Agent: {response1} | {response2} {RESET}")
        
        self.app.add_placebo_message((response1,response2)) # Call the function equivalent in your main application.
            
        return 'Messages sent successfully' 

    def stop(self):
        """
        This function is called when the agent wants to stop the agent.
        """
        if(self.debug):print(f"{RED}[STOP] Agent stopped.{RESET}")
        self.busy = False
        self.app.enable_agent()
        return 'Agent stopped successfully' 
    
    async def prompt_agent(self, prompt, image = None):
        """Prompt the agent 

        Args:
            prompt (str): The user prompt in text
            image (img(base64), optional): An encoded image to pass to the agent. Defaults to None.
        """
        
        if(self.busy):
            self.app.create_dashboard_notification("[AGENT] Agent was busy, ignoring previous prompt...")
            return
        
        self.app.create_dashboard_notification("[AGENT] Processing prompt!")
        self.busy = True
        self.app.disable_agent()
        await asyncio.to_thread(self.current_state.process_command, prompt, image)


    

    
