import streamlit as st

import os

#==========================================================================
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_feedback", url="http://localhost:3001"
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_feedback", path=build_dir)


def streamlit_feedback(
    feedback_type,
    optional_text_label=None,
    max_text_length=None,
    disable_with_score=None,
    on_submit=None,
    args=(),
    kwargs={},
    align="flex-end",
    key=None,
):
    """Create a new instance of "streamlit_feedback".

    Parameters
    ----------
    feedback_type: str
        The type of feedback; "thumbs" or "faces".
    optional_text_label: str or None
        An optional label to add as a placeholder to the textbox.
        If None, the "thumbs" or "faces" will not be accompanied by textual feedback.
    max_text_length: int or None
        Defaults to None. If set, enables the multi-line functionality and determines the maximum characters the textbox allows. Else, displays the default one-line textbox.
    disable_with_score: str
        An optional score to disable the component. Must be a "thumbs" emoji or a "faces" emoji. Can be used to pass state from one component to another.
    on_submit: callable
        An optional callback invoked when feedback is submitted. This function must accept at least one argument, the feedback response dict,
        allowing you to save the feedback to a database for example. Additional arguments can be specified using `args` and `kwargs`.
    args: tuple
        Additional positional arguments to pass to `on_submit`.
    kwargs: dict
        Additional keyword arguments to pass to `on_submit`.
    align: str
        Where to align the feedback component; "flex-end", "center" or "flex-start".
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    dict
        The user response, with the feedback_type, score and text fields. If on_submit returns a value, this value will be returned by the component.

    """
    if feedback_type == "thumbs":
        possible_thumbs = ["👍", "👎"]
        if disable_with_score not in [None] + possible_thumbs:
            raise ValueError(
                f"disable_with_score='{disable_with_score}' not recognised. Please only"
                f" use {possible_thumbs} for feedback_type='thumbs'."
            )
    elif feedback_type == "faces":
        possible_faces = ["😞", "🙁", "😐", "🙂", "😀"]
        if disable_with_score not in [None] + possible_faces:
            raise ValueError(
                f"disable_with_score='{disable_with_score}' not recognised. Please only"
                f" use {possible_faces} for feedback_type='faces'."
            )
    else:
        raise NotImplementedError(
            f"feedback_type='{feedback_type}' not implemented. Please select either"
            " 'thumbs' or 'faces'."
        )
    if align not in ["flex-end", "center", "flex-start"]:
        raise NotImplementedError(
            f"align='{align}' not implemented. Please select either 'flex-end',"
            " 'center' or 'flex-start'."
        )
    if max_text_length and optional_text_label is None:
        raise NotImplementedError(
            "max_text_length requires optional_text_label to be set."
        )

    if key is None:
        key = feedback_type

    if f"feedback_submitted_{key}" not in st.session_state:
        st.session_state[f"feedback_submitted_{key}"] = False

    component_value = _component_func(
        feedback_type=feedback_type,
        optional_text_label=optional_text_label,
        max_text_length=max_text_length,
        disable_with_score=disable_with_score,
        align=align,
        key=key,
        default=None,
    )

    if st.session_state[f"feedback_submitted_{key}"] is True:
        return None
    else:
        if component_value:
            st.session_state[f"feedback_submitted_{key}"] = True
            if on_submit:
                feedback = on_submit(component_value, *args, **kwargs)
                if feedback:
                    return feedback
                else:
                    return component_value
            else:
                return component_value
        else:
            return None


if not _RELEASE:

    # Added a try-except to make setting up the development environment for this project easier.
    try:
        from examples import (
            bare_bones_app,
            basic_app,
            chatbot_thumbs_app,
            single_prediction_faces_app,
            streaming_chatbot,
        )
    except:
        from .examples import (
            bare_bones_app,
            basic_app,
            chatbot_thumbs_app,
            single_prediction_faces_app,
            streaming_chatbot,
        )

    page_names_to_funcs = {
        "Chatbot": chatbot_thumbs_app,
        "Streaming chatbot": streaming_chatbot,
        "Faces": single_prediction_faces_app,
        "Basic": basic_app,
        "Bare bones": bare_bones_app,
    }

    demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
    page_names_to_funcs[demo_name](streamlit_feedback=streamlit_feedback, debug=True)
#==========================================================================
import requests, json
# send the POST request to create the serving endpoint
API_ROOT = "https://e2-demo-field-eng.cloud.databricks.com"
#API_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

endpoint_name = "databricks-mixtral-8x7b-instruct"

def _submit_feedback(user_response, emoji=None):
    st.toast(f"Feedback submitted: {user_response}", icon=emoji)
    return user_response.update({"some metadata": 123})
    
feedback_kwargs = {
        "feedback_type": "thumbs",
        "optional_text_label": "Please provide extra information",
        "on_submit": _submit_feedback,
    }

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
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

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

    streamlit_feedback(
            **feedback_kwargs, key=f"feedback_{int(len(st.session_state.messages)/2)}"
        )