from openai import OpenAI
import os
from dotenv import load_dotenv
from actions import get_response_time, restart_application
from restart_prompt import restart_system_prompt
from prompts import system_prompt
from json_helpers import extract_json
import sys

# Load environment variables
load_dotenv()

def generate_text_with_conversation(messages, model="gpt-4o"):

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.getenv("GITHUB_TOKEN")
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content


#Available actions are:
available_actions = {
    "restart_application": restart_application
}

user_prompt = input("Enter your command: ")

messages = [
    {"role": "system", "content": restart_system_prompt},
    {"role": "user", "content": user_prompt},
]

turn_count = 1
max_turns = 5

while turn_count < max_turns:
    print (f"Loop: {turn_count}")
    print("----------------------")
    turn_count += 1

    response = generate_text_with_conversation(messages, model="gpt-4o")

    print(response)

    json_function = extract_json(response)

    if json_function:
            function_name = json_function[0]['function_name']
            function_parms = json_function[0]['function_parms']
            if function_name not in available_actions:
                raise Exception(f"Unknown action: {function_name}: {function_parms}")
            print(f" -- running {function_name} {function_parms}")
            action_function = available_actions[function_name]
            #call the function
            result = action_function(**function_parms)
            function_result_message = f"Action_Response: {result}"
            messages.append({"role": "user", "content": function_result_message})
            print(function_result_message)
    else:
         break