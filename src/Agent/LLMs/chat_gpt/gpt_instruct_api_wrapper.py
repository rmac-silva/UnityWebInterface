import dotenv
from openai import OpenAI

# from response_parser_util import remove_json_from_string, filter_response

# Class that handles the communication with the chatbot and chatgpt
#  I intend on using either gpt 3.5 or 4.0 (depend on how much I'm whiling to spend).

env_vars = dotenv.dotenv_values()
_secret_key = env_vars['OPENAI_API_KEY']


# GPT3.5 Class that basically works like a wrapper for the CHATGPT API connection

class GPTModelInstruct:
    def __init__(self, api_key, model_name='gpt-3.5-turbo-instruct'):
        self.model_name = model_name
        self.api_key = api_key

        # Initialize the API client
        self.client = OpenAI(api_key=self.api_key)

    # This type of prompt only works for the GPT3.5 instruct model
    def prompt(self, prompt):
        response = self.client.completions.create(
            model=self.model_name,
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )

        answer = response.choices[0].text.strip()
        return answer


if __name__ == "__main__":
    # Test the GPT3.5 API
    gpt35 = GPTModelInstruct(_secret_key, 'gpt-3.5-turbo-instruct')
    test_prompt = f'You are aiding a customer in an online fashion store.\n' \
                  f'The sequence of events are described using the following pattern:\n' \
                  f'- Major Task\n' \
                  f'   - Fine Task\n' \
                  f'\n' \
                  f'You should only intervene if the user is at the start of a Major Task or at the end of a Major Task.\n' \
                  f'\n' \
                  f'The user did the following sequence of events:\n' \
                  f'\n' \
                  f'- Moves to the shopping menu;\n' \
                  f'   - Select the search bar option;\n' \
                  f'   - Types in sales;\n' \
                  f'   - Hits the Enter key;\n' \
                  f'\n' \
                  f'Write an eye-catching intervention using the following format:\n' \
                  f'\n' \
                  '{\n' \
                  f"\"intervention_text\": 'string',\n" \
                  f"\"should_you_intervene\": 'bool',\n" \
                  f"product_recommendation_query\": 'string',\n" \
                  f"\"contains_product\": 'bool'\n" \
                  '}'

    # print(prompt)
    test_answer = gpt35.prompt(test_prompt)
    print(test_answer)
