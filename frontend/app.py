import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from agent.llm import agent_reply

st.set_page_config(page_title="Restaurant Reservation AI Agent", layout="centered")


# -----------------------------------
# INITIALIZE SESSION STATE
# -----------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "input_key" not in st.session_state:
    st.session_state.input_key = 0


# -----------------------------------
# HEADER UI
# -----------------------------------
st.title("🍽️ Restaurant Reservation AI Agent")
st.write("Chat with the AI assistant to book a restaurant table.")

st.subheader("Chat History")


# -----------------------------------
# DISPLAY CHAT HISTORY
# -----------------------------------
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Agent:** {msg['content']}")

st.write("---")


# -----------------------------------
# MESSAGE INPUT BOX
# -----------------------------------
user_input = st.text_input(
    "Your message:",
    key=f"chat_input_{st.session_state.input_key}",
)


# -----------------------------------
# SEND MESSAGE
# -----------------------------------
if st.button("Send"):
    if user_input.strip():

        # Store user message
        st.session_state.history.append({"role": "user", "content": user_input})

        # Get response from the agent
        reply = agent_reply(user_input, st.session_state.history)

        # Store agent message
        st.session_state.history.append({"role": "assistant", "content": reply})

        # Increment input key to create a new text input widget (effectively clearing it)
        st.session_state.input_key += 1

        # Refresh screen
        st.rerun()
