import streamlit as st
from datetime import datetime
import pytz
import tempfile
import os
import shutil
from git import Repo
import requests
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import glob

# --- Configuration ---
st.set_page_config(page_title="Jain Yuva Bot (RAG)", page_icon="🙏")

# --- Hard-coded Repo URL ---
REPO_URL = "https://github.com/saumyasanghvi03/AI-Yashvi/"

# --- Bytez API Configuration ---
BYTEZ_API_KEY = "90d252f09c55cacf3dcc914b5bb4ac01"
BYTEZ_MODEL = "Qwen/Qwen3-4B-Instruct-2507"
BYTEZ_API_URL = f"https://api.bytez.com/models/{BYTEZ_MODEL}/run"

# --- Rate Limiting Logic ---
IST = pytz.timezone('Asia/Kolkata')

def initialize_user_session():
    """Initializes session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to Jain Yuva Bot (JYB)! 🙏\n\nI'm an expert on the AI-Yashvi repository. Ask me anything about its content, or general questions about Jainism.\n\n*Powered by Bytez Qwen3-4B-Instruct model*"}
        ]
    
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    
    if "last_reset_date" not in st.session_state:
        st.session_state.last_reset_date = datetime.now(IST).date()
    
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    
    if "embedding_model" not in st.session_state:
        st.session_state.embedding_model = None

def check_and_reset_limit():
    """Checks if the day has changed (midnight IST) and resets the limit."""
    today_ist = datetime.now(IST).date()
    
    if st.session_state.last_reset_date < today_ist:
        st.session_state.question_count = 0
        st.session_state.last_reset_date = today_ist
        st.info("Your daily question limit has been reset. You can ask up to 5 questions.")

def get_remaining_questions():
    """Returns the number of questions remaining."""
    return 5 - st.session_state.question_count

# --- Custom RAG Functions (No LangChain) ---

@st.cache_resource
def load_embedding_model():
    """Load the sentence transformer model for embeddings."""
    try:
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        return model
    except Exception as e:
        st.error(f"Error loading embedding model: {e}")
        return None

def load_repo_and_build_store():
    """
    Clones the GitHub repo, loads text files, splits them, and builds a FAISS index.
    Returns a tuple (documents, index, document_metadata)
    """
    try:
        progress_bar = st.progress(0, text="Initializing...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_bar.progress(5, text=f"Cloning {REPO_URL}...")
            Repo.clone_from(REPO_URL, temp_dir)
            
            progress_bar.progress(20, text="Loading documents from repo...")
            
            # Find all text files
            documents = []
            document_metadata = []
            
            # Define file patterns to search for
            patterns = ['**/*.txt', '**/*.md', '**/*.py', '**/*.rst']
            
            for pattern in patterns:
                for file_path in glob.glob(os.path.join(temp_dir, pattern), recursive=True):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.strip():  # Only add non-empty files
                                # Get relative path for display
                                rel_path = os.path.relpath(file_path, temp_dir)
                                documents.append(content)
                                document_metadata.append({
                                    'source': rel_path,
                                    'content': content
                                })
                    except Exception as e:
                        st.warning(f"Could not read {file_path}: {e}")
            
            if not documents:
                st.error("No compatible documents found in this repository.")
                return None, None, None

            progress_bar.progress(40, text=f"Loaded {len(documents)} documents. Splitting...")
            
            # Split documents into chunks (simple splitting)
            text_chunks = []
            chunk_metadata = []
            
            for doc_content, meta in zip(documents, document_metadata):
                # Simple chunking by character count
                chunk_size = 1000
                chunk_overlap = 200
                
                for i in range(0, len(doc_content), chunk_size - chunk_overlap):
                    chunk = doc_content[i:i + chunk_size]
                    if len(chunk.strip()) > 50:  # Only add substantial chunks
                        text_chunks.append(chunk)
                        chunk_metadata.append({
                            'source': meta['source'],
                            'content': chunk,
                            'chunk_id': len(text_chunks)
                        })
            
            progress_bar.progress(60, text=f"Created {len(text_chunks)} text chunks. Creating embeddings...")
            
            # Load embedding model
            embedding_model = load_embedding_model()
            if not embedding_model:
                return None, None, None
            
            # Create embeddings
            embeddings = embedding_model.encode(text_chunks)
            
            progress_bar.progress(80, text="Building vector store...")
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)  # Using Inner Product (cosine similarity)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            index.add(embeddings)
            
            progress_bar.progress(100, text="Knowledge base loaded successfully!")
            progress_bar.empty()
            
            return index, text_chunks, chunk_metadata

    except Exception as e:
        st.error(f"Error loading repository: {e}")
        return None, None, None

def search_similar_documents(query, index, text_chunks, chunk_metadata, k=4):
    """Search for similar documents using the FAISS index."""
    try:
        embedding_model = st.session_state.embedding_model
        if not embedding_model:
            return []
        
        # Encode query
        query_embedding = embedding_model.encode([query])
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = index.search(query_embedding, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(text_chunks):
                results.append({
                    'content': text_chunks[idx],
                    'metadata': chunk_metadata[idx],
                    'score': float(score)
                })
        
        return results
        
    except Exception as e:
        st.error(f"Error searching documents: {e}")
        return []

def call_bytez_api(messages):
    """
    Calls the Bytez API based on the JavaScript SDK example.
    """
    try:
        # Prepare the request payload
        payload = {
            "messages": messages
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {BYTEZ_API_KEY}"
        }
        
        # Make the API call
        response = requests.post(
            BYTEZ_API_URL, 
            json=payload, 
            headers=headers, 
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            error = result.get("error")
            output = result.get("output")
            return error, output
        else:
            return f"HTTP Error: {response.status_code} - {response.text}", None
            
    except Exception as e:
        return f"Error calling Bytez API: {str(e)}", None

def get_rag_response(question, index, text_chunks, chunk_metadata):
    """
    Gets relevant context and calls Bytez API for response.
    """
    try:
        # Search for similar documents
        similar_docs = search_similar_documents(question, index, text_chunks, chunk_metadata, k=4)
        
        # Combine context from relevant documents
        context = "\n\n".join([doc['content'] for doc in similar_docs])
        
        # Prepare the system prompt
        system_prompt = """You are Jain Yuva Bot (JYB), an AI assistant helping users understand
