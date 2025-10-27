import streamlit as st
from datetime import datetime
import pytz
import tempfile
import os
import shutil
from git import Repo
import requests
import json
import glob
import re

# --- Configuration ---
st.set_page_config(page_title="Jain Yuva Bot", page_icon="🙏")

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
    
    if "knowledge_base" not in st.session_state:
        st.session_state.knowledge_base = None

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

def load_repo_content():
    """
    Clones the GitHub repo and loads text files.
    Returns a list of documents with metadata.
    """
    try:
        progress_bar = st.progress(0, text="Initializing...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_bar.progress(5, text=f"Cloning {REPO_URL}...")
            Repo.clone_from(REPO_URL, temp_dir)
            
            progress_bar.progress(20, text="Loading documents from repo...")
            
            # Find all text files
            documents = []
            
            # Define file patterns to search for
            patterns = ['**/*.txt', '**/*.md', '**/*.py', '**/*.rst', '**/*.json']
            
            for pattern in patterns:
                for file_path in glob.glob(os.path.join(temp_dir, pattern), recursive=True):
                    try:
                        # Skip hidden files and directories
                        if os.path.basename(file_path).startswith('.'):
                            continue
                            
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.strip():  # Only add non-empty files
                                # Get relative path for display
                                rel_path = os.path.relpath(file_path, temp_dir)
                                documents.append({
                                    'source': rel_path,
                                    'content': content,
                                    'chunks': []
                                })
                    except Exception as e:
                        continue  # Skip files that can't be read

            if not documents:
                st.error("No compatible documents found in this repository.")
                return None

            progress_bar.progress(40, text=f"Loaded {len(documents)} documents. Processing...")
            
            # Split documents into chunks
            all_chunks = []
            chunk_metadata = []
            
            for doc in documents:
                content = doc['content']
                # Simple chunking by character count
                chunk_size = 1000
                chunk_overlap = 200
                
                chunks = []
                for i in range(0, len(content), chunk_size - chunk_overlap):
                    chunk = content[i:i + chunk_size]
                    if len(chunk.strip()) > 50:  # Only add substantial chunks
                        chunks.append(chunk)
                        all_chunks.append(chunk)
                        chunk_metadata.append({
                            'source': doc['source'],
                            'content': chunk,
                            'chunk_id': len(all_chunks)
                        })
                
                doc['chunks'] = chunks

            progress_bar.progress(100, text="Knowledge base loaded successfully!")
            progress_bar.empty()
            
            return {
                'documents': documents,
                'all_chunks': all_chunks,
                'chunk_metadata': chunk_metadata
            }

    except Exception as e:
        st.error(f"Error loading repository: {e}")
        return None

def search_keyword_documents(query, knowledge_base, k=4):
    """Search for documents using keyword matching."""
    try:
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        results = []
        
        for idx, chunk in enumerate(knowledge_base['all_chunks']):
            chunk_lower = chunk.lower()
            
            # Calculate simple keyword match score
            matches = sum(1 for word in query_words if word in chunk_lower)
            if matches > 0:
                score = matches / len(query_words) if query_words else 0
                results.append({
                    'content': chunk,
                    'metadata': knowledge_base['chunk_metadata'][idx],
                    'score': score
                })
        
        # Sort by score and return top k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]
        
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

def get_rag_response(question, knowledge_base):
    """
    Gets relevant context and calls Bytez API for response.
    """
    try:
        # Search for similar documents using keyword matching
        similar_docs = search_keyword_documents(question, knowledge_base, k=4)
        
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
            return f"Error: {error}", similar_docs
        elif output:
            return output, similar_docs
        else:
            return "No response received from the AI model.", similar_docs
        
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
if st.session_state.knowledge_base is None:
    with st.spinner("Loading knowledge base... This may take a few minutes."):
        # Load repository content
        knowledge_base = load_repo_content()
        if knowledge_base is not None:
            st.session_state.knowledge_base = knowledge_base
            st.success(f"✅ Knowledge base loaded successfully! ({len(knowledge_base['all_chunks'])} chunks from repository)")
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
                bot_response, source_docs = get_rag_response(prompt, st.session_state.knowledge_base)
                
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
                                    content_preview = doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content']
                                    st.code(content_preview)
                
                # Increment the question count
                st.session_state.question_count += 1
                # Rerun to update the "remaining" count
                st.rerun()

            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": "I encountered an error while processing your question. Please try again."})
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown("I encountered an error while processing your question. Please try again.")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ for the Jain community | Powered by [Bytez](https://bytez.com/)")
