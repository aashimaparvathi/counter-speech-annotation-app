import streamlit as st
import pandas as pd

# Load your data
data = pd.read_csv('TA1_TA2_Annotations.csv')

# Initialize session state for user login, guidelines toggle, and annotations
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_guidelines' not in st.session_state:
    st.session_state.show_guidelines = False
if 'annotations' not in st.session_state:
    st.session_state.annotations = [0] * len(data)  # Initialize with indices for 'Select a strategy'

# Function to handle user login
def user_login():
    with st.sidebar:
        user_name = st.text_input("Username")
        if st.button('Login'):
            st.session_state.username = user_name

# Function to toggle guidelines visibility
def toggle_guidelines():
    st.session_state.show_guidelines = not st.session_state.show_guidelines

# Title of your app
st.title('Annotation Task for Counterspeech Strategies')

# Check if user is logged in
user_login()
if st.session_state.username:
    st.write(f"Logged in as: {st.session_state.username}")

    # Define constants for pagination
    ITEMS_PER_PAGE = 10

    # Initialize session state for pagination
    if 'page' not in st.session_state:
        st.session_state.page = 0

    # Pagination function
    def next_page():
        st.session_state.page += 1

    def prev_page():
        st.session_state.page -= 1

    # Calculate the range of indices for the current page
    start_idx = st.session_state.page * ITEMS_PER_PAGE
    end_idx = (st.session_state.page + 1) * ITEMS_PER_PAGE
    page_data = data.iloc[start_idx:end_idx]

    # Display current page pairs
    strategy_options = ["Select a strategy", "Empathy and Affiliation", "Fact-Checking", 
                        "Humour/Sarcasm", "Warning of Consequences", "Shaming and Labelling",
                        "Denouncing", "Pointing Out Hypocrisy", "Counter Questions"]
    for index, row in page_data.iterrows():
        with st.expander(f"Pair {index + 1}"):
            st.text_area("Hate Speech", value=row['HATE_SPEECH'], height=100, disabled=True, key=f"hate_speech_{index}")
            st.text_area("Counter Speech", value=row['COUNTER_NARRATIVE'], height=100, disabled=True, key=f"counter_speech_{index}")
            
            current_strategy_index = st.session_state.annotations[index + start_idx]
            selected_index = st.selectbox("Choose the counterspeech strategy", 
                                          strategy_options,
                                          index=current_strategy_index,
                                          key=f"strategy{index}")

            # Ensure selected_index is handled as an integer for session state updates
            if isinstance(selected_index, int):
                st.session_state.annotations[index + start_idx] = selected_index

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
else:
    st.sidebar.warning("Please login to continue.")
