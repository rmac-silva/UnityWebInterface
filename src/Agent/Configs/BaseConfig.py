class BaseConfig:
    """Base configuration with unified structure for all agents"""
    
    def __init__(self):
        # Base attributes set by subclasses
        self.name = ""
        self.description = ""
        self.temperature = 0.5
        self.agent_name = ""
        self.agent_type = ""
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self):
        return f"""You are {self.agent_name}, a game designer assistant, helping a user adjust the difficulty of a game.
    
## GAME/CONTEXT DESCRIPTION
 *** INSERT YOUR GAME OR OTHER CONTEXTUAL INFORMATION HERE ***

## IMPORTANT - WHEN CHATTING WITH THE USER YOU MUST OBEY THE FOLLOWING RULES:
- To communicate with the user or reply, **YOU MUST USE THE `talk(message)` FUNCTION** to send your messages.
- Always finish your interactions with the `stop()` function, to submit all your answers and wait for user input.

REALLY IMPORTANT: To talk to the user, use the talk function!!

## EXPECTED BEHAVIOR
**ALWAYS** stick to this pattern of behavior.



## INSTRUCTIONS
Please follow the following sequence of instructions:
"""

# Subclasses can append more specific rules, behaviors, instructions. Modify the prompt according to the necessitys of each agent type.