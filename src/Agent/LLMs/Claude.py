from src.Agent.LanguageModel import LanguageModel, _create_empty_response
from src.Agent.LLMs.claude import *

import dotenv
import base64

# Set the API key
env_vars = dotenv.dotenv_values()
_secret_key = env_vars['ANTHROPIC_API_KEY']


def _process_claude_response(claude_response, response : dict):
    """
    This function is used to process the response from the Claude model.
    Args:
        claude_response: The response from the Claude model.
        response: The response to be updated with the Claude model's response.
    Returns:
        str: The processed response.
    """

    # grab tools
    output_text = claude_response.content[0].text
    tools, args, call_ids = [], [], []

    # Check for tool use in Claude response
    if hasattr(claude_response, 'content') and len(claude_response.content) > 1:
        for content_block in claude_response.content:
            if hasattr(content_block, 'type') and content_block.type == 'tool_use':
                # Extract tool information
                function_name = content_block.name
                function_args = content_block.input
                function_call_id = content_block.id

                # Debugging information
                print(f"[INFO] Function name: {function_name}")
                print(f"[INFO] Function args: {function_args}")

                # Call the function with the arguments
                tools.append(function_name)
                args.append(function_args)
                call_ids.append(function_call_id)

    # fill the response
    response['content'] = output_text

    # Tools and args are lists of function names and their arguments
    response['tools'] = tools
    response['args'] = args
    response['call_ids'] = call_ids

    return response


class Claude(LanguageModel):
    def __init__(self, model_name : str = "claude-3-5-sonnet-20241022", system_prompt : str = "You are a helpful assistant."):
        super().__init__(model_name, system_prompt)
        self.description = "This is a Claude API Wrapper."
        self.history = [] # the conversation history

        # Initialize the tools
        self.model = ClaudeModel(_secret_key, model_name=model_name, system_message=self.system_prompt)
        self.model.tools = self.tools
        self.history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def reset_system_prompt(self, new_prompt : str):
        """
        This function is used to clear the history and reset the system prompt of the LLM.
        Args:
            new_prompt (str): The new system prompt to be set.
        """
        # Clear the history and set the new system prompt
        self.model.clear_messages()
        self.model.add_message("user", new_prompt)

        # Update the system prompt in the LLM
        super().reset_system_prompt(new_prompt)

    def send_messages(self, temperature : float =0.7, max_tokens :int =600):
        llm_response = _create_empty_response(temperature)

        # Send the messages to the LLM
        claude_responses = self.model.query(temperature, max_tokens)

        # Process the response
        _process_claude_response(claude_responses, llm_response)
        llm_response['temperature'] = temperature

        # Tools and args are lists of function names and their arguments
        tool_calls = []

        # Handle Claude's response format
        if hasattr(claude_responses, 'content'):
            # Add assistant message
            self.model.add_message("assistant", llm_response["content"])
            
            # Handle tool calls if any
            for content_block in claude_responses.content:
                if hasattr(content_block, 'type') and content_block.type == 'tool_use':
                    tool_calls.append({
                        "type": "tool_use",
                        "id": content_block.id,
                        "name": content_block.name,
                        "input": content_block.input
                    })

        self.model.add_messages(tool_calls)
        self.history.append({"role": "assistant", "content": llm_response})
        return llm_response

    def query(self, message : str, temperature : float =0.7, max_tokens :int =600):
        """
        This function is used to prompt the LLM with a given prompt.

        Args:
            message (str): The prompt to be sent to the LLM.
            temperature (float): The temperature for the LLM.
            max_tokens (int): The maximum number of tokens for the LLM.
        Returns:
            str: The response from the LLM.
        """

        # Update the message history
        self.model.add_message("user", message)
        self.history.append({"role": "user", "content": message})

        # Send the messages to the LLM
        return self.send_messages(temperature, max_tokens)

    def query_with_images(self, prompt : str, images : list, temperature : float = 0.7, max_tokens : int = 600):
        """
        This function is used to prompt the LLM with a given prompt and an image.

        Args:
            prompt (str): The prompt to be sent to the LLM.
            images (list): The images to be sent to the LLM, in a byte array.
            temperature (float): The temperature for the LLM.
            max_tokens (int): The maximum number of tokens for the LLM.
        Returns:
            str: The response from the LLM.
        """

        # unpack the images
        if len(images) == 0:
            raise ValueError("No images provided for the query.")

        # Convert byte arrays to base64 strings
        images_b64 = [base64.b64encode(image).decode('utf-8') for image in images]

        # Add the images to the model - Claude expects a different format
        content = [{"type": "text", "text": prompt}]
        content = content + [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": img
                }
            }
            for img in images_b64
        ]

        # Add the message with content to the model
        self.model.add_message("user", content)
        self.history.append({"role": "user", "content": prompt, "images": content})

        # Send the messages to the LLM
        return self.send_messages(temperature, max_tokens)

    def add_tool_output(self, tool_output : str, tool_id : str):
        """
        This function is used to add the output of a tool to the LLM.
        Args:
            tool_output: The output of the tool to be added to the LLM.
            tool_id: The ID of the tool to be added to the LLM.
        """
        message = {
            "type": "tool_result",
            "tool_use_id": tool_id,
            "content": tool_output,
        }

        # Add the tool output to the model
        self.model.add_messages([message])
        self.history.append(message)

    def instruct_query(self, prompt : str):
        """
        This function is used to prompt the LLM with a given prompt.

        Args:
            prompt (str): The prompt to be sent to the LLM.
        Returns:
            str: The response from the LLM.
        """
        return self.model.instruct_query(prompt)