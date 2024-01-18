#domain = appchattest-jj33hkqjlgjsdxtg3axmd8.streamlit.app

import logging

import openai
import streamlit as st
import streamlit_authenticator as stauth
import bcrypt

logger = logging.getLogger(__name__)
if "logger" not in st.session_state:
    st.session_state["logger"] = logging.getLogger(__name__)
    st.session_state["logger"].setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO)
    st.session_state["logger"].info("-----------------------------------")
    st.session_state["logger"].debug("Logger started")


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        pwd_raw = st.session_state['password']
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and bcrypt.checkpw(
            pwd_raw.encode(),
            st.secrets.passwords[st.session_state["username"]].encode(),
        ):
            st.session_state["password_correct"] = True
            st.session_state["logger"].info(f"Questions From: {st.session_state['username']}")
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

st.title("ChatGPT-like clone")

openai.api_key = st.secrets["OPENAI_API_KEY"]



if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.session_state["logger"].info("Creating chat_input. Waiting for input")
prompt = st.chat_input("What is up?")
if prompt:
    previous_prompt = prompt
    st.session_state["logger"].info(f"----> Value of prompt input is: {previous_prompt}")
    st.session_state.messages.append({"role": "user", "content": previous_prompt})
    with st.chat_message("user"):
        st.markdown(previous_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        st.session_state["logger"].info(f"About to call the API")
        response = openai.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=st.session_state.messages,
            stream=True,
        )
        for part in response:
            full_response += (part.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state["logger"].info(f"Response added to messages")
        st.session_state.messages.append({"role": "assistant", "content": full_response})

st.session_state["logger"].info("End of loop")


