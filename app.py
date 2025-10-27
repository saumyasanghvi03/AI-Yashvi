import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
import tempfile
import os
import shutil
from git import Repo
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# --- Configuration ---
st.set_page_config(page_title="Jain Yuva Bot (RAG)", page_icon="🙏")

# --- API Key Setup ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    st.error("GEMINI_API_KEY not found in Streamlit secrets. Please add it.")
    st.stop()
except Exception:
    st.info("API Key not configured. Add your Google AI Studio API key to Streamlit secrets to run the app.")
    st.stop()

# --- Rate Limiting Logic (Unchanged) ---
IST = pytz.timezone('Asia/Kolkata')

def initialize_user_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "last_reset_date" not in st.session_state:
        st.session_state.last_reset_date = datetime.now(IST).date()
    # Add session state for RAG components
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None
    if "repo_url" not in st.session_state:
        st.session_state.repo_url = ""

def check_and_reset_limit():
    today_ist = datetime.now(IST).date()
    if st.session_state.last_reset_date < today_ist:
        st.session_state.question_count = 0
        st.session_state.last_reset_date = today_ist
        st.info("Your daily question limit has been reset. You can ask up to 5 questions.")

def get_remaining_questions():
    return 5 - st.session_state.question_count

# --- RAG Functions ---

@st.cache_resource(show_spinner="Loading repository content...")
def load_repo_and_build_store(repo_url):
    """
    Clones a GitHub repo, loads its text files, splits them,
    creates embeddings, and returns a FAISS vector store.
    """
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            st.write(f"Cloning {repo_url} into {temp_dir}...")
            # Clone the repo
            Repo.clone_from(repo_url, temp_dir)
            
            # Load documents (only .txt, .md, .py)
            st.write("Loading documents...")
            loader = DirectoryLoader(
                temp_dir,
                glob="**/*[.txt,.md,.py,.rst]",  # Load these file types
                loader_cls=TextLoader,
                use_multithreading=True,
                show_progress=True,
                silent_errors=True # Ignore files it can't read
            )
            documents = loader.load()

            if not documents:
                st.error("No compatible documents (.txt, .md, .py, .rst) found in this repository.")
                return None

            st.write(f"Loaded {len(documents)} documents.")
            
            # Split documents into chunks
            st.write("Splitting documents into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            st.write(f"Created {len(texts)} text chunks.")
            
            # Create embeddings
            st.write("Creating embeddings...")
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
            
            # Create FAISS vector store
            st.write("Building vector store... (This may take a moment)")
            vector_store = FAISS.from_documents(texts, embeddings)
            
            st.write("Vector store built successfully!")
            return vector_store

    except Exception as e:
        st.error(f"Error loading repository: {e}")
        return None

def create_qa_chain(vector_store):
    """Creates the RAG query chain."""
    
    # The "brain" for the RAG chain
    llm = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
    )
    
    # We use a custom prompt to combine the Jain Bot persona with RAG instructions
    prompt_template = """
    You are Jain Yuva Bot (JYB), an AI assistant helping users understand
    Jainism based on a specific knowledge base.
    
    Your mission is to provide accurate, respectful, and clear answers based *only*
    on the provided context from the GitHub repository.
    
    If the answer is not found in the context, clearly state that the 
    information is not available in the provided repository.
    
    CONTEXT:
    {context}
    
    QUESTION:
    {question}
    
    ANSWER:
    """
    
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    
    # Create the chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=genai.GenerativeModel('gemini-pro'), # Using gemini-pro for QA
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}), # Get top 4 results
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    return qa_chain

# --- Streamlit App UI ---

# Initialize
initialize_user_session()
check_and_reset_limit()

# --- Header (Unchanged) ---
st.title("Welcome to Jain Yuva Bot (JYB)! 🙏")
st.caption("✨ Bringing Sacred Knowledge to Life with AI ✨")
st.markdown("""
Ask questions about Jainism. You can also load a GitHub repository 
to ask questions specifically about its content.
""")

# --- GitHub Repo Input ---
st.divider()
st.subheader("Load Knowledge from GitHub")
st.write("Paste a public GitHub repo URL to make the bot an expert on its content.")

repo_url_input = st.text_input(
    "GitHub Repository URL", 
    value=st.session_state.repo_url,
    placeholder="https://github.com/user/repo-name"
)

if st.button("Load Repository"):
    if repo_url_input:
        st.session_state.repo_url = repo_url_input
        # This will cache the result
        vector_store = load_repo_and_build_store(st.session_state.repo_url)
        
        if vector_store:
            st.session_state.vector_store = vector_store
            st.session_state.qa_chain = create_qa_chain(vector_store)
            st.success(f"Successfully loaded repository! You can now ask questions about it.")
            st.rerun() # Rerun to update state
    else:
        st.warning("Please enter a valid GitHub URL.")

if st.session_state.qa_chain:
    st.success(f"Repository loaded: {st.session_state.repo_url}")
    if st.button("Clear Repository Knowledge"):
        st.session_state.vector_store = None
        st.session_state.qa_chain = None
        st.session_state.repo_url = ""
        st.rerun()
else:
    st.info("No repository loaded. Bot will use its general knowledge.")

st.divider()

# --- Chat UI ---
st.subheader("Chat with JYB")
remaining = get_remaining_questions()
st.info(f"**Note:** You can ask up to **{remaining}** more question(s) today. Your daily limit resets at midnight IST.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask your question..."):
    
    if st.session_state.question_count >= 5:
        st.warning("You have reached your daily limit of 5 questions. Please come back tomorrow!")
    else:
        # Add user message to session state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Show a spinner
        with st.spinner("JYB is thinking..."):
            try:
                bot_response = ""
                # --- RAG Logic ---
                if st.session_state.qa_chain:
                    # If repo is loaded, use the RAG chain
                    st.write("Searching repository knowledge...")
                    response_data = st.session_state.qa_chain({"query": prompt})
                    bot_response = response_data["result"]
                    
                    # Optional: Display sources
                    with st.expander("Show Sources from Repository"):
                        for doc in response_data["source_documents"]:
                            st.info(f"Source: `{doc.metadata['source']}` (snippet)")
                            st.code(doc.page_content[:500] + "...")
                
                else:
                    # --- General Knowledge Logic (Original) ---
                    # If no repo, use the general model
                    # We create a simple chat history for context
                    if "chat_session" not in st.session_state:
                         model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
                         st.session_state.chat_session = model.start_chat(history=[])
                         
                    response = st.session_state.chat_session.send_message(prompt)
                    bot_response = response.text
                
                # Add bot response to session state and display it
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                with st.chat_message("assistant"):
                    st.markdown(bot_response)
                
                # Increment the question count
                st.session_state.question_count += 1
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")
