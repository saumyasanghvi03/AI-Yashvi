# app.py

import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
import tempfile
import os
import shutil
from git import Repo
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter  # ✅ FIXED IMPORT
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
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
    st.error("❌ GEMINI_API_KEY not found in Streamlit secrets. Please add it under 'Secrets' in Streamlit Cloud.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error configuring Gemini API: {e}")
    st.stop()

# --- Rate Limiting Logic ---
IST = pytz.timezone('Asia/Kolkata')

def initialize_user_session():
    """Initializes session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "🙏 Welcome to **Jain Yuva Bot (JYB)**!\n\n"
                    "I’m an expert on the [AI-Yashvi repository](https://github.com/saumyasanghvi03/AI-Yashvi/). "
                    "Ask me anything about its content or general Jainism topics."
                )
            }
        ]
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "last_reset_date" not in st.session_state:
        st.session_state.last_reset_date = datetime.now(IST).date()
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None

def check_and_reset_limit():
    """Resets question count at midnight IST."""
    today_ist = datetime.now(IST).date()
    if st.session_state.last_reset_date < today_ist:
        st.session_state.question_count = 0
        st.session_state.last_reset_date = today_ist
        st.info("✅ Daily question limit reset. You can ask up to 5 questions.")

def get_remaining_questions():
    return max(0, 5 - st.session_state.question_count)

# --- RAG Functions ---

@st.cache_resource(show_spinner=False)
def load_repo_and_build_store():
    """
    Clones repo, loads documents, splits them, creates embeddings with HuggingFace,
    and returns FAISS vector store. Uses manual progress bar.
    """
    try:
        progress_bar = st.progress(0, text="Initializing...")

        with tempfile.TemporaryDirectory() as temp_dir:
            progress_bar.progress(10, text=f"Cloning repository from {REPO_URL}...")
            Repo.clone_from(REPO_URL, temp_dir)

            progress_bar.progress(25, text="Loading documents (.txt, .md, .py, .rst)...")
            loader = DirectoryLoader(
                temp_dir,
                glob="**/*[.txt,.md,.py,.rst]",
                loader_cls=TextLoader,
                use_multithreading=True,
                silent_errors=True
            )
            documents = loader.load()

            if not documents:
                st.error("No compatible documents found in repository.")
                progress_bar.empty()
                return None

            progress_bar.progress(40, text=f"Loaded {len(documents)} documents. Splitting into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)

            progress_bar.progress(60, text=f"Creating embeddings for {len(texts)} chunks...")
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

            progress_bar.progress(80, text="Building FAISS vector store...")
            vector_store = FAISS.from_documents(texts, embeddings)

            progress_bar.progress(100, text="✅ Knowledge base ready!")
            progress_bar.empty()

            return vector_store

    except Exception as e:
        st.error(f"Error building knowledge base: {e}")
        return None

def create_qa_chain(vector_store):
    """Creates RetrievalQA chain using Gemini LLM and custom prompt."""
    try:
        # Use a newer/faster Gemini model if available
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Faster & cheaper than 1.5-pro
            google_api_key=GEMINI_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )

        prompt_template = """
You are Jain Yuva Bot (JYB), a respectful and knowledgeable assistant on Jainism and the AI-Yashvi repository.

Answer the question using ONLY the context below if it contains relevant information.
If the context does NOT contain the answer, use your general knowledge of Jainism to respond accurately.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

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
        return None

# --- Streamlit UI ---

initialize_user_session()
check_and_reset_limit()

st.title("🙏 Jain Yuva Bot (JYB)")
st.caption(f"Expert on the [AI-Yashvi Repository]({REPO_URL})")
st.markdown("Ask any question about Jainism or the repository content!")

# Auto-load knowledge base
if st.session_state.qa_chain is None:
    with st.spinner("🧠 Loading knowledge base..."):
        vector_store = load_repo_and_build_store()
        if vector_store:
            st.session_state.qa_chain = create_qa_chain(vector_store)
        else:
            st.error("❌ Failed to load knowledge base. App cannot proceed.")
            st.stop()

# Display chat history
chat_container = st.container(border=True)
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Show remaining questions
remaining = get_remaining_questions()
st.info(f"📝 You have **{remaining}** question(s) left today. Resets at midnight IST.")

# Handle user input
if prompt := st.chat_input("Type your question here..."):
    if st.session_state.question_count >= 5:
        st.warning("⏳ Daily limit reached. Please come back tomorrow!")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Generate bot response
        with st.spinner("🤔 JYB is thinking..."):
            try:
                response_data = st.session_state.qa_chain.invoke({"query": prompt})
                bot_response = response_data["result"]

                # Add & display assistant response
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(bot_response)
                        with st.expander("📚 View Source Snippets"):
                            for i, doc in enumerate(response_data["source_documents"], 1):
                                source_path = doc.metadata.get('source', 'Unknown')
                                # Clean up path for display (remove temp dir prefix)
                                display_source = source_path.split('/')[-1] if '/' in source_path else source_path
                                st.markdown(f"**Source {i}:** `{display_source}`")
                                st.code(doc.page_content[:300] + "...")

                st.session_state.question_count += 1
                st.rerun()  # Refresh to update counter and clear input

            except Exception as e:
                error_msg = f"❌ Error generating response: {e}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                with chat_container:
                    with st.chat_message("assistant"):
                        st.error(error_msg)
