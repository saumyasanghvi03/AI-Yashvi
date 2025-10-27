import streamlit as st
from datetime import datetime
import pytz
import tempfile
import os
import shutil
from git import Repo

# --- Configuration ---
st.set_page_config(page_title="Jain Yuva Bot (RAG)", page_icon="🙏")

# --- Hard-coded Repo URL ---
REPO_URL = "https://github.com/saumyasanghvi03/AI-Yashvi/"

# --- Rate Limiting Logic ---
IST = pytz.timezone('Asia/Kolkata')

def initialize_user_session():
    """Initializes session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to Jain Yuva Bot (JYB)! 🙏\n\nI'm an expert on the AI-Yashvi repository. Ask me anything about its content, or general questions about Jainism.\n\n*Note: Currently in simplified mode - advanced features disabled.*"}
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
    Simple function to load and display repo content without complex LangChain dependencies.
    Returns a dictionary with filename -> content mapping.
    """
    try:
        with st.spinner("Loading repository content..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                Repo.clone_from(REPO_URL, temp_dir)
                
                # Simple file reading without LangChain
                repo_content = {}
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.txt', '.md', '.py', '.rst')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    # Store relative path as key
                                    rel_path = os.path.relpath(file_path, temp_dir)
                                    repo_content[rel_path] = content
                            except Exception as e:
                                st.warning(f"Could not read {file_path}: {e}")
                
                return repo_content
    except Exception as e:
        st.error(f"Error loading repository: {e}")
        return None

def search_in_content(query, repo_content):
    """
    Simple search function to find relevant content in the repository.
    Returns relevant snippets and their sources.
    """
    if not repo_content:
        return []
    
    query_lower = query.lower()
    results = []
    
    for filename, content in repo_content.items():
        content_lower = content.lower()
        if query_lower in content_lower:
            # Find the context around the query
            index = content_lower.find(query_lower)
            start = max(0, index - 200)
            end = min(len(content), index + len(query) + 200)
            snippet = content[start:end]
            
            results.append({
                'source': filename,
                'content': snippet,
                'relevance': 1  # Simple binary relevance
            })
    
    # Also search for individual words if no direct matches
    if not results:
        query_words = query_lower.split()
        for filename, content in repo_content.items():
            content_lower = content.lower()
            word_matches = sum(1 for word in query_words if word in content_lower)
            if word_matches > 0:
                # Take first 500 chars as snippet
                snippet = content[:500] + "..." if len(content) > 500 else content
                results.append({
                    'source': filename,
                    'content': snippet,
                    'relevance': word_matches / len(query_words)
                })
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return results[:3]  # Return top 3 results

def get_ai_response(query, context_snippets):
    """
    Simple AI response using available context.
    In a real implementation, this would use an LLM.
    """
    if not context_snippets:
        return "I couldn't find specific information about this in the repository. Please try asking about general Jain principles or check if your question relates to the content in the AI-Yashvi repository."
    
    # Build context string
    context_str = "\n\n".join([f"From {snippet['source']}:\n{snippet['content']}" for snippet in context_snippets])
    
    # Simple response based on found content
    response = f"Based on the repository content, I found this information:\n\n{context_str}\n\n"
    response += "This is a simplified response. For more detailed answers, please refer to the actual repository files."
    
    return response

# --- Streamlit App UI ---

# Initialize
initialize_user_session()
check_and_reset_limit()

# --- Header ---
st.title("Welcome to Jain Yuva Bot (JYB)! 🙏")
st.caption(f"✨ Expert on the [`AI-Yashvi` GitHub repository]({REPO_URL}). ✨")
st.markdown("""
Ask any questions about its knowledge files!

**🔒 Simplified version - no external dependencies required!**
""")

# --- Load Knowledge Base Automatically ---
if st.session_state.knowledge_base is None:
    repo_content = load_repo_content()
    if repo_content:
        st.session_state.knowledge_base = repo_content
        st.success(f"✅ Loaded {len(repo_content)} files from repository!")
    else:
        st.error("❌ Failed to load the knowledge base. The app cannot start.")
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
        with st.spinner("Searching in repository..."):
            try:
                # Search for relevant content
                context_snippets = search_in_content(prompt, st.session_state.knowledge_base)
                
                # Generate response
                bot_response = get_ai_response(prompt, context_snippets)
                
                # Add bot response to session state
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                # Display bot response in the container
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(bot_response)
                        
                        # Show sources if we found any
                        if context_snippets:
                            with st.expander("📁 Sources from Repository"):
                                for snippet in context_snippets:
                                    st.info(f"**File:** `{snippet['source']}`")
                                    st.code(snippet['content'])
                
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
