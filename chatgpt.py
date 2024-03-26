import streamlit as st

import requests, json
# send the POST request to create the serving endpoint
API_ROOT = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get() 
API_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

endpoint_name = "databricks-mixtral-8x7b-instruct"
headers = {"Context-Type": "text/json", "Authorization": f"Bearer {API_TOKEN}"}

def get_response(question="What is Databricks?"):
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
    response = response.json()["choices"][0]["message"]["content"]
    return response

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by Databricks Foundational Models")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    #response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    response = get_response(question=st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(msg)