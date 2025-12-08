import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

# Load the API key from the .env file.
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# The model we will be using for the core logic
MODEL_NAME = "gemini-2.5-flash"

# --- Function to interact with the Gemini API ---
def get_gemini_response(user_prompt, model_name=MODEL_NAME):
    """
    Sends a prompt to the Gemini model and returns the response text.
    """
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(user_prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def get_gemini_chat_response(messages, model_name=MODEL_NAME):
    """
    Handles a multi-turn chat with the Gemini model.
    """
    try:
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat()
        response = chat.send_message(messages)
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# --- Streamlit UI Components ---
st.set_page_config(page_title="AI Interview Coach", layout="wide")

# Custom CSS for a clean, professional dark-mode look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .st-emotion-cache-183n499 {
        font-family: "Inter", sans-serif;
    }
    .st-emotion-cache-1c5p8w4 {
        color: #e0e0e0;
    }
    .main {
        background-color: #121212;
    }
    .card {
        background-color: #1f1f1f;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
        border: 1px solid #333333;
    }
    h1 {
        text-align: center;
        color: #f5f5f5;
        font-size: 2.5rem;
        margin-bottom: 0;
    }
    .st-emotion-cache-pk-m7h {
        border-color: #333333;
        background-color: #2b2b2b;
        color: #f5f5f5;
    }
    .st-emotion-cache-1r70ds6 {
        border-radius: 10px;
        background-color: #2e8b57;
        color: white;
        border: none;
        padding: 12px;
        font-size: 16px;
        transition: background-color 0.2s ease;
    }
    .st-emotion-cache-1r70ds6:hover {
        background-color: #3cb371;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #777;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p{
        font-size: 1.1rem;
        font-weight: 600;
        color: #f5f5f5;
    }
    .stTabs [data-baseweb="tab-list"] button{
        background-color: #1f1f1f;
        border-radius: 10px;
        margin-right: 10px;
    }
    .stTabs [aria-selected="true"] button{
        border-bottom-color: #2e8b57 !important;
        background-color: #2e8b57 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("AI-Powered Interview Coach")
st.markdown("---")

tab1, tab2 = st.tabs(["Practice Mode", "Chat Interview"])

with tab1:
    # Use a session state to manage the conversation flow for Practice Mode
    if "question_practice" not in st.session_state:
        st.session_state.question_practice = ""
    if "feedback_practice" not in st.session_state:
        st.session_state.feedback_practice = ""

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Step 1: Tell me the job you're preparing for.")
        job_role = st.text_input("Enter the job title (e.g., 'Software Engineer', 'Data Scientist')", key="job_role_practice")
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate a Question", use_container_width=True):
                if job_role:
                    prompt = f"""
                    You are a career interview coach. Generate one realistic interview question for a candidate applying for the job of a {job_role}. The question should be challenging and relevant to the role.
                    Do not provide an answer or any other text, just the question itself.
                    """
                    question = get_gemini_response(prompt)
                    if question:
                        st.session_state.question_practice = question
                        st.session_state.feedback_practice = ""
                else:
                    st.warning("Please enter a job role first.")

        with col2:
            if st.session_state.question_practice:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("### Step 2: Answer the Question")
                st.info(st.session_state.question_practice)
                user_answer = st.text_area("Type your answer here:", height=200, key="user_answer_practice")
                st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button("Get Feedback", use_container_width=True):
                    if user_answer:
                        feedback_prompt = f"""
                        You are a professional and encouraging career coach. I am preparing for an interview for a {job_role} role.

                        Here is the question: "{st.session_state.question_practice}"
                        
                        And here is my answer: "{user_answer}"
                        
                        Provide constructive feedback on my answer. Focus on:
                        - The strengths of the answer.
                        - Areas for improvement, with specific suggestions.
                        - Tips on how to structure the answer better (e.g., using the STAR method).
                        - Keep your tone positive and helpful. Format your response in a clear, easy-to-read way with headings.
                        """
                        feedback = get_gemini_response(feedback_prompt)
                        if feedback:
                            st.session_state.feedback_practice = feedback
                    else:
                        st.warning("Please enter your answer first.")

        if st.session_state.feedback_practice:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Your Feedback")
            st.markdown(st.session_state.feedback_practice)
            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    # Use a session state to manage the conversation flow for Chat Interview
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_enabled" not in st.session_state:
        st.session_state.chat_enabled = False
    if "job_role_chat_session" not in st.session_state:
        st.session_state.job_role_chat_session = ""
    
    st.markdown("### Step 1: Start a New Interview")
    job_role_chat = st.text_input("Enter the job role for the chat interview:", key="job_role_chat_input")
    if st.button("Start Chat Interview"):
        if job_role_chat:
            st.session_state.chat_enabled = True
            st.session_state.chat_messages = []
            st.session_state.job_role_chat_session = job_role_chat
            initial_prompt = f"""
            You are a professional and friendly career coach conducting a mock interview for a {job_role_chat} role.
            Start the conversation by greeting the candidate and asking your first, challenging question relevant to this role.
            Keep your tone positive and professional. Do not provide a list of questions, just ask one at a time.
            """
            response = get_gemini_chat_response(initial_prompt)
            if response:
                st.session_state.chat_messages.append({"role": "model", "content": response})
        else:
            st.warning("Please enter a job role to start the chat.")

    st.markdown("---")
    st.markdown("### Step 2: Your Chat Interview")

    if st.session_state.chat_enabled:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_prompt := st.chat_input("Your response:"):
            st.chat_message("user").markdown(user_prompt)
            st.session_state.chat_messages.append({"role": "user", "content": user_prompt})

            chat_history = [m["content"] for m in st.session_state.chat_messages]
            
            full_prompt = f"""
            You are a professional and friendly career coach conducting a mock interview for a {st.session_state.job_role_chat_session} role.
            Your tone is positive and professional. You remember the entire conversation.
            Here is the full conversation so far:
            
            {chat_history}
            
            Now, respond with your next question or a follow-up to the user's last response.
            Do not provide an answer or feedback, just continue the conversation.
            """
            
            response = get_gemini_chat_response(full_prompt)
            if response:
                with st.chat_message("model"):
                    st.markdown(response)
                st.session_state.chat_messages.append({"role": "model", "content": response})

st.markdown("<div class='footer'>AI Interview Coach powered by Google Gemini</div>", unsafe_allow_html=True)
