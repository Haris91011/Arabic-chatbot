import streamlit as st
import requests
import json
import uuid

# Configure the base URL for your FastAPI backend
BASE_URL = "https://testing.murshed.marahel.sa/"  # Adjust this to your FastAPI server URL

def main():
    st.title("MARAHEL QA chatBot")
    
    # Initialize session state variables if they don't exist
    if 'current_uuid' not in st.session_state:
        st.session_state.current_uuid = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar for configuration and file upload
    with st.sidebar:
        st.header("Configuration")
        
        # LLM Model selection
        llm_model = st.selectbox(
            "Select LLM Model",
            ["OpenAI", "Claude-3-Sonnet"],
            key="llm_model"
        )
        
        # Embeddings Model selection
        embeddings_model = st.selectbox(
            "Select Embeddings Model",
            ["openai", "asafaya/bert-base-arabic", 
            "Omartificial-Intelligence-Space/Arabic-mpnet-base-all-nli-triplet",
            "Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2"],
            key="embeddings_model"
        )
        
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
                        # Read the file content
                        file_content = uploaded_file.read()
                        # Log file details
                        st.write(f"Processing file: {uploaded_file.name}, Size: {len(file_content)} bytes")
                        files.append(('files', (uploaded_file.name, file_content, uploaded_file.type)))
                    
                    # Log request details
                    st.write(f"Sending request to: {BASE_URL}/api/Ingestion_File")
                    st.write(f"Selected embeddings model: {embeddings_model}")
                    
                    response = requests.post(
                        f"{BASE_URL}/api/Ingestion_File",
                        files=files,
                        params={"Embeddings_model": embeddings_model}
                    )
                    
                    # Log response details
                    st.write(f"Response status code: {response.status_code}")
                    st.write(f"Response content: {response.text}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.current_uuid = result["uuid"]
                        st.success("Documents processed successfully!")
                        st.write(f"Collection UUID: {st.session_state.current_uuid}")
                    else:
                        error_message = response.json().get('message', 'Unknown error occurred')
                        st.error(f"Error: {error_message}")
                        st.write(f"Full error response: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Network error: {str(e)}")
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON response: {str(e)}")
        
        # Delete collection button
        if st.session_state.current_uuid and st.button("Delete Current Collection"):
            try:
                response = requests.delete(
                    f"{BASE_URL}/api/delete-collection",
                    json={"uuid": st.session_state.current_uuid}
                )
                if response.status_code == 200:
                    st.success("Collection deleted successfully!")
                    st.session_state.current_uuid = None
                    st.session_state.chat_history = []
                else:
                    st.error(f"Error: {response.json()['message']}")
            except Exception as e:
                st.error(f"Error deleting collection: {str(e)}")

    # Main chat interface
    st.header("Chat Interface")
    
    if st.session_state.current_uuid:
        # Display chat history
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]
            with st.chat_message(role):
                st.write(content)

        # Chat input
        if prompt := st.chat_input("Ask a question about your documents"):
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
                        "uuid": st.session_state.current_uuid,
                        "llm_model": llm_model
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
        st.info("Please upload documents to start chatting.")

if __name__ == "__main__":
    main()