Jainism based on a specific knowledge base and your general training.

Your mission is to provide an accurate, respectful, and clear answer.

Follow these steps:
1. First, look for the answer *only* within the provided CONTEXT.
2. If the answer is clearly found in the CONTEXT, base your entire answer on that CONTEXT.
3. If the answer is *not* found in the CONTEXT, then answer the question using your general knowledge of Jainism.

CONTEXT:
{context}"""

        # Prepare messages for the API
        messages = [
            {
                "role": "system",
                "content": system_prompt.format(context=context)
            },
            {
                "role": "user", 
                "content": question
            }
        ]
        
        # Call Bytez API
        error, output = call_bytez_api(messages)
        
        if error:
            return f"Error: {error}", []
        else:
            return output, similar_docs
        
    except Exception as e:
        return f"Error in RAG pipeline: {str(e)}", []

# --- Streamlit App UI ---

# Initialize
initialize_user_session()
check_and_reset_limit()

# --- Header ---
st.title("Welcome to Jain Yuva Bot (JYB)! 🙏")
st.caption(f"✨ Expert on the [`AI-Yashvi` GitHub repository]({REPO_URL}). ✨")
st.markdown(f"""
Ask any questions about its knowledge files!

**🚀 Powered by Bytez - {BYTEZ_MODEL}**
""")

# --- Load Knowledge Base Automatically ---
if st.session_state.vector_store is None:
    with st.spinner("Loading knowledge base... This may take a few minutes."):
        # Load embedding model first
        st.session_state.embedding_model = load_embedding_model()
        if not st.session_state.embedding_model:
            st.error("Failed to load embedding model. The app cannot start.")
            st.stop()
        
        # Load repository and build vector store
        index, text_chunks, chunk_metadata = load_repo_and_build_store()
        if index is not None:
            st.session_state.vector_store = {
                'index': index,
                'text_chunks': text_chunks,
                'chunk_metadata': chunk_metadata
            }
            st.success(f"✅ Knowledge base loaded successfully! ({len(text_chunks)} chunks)")
        else:
            st.error("Failed to load the knowledge base. The app cannot start.")
            st.stop()

# --- Chat UI ---
chat_container = st.container(border=True)

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Place info and chat input
remaining = get_remaining_questions()
st.info(f"**Note:** You can ask up to **{remaining}** more question(s) today. Your daily limit resets at midnight IST.")

# Chat input
if prompt := st.chat_input("Ask your question..."):
    
    if st.session_state.question_count >= 5:
        st.warning("You have reached your daily limit of 5 questions. Please come back tomorrow!")
    else:
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in the container
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Show a spinner
        with st.spinner("JYB is thinking..."):
            try:
                # Get RAG response using Bytez
                vector_data = st.session_state.vector_store
                bot_response, source_docs = get_rag_response(
                    prompt, 
                    vector_data['index'], 
                    vector_data['text_chunks'], 
                    vector_data['chunk_metadata']
                )
                
                # Add bot response to session state
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                # Display bot response in the container
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(bot_response)
                        
                        # Display sources if available
                        if source_docs:
                            with st.expander("📁 Sources from Repository"):
                                for doc in source_docs:
                                    st.info(f"**File:** `{doc['metadata']['source']}` (Relevance: {doc['score']:.3f})")
                                    st.code(doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'])
                
                # Increment the question count
                st.session_state.question_count += 1
                # Rerun to update the "remaining" count
                st.rerun()

            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(error_msg)
