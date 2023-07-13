from my_openai_api import *
"""
# Q/A model by Ridz
----

##  How is works? 
1. You need to input your PDF file with your lecture, from which you want to get question and answers from.
2. Press **Get result** button
3. Download the JSON file by pressing **q/a**
Addiction: you can download txt format of your base, if you want to modify this
----
"""

uploaded_file = st.file_uploader("Upload your knowledge file", type=['pdf'])

if uploaded_file is not None:
    kb, generate_answer, result = st.columns(3, gap='medium')

    knowledge_base = extract_text_from_pdf(uploaded_file)
    st.sidebar.metric('Knowledge base tokens', str(num_tokens_from_string(knowledge_base)))

    with kb:
        download_file(knowledge_base, '**Knowledge Base**', generate_log_name() + '.txt', 'text/plain')

    with generate_answer:
        generate_answer.button('**Get result**')

    if generate_answer:
        response = chat_completion_request(qa_prompt(knowledge_base))
        message = get_message_from_response(response)
        st.sidebar.metric('Response tokens:', num_tokens_from_string(message))
        st.json(message)
        save_response_to_log(response)
        with result:
            download_file(message, '**Q/A**', generate_log_name() + '.json', 'application/json')
