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
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# --- Configuration ---
st.set_page_config(page_title="Jain Yuva Bot (RAG)", page_icon="🙏")

# --- Hard-coded Repo URL ---
REPO_URL = "https://github.com/saumyasanghvi03/AI-Yashvi/"

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
    # RAG chain will be stored here
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None

def check_and_reset_limit():
    today_ist = datetime.now(IST).date()
    if st.session_state.last_reset_date < today_ist:
        st.session_state.question_count = 0
        st.session_state.last_reset_date = today_ist
        st.info("Your daily question limit has been reset. You can ask up to 5 questions.")

def get_remaining_questions():
    return 5 - st.session_state.question_count

# --- RAG Functions ---

@st.cache_resource(show_spinner="Loading knowledge from AI-Yashvi repo...")
def load_repo_and_build_store():
    """
    Clones the hard-coded GitHub repo, loads text files, splits them,
    creates embeddings, and returns a FAISS vector store.
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            st.write(f"Cloning {REPO_URL}...")
            Repo.clone_from(REPO_URL, temp_dir)
            
            st.write("Loading documents...")
            loader = DirectoryLoader(
                temp_dir,
                glob="**/*[.txt,.md,.py,.rst]",  # Load specified file types
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
            
            st.write("Splitting documents into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            st.write(f"Created {len(texts)} text chunks.")
            
            st.write("Creating embeddings...")
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
            
            st.write("Building vector store... (This may take a moment)")
            vector_store = FAISS.from_documents(texts, embeddings)
            
            st.success("Knowledge base loaded successfully!")
            return vector_store

    except Exception as e:
        st.error(f"Error loading repository: {e}")
        return None

def create_qa_chain(vector_store):
    """Creates the RAG query chain."""
    try:
        # Use the Langchain wrapper for the Gemini LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=GEMINI_API_KEY,
            temperature=0.3 # Make responses more factual
        )
        
        # We use a custom prompt to combine the Jain Bot persona with RAG instructions
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
            retriever=vector_store.as_retriever(search_kwargs={"k": 4}), # Get top 4 results
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        return qa_chain
    except Exception as e:
        st.error(f"Error creating QA chain: {e}")
        return None

# --- Streamlit App UI ---

# Initialize
initialize_user_session()
check_and_reset_limit()

# --- Header ---
st.title("Welcome to Jain Yuva Bot (JYB)! 🙏")
st.caption("✨ Bringing Sacred Knowledge to Life with AI ✨")
st.markdown(f"""
This bot is an expert on the content found in the
[`AI-Yashvi` GitHub repository]({REPO_URL}).
Ask any questions about its knowledge files!
""")

# --- Load Knowledge Base Automatically ---
if st.session_state.qa_chain is None:
    vector_store = load_repo_and_build_store()
    if vector_store:
        st.session_state.qa_chain = create_qa_chain(vector_store)
    else:
        st.error("Failed to load the knowledge base. The app cannot start.")
        st.stop() # Stop the app if knowledge loading fails

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
        with st.spinner("JYB is searching the knowledge base..."):
            try:
                bot_response = ""
                
                # --- RAG Logic ---
                # We only use the RAG chain now
                if st.session_state.qa_chain:
                    response_data = st.session_state.qa_chain.invoke({"query": prompt})
                    bot_response = response_data["result"]
                    
                    # Optional: Display sources
                    with st.expander("Show Sources from Repository"):
                        for doc in response_data["source_documents"]:
                            st.info(f"Source: `{doc.metadata['source']}` (snippet)")
                            st.code(doc.page_content[:500] + "...")
                
                else:
                    bot_response = "Error: The question-answering chain is not loaded. Please reload the app."

                # Add bot response to session state and display it
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                with st.chat_message("assistant"):
                    st.markdown(bot_response)
                
                # Increment the question count
                st.session_state.question_count += 1
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")


