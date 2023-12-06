#domain = appchattest-jj33hkqjlgjsdxtg3axmd8.streamlit.app

import logging

import openai
import streamlit as st
import streamlit_authenticator as stauth

logger = logging.getLogger(__name__)

st.title("ChatGPT-like clone")

openai.api_key = st.secrets["OPENAI_API_KEY"]

authenticator = stauth.Authenticate(
    dict(st.secrets['credentials']),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days'],
    st.secrets['preauthorized']
)

if "logger" not in st.session_state:
    st.session_state["logger"] = logging.getLogger(__name__)
    st.session_state["logger"].setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO)
    st.session_state["logger"].info("-----------------------------------")
    st.session_state["logger"].info("Logger started")

st.session_state["logger"].info(f"About to call authenticator")
name, authentication_status, username = authenticator.login('Login', 'sidebar') # location is 'sidebar' or 'main'

if authentication_status:
    st.session_state["logger"].info(f"User is authenticated")
    authenticator.logout('Logout', 'sidebar')
    if st.session_state['authentication_status'] != True:
        st.session_state["logger"].info(f"User has manually logged out")


    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state["logger"].info(f"----> Value of prompt input is: {prompt}")
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            response = openai.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=st.session_state.messages,
                stream=True,
            )
            for part in response:
                full_response += (part.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

elif authentication_status == False:
    st.session_state["logger"].info(f"User is not authenticated because some combination of their username or password is incorrect")
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.session_state["logger"].info(f"User is not authenticated because they have not entered their username or password")
    st.warning('Please enter your username and password')

