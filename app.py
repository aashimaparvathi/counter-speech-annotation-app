import streamlit as st
import pandas as pd
import csv
from collections import defaultdict

# Load the data
data = pd.read_csv('data/intentconanv2/40-per-target-sample.csv')

user_mapping = {
    'CSAT1758': (0, 40),
    'CSAT3968': (40, 80),
    'CSAT1245': (80, 120),
    'CSAT9877': (120, 160),
    'CSAT1290': (160, 200),
    'CSAT7463': (200, 240),
    'CSAT0986': (240, 280),
    'CSAT2365': (280, 320),
    'CSAT9833': (320, 360),
    'CSAT7657': (360, 400),
    'CSAT4535': (400, 440),
    'CSAT8973': (440, 480),
    'CSAT5361': (480, 520),
    'CSAT7492': (520, 560),

    'CSAT0578': (0, 40),
    'CSAT1698': (40, 80),
    'CSAT2425': (80, 120),
    'CSAT3787': (120, 160),
    'CSAT4920': (160, 200),
    'CSAT5643': (200, 240),
    'CSAT6896': (240, 280),
    'CSAT7635': (280, 320),
    'CSAT8383': (320, 360),
    'CSAT9567': (360, 400),
    'CSAT0355': (400, 440),
    'CSAT1793': (440, 480),
    'CSAT2631': (480, 520),
    'CSAT3942': (520, 560),
}

# Initialize session state for user login, guidelines toggle, annotations, comments, and debug mode
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_guidelines' not in st.session_state:
    st.session_state.show_guidelines = True
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

    # Write annotations to CSV file
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
    current_page_data = page_data.iloc[st.session_state.page * ITEMS_PER_PAGE:(st.session_state.page + 1) * ITEMS_PER_PAGE]
    if all(len(st.session_state.annotations[idx]) > 0 for idx in current_page_data.index):
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

# Title
st.title('Counterspeech Strategy Annotation')

# Check if user is logged in
user_login()
if st.session_state.username:
    st.write(f"Logged in as: {st.session_state.username}")

    # Get the subset range for the logged-in user (based on pre-defined user-mapping)
    if st.session_state.username in user_mapping:
        start_idx, end_idx = user_mapping[st.session_state.username]
        page_data = data.iloc[start_idx:end_idx]  # Initialize the user's data subset here
    else:
        st.error("Username not recognized!")
        st.stop()  # Stop the app if the username is not recognized

    # Determine the button label based on whether the guidelines are currently shown or hidden
    button_label = "Hide Annotation Guidelines" if st.session_state.show_guidelines else "View Annotation Guidelines"

    # Placeholder for Annotation guidelines
    if st.sidebar.button(button_label):
        toggle_guidelines()
        st.rerun()  # Rerun the app to update the button label immediately

    # Ensure page_data is always defined before any further processing
    ITEMS_PER_PAGE = 5
    start_page_idx = st.session_state.page * ITEMS_PER_PAGE
    end_page_idx = (st.session_state.page + 1) * ITEMS_PER_PAGE
    current_page_data = page_data.iloc[start_page_idx:end_page_idx]

    # Display the annotation guidelines if they're set to show
    if st.session_state.show_guidelines:
        guidelines = [
            {"Strategy": "Empathy and Affiliation", "Explanation": "Uses kind, compassionate, or understanding language expressing empathy or concern towards the speaker or targeted group; Focuses on promoting peace, understanding, or common ground."},
            {"Strategy": "Warning of Consequences", "Explanation": "Highlights potential negative outcomes such as legal, social, or personal consequences of the hate speech; Serious, cautionary, or urgent tone."},
            {"Strategy": "Pointing Out Hypocrisy", "Explanation": "Highlights inconsistencies, illogical reasoning, contradictions, or double standards in the hate speech; Critical, logical, or analytical tone."},
            {"Strategy": "Shaming and Labelling", "Explanation": "Attacks/condemns and shames the speaker with negative terms or labels to highlight immorality or inappropriateness; Confrontational or accusatory tone."},
            {"Strategy": "Denouncing", "Explanation": "Explicitly condemns or rejects the hateful views/ideas expressed in the hate speech by stating it is wrong, unacceptable, harmful, etc.; Firm, direct tone without personal attacks."},
            {"Strategy": "Fact-Checking", "Explanation": "Mentions specific (sometimes verifiable) information such as facts, statistics, articles, or evidence to contradict claims made in the hate speech; Neutral tone focused on correcting misinformation."},
            {"Strategy": "Humour/Sarcasm", "Explanation": "Uses humour, irony, or sarcasm to undermine hate speech by mocking the comment or the speaker in a light-hearted or biting way; Playful, funny, or mocking tone."},
            {"Strategy": "Questioning", "Explanation": "Questions the hate speech or speaker by challenging the assumptions or logic or simply asking for clarification; Inquisitive or probing tone."}
        ]

        guidelines_df = pd.DataFrame(guidelines).reset_index(drop=True)
        html_table = guidelines_df.to_html(index=False, classes='table', border=0)
        st.markdown(html_table, unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)

    strategy_options = ["Empathy and Affiliation", "Warning of Consequences",
                        "Pointing Out Hypocrisy", "Shaming and Labelling",
                        "Denouncing", "Fact-Checking", "Humour", "Questioning"]

    for i, row in enumerate(current_page_data.itertuples(), start=start_idx + start_page_idx):
        st.write(f"**Case {i + 1}**")
        st.text_area("Hate Speech", value=row.hatespeech, height=100, disabled=True, key=f"hate_speech_{i}")
        st.text_area("Counter Speech", value=row.counterspeech, height=100, disabled=True, key=f"counter_speech_{i}")

        selected_strategies = st.session_state.annotations[i]

        # Display buttons for strategy selection as two rows
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
        if end_page_idx < len(page_data):
            st.button("Next", on_click=next_page)

    # Display any messages at the bottom with appropriate formatting
    if st.session_state.message:
        if st.session_state.message_type == "success":
            st.success(st.session_state.message)
        elif st.session_state.message_type == "warning":
            st.warning(st.session_state.message)

    # Toggle debug mode to display annotations
    # NOTE: Re-enable when required
    st.sidebar.checkbox("Debug Mode", on_change=toggle_debug_mode)

    if st.session_state.debug_mode:
        show_annotated_cases()

    # Save annotations
    st.button("Save Annotations", on_click=save_annotations)

else:
    st.sidebar.warning("Please login to continue.")
