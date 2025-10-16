from src.Agent.Agent import Agent

class ProactiveAgent(Agent):
    def __init__(self, **kwargs):
        """
        Initialize the ReactiveAgent with the given parameters.

        Args:
            **kwargs: Additional parameters for the agent.
        """

        # import the configuration

        # Set the default values
        super().__init__(**kwargs)

        # Initialize the LLM
        self.name = self.config.name
        self.description = self.config.description

        self._update_system_prompt(self.system_prompt)
        self.temperature = self.config.temperature


    def instruct_query(self, prompt : str):
        """
        This function is used to prompt the LLM with a given prompt.

        Args:
            prompt (str): The prompt to be sent to the LLM.
        Returns:
            str: The response from the LLM.
        """
        return self.llm.instruct_query(prompt)