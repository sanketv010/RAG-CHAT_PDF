import streamlit as st
import requests

# Define the base URL of your FastAPI server
API_URL = "https://rag-chat-pdf.onrender.com/"  # Ensure this matches your FastAPI server URL

# Function to create a new session
def create_session():
    response = requests.get(f"{API_URL}/create_session")
    if response.status_code == 200:
        return response.json()["session_id"]
    else:
        st.error("Failed to create a session.")
        return None

# Function to delete a session
def delete_session(session_id):
    response = requests.post(f"{API_URL}/delete_session", json={"session_id": session_id})
    return response

# Function to upload files
def upload_files(session_id, model, files):
    if not files:
        st.error("Please upload at least one file.")
        return None

    # Prepare the files dictionary for the request
    files_dict = {f"files": (file.name, file, "application/pdf") for file in files}

    response = requests.post(
        f"{API_URL}/upload_files",
        data={"session_id": session_id, "model": model},  # Form data
        files=files_dict  # Files must be sent in the 'files' argument
    )
    
    return response

# Function to chat
def chat(session_id, question):
    response = requests.post(f"{API_URL}/chat", json={"session_id": session_id, "question": question})
    return response

# Streamlit app layout
st.title("FastAPI Chat Interface")

# Create a new session
if st.button("Create Session"):
    session_id = create_session()
    st.session_state.session_id = session_id
    if session_id:
        st.success(f"Session created: {session_id}")

# Upload files
if 'session_id' in st.session_state:
    st.header("Upload Files")
    st.write("Choose PDF files to upload:")  # Label for the file uploader
    uploaded_files = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True)

    st.write("Select a model:")  # Label for the model selection
    model = st.selectbox("Model", ["GOOGLE"])  # Example models

    if st.button("Upload Files"):
        if uploaded_files:
            response = upload_files(st.session_state.session_id, model, uploaded_files)
            if response and response.status_code == 200:
                st.success("Files uploaded successfully!")
            else:
                st.error("Failed to upload files.")

    # Delete session button
    if st.button("Delete Session"):
        response = delete_session(st.session_state.session_id)
        if response and response.status_code == 200:
            st.success("Session deleted successfully!")
            del st.session_state.session_id  # Clear the session ID from state
        else:
            st.error("Failed to delete session.")

# Chat interface
if 'session_id' in st.session_state:
    st.header("Chat with the Model")
    st.write("Ask a question about the uploaded documents:")  # Label for the question input
    question = st.text_input("Your question:")
    
    if st.button("Send"):
        if question:
            response = chat(st.session_state.session_id, question)
            if response and response.status_code == 200:
                answer = response.json().get("response", "No response from server.")
                st.success(answer)
            else:
                st.error("Failed to get response from the server.")
else:
    st.warning("Create a session to upload files and chat.")
