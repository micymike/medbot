import streamlit as st
import replicate
import os
import webbrowser
from config import REPLICATE_API_KEY

# Set the app's title
st.set_page_config(page_title="Travel Assistant")

# Sidebar setup
with st.sidebar:
    st.title("Travel Assistant")

    # Check if the imported API key is valid
    if REPLICATE_API_KEY.startswith('r8_') and len(REPLICATE_API_KEY) == 40:
        st.success('API key loaded from config!', icon='✅')
        os.environ['REPLICATE_API_TOKEN'] = REPLICATE_API_KEY  # Use the imported API key
        replicate_api = REPLICATE_API_KEY
    else:
        replicate_api = st.text_input('Enter Replicate API Key:', type='password', key='replicate_api_key')
        if replicate_api.startswith('r8_') and len(replicate_api) == 40:
            st.success('API key set!', icon='✅')
            os.environ['REPLICATE_API_TOKEN'] = replicate_api  # Set the API key if valid
        else:
            st.error('Invalid API key! Please enter a valid Replicate API key.')

    # Hidden model selection and parameters
    with st.empty():
        st.subheader('Models and Parameters')
        selected_model = st.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
        if selected_model == 'Llama2-7B':
            llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
        elif selected_model == 'Llama2-13B':
            llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'

    # Feedback and Rating section
    st.subheader('Feedback')
    feedback = st.text_area('Provide your feedback here', key='feedback')
    if st.button('Submit Feedback', key='submit_feedback'):
        st.write('Thank you for your feedback!')

    st.subheader('Rate the Assistant')
    rating = st.slider('Rate your experience', 1, 5, 3, key='rating')
    if st.button('Submit Rating', key='submit_rating'):
        st.write(f'Thank you for rating us {rating} stars!')

# Initialize session state for chat messages if not already initialized
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.experimental_rerun()  # Rerun the app to clear the chat history
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function to check if the question is relevant
def is_relevant_question(prompt_input):
    relevant_keywords = ["travel", "tourism", "wildlife", "hotels", "destination", "adventure", "safari", "bird", "park", "species", "reserve", "sanctuary", "animal", "food", "culinary", "sightseeing", "trails", "hiking", "luxury", "beach", "pet-friendly", "visit"]
    prompt_lower = prompt_input.lower()
    return any(keyword in prompt_lower for keyword in relevant_keywords)

# Function to generate LLaMA2 response
def generate_llama2_response(prompt_input):
    if not is_relevant_question(prompt_input):
        return ["I'm sorry, I can only answer questions regarding travel, tourism, wildlife, and hotels."]

    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'.\n\n"
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"

    output = replicate.run(
        llm,  # Use the selected model
        input={"prompt": f"{string_dialogue} {prompt_input}\nAssistant: ", "temperature": 0.1, "top_p": 0.9, "max_length": 120, "repetition_penalty": 1.0}
    )
    return output

# Chat input and response generation
if replicate_api:
    prompt = st.text_input("You:", key="user_input")
    if st.button("Send", key="send_button"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            full_response = ''.join(response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

def open_blog():
    webbrowser.open_new_tab("https://www.google.com/index.html")

st.sidebar.button("Back to Blog", on_click=open_blog)