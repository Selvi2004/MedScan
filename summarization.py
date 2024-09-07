import os
import pandas as pd
import streamlit as st
from pathlib import Path
from streamlit_option_menu import option_menu
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains import LLMChain
from langchain.llms import OpenAI
import yaml
from json_execution import execute_mysql_query
from prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE1
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import openai

# Set Streamlit page configuration
st.set_page_config(page_title="MedScan", layout="wide")

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if "sql_queries" not in st.session_state:
    st.session_state["sql_queries"] = []
if "input_history" not in st.session_state:
    st.session_state.input_history = []
if "output_tables" not in st.session_state:
    st.session_state["output_tables"] = []
if "con_history" not in st.session_state:
    st.session_state.con_history = []
if "sql_statement" not in st.session_state:
    st.session_state.sql_statement = []
if 'chart_buffer' not in st.session_state:
    st.session_state['chart_buffer'] = None
if "sidebar_selection" not in st.session_state:
    st.session_state["sidebar_selection"] = "MedScan"

history = st.session_state["past"]

def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + str(st.session_state["generated"][i]))
    session = [(user, bot) for user, bot in zip(st.session_state["past"], st.session_state["generated"])]
    st.session_state["stored_session"].append(session)
    # Reset the session state
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state["output_tables"] = []
    st.session_state["input_history"] = []
    st.session_state["sql_queries"] = []
    st.session_state["con_history"] = []
    st.session_state["sql_statement"] = []
    st.session_state.entity_memory.buffer.clear()
    
    
os.environ['GOOGLE_API_KEY'] ="AIzaSyBEeIGxpdKR7rAg6ALiLD9pgYNkVJOyt2A"



llm = ChatGoogleGenerativeAI(model="gemini-pro",temperature=0)

openai.api_key = OPEN_API_KEY

#llm = OpenAI(temperature=0, openai_api_keY=OPEN_API_KEY, model="gpt-3.5-turbo-instruct", verbose=False)


if "entity_memory" not in st.session_state:
    st.session_state.entity_memory = ConversationEntityMemory(llm=llm)

conversation_chain = ConversationChain(llm=llm, prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE1, verbose=True, memory=st.session_state.entity_memory)


