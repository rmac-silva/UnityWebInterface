import inspect
from src.Agent.AgentAction import AgentAction


class ActionHandler:
    def __init__(self, actions = None):
        if actions is None:
            actions = []
        self.actions = actions

    def _extract_tool_from_action(self, action: AgentAction):
        """
        Extracts the tool from the action in the required OpenAI API format.
        Args:
            action (AgentAction): The action to extract the tool from.
        Returns:
            dict: The tool formatted for the OpenAI API.
        """
        # Extract function signature
        signature = inspect.signature(action.function)
        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }

        for name, param in signature.parameters.items():
            # Map Python type hints to OpenAPI-compatible types
            param_type = {"type": "string"}  # Default to string if no annotation
            if param.annotation in [int, float, bool, str, dict, list]:
                param_type = {"type": param.annotation.__name__}
            elif param.annotation == inspect.Parameter.empty:
                param_type = {"type": "string"}  # Default if no type hint

            # Add parameter to properties
            parameters["properties"][name] = param_type

            # Add to required if no default value
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(name)

        tool = {
            "type": "function",
            "name": action.function.__name__,
            "description": action.description,
            "parameters": parameters,
            "strict": True
        }
        return tool

    def extract_tools_from_actions (self):
        """
        This function is used to extract the LLM tools from the available actions.
        Returns:
            list: The list of tools extracted from the actions.
        """
        tools = []
        for action in self.actions:
            tool = self._extract_tool_from_action(action)
            tools.append(tool)
        return tools

    def _get_action_by_name(self, function_name : str):
        """
        This function is used to get the action by its name.
        Args:
            function_name (str): The name of the function to be called.
        Returns:
            AgentAction: The action object with the given name.
        """
        return next((action for action in self.actions if action.function.__name__ == function_name), None)

    def call_action(self, function_name: str, **args):
        """
        This function is used to call a function with the given name and arguments.
        Args:
            function_name (str): The name of the function to be called.
            **args: Positional arguments to pass to the function.
        Returns:
            str: The response from the function.
        """
        action = self._get_action_by_name(function_name)

        if action:
            try:
                # Call the function with the provided arguments
                result = action.function(**args)

                # Make sure the function returns something
                assert result is not None
                return result

            except Exception as e:
                # Handle any exceptions that occur during the function call
                print(f"[ERROR] Function call failed: {repr(e)}")
                return f"Function calling failed with exception: {repr(e)}."

        # If the action is not found, return None
        return f"Tool {function_name} doesn't exist."

