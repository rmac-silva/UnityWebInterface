from openai import OpenAI
import dotenv

# Set the API key
env_vars = dotenv.dotenv_values()
_secret_key = env_vars['OPENAI_API_KEY']


class GPTModel:
    def __init__(self, api_key, system_message='You are a helpful assistance.', model_name='gpt-3.5-turbo-instruct'):
        self.model_name = model_name
        self.api_key = api_key

        # Initialize the API client
        self.client = OpenAI(api_key=self.api_key)
        self.messages = []  # role : string, content : string
        self.system_message = system_message
        self.messages.append({"role": "system", "content": system_message})
        self.tools = []  # the tools that the agent can use

    # add a message to the conversation
    def add_message(self, role, content, name=''):
        if name != '':
            self.messages.append({"role": role, "name": name, "content": content})
            return

        self.messages.append({"role": role, "content": content})

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
        if self.tools:
            response = self.client.responses.create(
                model=self.model_name,
                input=self.messages,
                tools=self.tools,
                max_output_tokens= max_tokens,
                temperature=temperature
            )

        else:
            response = self.client.responses.create(
                model=self.model_name,
                input=self.messages,
                max_output_tokens= max_tokens,
                temperature=temperature
            )

        return response

    def instruct_query(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt},
            ]
        )

        answer = response.choices[0].message.content
        return answer


stat_question_1 = "You are a Python programmer aiding me in my Data Science task. I have a data frame with scores from " \
                  "users. I want to do a Chi-Square test that has the following signature:\n" \
                  "\n" \
                  "```py\n" \
                  "# df - dataframe\n" \
                  "def chi_square_test(df, column1, column2):\n" \
                  "   # TODO: Implement\n" \
                  "   return 0\n" \
                  "```\n" \
                  "\n" \
                  "This function will see if there is a statistical difference between these scores. " \
                  "So, my hypothesis is: THESE SCORES ARE DIFFERENT. Keep this in mind!\n" \
                  "Explain your reasoning step by step, and then complete the function."

stat_question_2 = "Hello! I want to see if two rows of discrete values are significantly different. " \
                  "Knowing that these are discrete values from two interfaces that were " \
                  "attributed by users. Remember that this are DISCRETE VALUES, meaning you can't perform a t-tes. my " \
                  "hypothesis is that \"THESE SCORES ARE " \
                  "DIFFERENT,\" find the correct approach to prove this. Keep in mind that the " \
                  "users evaluated both interfaces, but the test order was alternated to reduce " \
                  "the learning bias. Explain your reasoning step by step and end with a Python " \
                  "implementation of this proof."

rq_contribution = "You are a helpful assistant, aiding me in my academic writing. I want to highlight the contributions " \
                  "of my paper in the introduction. We can summarize the contribution in the following paragraphs explaining our conclusions:\n" \
                  "\"With this user test, we were able to conclude that, in our interface, the user's engagement is much higher when " \
                  "interacting with the store with the conversational agent, compared to interacting with the store " \
                  "by itself or just the conversational agent. This might have to do with the perceived usability of " \
                  "the store, with the conversational agent being much higher than the conversational agent by " \
                  "itself. Furthermore, users considered the experience of interacting with the first interface much " \
                  "more rewarding than the latter, which also explains their increase in engagement." \
                  "Another interesting conclusion is that users tended to either ignore or get annoyed by the message " \
                  "attention grabbers that conversational agents would send during their interaction with the agent, with more than 90% of users not noticing the message notifications." \
                  "With this paper, we were also able to identify the future points of interest for further research and what problems should be tackled in other research.\"" \
                  "\n" \
                  "Explain step by step how you should present and explain Research Questions and Contributions in a paper's introduction, and afterward, write 2 to 4 bullet points in latex for my paper's research questions and contributions."


