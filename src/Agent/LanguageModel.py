
def _create_empty_response(temperature : float = 0.7):
    """
    This function is used to create an empty response for the LLM.
    Returns:
        dict: The empty response from the LLM.
    """

    return {
        'role': 'assistant',
        'content': '',
        'weights': 0.5,
        'sequence_length': -1,
        'temperature': temperature,
        'tools': [],
        'args': []
    }


class LanguageModel:
    def __init__(self, model_name : str = "LLM", system_prompt : str = "You are a helpful assistant."):
        self.name = model_name
        self.system_prompt = system_prompt
        self.description = "This is a LLM agent"
        self.history = [] # the conversation history
        self.tools = [] # list of possible actions the agent can take

    def reset_system_prompt(self, new_prompt : str):
        """
        This function is used to clear and update the system prompt of the LLM.
        Args:
            new_prompt (str): The new system prompt to be set.
        """

        system_prompt = { "content" : new_prompt, "role" : "system" }
        self.system_prompt = system_prompt
        self.history = [system_prompt]

    def add_tool(self, tool):
        """
        This function is used to add a tool to the LLM.
        Args:
            tool: The tool to be added to the LLM.
        """

        self.tools.append(tool)

    def add_tools(self, tools):
        self.tools += tools

    def add_tool_output(self, tool_output : str, tool_id : str):
        """
        This function is used to add the output of a tool to the LLM.
        Args:
            tool_name: The name of the tool to be added to the LLM.
            tool_output: The output of the tool to be added to the LLM.
            tool_id: The ID of the tool to be added to the LLM.
        """
        return -1 # TODO: Not implemented

    def instruct_query(self, prompt : str):
        """
        This function is used to prompt the LLM with a given prompt.
        TODO: You need to implement the logic to send the prompt to the LLM and get the response.

        Args:
            prompt (str): The prompt to be sent to the LLM.
        Returns:
            str: The response from the LLM.
        """

        return {
            'role': 'assistant',
            'content': 'This is a response from the LLM.',
            'weights': [],
            'sequence_length': 10,
            'temperature': 0.7
        }

    def query_with_images(self, prompt : str, images : list, temperature : float = 0.7, max_tokens : int = 600):
        """
        This function is used to prompt the LLM with a given prompt and an image.

        Args:
            prompt (str): The prompt to be sent to the LLM.
            images(list): The image to be sent to the LLM.
            temperature (float): The temperature for the LLM.
            max_tokens (int): The maximum number of tokens for the LLM.
        Returns:
            str: The response from the LLM.
        """

        return {
            'role': 'assistant',
            'content': 'This is a response from the LLM with an image.',
            'weights': 0.5,
            'sequence_length': 10,
            'temperature': 0.7
        }

    def send_messages(self, temperature : float = 0.7, max_tokens : int = 600):
        """
        This function is used to send the messages to the LLM.
        Args:
            temperature (float): The temperature for the LLM.
            max_tokens (int): The maximum number of tokens for the LLM.
        Returns:
            str: The response from the LLM.
        """

        return -1 # Not implemented yet

    def query(self, prompt : str, temperature : float =0.7, max_tokens :int =600):
        """
        This function is used to prompt the LLM with a given prompt.

        Args:
            prompt (str): The prompt to be sent to the LLM.
        Returns:
            str: The response from the LLM.
        """

        return {
            'role': 'assistant',
            'content': 'This is a response from the LLM.',
            'weights': 0.5,
            'sequence_length': 10,
            'temperature': 0.7,
            'tools': [],
            'args': []
        }

