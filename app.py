import streamlit as st
import pandas as pd
import csv
from collections import defaultdict
from datetime import datetime  # Import to include timestamps

# control the number of cases assigned per participant
TOTAL_CASES = 5  # change this value to control the number of cases

# Load the data
data = pd.read_csv('data/iconan/40-per-target-sample.csv')

# Initialise session state for user login, guidelines toggle, annotations, comments, and debug mode
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
if 'assigned_set' not in st.session_state:
    st.session_state.assigned_set = None

assignments_file = filename = f'data/control/assignments.csv'
completed_file = filename = f'data/control/completed.csv'


# strategies
strategy_options = [
    "Empathy and Affiliation",
    "Warning of Consequence",
    "Hypocrisy / Contradiction",
    "Shaming / Labelling",
    "Denouncing",
    "Fact-Checking",
    "Humour / Sarcasm",
    "Questioning"
]

# mapping between strategies and their explanations for tooltips
strategy_guidelines = {
    "Empathy and Affiliation": "Uses kind, compassionate, or understanding language expressing empathy or concern towards the speaker or targeted group; Focuses on promoting understanding or common ground.",
    "Warning of Consequence": "Warns the speaker about potential negative outcomes of the hate speech such as legal, social, or personal consequences; Serious, cautionary, or urgent tone.",
    "Hypocrisy / Contradiction": "Points out inconsistencies, illogical reasoning, contradictions, or double standards in the hate speech; Critical, logical, or analytical tone.",
    "Shaming / Labelling": "Attacks, condemns or shames the speaker with negative terms or labels to highlight immorality or inappropriateness; Confrontational or accusatory tone.",
    "Denouncing": "Explicitly condemns or MORALLY rejects the hateful views expressed in the hate speech by stating it is wrong, unacceptable, harmful, etc.; Firm, moral tone without personal attacks.",
    "Fact-Checking": "Mentions relevant information or facts with or without evidence to contradict the hate speech or asks for evidence for the claims made; Focused on FACTUALLY correcting misinformation.",
    "Humour / Sarcasm": "Uses humour, sarcasm, or irony to undermine hate speech by mocking the comment or the speaker, sometimes in a biting way; Funny, mocking, or playful tone.",
    "Questioning": "Questions the hate speech or speaker, usually expecting an answer, by challenging the logic or simply asking for clarification."
}

# fetch Prolific PID from URL
def get_prolific_pid():
    query_params = st.query_params
    if 'PROLIFIC_PID' in query_params:
        prolific_pid = query_params['PROLIFIC_PID']
        if isinstance(prolific_pid, list):  # Check if list and retrieve the first element
            return prolific_pid[0]
        return prolific_pid  # If it's already a string, return it directly
    return None

