import streamlit as st
import requests
import json
from typing import List
import os

# Configure the API endpoint
API_BASE_URL = "https://murshad-chatbot-542808340038.us-central1.run.app/"  # Change this to your deployed API URL

def main():
    st.title("Marahel Document Q&A ")
    
    # Initialize session state variables if they don't exist
    if 'collection_name' not in st.session_state:
        st.session_state.collection_name = None
    if 'embeddings_model' not in st.session_state:
        st.session_state.embeddings_model = None

    # Sidebar for file upload and model selection
    with st.sidebar:
        st.header("Document Upload")
        uploaded_files = st.file_uploader(
            "Upload your documents", 
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt'],
            key="unique_file_uploader_key"
        )
        
        embeddings_model = st.text_input(
            "Embeddings Model Name",
            value="Omartificial-Intelligence-Space/Arabic-mpnet-base-all-nli-triplet"
        )
        
        if uploaded_files and st.button("Process Documents"):
            files = [("files", file) for file in uploaded_files]
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/Ingestion_File",
                    params={"Embeddings_model": embeddings_model},
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.collection_name = result["data"]["collection_name"]
                    st.session_state.embeddings_model = result["data"]["Embeddings_model"]
                    st.success("Documents processed successfully!")
                else:
                    st.error(f"Error: {response.json()['message']}")
            
            except Exception as e:
                st.error(f"Error connecting to the API: {str(e)}")

        # Sidebar for deleting a collection
        st.header("Delete Collection")
        collection_to_delete = st.text_input("Collection Name to Delete")
        if st.button("Delete Collection"):
            try:
                response = requests.delete(
                    f"{API_BASE_URL}/api/delete-collection",
                    params={"collection_name": collection_to_delete}
                )
                print(response.text)
                if response.status_code == 200:
                    st.success("Collection deleted successfully!")
                else:
                    st.error(f"Error: {response.json()['message']}")
            
            except Exception as e:
                st.error(f"Error connecting to the API: {str(e)}")

    # Main chat interface
    st.header("Chat with your Documents")
    
    if st.session_state.collection_name:
        st.info(f"Current Collection: {st.session_state.collection_name}")
        
        # Chat interface
        with st.form(key='chat_form'):
            user_question = st.text_input("Ask a question about your documents:")
            submit_button = st.form_submit_button(label='Get Answer')
        
        if submit_button:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/chat-bot",
                    json={
                        "query": user_question,
                        "collection_name": st.session_state.collection_name,
                        "Embeddings_model": st.session_state.embeddings_model
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.write("Answer:")
                    st.write(result["data"])
                else:
                    st.error(f"Error: {response.json()['message']}")
                    
            except Exception as e:
                st.error(f"Error connecting to the API: {str(e)}")
    
    else:
        st.info("Please upload documents first using the sidebar.")

    # Removed "Start New Session" button and its functionality

if __name__ == "__main__":
    if 'rerun' in st.session_state:
        del st.session_state['rerun']
        st.experimental_rerun()
    main()