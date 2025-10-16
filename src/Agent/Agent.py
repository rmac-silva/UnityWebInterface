from src.Agent.LanguageModel import LanguageModel
from src.Agent.ActionHandler import ActionHandler


class Agent:
    """
    This class is used to manage the agent's state and interact with the LLM.
    It call functions from the LLM class to get the response.
    """

    def __init__(self, llm: LanguageModel, handler: ActionHandler, config, debug: bool):
        self.name = ""
        self.llm = llm
        self.debug = debug
        self.config = config
        
        # Update the LLM system prompt with the one from config
        self.system_prompt = config.system_prompt
        self.llm.reset_system_prompt(self.system_prompt)

        # Initialize the tools
        self.tools = []  # list of possible actions the agent can take
        self.handler = handler

        # Update the tools
        tools = self.handler.extract_tools_from_actions()
        self.llm.add_tools(tools)

        # Use temperature from config
        self.temperature = config.temperature
        self.max_tokens = 600

    def update_config(self, new_config):
        """
        Updates the agent's configuration with a new config object.
        This will update the system prompt, temperature, and other configurable parameters.
        
        Args:
            new_config: A configuration object that follows the same interface as the current config
        """
        self.config = new_config
        
        # Update system prompt
        self.system_prompt = new_config.system_prompt
        self.llm.reset_system_prompt(self.system_prompt)
        
        # Update temperature
        self.temperature = new_config.temperature
        
        if self.debug:
            print(f"[Agent] Updated configuration:")
            print(f"  - System prompt updated")
            print(f"  - Temperature set to {self.temperature}")

    def _update_system_prompt(self, system_prompt : str):
        self.system_prompt = system_prompt
        self.llm.reset_system_prompt(system_prompt)

    def _update_tools(self, model_response : dict):
        """
        This function is used to update the tools of the LLM.
        Args:
            model_response (dict): The response from the LLM.
        """

        # Check if the first tool is a function call
        for tool, args, tool_id in zip(model_response["tools"], model_response["args"], model_response["call_ids"]):
            # Calculate the tool output and add it to the LLM
            tool_output = self.handler.call_action(tool, **args)

            # verify if it is a byte array
            if isinstance(tool_output, list):
                tool_output = [str(item) for item in tool_output]

            self.llm.add_tool_output(str(tool_output), tool_id)

        # Send the messages to the LLM
        model_response = self.llm.send_messages(self.temperature, self.max_tokens)

        # Process the tool output
        if(self.debug):
            print(f"[INFO] model response: {model_response}")

        if len(model_response["tools"]) > 0:
            return self._update_tools(model_response)

        return model_response

    def plan_and_execute(self, user_message : str):
        """
        This function is used to converse with the LLM.

        Args:
            user_message (str): The message to be sent to the LLM.
        Returns:
            str: The response from the LLM.
        """
        model_response = self.llm.query(user_message, self.temperature, self.max_tokens)

        # Verify tool usage
        if(self.debug):print(f"[INFO] Model response: {model_response}")

        if len(model_response["tools"]) > 0:
            self._update_tools(model_response)

        return model_response

    def plan_and_execute_with_images(self, user_message : str, images : list):
        """
        This function is used to converse with the LLM with images.

        Args:
            user_message (str): The message to be sent to the LLM.
            images (list): The images to be sent to the LLM, in a byte array.
        Returns:
            str: The response from the LLM.
        """
        model_response = self.llm.query_with_images(user_message, images, self.temperature, self.max_tokens)

        # Verify tool usage
        if(self.debug):print(f"[INFO] Model response: {model_response}")

        if len(model_response["tools"]) > 0:
            self._update_tools(model_response)

        return model_response

    def instruct_query(self, prompt : str):
        """
        This function is used to prompt the LLM with a given prompt.

        Args:
            prompt (str): The prompt to be sent to the LLM.
        Returns:
            str: The response from the LLM.
        """

        return self.llm.instruct_query(prompt)
    
    