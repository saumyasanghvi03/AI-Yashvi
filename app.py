import streamlit as st
from datetime import datetime
import pytz
import tempfile
import os
import shutil
from git import Repo
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# --- COMPLETELY FREE/LOCAL IMPORTS ---
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
# --- END FREE IMPORTS ---

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# --- Configuration ---
st.set_page_config(page_title="Jain Yuva Bot (RAG)", page_icon="🙏")

# --- Hard-coded Repo URL ---
REPO_URL = "https://github.com/saumyasanghvi03/AI-Yashvi/"

# --- Rate Limiting Logic (Unchanged) ---
IST = pytz.timezone('Asia/Kolkata')

def initialize_user_session():
    """Initializes session state variables if they don't exist."""
    if "messages" not in st.session_state:
        # Add a welcome message to start the chat
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to Jain Yuva Bot (JYB)! 🙏\n\nI'm an expert on the AI-Yashvi repository. Ask me anything about its content, or general questions about Jainism.\n\n*Running completely locally with free models!*"}
        ]
    
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    
    if "last_reset_date" not in st.session_state:
        st.session_state.last_reset_date = datetime.now(IST).date()
    
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None

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
        # Create a progress bar
        progress_bar = st.progress(0, text="Initializing...")
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_bar.progress(5, text=f"Cloning {REPO_URL}...")
            Repo.clone_from(REPO_URL, temp_dir)
            
            # Load documents
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
            
            # Create FAISS vector store
            progress_bar.progress(80, text="Building vector store... (This may take a moment)")
            vector_store = FAISS.from_documents(texts, embeddings)
            
            progress_bar.progress(100, text="Knowledge base loaded successfully!")
            progress_bar.empty()
            
            return vector_store

    except Exception as e:
        st.error(f"Error loading repository: {e}")
        return None

def create_qa_chain(vector_store):
    """Creates the RAG query chain using local LLM."""
    try:
        # Use Ollama with a free local model
        # Make sure you have Ollama installed and the model downloaded
        # You can install Ollama from: https://ollama.ai/
        # Then run: ollama pull llama2 (or any other model)
        
        llm = Ollama(
            model="llama2",  # or "mistral", "codellama", "llama2:13b", etc.
            temperature=0.3
        )
        
        # Alternative: If you want to use a different local model, you can use:
        # from langchain_community.llms import HuggingFacePipeline
        # from transformers import pipeline
        #
        # pipe = pipeline(
        #     "text-generation",
        #     model="HuggingFaceH4/zephyr-7b-beta",  # or any other model
        #     temperature=0.3,
        #     max_new_tokens=500
        # )
        # llm = HuggingFacePipeline(pipeline=pipe)
        
        # Custom prompt for Jain Bot
        prompt_template = """
        You are Jain Yuva Bot (JYB), an AI assistant helping users understand
        Jainism based on a specific knowledge base and your general training.
        
        Your mission is to provide an accurate, respectful, and clear answer.
        
        Follow these steps:
        1. First, look for the answer *only* within the provided CONTEXT.
        2. If the answer is clearly found in the CONTEXT, base your entire answer on that CONTEXT.
        3. If the answer is *not* found in the CONTEXT, then answer the question using your general knowledge of Jainism.
        
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
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        return qa_chain
    except Exception as e:
        st.error(f"Error creating QA chain: {e}")
        st.info("Make sure you have Ollama installed and running. Visit https://ollama.ai/ for installation instructions.")
        return None

# --- Streamlit App UI ---

# Initialize
initialize_user_session()
check_and_reset_limit()

# --- Header ---
st.title("Welcome to Jain Yuva Bot (JYB)! 🙏")
st.caption(f"✨ Expert on the [`AI-Yashvi` GitHub repository]({REPO_URL}). ✨")
st.markdown("""
Ask any questions about its knowledge files!

**🔒 Completely local and free - no API keys required!**
""")

# --- Load Knowledge Base Automatically ---
if "qa_chain" not in st.session_state or st.session_state.qa_chain is None:
    vector_store = load_repo_and_build_store()
    if vector_store:
        st.session_state.qa_chain = create_qa_chain(vector_store)
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
        with st.spinner("JYB is thinking (running locally...)..."):
            try:
                bot_response = ""
                
                # --- RAG Logic ---
                if st.session_state.qa_chain:
                    response_data = st.session_state.qa_chain.invoke({"query": prompt})
                    bot_response = response_data["result"]
                    
                    # Add bot response to session state
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                    # Display bot response in the container
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.markdown(bot_response)
                            # Optional: Display sources
                            with st.expander("Show Sources from Repository"):
                                for doc in response_data["source_documents"]:
                                    st.info(f"Source: `{doc.metadata['source']}` (snippet)")
                                    st.code(doc.page_content[:500] + "...")
                
                else:
                    bot_response = "Error: The question-answering chain is not loaded. Please reload the app."
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.markdown(bot_response)

                # Increment the question count
                st.session_state.question_count += 1
                # Rerun to update the "remaining" count
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")
