from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage

from src.Agent.LanguageModel import LanguageModel, _create_empty_response
from src.Agent.LLMs.chat_gpt.gpt_api_wrapper import GPTModel
import dotenv
import json

import base64

# Set the API key
env_vars = dotenv.dotenv_values()
_secret_key = env_vars['OPENAI_API_KEY']


def _process_gpt_response(gpt_response, response : dict):
    """
    This function is used to process the response from the GPT model.
    Args:
        gpt_response: The response from the GPT model.
        response: The response to be updated with the GPT model's response.
    Returns:
        str: The processed response.
    """

    # grab tools
    output_text = gpt_response.output_text
    tools, args, call_ids = [], [], []

    for model_response_output in gpt_response.output:
        # check if the first tool is a function call
        if isinstance(model_response_output, ResponseFunctionToolCall):

            # call the function
            function_name = model_response_output.name
            function_args = json.loads(model_response_output.arguments)
            function_call_id = model_response_output.call_id

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


class GPT(LanguageModel):
    def __init__(self, model_name : str = "gpt-4o-mini", system_prompt : str = "You are a helpful assistant."):
        super().__init__(model_name, system_prompt)
        self.description = "This is a GPT4oMini API Wrapper."
        self.history = [] # the conversation history

        # Initialize the tools
        self.model = GPTModel(_secret_key, model_name=model_name,system_message=self.system_prompt)
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
        self.model.add_message("system", new_prompt)

        # Update the system prompt in the LLM
        super().reset_system_prompt(new_prompt)

    def send_messages(self, temperature : float =0.7, max_tokens :int =600):
        llm_response = _create_empty_response(temperature)

        # Send the messages to the LLM
        gpt_responses = self.model.query(temperature, max_tokens)

        # Process the response
        _process_gpt_response(gpt_responses, llm_response)
        llm_response['temperature'] = temperature

        # Tools and args are lists of function names and their arguments
        tool_calls = []

        for gpt_response in gpt_responses.output:
            if isinstance(gpt_response, ResponseOutputMessage):
                self.model.add_message("assistant", llm_response["content"])
            else:
                tool_calls.append({
                    "type": "function_call",
                    "id": gpt_response.id,
                    "call_id": gpt_response.call_id,
                    "name": gpt_response.name,
                    "arguments": gpt_response.arguments
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

        # Add the images to the model
        content = [{"type": "text", "text": prompt}]
        content = content + [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img}"}
            }
            for img in images_b64
        ]

        self.model.add_message("user", prompt, content)
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
            "type": "function_call_output",
            "call_id": tool_id,
            "output": tool_output,
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