# Check if the PID has already completed the task by checking completed.csv
def has_completed_task(prolific_pid):
    try:
        with open(completed_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == prolific_pid:
                    return True
    except FileNotFoundError:
        return False
    return False

# Save the PID to completed.csv after annotations are saved
def mark_as_completed(prolific_pid):
    with open(completed_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([prolific_pid])

# assign a set of cases to each participant, ensuring two participants get the same set
def assign_set(prolific_pid, max_sets=20):
    assignments = {}  # storing past case assignments
    assigned_counts = defaultdict(int)  # track how many times a set has been assigned

    # Load existing assignments
    try:
        with open(assignments_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                assignments[row[0]] = int(row[1])
                assigned_counts[int(row[1])] += 1
    except FileNotFoundError:
        pass

    # Check if PID already has an assignment
    if prolific_pid in assignments:
        st.session_state.assigned_set = assignments[prolific_pid]
    else:
        # find next available set with less than 2 assignments
        for set_id in range(max_sets):
            if assigned_counts[set_id] < 2:
                st.session_state.assigned_set = set_id
                assignments[prolific_pid] = set_id
                assigned_counts[set_id] += 1
                break

        # save new assignment
        with open(assignments_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for pid, set_id in assignments.items():
                writer.writerow([pid, set_id])

# load Prolific PID and assign a set of cases
prolific_pid = get_prolific_pid()
if prolific_pid:
    # Check if the user has already completed the task
    if has_completed_task(prolific_pid):
        st.error("You have already completed this task. Thank you!")
        st.stop()

    st.session_state.username = prolific_pid  # Set PID as the username
    assign_set(prolific_pid)
else:
    st.error("No Prolific PID found. Please make sure you are accessing the app through the Prolific platform.")

# Select the assigned set of examples from the dataset (note: controlled by TOTAL_CASES)
if st.session_state.assigned_set is not None:
    start_idx = st.session_state.assigned_set * TOTAL_CASES
    end_idx = start_idx + TOTAL_CASES
    page_data = data.iloc[start_idx:end_idx]  # Assign set of cases to the participant
else:
    st.error("No set has been assigned yet.")

# save annotations to a CSV file
def save_annotations():
    annotated_data = {
        'username': [],
        'id': [],
        #'hs_id': [],
        #'id_orig': [],
        'hatespeech': [],
        'counterspeech': [],
        'annotations': [],
        'comments': []
    }

    username = st.session_state.username  # Use Prolific PID as username

    for index, annotations in st.session_state.annotations.items():
        actual_index = int(index)
        annotated_data['username'].append(username)
        annotated_data['id'].append(data.iloc[actual_index]['id'])
        #'].append(data.iloc[actual_index]['hs_id'])
        #annotated_data['id_orig'].append(data.iloc[actual_index]['id_orig'])
        annotated_data['hatespeech'].append(data.iloc[actual_index]['hatespeech'])
        annotated_data['counterspeech'].append(data.iloc[actual_index]['counterspeech'])
        annotated_data['annotations'].append(", ".join(annotations))
        annotated_data['comments'].append(st.session_state.comments[actual_index])

    # generate filename with Prolific PID and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'data/annotations/{username}_annotated_data_{timestamp}.csv'  # file name with timestamp

    # write annotations to CSV file
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        #writer.writerow(['username', 'id', 'hs_id', 'id_orig', 'hatespeech', 'counterspeech', 'annotations', 'comments'])
        writer.writerow(['username', 'id', 'hatespeech', 'counterspeech', 'annotations', 'comments'])
        for i in range(len(annotated_data['id'])):
            writer.writerow([
                annotated_data['username'][i],
                annotated_data['id'][i],
                #annotated_data['hs_id'][i],
                #annotated_data['id_orig'][i],
                annotated_data['hatespeech'][i],
                annotated_data['counterspeech'][i],
                annotated_data['annotations'][i],
                annotated_data['comments'][i]
            ])

    # Mark the PID as completed
    mark_as_completed(username)

    # exit screen
    st.success("Thank you for completing the task! You may now close this window.")
    st.stop()  # Stop further execution and display the message

# Function to calculate the max width and height needed for buttons
def get_max_button_size(strategy_options):
    max_width = max([len(strategy) for strategy in strategy_options]) * 10  # Estimate width
    max_height = 60  # Fixed height
    return max_width, max_height


# Custom CSS to ensure all buttons have the same height
max_width, max_height = get_max_button_size(strategy_options)

st.markdown(f"""
    <style>
        div[data-testid="stHorizontalBlock"] > div {{
            flex: 1;
            max-width: {max_width}px;
            max-height: {max_height}px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        button {{
            width: 100%;
            height: {max_height}px;
            font-size: 16px;
            margin: 0px;
        }}
    </style>
""", unsafe_allow_html=True)

# pagination functions
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

# Display Prolific PID (username)
if st.session_state.username:
    st.write(f"Prolific PID: {st.session_state.username}") # DEBUG

# View/Hide Annotation Guidelines toggle sync
button_label = "Hide Annotation Guidelines" if st.session_state.show_guidelines else "View Annotation Guidelines"

with st.sidebar:
    if st.button(button_label):
        # Toggle the visibility of the guidelines and rerun the app to sync the label
        st.session_state.show_guidelines = not st.session_state.show_guidelines
        st.rerun()

    # Show or hide the annotation guidelines based on user selection
    if st.session_state.show_guidelines:
        st.subheader("Annotation Guidelines")
        guidelines = [
                {"Strategy": "Empathy and Affiliation",
                "Explanation": "Uses kind, compassionate, or understanding language expressing empathy or concern towards the speaker or targeted group; Focuses on promoting understanding or common ground.",
                "Examples": "HS: We can't bring in millions of refugees, and we shouldn't just accept the ills of Islam. CS: These are people in need—our brothers and sisters. We should help them."},

                {"Strategy": "Warning of Consequence",
                 "Explanation": "Warns the speaker about potential negative outcomes of the hate speech such as legal, social, or personal consequences; Serious, cautionary, or urgent tone.",
                 "Examples": "HS: We should forget the Shoah and solve the Jewish issue once and for all. CS: Ignoring history risks hurting future generations by not teaching them the lessons of the past."},

                {"Strategy": "Hypocrisy / Contradiction",
                 "Explanation": "Points out inconsistencies, illogical reasoning, contradictions, or double standards in the hate speech; Critical, logical, or analytical tone.",
                 "Examples": "HS: Zionist and Jewish control of America is the main cause of global terrorism and conflict. CS: Isn't colonialism and Western intervention abroad what led to much of the extremism?"},

                {"Strategy": "Shaming / Labelling",
                 "Explanation": "Attacks, condemns or shames the speaker with negative terms or labels to highlight immorality or inappropriateness; Confrontational or accusatory tone.",
                 "Examples": "HS: Faggots are ruining this country. CS: It seems you've become intolerant to homosexuals, maybe reflect on why love bothers you so much."},

                {"Strategy": "Denouncing",
                 "Explanation": "Explicitly condemns or MORALLY rejects the hateful views expressed in the hate speech by stating it is wrong, unacceptable, harmful, etc.; Firm, moral tone without personal attacks.",
                 "Examples": "HS: I miss the good old days when we had black domestic workers. CS: The West got rid of slavery. But we've never really left racism."},

                {"Strategy": "Fact-Checking",
                 "Explanation": "Mentions relevant information or facts with or without evidence to contradict the hate speech or asks for evidence for the claims made; Focused on FACTUALLY correcting misinformation.",
                 "Examples": "HS: Women can't handle money. CS: What proof do you have? The stereotype comes from medieval myths, not real financial behavior."},

                {"Strategy": "Humour / Sarcasm",
                 "Explanation": "Uses humour, sarcasm, or irony to undermine hate speech by mocking the comment or the speaker, sometimes in a biting way; Funny, mocking, or playful tone.",
                 "Examples": "HS: Jews are why the World Cup is so expensive. CS: Oh, I thought it was players' salaries... but sure, let's blame the usual Jewish conspiracy!"},

                {"Strategy": "Questioning",
                 "Explanation": "Questions the hate speech or speaker, usually expecting an answer, by challenging the logic or simply asking for clarification.",
                 "Examples": "HS: All Muslims are incompatible with any Western society. CS: I'm not sure what you are trying to say by incompatible. What do you mean by incompatible?"}
            ]
        guidelines_df = pd.DataFrame(guidelines)
        html_table = guidelines_df.to_html(index=False, classes='table', border=0)
        st.markdown(html_table, unsafe_allow_html=True)

# Show warning at the start if annotations are incomplete
if 'page_data' in locals():  # Ensures page_data exists
    if not all(len(st.session_state.annotations[idx]) > 0 for idx in page_data.index):
        st.warning("Please complete all annotations before exiting.")

# Check if user is logged in (DEBUG)
if st.session_state.assigned_set is not None:
    st.write(f"Assigned Set: {st.session_state.assigned_set + 1}") # DEBUG

    # page_data
    ITEMS_PER_PAGE = 1  # only 1 case per page
    start_page_idx = st.session_state.page * ITEMS_PER_PAGE
    end_page_idx = (st.session_state.page + 1) * ITEMS_PER_PAGE
    current_page_data = page_data.iloc[start_page_idx:end_page_idx]

    for i, row in enumerate(current_page_data.itertuples(), start=start_page_idx):
        st.write(f"**Case {i + 1}**") # DEBUG

        st.markdown(f"**Hate Speech (HS):** {row.hatespeech}")
        st.markdown(f"**Counter Speech (CS):** {row.counterspeech}")
        st.markdown("<br><br>", unsafe_allow_html=True)

        selected_strategies = st.session_state.annotations[i]

        # Display buttons for strategy selection as two rows
        cols = st.columns(4)
        for j, strategy in enumerate(strategy_options):
            is_selected = strategy in selected_strategies
            button_label = f"✅ {strategy}" if is_selected else strategy

            # Get the corresponding guideline for this strategy
            guideline_tooltip = strategy_guidelines.get(strategy, "Click to select or deselect")

            # Display button with the guideline tooltip
            if cols[j % 4].button(button_label, key=f"strategy_{i}_{strategy}", help=guideline_tooltip):
                if strategy in selected_strategies:
                    selected_strategies.remove(strategy)
                else:
                    selected_strategies.append(strategy)
                st.session_state.annotations[i] = selected_strategies
                st.rerun()  # Immediately rerun to sync the button state

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Free text box for comments with help text and placeholder
        comment_help_text = """
        Optional: Please share your thoughts about the case, such as:
        - Confusion between strategies (e.g., confused between strategy X and Y)
        - Issues with the case (e.g., mismatch between hate speech and counterspeech)
        - e.g., the counterspeech itself appears offensive
        - e.g., this case is particularly difficult to annotate because ...
        """
        st.session_state.comments[i] = st.text_area(
            "Comments (optional but encouraged)",
            value=st.session_state.comments[i],
            key=f"comments_{i}",
            help=comment_help_text,
            placeholder="e.g., Confused between strategy X and Y, mismatch between HS and CS, counterspeech itself seems offensive, this case is difficult to annotate because ..."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    # Pagination buttons
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.session_state.page > 0:
            st.button("Previous", on_click=prev_page)
    with col3:
        if end_page_idx < len(page_data):
            st.button("Next", on_click=next_page)

    # Calculate progress for progress bar
    total_cases = len(page_data)
    completed_cases = sum(len(annotations) > 0 for annotations in st.session_state.annotations.values())
    progress = completed_cases / total_cases

    # display progress bar and progress text
    st.write(f"{completed_cases}/{total_cases}")
    st.progress(progress)

    # Show Save and Exit button only on the last page and only if all annotations are complete
    last_page = (len(page_data) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE - 1
    if st.session_state.page == last_page:
        if all(len(st.session_state.annotations[idx]) > 0 for idx in page_data.index):
            st.button("Save and Exit", on_click=save_annotations)
else:
    st.sidebar.warning("No set has been assigned to you yet. Please refresh the page or check the Prolific link.")


#BACKUP
# Display buttons for strategy selection as two rows
#        cols = st.columns(4)
#        for j, strategy in enumerate(strategy_options):
#            is_selected = strategy in selected_strategies
#            button_label = f"✅ {strategy}" if is_selected else strategy
#            if cols[j % 4].button(button_label, key=f"strategy_{i}_{strategy}", help="Click to select or deselect"):
#                if strategy in selected_strategies:
#                    selected_strategies.remove(strategy)
#                else:
#                    selected_strategies.append(strategy)
#                st.session_state.annotations[i] = selected_strategies
#                st.rerun()  # Immediately rerun to sync the button state


