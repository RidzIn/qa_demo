import requests
import openai
from tenacity import wait_random_exponential, stop_after_attempt, retry
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='config.env')

GPT_MODEL = os.getenv('GPT_MODEL')
API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = API_KEY

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    # Заголовки для отправки HTTP запроса
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def get_message_from_response(response, choice_index=0):
    try:
        return response.json()['choices'][choice_index]['message']['content']
    except Exception as e:
        print('Could not load message from response')
        print(f'Exception: {e}')
        return e

def generate_log_name():
    now = datetime.now()
    return now.strftime("%d-%m-%Y_%H-%M-%S")

def save_message_to_log(message):
    f = open('logs/'+generate_log_name()+'.txt', 'w+')
    f.write(message)
    f.close()

def generate_singe_prompt(prompt: str):
    return [{'role': 'user', 'content': prompt}]
