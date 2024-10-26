import streamlit as st
import requests

API_URL = "https://rag-chat-pdf.onrender.com/"

def create_session():
    response = requests.get(f"{API_URL}/create_session")
    if response.status_code == 200:
        return response.json()["session_id"]
    else:
        st.sidebar.error("Failed to create a session.")
        return None

def delete_session(session_id):
    response = requests.post(f"{API_URL}/delete_session", json={"session_id": session_id})
    return response

def upload_files(session_id, model, files):
    if not files:
        st.sidebar.error("Please upload at least one file.")
        return None

    files_dict = {f"files": (file.name, file, "application/pdf") for file in files}

    response = requests.post(
        f"{API_URL}/upload_files",
        data={"session_id": session_id, "model": model},
        files=files_dict
    )
    
    return response

def chat(session_id, question):
    response = requests.post(f"{API_URL}/chat", json={"session_id": session_id, "question": question})
    return response

st.title("AI SCHOLAR")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.header("Document Upload")
    
    if st.button("Create Session"):
        session_id = create_session()
        st.session_state.session_id = session_id
        if session_id:
            st.success(f"Session created: {session_id}")
    
    if 'session_id' in st.session_state:
        st.subheader("Upload Files")
        uploaded_files = st.file_uploader(
            "Select PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload your PDF documents here"
        )
        
        model = st.selectbox(
            "Select Model",
            ["GOOGLE"],
            help="Choose the model for processing your documents"
        )
        
        if st.button("Upload Files"):
            if uploaded_files:
                response = upload_files(st.session_state.session_id, model, uploaded_files)
                if response and response.status_code == 200:
                    st.success("Files uploaded successfully!")
                else:
                    st.error("Failed to upload files.")
        
        if st.button("Delete Session"):
            response = delete_session(st.session_state.session_id)
            if response and response.status_code == 200:
                st.success("Session deleted successfully!")
                del st.session_state.session_id
                del st.session_state.chat_history  
            else:
                st.error("Failed to delete session.")

if 'session_id' in st.session_state:
    # st.subheader("Chat History")
    for question, answer in st.session_state.chat_history:
        st.markdown(f"**You:** {question}")
        st.markdown(f"**AI:** {answer}")
    

    chat_container = st.container()
    
    with chat_container:
        question = st.text_input(
            "Ask a question about your documents:",
            placeholder="Type your question here..."
        )
        
        if st.button("Send", key="send_button"):
            if question:
                with st.spinner("Getting response..."):
                    response = chat(st.session_state.session_id, question)
                    if response and response.status_code == 200:
                        answer = response.json().get("response", "No response from server.")
                        st.success(answer)

                        st.session_state.chat_history.append((question, answer))
                    else:
                        st.error("Failed to get response from the server.")
else:
    st.info("👈 Please create a session and upload documents using the sidebar to start chatting.")