import anthropic
import dotenv
import json
import base64

# Set the API key
env_vars = dotenv.dotenv_values()
_secret_key = env_vars['ANTHROPIC_API_KEY']


class ClaudeModel:
    def __init__(self, api_key, system_message='You are a helpful assistant.', model_name='claude-3-5-sonnet-20241022'):
        self.model_name = model_name
        self.api_key = api_key

        # Initialize the API client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.messages = []  # role : string, content : string
        self.system_message = system_message
        self.tools = []  # the tools that the agent can use

    # add a message to the conversation
    def add_message(self, role, content, name=''):
        if name != '':
            self.messages.append({"role": role, "name": name, "content": content})
            return

        # Handle content parameter - it can be a string or a list of content blocks
        if isinstance(content, list):
            # Content is already in the correct format for Claude
            self.messages.append({"role": role, "content": content})
        else:
            # Content is a string, convert to Claude format
            self.messages.append({"role": role, "content": [{"type": "text", "text": content}]})

    # add a list of messages to the conversation
    def add_messages(self, messages):
        self.messages.extend(messages)

    # clear the conversation
    def clear_messages(self):
        self.messages = []

    # get the last message of the conversation
    def get_last_message(self):
        return self.messages[-1]

    # send the messages to the API and get the response
    def query(self, temperature=0.7, max_tokens=600):
        # Convert messages to Claude format
        claude_messages = []
        for msg in self.messages:
            if msg["role"] == "system":
                # Claude doesn't use system messages in the same way, so we'll prepend to the first user message
                continue
            elif msg["role"] == "user":
                # Handle content format - it can be a list or string
                if isinstance(msg["content"], list):
                    # Content is already in Claude format
                    claude_messages.append({"role": "user", "content": msg["content"]})
                else:
                    # Content is a string, convert to Claude format
                    claude_messages.append({"role": "user", "content": [{"type": "text", "text": msg["content"]}]})
            elif msg["role"] == "assistant":
                # Handle content format for assistant messages
                if isinstance(msg["content"], list):
                    claude_messages.append({"role": "assistant", "content": msg["content"]})
                else:
                    claude_messages.append({"role": "assistant", "content": [{"type": "text", "text": msg["content"]}]})

        # Add system message to the first user message if it exists
        if claude_messages and claude_messages[0]["role"] == "user":
            # Prepend system message to the first user message
            if isinstance(claude_messages[0]["content"], list):
                # Insert system message at the beginning of the content list
                claude_messages[0]["content"].insert(0, {"type": "text", "text": self.system_message})
            else:
                # Convert to list format and add system message
                claude_messages[0]["content"] = [
                    {"type": "text", "text": self.system_message},
                    {"type": "text", "text": claude_messages[0]["content"]}
                ]

        if self.tools:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=claude_messages,
                tools=self.tools
            )
        else:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=claude_messages
            )

        return response

    def instruct_query(self, prompt):
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=600,
            temperature=0.7,
            messages=[
                {"role": "user", "content": f"{self.system_message}\n\n{prompt}"},
            ]
        )

        answer = response.content[0].text
        return answer 