import streamlit as st
import openai
import requests

# Set your OpenAI API key
openai.api_key = ""

# Function to get Moodle data
def get_moodle_data(username, password):
    moodle_url = "https://moodle.htw-berlin.de"
    service = "moodle_mobile_app"

    # Get token
    login_url = f"{moodle_url}/login/token.php?username={username}&password={password}&service={service}"
    response = requests.get(login_url)

    st.write("Login Response Status Code:", response.status_code)
    st.write("Login Response Text:", response.text)

    if response.status_code == 200:
        response_data = response.json()
        if 'token' in response_data:
            user_token = response_data['token']

            # Get assignments using the user's token
            assignments_url = f"{moodle_url}/webservice/rest/server.php?wstoken={user_token}&wsfunction=mod_assign_get_assignments&moodlewsrestformat=json"
            assignments_response = requests.get(assignments_url).json()

            # Print the entire JSON response for debugging
            st.write("Assignments Response:", assignments_response)

            # Adapt this based on the actual JSON structure
            assignments = []
            for course in assignments_response.get('courses', []):
                for assignment in course.get('assignments', []):
                    assignments.append({
                        "course": course.get('fullname', 'Unknown Course'),
                        "due_date": assignment.get('duedate', 'No Due Date'),
                        "workload": "high"  # You might want to determine workload dynamically
                    })

            return {"assignments": assignments}
        else:
            st.error("Moodle login failed: Token not found in response.")
            return None
    else:
        st.error(f"Moodle login failed with status code {response.status_code}")
        return None

# Function to get OpenAI response
def get_ai_response(prompt, history):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=history,
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

# Function to get AI recommendations
def get_ai_recommendations(moodle_data):
    prompt = f"""
    You are an AI assistant for university students. Here is the data for a student:
    Assignments:
    {moodle_data['assignments']}

    Provide a personalized study plan and reminders.
    """
    history = [{"role": "system", "content": prompt}]
    response = get_ai_response(prompt, history)
    return response

# Streamlit UI
st.title("AI-Based Learning Assistant for Students")

# User login
st.subheader("Login to your Moodle Account")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    moodle_data = get_moodle_data(username, password)
    if moodle_data:
        st.session_state['moodle_data'] = moodle_data
        st.success("Logged in successfully!")

# Check if user is logged in
if 'moodle_data' in st.session_state:
    moodle_data = st.session_state['moodle_data']

    # Display Moodle data
    st.subheader("Your Assignments")
    for assignment in moodle_data['assignments']:
        st.write(f"Course: {assignment['course']}, Due Date: {assignment['due_date']}, Workload: {assignment['workload']}")

    # Get AI recommendations
    st.subheader("AI Recommendations")
    recommendations = get_ai_recommendations(moodle_data)
    st.write(recommendations)

    # Chat with AI
    st.subheader("Ask the AI")
    user_question = st.text_input("Your Question")

    if st.button("Send"):
        if user_question:
            history = [{"role": "system", "content": "You are an AI-based learning assistant for students."}]
            history.append({"role": "user", "content": user_question})
            ai_response = get_ai_response(user_question, history)
            st.write(f"AI: {ai_response}")
