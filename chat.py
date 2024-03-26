import os

import streamlit as st
import streamlit.components.v1 as components

import openai
import streamlit as st

def _submit_feedback(user_response, emoji=None):
    st.toast(f"Feedback submitted: {user_response}", icon=emoji)
    return user_response.update({"some metadata": 123})


def chatbot_thumbs_app(streamlit_feedback, debug=False):
    st.title("💬 Chatbot")

    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API Key",
            key="chatbot_api_key",
            type="password",
            value=st.secrets.get("OPENAI_API_KEY"),
        )

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    messages = st.session_state.messages

    for n, msg in enumerate(messages):
        st.chat_message(msg["role"]).write(msg["content"])

        if msg["role"] == "assistant" and n > 1:
            feedback_key = f"feedback_{int(n/2)}"

            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = None

            streamlit_feedback(
                feedback_type="thumbs",
                optional_text_label="Please provide extra information",
                on_submit=_submit_feedback,
                key=feedback_key,
            )

    if prompt := st.chat_input():
        messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if debug:
            st.session_state["response"] = "dummy response"
        else:
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()
            else:
                openai.api_key = openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
            st.session_state["response"] = response.choices[0].message.content
        with st.chat_message("assistant"):
            messages.append(
                {"role": "assistant", "content": st.session_state["response"]}
            )
            st.write(st.session_state["response"])
            st.rerun()


def single_prediction_faces_app(streamlit_feedback, debug=False):
    st.title("LLM User Feedback with Trubrics")

    if "response" not in st.session_state:
        st.session_state["response"] = ""
    if "feedback_key" not in st.session_state:
        st.session_state.feedback_key = 0

    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API Key",
            key="chatbot_api_key",
            type="password",
            value=st.secrets.get("OPENAI_API_KEY"),
        )

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    else:
        openai.api_key = openai_api_key

    prompt = st.text_area(
        label="Prompt",
        label_visibility="collapsed",
        placeholder="What would you like to know?",
    )
    button = st.button(f"Ask text-davinci-002")

    if button:
        if debug:
            st.session_state["response"] = "dummy response: " + prompt.strip()
        else:
            st.session_state["response"] = openai.Completion.create(
                model="text-davinci-002", prompt=prompt, temperature=0.5, max_tokens=200
            )
            st.session_state["response"] = (
                st.session_state["response"].choices[0].text.replace("\n", "")
            )
        st.session_state.feedback_key += 1  # overwrite feedback component

    if st.session_state["response"]:
        st.markdown(f"#### :violet[{st.session_state['response']}]")

        streamlit_feedback(
            feedback_type="faces",
            optional_text_label="Please provide extra information",
            align="flex-start",
            on_submit=_submit_feedback,
            key=f"feedback_{st.session_state.feedback_key}",
        )


def basic_app(streamlit_feedback, debug):
    st.title("Component demo")

    if "feedback_key" not in st.session_state:
        st.session_state.feedback_key = 0

    st.button("Random button")

    if st.button("Refresh feedback component"):
        st.session_state.feedback_key += 1  # overwrite feedback component

    multiline = st.toggle("Multiline", value=False)

    if multiline:
        feedback = streamlit_feedback(
            feedback_type="faces",
            # on_submit=_submit_feedback,
            key=f"feedback_{st.session_state.feedback_key}",
            optional_text_label="Please provide some more information",
            max_text_length=500,
            args=["✅"],
        )
    else:
        feedback = streamlit_feedback(
            feedback_type="faces",
            # on_submit=_submit_feedback,
            key=f"feedback_{st.session_state.feedback_key}",
            optional_text_label="Please provide some more information",
            args=["✅"],
        )

    if feedback:
        st.write(":orange[Component output:]")
        st.write(feedback)


def bare_bones_app(streamlit_feedback, debug):
    feedback = streamlit_feedback(feedback_type="faces", on_submit=_submit_feedback)

    if feedback:
        st.write(":orange[Component output:]")
        st.write(feedback)


def streaming_chatbot(streamlit_feedback, debug):

    st.title("💬 Streaming Chatbot")

    openai.api_key = st.secrets["OPENAI_API_KEY"]

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "feedback_key" not in st.session_state:
        st.session_state.feedback_key = 0

    feedback_kwargs = {
        "feedback_type": "thumbs",
        "optional_text_label": "Please provide extra information",
        "on_submit": _submit_feedback,
    }

    for n, msg in enumerate(st.session_state.messages):
        st.chat_message(msg["role"]).write(msg["content"])

        if msg["role"] == "assistant" and n > 1:
            feedback_key = f"feedback_{int(n/2)}"

            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = None

            disable_with_score = (
                st.session_state[feedback_key].get("score")
                if st.session_state[feedback_key]
                else None
            )
            streamlit_feedback(
                **feedback_kwargs,
                key=feedback_key,
                disable_with_score=disable_with_score,
            )

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
        streamlit_feedback(
            **feedback_kwargs, key=f"feedback_{int(len(st.session_state.messages)/2)}"
        )


# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_feedback", url="https://e2-demo-field-eng.cloud.databricks.com/driver-proxy/o/1444828305810485/0124-131936-71bn71qx/8501/app"
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

    page_names_to_funcs = {
        "Chatbot": chatbot_thumbs_app,
        "Streaming chatbot": streaming_chatbot,
        "Faces": single_prediction_faces_app,
        "Basic": basic_app,
        "Bare bones": bare_bones_app,
    }

    demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
    page_names_to_funcs[demo_name](streamlit_feedback=streamlit_feedback, debug=True)
    
feedback = streamlit_feedback(
    feedback_type="thumbs",
    optional_text_label="[Optional] Please provide an explanation",
)
feedback