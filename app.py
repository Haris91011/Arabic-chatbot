import streamlit as st
import requests
import json
from typing import List
import os

# Configure the API endpoint
API_BASE_URL = "https://murshad-openai-542808340038.us-central1.run.app/"  # Change this to your deployed API URL

# Add this near the top of the file
EMBEDDING_MODELS = [
    "openai",
    "asafaya/bert-base-arabic",
    "Omartificial-Intelligence-Space/Arabic-mpnet-base-all-nli-triplet",
    "Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2",
]

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
            type=['pdf', 'docx', 'txt', 'doc'],
            key="unique_file_uploader_key"
        )
        
        embeddings_model = st.selectbox(
            "Select Embeddings Model",
            options=EMBEDDING_MODELS,
            index=1  # Default to the second option
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
        
        # Initialize chat history if it doesn't exist
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display assistant response
            with st.chat_message("assistant"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/chat-bot",
                        json={
                            "query": prompt,
                            "collection_name": st.session_state.collection_name,
                            "Embeddings_model": st.session_state.embeddings_model
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result["data"]
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        error_message = f"Error: {response.json()['message']}"
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
                        
                except Exception as e:
                    error_message = f"Error connecting to the API: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

    else:
        st.info("Please upload documents first using the sidebar.")

    # Removed "Start New Session" button and its functionality

if __name__ == "__main__":
    if 'rerun' in st.session_state:
        del st.session_state['rerun']
        st.experimental_rerun()
    main()