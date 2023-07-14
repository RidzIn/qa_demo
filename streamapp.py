from utils import *
"""
# Q/A model by Ridz
----

##  How is works? 

1. You need to input your PDF file with your lecture, from which you want to get question and answers from.
2. Press **Get result** button
3. Download the JSON file by pressing **q/a**
Addiction: you can download txt format of your base, if you want to modify this


## Suggestions:
----
In left column as you upload your file you will see amount of tokens you file has. 

Application using 16k context gpt 3.5 model, so if you exceed this limit, your app will be crashed.

If you want to get as much question as it possible, upload short documents. 

If you want to see what this document is about use documents 5-10k context, but you may lose important information.

----
In source code in **utils.py** you can find **qa_prompt()** function, 

feel free to experiment with prompt, to get result you want.

----

To get more information about OpenAI API see: 
1. [OpenAI API references](https://platform.openai.com/docs/api-reference/introduction)
2. [OpenAI cookbook](https://github.com/RidzIn/qa_demo)
3. [OpenAI references](https://platform.openai.com/docs/introduction/overview)
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
