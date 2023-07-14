import json
import tempfile
import PyPDF2
import streamlit as st
import requests
import openai
from tenacity import wait_random_exponential, stop_after_attempt, retry
from datetime import datetime
import os
from dotenv import load_dotenv
import tiktoken

load_dotenv(dotenv_path='config.env')

GPT_MODEL = os.getenv('GPT_MODEL')
API_KEY = os.getenv('OPENAI_API_KEY')

ENCODING_NAME = os.getenv('ENCODING_NAME')

openai.api_key = API_KEY


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    """
    Sends a request to the OpenAI API for chat completion.
    """
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
    """
        Extracts the message content from the response object.
    """
    try:
        return response.json()['choices'][choice_index]['message']['content']
    except Exception as e:
        print('Could not load message from response')
        print(f'Exception: {e}')
        return e


def generate_log_name():
    """
    Generates a log name based on the current timestamp.
    """
    try:
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        return f"log_{timestamp}"
    except Exception as e:
        print(f'An unexpected error occurred in generate_log_name(): {str(e)}')


def save_response_to_log(response):
    """
     Saves the API response to a log file.
    """
    try:
        log_file_name = generate_log_name()
        file_path = f"logs/{log_file_name}.json"
        with open(file_path, 'w+') as file:
            json.dump(response.json(), file)
    except OSError as e:
        print(f"Error occurred while saving response to log file: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred in save_response_to_log(): {str(e)}")


def download_file(data, button_name, filename, mime):
    """
        Downloads a file with the specified data, button name, filename, and MIME type.

        Args:
            data (str): The data to be written to the file.
            button_name (str): The label of the download button.
            filename (str): The name of the file to be downloaded.
            mime (str): The MIME type of the file.

        Raises:
            ValueError: If the provided MIME type is not supported.

    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        if mime == 'text/plain':
            text_with_spaces = ' '.join(data.splitlines())
            temp_file.write(text_with_spaces.encode())
        elif mime == 'application/json':
            temp_file.write(data.encode())
        else:
            raise ValueError('Unsupported MIME type.')

        temp_file.close()

        with open(temp_file.name, 'rb') as file:
            file_data = file.read()
            st.download_button(
                label=f'{button_name}',
                data=file_data,
                file_name=filename,
                mime=mime
            )


def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            text = file.read()
            return text
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print(f"An error occurred while reading the file '{file_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred in read_file(): {str(e)}")


def qa_prompt(knowledge_base):
    """
    Generates a question-answering prompt based on the provided knowledge base.
    """
    form = "{number: [{question:answer}]}"

    system_prompt_content = f"""User will provide you with knowledge base.
                                Your task: generate questions and answers.
                                Format: JSON dictionary {form}
                                Question: should be which can be appeared on the test. 
                                Pay attention to definitions and algorithms in text, they are the most important, and
                                must be included in questions.
                                Answers: should be short, but don't lose context.
                                Make AS MUCH AS YOU CAN questions and answers, but keep them different.
                                USE ONLY provided knowledge base, you don't know anything except that knowledge base.
                                """
    return [{'role': 'system',
             'content': system_prompt_content},
            {'role': 'user',
             'content': knowledge_base}]


def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file.

    """
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    num_tokens = len(encoding.encode(string))
    return num_tokens
