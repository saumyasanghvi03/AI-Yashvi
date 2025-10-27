import streamlit as st
from datetime import datetime
import pytz
import tempfile
import os
import shutil
from git import Repo
import requests
import json

# --- LangChain imports for document processing ---
try:
    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    st.error("Required LangChain components not found. Please check the requirements.")
    st.stop()

# --- Configuration ---
st.set_page_config(page_title="Jain Yuva Bot (RAG)", page_icon="🙏")

# --- Hard-coded Repo URL ---
REPO_URL = "https://github.com/saumyasanghvi03/AI-Yashvi/"

# --- Bytez API Configuration ---
# Based on your JavaScript example
BYTEZ_API_KEY = "90d252f09c55cacf3dcc914b5bb4ac01"  # Using the key from your example
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

# --- RAG Functions ---

@st.cache_resource()
def load_repo_and_build_store():
    """
    Clones the hard-coded GitHub repo, loads its text files, splits them,
    creates embeddings using a local model, and returns a FAISS vector store.
    """
    try:
        progress_bar = st.progress(0, text="Initializing...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_bar.progress(5, text=f"Cloning {REPO_URL}...")
            Repo.clone_from(REPO_URL, temp_dir)
            
            progress_bar.progress(20, text="Loading documents from repo...")
            loader = DirectoryLoader(
                temp_dir,
                glob="**/*[.txt,.md,.py,.rst]",
                loader_cls=TextLoader,
                use_multithreading=True,
                show_progress=False,
                silent_errors=True
            )
            documents = loader.load()

            if not documents:
                st.error("No compatible documents (.txt, .md, .py, .rst) found in this repository.")
                return None

            progress_bar.progress(40, text=f"Loaded {len(documents)} documents. Splitting...")
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            progress_bar.progress(60, text=f"Created {len(texts)} text chunks. Creating embeddings...")
            
            # Use a free, local model from HuggingFace for embeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            progress_bar.progress(80, text="Building vector store... (This may take a moment)")
            vector_store = FAISS.from_documents(texts, embeddings)
            
            progress_bar.progress(100, text="Knowledge base loaded successfully!")
            progress_bar.empty()
            
            return vector_store

    except Exception as e:
        st.error(f"Error loading repository: {e}")
        return None

def call_bytez_api(messages):
    """
    Calls the Bytez API based on the JavaScript SDK example.
    
    Args:
        messages: List of message objects with role and content
        
    Returns:
        tuple: (error, output)
    """
    try:
        # Prepare the request payload based on the JavaScript example
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
            timeout=60  # Increased timeout for model inference
        )
        
        if response.status_code == 200:
            result = response.json()
            # Based on the JavaScript example, we expect { error, output }
            error = result.get("error")
            output = result.get("output")
            return error, output
        else:
            return f"HTTP Error: {response.status_code}", None
            
    except Exception as e:
        return f"Error calling Bytez API: {str(e)}", None

def get_rag_response(question, vector_store):
    """
    Gets relevant context from vector store and calls Bytez API for response.
    """
    try:
        # Get relevant documents from vector store
        relevant_docs = vector_store.similarity_search(question, k=4)
        
        # Combine context from relevant documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
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
            return output, relevant_docs
        
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
        vector_store = load_repo_and_build_store()
        if vector_store:
            st.session_state.vector_store = vector_store
            st.success("Knowledge base loaded successfully!")
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
                bot_response, source_docs = get_rag_response(prompt, st.session_state.vector_store)
                
                # Add bot response to session state
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                # Display bot response in the container
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(bot_response)
                        
                        # Display sources if available
                        if source_docs:
                            with st.expander("Show Sources from Repository"):
                                for doc in source_docs:
                                    st.info(f"Source: `{doc.metadata['source']}` (snippet)")
                                    st.code(doc.page_content[:500] + "...")
                
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
