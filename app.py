import streamlit as st
import requests
import json
import uuid

# Configure the base URL for your FastAPI backend
BASE_URL = "https://murshed.marahel.sa/"  # Adjust this to your FastAPI server URL

# Hardcoded chatbot ID
DEFAULT_CHATBOT_ID = "de305d54-75b4-431b-adb2-eb6b9e546014"

def main():
    st.title("MARAHEL QA chatBot")
    
    # Initialize session state variables if they don't exist
    if 'chatbot_id' not in st.session_state:
        st.session_state.chatbot_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar for configuration and file upload
    with st.sidebar:
        st.header("Configuration")
        
        # Chatbot ID input with default value hint
        st.info(f"Default Chatbot ID: {DEFAULT_CHATBOT_ID}")
        chatbot_id = st.text_input("Enter Chatbot ID", key="chatbot_id_input")
        if chatbot_id:
            st.session_state.chatbot_id = chatbot_id
        else:
            st.session_state.chatbot_id = DEFAULT_CHATBOT_ID
            
        # User ID input
        user_id = st.text_input("Enter User ID", key="user_id_input")
        if user_id:
            st.session_state.user_id = user_id
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload Documents",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt', 'doc']
        )
        
        if uploaded_files and st.button("Process Documents"):
            with st.spinner("Processing documents..."):
                try:
                    # Create a list of files in the correct format for multipart/form-data
                    files = []
                    for uploaded_file in uploaded_files:
                        file_content = uploaded_file.read()
                        st.write(f"Processing file: {uploaded_file.name}, Size: {len(file_content)} bytes")
                        files.append(('files', (uploaded_file.name, file_content, uploaded_file.type)))
                    
                    # Log request details
                    st.write(f"Sending request to: {BASE_URL}/api/Ingestion_File")
                    
                    # Include only chatbot_id in the form data for file insertion
                    response = requests.post(
                        f"{BASE_URL}/api/Ingestion_File",
                        files=files,
                        data={"chatbot_id": st.session_state.chatbot_id}
                    )
                    
                    # Log response details
                    st.write(f"Response status code: {response.status_code}")
                    st.write(f"Response content: {response.text}")
                    
                    if response.status_code == 200:
                        st.success("Documents processed successfully!")
                    else:
                        error_message = response.json().get('message', 'Unknown error occurred')
                        st.error(f"Error: {error_message}")
                        st.write(f"Full error response: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Network error: {str(e)}")
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON response: {str(e)}")
        
        # Delete collection button
        if st.button("Delete Current Collection"):
            try:
                response = requests.delete(
                    f"{BASE_URL}/api/delete-collection",
                    json={"chatbot_id": st.session_state.chatbot_id}
                )
                if response.status_code == 200:
                    st.success("Collection deleted successfully!")
                    st.session_state.chat_history = []
                else:
                    st.error(f"Error: {response.json()['message']}")
            except Exception as e:
                st.error(f"Error deleting collection: {str(e)}")

    # Main chat interface
    st.header("Chat Interface")
    
    if hasattr(st.session_state, 'user_id'):
        # Display chat history
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]
            with st.chat_message(role):
                st.write(content)

        # Chat input
        if prompt := st.chat_input("Ask a question about your documents"):
            if not st.session_state.user_id:
                st.error("Please enter a User ID first")
                return
                
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Get AI response
            try:
                response = requests.post(
                    f"{BASE_URL}/api/chat-bot",
                    json={
                        "query": prompt,
                        "chatbot_id": st.session_state.chatbot_id,
                        "user_id": st.session_state.user_id
                    }
                )
                
                if response.status_code == 200:
                    ai_response = response.json()["data"]
                    # Display AI response
                    with st.chat_message("assistant"):
                        st.write(ai_response)
                    # Add AI response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                else:
                    st.error(f"Error: {response.json()['message']}")
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")
    else:
        st.info("Please enter User ID to start chatting.")

if __name__ == "__main__":
    main()
