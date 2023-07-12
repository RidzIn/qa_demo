import streamlit as st
from my_openai_api import *
"""
# Q/A model by Ridz

## Rules
**You need to upload your knowledge base in text field below. Model will generate JSON format text using ONLY data you 
provided.**
"""

uploaded_file = st.file_uploader("Upload your knowledge file", type=['pdf'])

if uploaded_file is not None:
    knowledge_base = extract_text_from_pdf(uploaded_file)
    download_text_as_file(knowledge_base, generate_log_name() + '.txt')

    generate_answer = st.button('**Get answer**')
    if generate_answer:
        response = chat_completion_request(qa_prompt(knowledge_base))
        message = get_message_from_response(response)
        st.json(message)
        save_response_to_log(response)
        download_text_as_file(message, generate_log_name() + '.txt')


