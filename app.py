import streamlit as st
import pandas as pd
import csv
from collections import defaultdict

# Load your data
data = pd.read_csv('data/intentconanv2/equal-target-sample.csv')

# Initialize session state for user login, guidelines toggle, annotations, comments, and debug mode
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_guidelines' not in st.session_state:
    st.session_state.show_guidelines = False
if 'annotations' not in st.session_state:
    st.session_state.annotations = defaultdict(lambda: [])
if 'comments' not in st.session_state:
    st.session_state.comments = defaultdict(str)
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False
if 'message' not in st.session_state:
    st.session_state.message = ""
if 'message_type' not in st.session_state:
    st.session_state.message_type = ""

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
        'hatespeech': [],
        'counterspeech': [],
        'annotations': [],
        'comments': []
    }
    for index, annotations in st.session_state.annotations.items():
        actual_index = int(index)
        annotated_data['id'].append(data.iloc[actual_index]['id'])
        annotated_data['hatespeech'].append(data.iloc[actual_index]['hatespeech'])
        annotated_data['counterspeech'].append(data.iloc[actual_index]['counterspeech'])
        annotated_data['annotations'].append(", ".join(annotations))
        annotated_data['comments'].append(st.session_state.comments[actual_index])

    username = st.session_state.username  # Get the username from session state
    filename = f'data/{username}_annotated_data.csv'  # Use f-string to create the filename

    # Write to CSV file
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'hatespeech', 'counterspeech', 'annotations', 'comments'])
        for i in range(len(annotated_data['id'])):
            writer.writerow([annotated_data['id'][i],
                             annotated_data['hatespeech'][i],
                             annotated_data['counterspeech'][i],
                             annotated_data['annotations'][i],
                             annotated_data['comments'][i]])
    st.session_state.message = "Annotations saved successfully!"
    st.session_state.message_type = "success"

# Function to show only annotated cases
def show_annotated_cases():
    annotated_cases = {k: v for k, v in st.session_state.annotations.items() if len(v) > 0}
    if annotated_cases:
        st.write("Annotated Cases:")
        for index, labels in annotated_cases.items():
            actual_index = int(index)
            st.write(f"ID: {data.iloc[actual_index]['id']}")
            st.write(f"Hate Speech: {data.iloc[actual_index]['hatespeech']}")
            st.write(f"Counter Speech: {data.iloc[actual_index]['counterspeech']}")
            st.write(f"Annotations: {labels}")
            st.write(f"Comments: {st.session_state.comments[actual_index]}")
            st.write("---")
    else:
        st.write("No annotations yet.")

# Function to handle pagination
def next_page():
    if all(len(st.session_state.annotations[i]) > 0 for i in range(st.session_state.page * ITEMS_PER_PAGE, min(len(data), (st.session_state.page + 1) * ITEMS_PER_PAGE))):
        st.session_state.page += 1
        st.session_state.message = ""
        st.session_state.message_type = ""
    else:
        st.session_state.message = "Please select at least one strategy for each case before moving to the next page."
        st.session_state.message_type = "warning"

def prev_page():
    st.session_state.page -= 1
    st.session_state.message = ""
    st.session_state.message_type = ""

# Title of your app
st.title('Annotation Task for Counterspeech Strategies')

# Check if user is logged in
user_login()
if st.session_state.username:
    st.write(f"Logged in as: {st.session_state.username}")

    # Define constants for pagination
    ITEMS_PER_PAGE = 5

    # Calculate the range of indices for the current page
    start_idx = st.session_state.page * ITEMS_PER_PAGE
    end_idx = (st.session_state.page + 1) * ITEMS_PER_PAGE
    page_data = data.iloc[start_idx:end_idx]

    # Display current page pairs
    strategy_options = ["Empathy and Affiliation", "Warning of Consequences",
                        "Pointing Out Hypocrisy", "Shaming and Labelling",
                        "Denouncing", "Fact-Checking", "Humour", "Questioning"]

    for i, row in enumerate(page_data.itertuples(), start=start_idx):
        st.write(f"**Case {i + 1}**")
        st.text_area("Hate Speech", value=row.hatespeech, height=100, disabled=True, key=f"hate_speech_{i}")
        st.text_area("Counter Speech", value=row.counterspeech, height=100, disabled=True, key=f"counter_speech_{i}")

        selected_strategies = st.session_state.annotations[i]

        # Display buttons for strategy selection in two rows
        cols = st.columns(4)
        for j, strategy in enumerate(strategy_options):
            is_selected = strategy in selected_strategies
            button_label = f"✅ {strategy}" if is_selected else strategy
            if cols[j % 4].button(button_label, key=f"strategy_{i}_{strategy}", help="Click to select or deselect"):
                if strategy in selected_strategies:
                    selected_strategies.remove(strategy)
                else:
                    selected_strategies.append(strategy)
                st.session_state.annotations[i] = selected_strategies
                st.rerun()  # Immediately rerun to sync the button state

        # Add a free text box for comments
        st.session_state.comments[i] = st.text_area("Comments", value=st.session_state.comments[i], key=f"comments_{i}")

    # Pagination buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.page > 0:
            st.button("Previous", on_click=prev_page)
    with col2:
        if end_idx < len(data):
            st.button("Next", on_click=next_page)

    # Display any messages at the bottom with appropriate formatting
    if st.session_state.message:
        if st.session_state.message_type == "success":
            st.success(st.session_state.message)
        elif st.session_state.message_type == "warning":
            st.warning(st.session_state.message)

    # Placeholder for Annotation guidelines
    if st.sidebar.button("Annotation Guidelines"):
        toggle_guidelines()

    if st.session_state.show_guidelines:
        st.write("Counterspeech Annotation Guidelines")
        for strategy, description in {
            "Empathy and Affiliation": "Use a positive and constructive tone.",
            "Warning of Consequences": "Highlight potential negative outcomes, like social or legal consequences.",
            "Pointing Out Hypocrisy": "Underline logical flaws or double standards in the hate speech.",
            "Shaming and Labelling": "Call out hate speech by labeling it as discriminatory.",
            "Denouncing": "Express outright rejection of the hateful views.",
            "Fact-Checking": "Address inaccuracies by presenting factual information.",
            "Humour/Sarcasm": "Use wit or sarcasm to lighten the conversation's tone.",
            "Questioning": "Ask questions to challenge the hate speech."
        }.items():
            st.write(f"**{strategy}**: {description}")

    # Toggle debug mode to display annotations
    if st.sidebar.checkbox("Debug Mode", value=st.session_state.debug_mode):
        toggle_debug_mode()

    if st.session_state.debug_mode:
        show_annotated_cases()

    # Save annotations
    st.button("Save Annotations", on_click=save_annotations)

else:
    st.sidebar.warning("Please login to continue.")
