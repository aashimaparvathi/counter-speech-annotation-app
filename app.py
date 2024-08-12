import streamlit as st
import pandas as pd
import csv
from collections import defaultdict

# Load your data
data = pd.read_csv('data/csv/iconan_train.csv')

# Initialize session state for user login, guidelines toggle, annotations, and debug mode
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_guidelines' not in st.session_state:
    st.session_state.show_guidelines = False
if 'annotations' not in st.session_state:
    st.session_state.annotations = defaultdict(lambda: [])
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

# Function to save annotations to a CSV file
def save_annotations():
    annotated_data = {
        'id': [],
        'hateSpeech': [],
        'counterSpeech': [],
        'annotation_1': [],
        'annotation_2': []
    }
    for index, annotations in st.session_state.annotations.items():
        if len(annotations) == 2:
            actual_index = int(index)
            annotated_data['id'].append(data.iloc[actual_index]['id'])
            annotated_data['hateSpeech'].append(data.iloc[actual_index]['hateSpeech'])
            annotated_data['counterSpeech'].append(data.iloc[actual_index]['counterSpeech'])
            annotated_data['annotation_1'].append(annotations[0])
            annotated_data['annotation_2'].append(annotations[1])

    username = st.session_state.username  # Get the username from session state
    filename = f'{username}_annotated_data.csv'  # Use f-string to create the filename

    # Write to CSV file
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'hateSpeech', 'counterSpeech', 'annotation_1', 'annotation_2'])
        for i in range(len(annotated_data['id'])):
            writer.writerow([annotated_data['id'][i],
                             annotated_data['hateSpeech'][i],
                             annotated_data['counterSpeech'][i],
                             annotated_data['annotation_1'][i],
                             annotated_data['annotation_2'][i]])
    st.success("Annotations saved successfully!")

# Function to show only annotated cases
def show_annotated_cases():
    annotated_cases = {k: v for k, v in st.session_state.annotations.items() if len(v) == 2}
    if annotated_cases:
        st.write("Annotated Cases:")
        for index, labels in annotated_cases.items():
            actual_index = int(index)
            st.write(f"ID: {data.iloc[actual_index]['id']}")
            st.write(f"Hate Speech: {data.iloc[actual_index]['hateSpeech']}")
            st.write(f"Counter Speech: {data.iloc[actual_index]['counterSpeech']}")
            st.write(f"Annotations: {labels}")
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
    strategy_options = ["Empathy and Affiliation", "Fact-Checking",
                        "Humour/Sarcasm", "Warning of Consequences", "Shaming and Labelling",
                        "Denouncing", "Pointing Out Hypocrisy", "Counter Questions"]

    for i, row in enumerate(page_data.itertuples(), start=start_idx):
        with st.expander(f"Case {i + 1}"):
            st.text_area("Hate Speech", value=row.hateSpeech, height=100, disabled=True, key=f"hate_speech_{i}")
            st.text_area("Counter Speech", value=row.counterSpeech, height=100, disabled=True, key=f"counter_speech_{i}")

            selected_strategies = st.session_state.annotations[i]

            # Display checkboxes for strategy selection
            checkboxes = []
            for strategy in strategy_options:
                is_checked = strategy in selected_strategies
                checkbox = st.checkbox(strategy, value=is_checked, key=f"strategy_{i}_{strategy}")
                checkboxes.append(checkbox)

            # Update the selected strategies
            selected_strategies = [strategy for strategy, checked in zip(strategy_options, checkboxes) if checked]

            if len(selected_strategies) > 2:
                st.warning("Please select only two strategies.")
            else:
                st.session_state.annotations[i] = selected_strategies

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

    # Save annotations periodically
    st.button("Save Annotations", on_click=save_annotations)

else:
    st.sidebar.warning("Please login to continue.")
