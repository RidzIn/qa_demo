import streamlit as st
from my_openai_api import *
"""
# GPT Chat by Ridz
"""

example = 'Generate 500 word text, include key words and definitions, but keep text unstructured. ' \
          'Topic: Machine Learning.'

prompt = st.text_area('**Input your prompt to Chat**')

generate_answer = st.button('**Get answer**')
if generate_answer:
    formatted_prompt = [{'role': 'user', 'content': prompt}]
    response = chat_completion_request(formatted_prompt)
    st.write(get_message_from_response(response))