st.markdown(
    """
    <style>
    button.st-emotion-cache-s48dsx{
        align-content: center;
        height: auto;
        width: auto;
        padding-left: 70px !important;
        padding-right: 70px !important;
    }
    div.stButton > button:first-child {
            background-color: #2596BE;  /* Blue color */
            color: white;
            font-size: 20px;
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    selected = option_menu("Chat Interface", ["MedScan"], 
        icons=['database'], default_index=0, orientation="vertical",
        styles={
            "container": {"width": "290px", "padding": "5px", "float": "left", "background-color": "#FFFFFF", "font-family": "'Trebuchet MS',Helvetica,sans-serif"},
            "icon": {"color": "white", "font-size": "20px"},
            "nav-link": {"color": "white", "font-size": "20px", "margin": "0px", "hover-color": "red"},
            "nav-link-selected": {"background-color": "#2596BE"}
        })
    
st.session_state.sidebar_selection = selected

s = f"<center><span style='font-size:55px; color:#2596BE'>Patient Data </span><span style='font-size:55px; color:rgb(0,0,0)'>Retrieval Assistant</span></center>"
st.markdown(s, unsafe_allow_html=True)
st.divider()




def summarize_text(text, max_length=200):
   
    if not openai.api_key:
        raise ValueError("OpenAI API key is not set. Please set the API key.")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
            ]
        )

        summary = response.choices[0].message['content'].strip()
        return summary

    except openai.error.OpenAIError as e:
        return f"Error: API request failed with error - {e}"


if st.session_state.sidebar_selection == "MedScan":
    st.sidebar.button("New Chat", on_click=new_chat)

    user_input = st.chat_input("Your AI assistant is here! Ask me anything ..")
    
    user_icon = "👤"
    bot_icon = "🤖"
    
    download_data = []
    if user_input:
        
        sql_query = conversation_chain.run(input=user_input)
        print(f"Generated SQL Query: {sql_query}")
        input_with_sql = f"{user_input} {sql_query}" if sql_query else user_input
        output = conversation_chain.run(input_with_sql)
        
        st.session_state.sql_statement.append(sql_query)
        
        
        if "SELECT" in sql_query or "SHOW" in sql_query:
            df = execute_mysql_query(sql_query)
            if not None:
             output = df

           
             if "summarize" in user_input.lower():
                text_data = output.to_string(index=False)
                summarized_output = summarize_text(text_data)
                output = summarized_output
                st.session_state.past.append(user_input)
                st.session_state.generated.append(output)
               
             if isinstance(output,pd.DataFrame):
                 st.session_state.input_history.append(user_input)
                 st.session_state.output_tables.append(output)
             else:
                 st.session_state.input_history.append(user_input)
                 st.session_state.output_tables.append(output)
        else:
            
            st.session_state.past.append(user_input)
            st.session_state.generated.append(sql_query)
            if isinstance(sql_query, type(sql_query)):
                st.session_state.con_history.append(sql_query)
                st.session_state.input_history.append(user_input)
        
       st.markdown(
                    """
                        <style>        
                    .chat-row {
                        display: flex;
                        margin: 5px;
                        width: 100%;
                    }

                    .row-reverse {
                         display: flex;
                         flex-direction: row-reverse;
                         margin: 5px;
                    }
                    .row-reverse1 {
                         display: flex;
                         margin: 5px;
                    }
                    .chat-bubble {
                        font-family: "Source Sans Pro", sans-serif, "Segoe UI", "Roboto", sans-serif;
                        border: 1px solid transparent;
                        padding: 5px 10px;
                        margin: 0px 7px;
                        max-width: 70%;  /* Ensures both bubbles adjust size */
                        word-wrap: break-word;
                        display:flex;
                    }

                    .ai-bubble {
                        background: rgb(240, 242, 246);
                        border-radius: 10px;
                        display:flex;
                        margin: 5px;
                    }

                    .human-bubble {
                        background: linear-gradient(135deg, rgb(0, 178, 255) 0%, rgb(0, 106, 255) 100%); 
                        color: white;
                        border-radius: 20px;
                       
                    }

                    .chat-icon {
                        border-radius: 5px;
                    }
                    
                    </style>
        """,
            unsafe_allow_html=True,
        )

       for input_, output, sql_query1 in zip(st.session_state.input_history, st.session_state.generated, st.session_state.sql_statement):
           st.markdown(f"<div class='chat-row row-reverse'>{user_icon}<b> <span style='color:#2596BE'>Your Input</span></b></div>", unsafe_allow_html=True)
           with st.container():
                st.markdown(f"<div class='row-reverse'><div class='chat-bubble human-bubble '>{input_}</div></div>", unsafe_allow_html=True)
                
                st.write("")
                st.markdown(f"<div class='chat-row'>{bot_icon}<b>  <span style='color:#2596BE'>AI Response:</span></b></div>", unsafe_allow_html=True)

                with st.container():
                    if isinstance(output, pd.DataFrame):
                        tab_titles = ["Output", "SQL Query"]
                        tabs = st.tabs(tab_titles)
                        with tabs[0]:
                            st.markdown("<span style='color:#2596BE'>Output:</span>", unsafe_allow_html=True)
                            st.write(output)
                        with tabs[1]:
                            st.markdown("<span style='color:#2596BE'>Generated SQL Query:</span>", unsafe_allow_html=True)
                            st.code(sql_query1)
                    else:
                        st.markdown(f"{output}", unsafe_allow_html=True)
                    
       

    download_str = "\n".join(map(str, download_data))
    if download_str:
        st.download_button("Download", download_str)

    for i, sublist in enumerate(st.session_state.stored_session):
        with st.sidebar.expander(label=f"Conversation-Session:{i}"):
            st.write(sublist)
    
    if st.session_state.stored_session:
        if st.sidebar.checkbox("Clear-all"):
            del st.session_state.stored_session
