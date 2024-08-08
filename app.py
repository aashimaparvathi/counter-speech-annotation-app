import streamlit as st
import pandas as pd
import json
from collections import defaultdict

# Load your data
data = pd.read_csv('data/csv/iconan_train.csv')

# Initialize session state for user login, guidelines toggle, annotations, and debug mode
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_guidelines' not in st.session_state:
    st.session_state.show_guidelines = False
if 'annotations' not in st.session_state:
    st.session_state.annotations = defaultdict(lambda: "Select a strategy")
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# Function to handle user login
def user_login():
    with st.sidebar:
        user_name = st.text_input("Username")
        if st.button('Login'):
            st.session_state.username = user_name

# Function to toggle guidelines visibility
def toggle_guidelines():
    st.session_state.show_guidelines = not st.session_state.show_guidelines

# Function to toggle debug mode
def toggle_debug_mode():
    st.session_state.debug_mode = not st.session_state.debug_mode

# Function to save annotations to a JSON file
def save_annotations():
    annotations = {
        'id': [],
        'hateSpeech': [],
        'counterSpeech': [],
        'annotation': []
    }
    for index, annotation in st.session_state.annotations.items():
        if annotation != "Select a strategy":
            annotations['id'].append(data.iloc[index]['id'])
            annotations['hateSpeech'].append(data.iloc[index]['hateSpeech'])
            annotations['counterSpeech'].append(data.iloc[index]['counterSpeech'])
            annotations['annotation'].append(annotation)

    with open('annotated_data.json', 'w') as f:
        json.dump(annotations, f)
    st.success("Annotations saved successfully!")

# Function to show only annotated cases
def show_annotated_cases():
    annotated_cases = {k: v for k, v in st.session_state.annotations.items() if v != "Select a strategy"}
    if annotated_cases:
        st.write("Annotated Cases:")
        for index, label in annotated_cases.items():
            st.write(f"ID: {data.iloc[index]['id']}")
            st.write(f"Hate Speech: {data.iloc[index]['hateSpeech']}")
            st.write(f"Counter Speech: {data.iloc[index]['counterSpeech']}")
            st.write(f"Annotation: {label}")
            st.write("---")
    else:
        st.write("No annotations yet.")

# Function to handle pagination
def next_page():
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1

# Title of your app
st.title('Annotation Task for Counterspeech Strategies')

# Check if user is logged in
user_login()
if st.session_state.username:
    st.write(f"Logged in as: {st.session_state.username}")

    # Define constants for pagination
    ITEMS_PER_PAGE = 10

    # Calculate the range of indices for the current page
    start_idx = st.session_state.page * ITEMS_PER_PAGE
    end_idx = (st.session_state.page + 1) * ITEMS_PER_PAGE
    page_data = data.iloc[start_idx:end_idx]

    # Display current page pairs
    strategy_options = ["Select a strategy", "Empathy and Affiliation", "Fact-Checking",
                        "Humour/Sarcasm", "Warning of Consequences", "Shaming and Labelling",
                        "Denouncing", "Pointing Out Hypocrisy", "Counter Questions"]
    for index, row in page_data.iterrows():
        with st.expander(f"Case {index + 1}"):
            st.text_area("Hate Speech", value=row['hateSpeech'], height=100, disabled=True, key=f"hate_speech_{index}")
            st.text_area("Counter Speech", value=row['counterSpeech'], height=100, disabled=True, key=f"counter_speech_{index}")

            current_strategy = st.session_state.annotations[index + start_idx]
            selected_strategy = st.selectbox("Choose the counterspeech strategy",
                                             strategy_options,
                                             index=strategy_options.index(current_strategy),
                                             key=f"strategy{index}")

            st.session_state.annotations[index + start_idx] = selected_strategy

    # Pagination buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.page > 0:
            st.button("Previous", on_click=prev_page)
    with col2:
        if end_idx < len(data):
            st.button("Next", on_click=next_page)

    # Placeholder for Annotation guidelines
    guidelines = {
        "Empathy and Affiliation": "Connect on a personal level, showing understanding or solidarity.",
        "Fact-Checking": "Address inaccuracies by presenting factual information.",
        "Humour/Sarcasm": "Use wit or sarcasm to lighten the conversation's tone.",
        "Warning of Consequences": "Highlight potential negative outcomes, like social or legal consequences.",
        "Shaming and Labelling": "Call out hate speech by labeling it as discriminatory.",
        "Denouncing": "Express outright rejection of the hateful views.",
        "Pointing Out Hypocrisy": "Underline logical flaws or double standards in the hate speech.",
        "Counter Questions": "Question the hate speech."
    }

    if st.sidebar.button("Annotation Guidelines", on_click=toggle_guidelines):
        if st.session_state.show_guidelines:
            st.write("Counterspeech Annotation Guidelines")
            for strategy, description in guidelines.items():
                st.write(f"**{strategy}**: {description}")

    # Toggle debug mode to display annotations
    st.sidebar.checkbox("Debug Mode", on_change=toggle_debug_mode)

    if st.session_state.debug_mode:
        show_annotated_cases()

    # Exit button with confirmation
    if st.sidebar.button("Exit"):
        st.warning("Are you sure you wish to exit?")
        if st.button("Yes, exit and save annotations"):
            save_annotations()
            st.stop()
        if st.button("No, continue annotating"):
            st.write("Continuing annotation...")

else:
    st.sidebar.warning("Please login to continue.")
