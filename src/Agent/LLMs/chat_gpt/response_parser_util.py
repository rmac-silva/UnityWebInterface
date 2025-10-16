import json
import re
import ast


# Function that removes a JSON object from a string and returns the string and the JSON object
def remove_json_from_string(input_string, convert_to_json=False):
    results = {}
    # Regularly find {} or [] shapes in texts
    for match in re.findall(r'\{.*?\}|\[.*?\]', input_string, re.S):
        try:
            # Try to read a string as json
            results = json.loads(match)
        except json.JSONDecodeError:
            pass

    # Convert json to string
    results_string = json.dumps(results)
    return results_string, results


def extract_dictionary(content):
    # Using regular expressions to remove content between brackets
    dictionary_str = re.findall(r'\{.*?\}', content, re.S)

    # Convert str representation of dictionary to actual dictionary
    dictionary = ast.literal_eval(dictionary_str[-1])
    return dictionary


def remove_python_dictionary_from_string(input_string):
    return extract_dictionary(input_string)


# Function that removes a substring from a string
def remove_matching_substring(input_string, regex_pattern):
    result = re.sub(regex_pattern, '', input_string)
    return result


# Function that filters the response and removes two things:
#  - Quotation marks from the response
#  - Substrings that are not part of the response
def filter_response(input_string):
    pattern = r'(["\'])|(.+?(?=:))|(:)'
    result = remove_matching_substring(input_string, pattern)
    return result


if __name__ == '__main__':
    # test
    input_text = ("Given the current state of the user\'s interaction:\r\n\r\n```python\r\n{\"actions\":[\"[CBP] The "
                  "user entered the master view\"],\"ActiveItem\":\"\",\"RecommendedItems\":[],\"ItemsInCart\":["
                  "]}\r\n```\r\n\r\nThe user has just entered the master view of the online fashion store, "
                  "which signifies a Coarse Breakpoint (CBP). This indicates a significant change in the user\'s "
                  "interaction flow, such as entering a new section of the store or starting a new task. At this "
                  "stage, the user has not selected any items nor have they received any recommendations. This is a "
                  "critical moment to make a first impression and guide the user through their shopping "
                  "experience.\r\n\r\nGiven the context, it is appropriate to provide an intervention. The best "
                  "approach is to offer a welcoming message along with a broad recommendation to encourage "
                  "exploration. Since no specific preferences have been indicated yet, the recommendation should be "
                  "general, focusing on popular or new items that could appeal to a wide range of "
                  "users.\r\n\r\nTherefore, the intervention could be structured as follows:\r\n\r\n```python\r\n{"
                  "\r\n\"MessageText\": \"Welcome to our store! May we suggest some of our favorites?\","
                  "\r\n\"Action\": \"recommendation based on the user actions\",\r\n\"Reason\": \"To provide "
                  "inspiration and help you discover our best selections.\",\r\n\"ProductQuery\": \"popular items "
                  "from various brands, in multiple colors\"\r\n}\r\n```\r\n\r\nThis approach aims to engage the user "
                  "by offering assistance right at the beginning of their shopping journey, potentially enhancing "
                  "their experience and guiding them towards products they might like. The recommendation is "
                  "deliberately kept broad to cater to diverse tastes and to invite exploration.")
    print(remove_python_dictionary_from_string(input_text))