dictionary_question = ("Write a Python function to extract a dictionary from a markdown file. Remember, the file "
                       "usually starts { and ends with }, and the markdown may contain additional text; the "
                       "dictionary may contain comments. Lie we see in this example: \r\n\r\n- Example 1:\r\nGiven "
                       "the user\'s actions, it seems the user is particularly interested in Diesel brand products, "
                       "specifically shirts and has also purchased a Diesel aviator felt jacket. Despite the variety "
                       "of interactions, there is a clear pattern of interest in Diesel\'s offerings, particularly in "
                       "shirts based on the repeated selection of the check-pattern long-sleeve shirt and the "
                       "long-sleeved cotton denim shirt.\r\n\r\nAt this point, the user has just performed a search "
                       "for another item (presumably misspelled \"Carhartt\" as \"caarhart\"), indicating they might "
                       "be looking to explore items beyond Diesel or are interested in similar brands. This presents "
                       "an opportune moment to intervene with a recommendation, as it follows a Fine Breakpoint (FBP) "
                       "related to searching for items. Recommending products at this juncture could enhance the "
                       "user\'s shopping experience by aligning with their current exploratory behavior and "
                       "interests, potentially guiding them towards items that compliment their recent Diesel "
                       "purchases or exploring similar brands like Carhartt.\r\n\r\nConsidering the user\'s "
                       "demonstrated interest and the timing after a search action (which might indicate the user "
                       "hasn\'t found what they were looking for or is open to suggestions), intervention seems "
                       "appropriate. The recommendation should focus on either Diesel products, given the user\'s "
                       "clear interest, or offer alternatives from a similar brand like Carhartt, which the user "
                       "attempted to search for. With the focus on shirts (based on past selections), "
                       "a recommendation along these lines would be most relevant.\r\n\r\nTherefore, the intervention "
                       "could be structured as follows:\r\n\r\n```python\r\n{\r\n\"MessageText\": \"Explore more from "
                       "Diesel and similar brands!\",\r\n\"Action\": \"recommendations based on the viewed items\","
                       "\r\n\"Reason\": \"You seem to like Diesel. Here\'s something similar you might enjoy.\","
                       "\r\n\"ProductQuery\": \"shirt from Carhartt, in any color\" # Assuming the user\'s misspelled "
                       "search indicates an interest in Carhartt.\r\n}\r\n```\r\n\r\nStart your answer by giving "
                       "another 5 unique examples and then write the code.")

help = ('write ta a pyhton regular expression that removes all the content that is sealed by two bracket, '
        'like this:\r\nInput: Given the user\'s action sequence and the current state of their interaction, '
        'it seems that the user has just applied a filter for shoes, which is a significant action indicating their '
        'interest in a specific type of product. This action can be considered a Coarse Breakpoint ([CBP]) since it '
        'significantly narrows down the scope of the user\'s interest within the master view. Given that the best '
        'practice is to intervene at or just after a coarse breakpoint, this would be an appropriate moment to offer '
        'assistance.\r\n\r\nThe user has not yet selected an active item or added anything to their cart, suggesting '
        'they are still in the browsing phase and might benefit from a recommendation that aligns with their current '
        'interest (shoes). This intervention should aim to enhance their shopping experience by suggesting items that '
        'match their search criteria, potentially leading to a higher level of engagement or a '
        'purchase.\r\n\r\nConsidering these factors, the intervention should be as follows:\r\n\r\n```python\r\n{'
        '\r\n\"MessageText\": \"Check out the latest trends in footwear!\",\r\n\"Action\": \"recommendation based on '
        'the user actions\",\r\n\"Reason\": \"You might like these shoes based on your search.\",'
        '\r\n\"ProductQuery\": \"shoes from popular brands, in various colors\"\r\n}\r\n```\r\n\r\nThis '
        'recommendation is based on the user\'s action of filtering for shoes, indicating a clear interest in this '
        'type of product. The recommended action is to suggest similar products, specifically shoes from popular '
        'brands and in various colors, to cater to a broad taste and potentially match the user\'s preferences. The '
        'message is concise and aims to pique the user\'s interest by highlighting the latest trends, making the '
        'shopping experience more engaging.\r\n\r\nShould I interrupt the user? Yes, because this is a strategic '
        'point to offer relevant recommendations that align with their expressed interest, potentially enhancing '
        'their shopping experience and guiding them towards a purchase.;\r\nOutput: {\r\n\"MessageText\": \"Check out '
        'the latest trends in footwear!\",\r\n\"Action\": \"recommendation based on the user actions\",'
        '\r\n\"Reason\": \"You might like these shoes based on your search.\",\r\n\"ProductQuery\": \"shoes from '
        'popular brands, in various colors\"\r\n}')


if __name__ == '__main__':
    client = OpenAI(api_key=_secret_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Your are professional python programmer."},
            {"role": "user", "content": help},
        ]
    )

    print(response.choices[0].message.content)
