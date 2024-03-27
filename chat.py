import streamlit as st
import time
from streamlit_feedback import streamlit_feedback

import requests, json
# send the POST request to create the serving endpoint
#API_ROOT = "https://<DATABRICKS_WORKSPACE_URL>"
API_ROOT="https://e2-demo-field-eng.cloud.databricks.com"

endpoint_name = "databricks-mixtral-8x7b-instruct"

def _submit_feedback(user_response, emoji=None):
    print(f"Feedback submitted: {user_response}")
    time.sleep(1)
    st.toast(f"Feedback submitted: {user_response}", icon=emoji)
    time.sleep(1)
    st.chat_message("user").write(f"Feedback submitted: {user_response}")
    st.session_state.messages.append({"role": "user", "content": f"Feedback submitted: {user_response}"})
    return user_response.update({"some_metadata": 123})

def get_response(question="What is Databricks?", API_TOKEN=""):
    headers = {"Context-Type": "text/json", "Authorization": f"Bearer {API_TOKEN}"}
    data = {
    "messages": [
        {
        "role": "user",
        "content": question
        }
    ],
    "max_tokens": 128
    }
    response = requests.post(
        url=f"{API_ROOT}/serving-endpoints/{endpoint_name}/invocations", json=data, headers=headers
    )
    return response.json()["choices"][0]["message"]["content"]

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    #"[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    #"[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    #"[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by Databricks Foundational Models")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = get_response(question=st.session_state.messages[-1]["content"], API_TOKEN=openai_api_key)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Optional] Please provide an explanation",
        on_submit = _submit_feedback
    )
    feedback