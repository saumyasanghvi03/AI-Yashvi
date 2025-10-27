import streamlit as st
from datetime import datetime
import pytz
import tempfile
import os
import shutil
from git import Repo
import glob
import re

# --- Bytez SDK Import ---
try:
    from bytez import Bytez
except ImportError:
    st.error("Bytez package not installed. Please install it with: pip install bytez")
    st.stop()

# --- Configuration ---
st.set_page_config(page_title="JainQuest", page_icon="🙏")

# --- Hard-coded Repo URL ---
REPO_URL = "https://github.com/saumyasanghvi03/AI-Yashvi/"

# --- Bytez Configuration ---
BYTEZ_API_KEY = "90d252f09c55cacf3dcc914b5bb4ac01"

# --- Rate Limiting Logic ---
IST = pytz.timezone('Asia/Kolkata')
DAILY_QUESTION_LIMIT = 10

def initialize_user_session():
    """Initializes session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to JainQuest! 🙏\n\nEmbark on a journey through Jain philosophy. I can help you explore core concepts, ethical frameworks, cosmology, spiritual practices, and scriptural wisdom."}
        ]
    
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    
    if "last_reset_date" not in st.session_state:
        st.session_state.last_reset_date = datetime.now(IST).date()
    
    if "repo_content" not in st.session_state:
        st.session_state.repo_content = None
    
    if "bytez_model" not in st.session_state:
        st.session_state.bytez_model = None

def check_and_reset_limit():
    """Checks if the day has changed (midnight IST) and resets the limit."""
    today_ist = datetime.now(IST).date()
    
    if st.session_state.last_reset_date < today_ist:
        st.session_state.question_count = 0
        st.session_state.last_reset_date = today_ist
        st.success("🎉 Your daily question limit has been reset! You can ask up to 10 questions today.")

def get_remaining_questions():
    """Returns the number of questions remaining."""
    return DAILY_QUESTION_LIMIT - st.session_state.question_count

def initialize_bytez_model():
    """Initialize Bytez SDK and model with fallback options."""
    try:
        # Initialize SDK
        sdk = Bytez(BYTEZ_API_KEY)
        
        # Try Qwen model first
        try:
            model = sdk.model("Qwen/Qwen3-4B-Instruct-2507")
            return model
        except Exception as qwen_error:
            # Fallback to Gemma model
            try:
                model = sdk.model("google/gemma-3-4b-it")
                return model
            except Exception as gemma_error:
                return None
                
    except Exception as e:
        st.error(f"Failed to initialize Bytez SDK: {e}")
        return None

def load_repo_content():
    """
    Clones the GitHub repo and loads text files.
    Returns a list of documents with metadata.
    """
    try:
        with st.spinner("🔄 Loading knowledge base..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                Repo.clone_from(REPO_URL, temp_dir)
                
                # Find all text files
                documents = []
                
                # Define file patterns to search for
                patterns = ['**/*.txt', '**/*.md', '**/*.py', '**/*.rst', '**/*.json', '**/*.yaml', '**/*.yml']
                
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
                                        'file_size': len(content)
                                    })
                        except Exception:
                            continue  # Skip files that can't be read

                if not documents:
                    st.error("No compatible documents found in this repository.")
                    return None

                return documents

    except Exception as e:
        st.error(f"Error loading repository: {e}")
        return None

def search_in_repo(query, documents, max_results=5):
    """Enhanced keyword search in repository documents."""
    try:
        query_lower = query.lower().strip()
        if not query_lower:
            return []
            
        results = []
        
        for doc in documents:
            content_lower = doc['content'].lower()
            source_lower = doc['source'].lower()
            
            # Score based on different criteria
            score = 0
            
            # 1. Exact phrase match in content (highest priority)
            if query_lower in content_lower:
                score += 10
                # Find the best matching snippet
                index = content_lower.find(query_lower)
                start = max(0, index - 150)
                end = min(len(doc['content']), index + len(query) + 150)
                snippet = doc['content'][start:end]
                
            # 2. File name match
            elif query_lower in source_lower:
                score += 8
                snippet = doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content']
                
            # 3. Individual word matches
            else:
                query_words = set(re.findall(r'\w+', query_lower))
                content_words = set(re.findall(r'\w+', content_lower))
                common_words = query_words.intersection(content_words)
                
                if common_words:
                    score = len(common_words) / len(query_words) * 6
                    snippet = doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content']
                else:
                    continue  # No matches, skip this document
            
            if score > 0:
                results.append({
                    'source': doc['source'],
                    'content': snippet,
                    'score': score,
                    'file_size': doc['file_size']
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
        
    except Exception as e:
        st.error(f"Error searching documents: {e}")
        return []

def call_bytez_model(model, messages):
    """
    Calls the Bytez model using the official SDK.
    """
    try:
        # Call the model using the SDK
        output, error = model.run(messages)
        
        if error:
            return f"Model Error: {error}", None
        else:
            return None, output
            
    except Exception as e:
        return f"Exception calling model: {str(e)}", None

def refine_answer_format(answer):
    """
    Refines the answer format to ensure proper structure and markdown formatting.
    """
    # Fix for the error: ensure answer is a string before processing
    if not isinstance(answer, str):
        return str(answer)
    
    # Clean up common formatting issues
    refined = answer.strip()
    
    # Ensure proper markdown headers
    refined = re.sub(r'^(\d+\.)\s*', r'## \1 ', refined, flags=re.MULTILINE)
    refined = re.sub(r'^(###?\s+.+)$', r'\1\n', refined, flags=re.MULTILINE)
    
    # Ensure bullet points are properly formatted
    refined = re.sub(r'^-\s*', '- ', refined, flags=re.MULTILINE)
    refined = re.sub(r'^\*\s*', '- ', refined, flags=re.MULTILINE)
    
    # Add spacing between sections
    refined = re.sub(r'\n(## )', r'\n\n\1', refined)
    
    return refined

def detect_question_quality(question):
    """
    Detects if the question is well-structured and comprehensive.
    Returns a quality score and suggestions for improvement.
    """
    quality_score = 0
    suggestions = []
    
    # Check question length
    if len(question.split()) >= 5:
        quality_score += 1
    else:
        suggestions.append("Try asking more detailed questions for better answers")
    
    # Check for specific question words
    question_words = ['what', 'how', 'why', 'explain', 'describe', 'compare', 'difference']
    if any(word in question.lower() for word in question_words):
        quality_score += 1
    else:
        suggestions.append("Use question words like 'what', 'how', or 'why' for clearer answers")
    
    # Check for context or specificity
    if any(word in question.lower() for word in ['jain', 'philosophy', 'concept', 'principle']):
        quality_score += 1
    
    return quality_score, suggestions

def get_ai_response(question, documents, bytez_model):
    """
    Gets relevant context and calls Bytez model for response.
    """
    try:
        # Analyze question quality
        quality_score, suggestions = detect_question_quality(question)
        
        # Search for relevant documents
        relevant_docs = search_in_repo(question, documents, max_results=3)
        
        # Combine context from relevant documents
        context = "\n\n".join([doc['content'] for doc in relevant_docs])
        
        # Enhanced system prompt for refined answers
        base_prompt = """You are JainQuest, an AI assistant with deep expertise in Jainism.

YOUR RESPONSE FORMAT REQUIREMENTS:
- Use proper Markdown formatting with headers (##, ###)
- Structure your answer with clear, logical sections
- Include bullet points for lists and key points
- Use **bold** for important terms and concepts
- Provide comprehensive coverage of the topic
- Include practical applications and contemporary relevance
- Conclude with a summary or key takeaways
- Use emojis sparingly for visual organization (🌍, 📚, 🙏, etc.)

IMPORTANT: Your answer should be well-structured, comprehensive, and academically rigorous while remaining accessible."""

        if context.strip():
            system_prompt = f"""{base_prompt}

CONTEXT FROM REPOSITORY:
{context}

INSTRUCTIONS:
1. FIRST prioritize information from the CONTEXT above
2. If CONTEXT is insufficient, supplement with your comprehensive knowledge
3. Structure your answer with these typical sections:
   - ## Core Concept & Definition
   - ## Detailed Explanation
   - ## Key Principles & Components
   - ## Scriptural References & Sources
   - ## Practical Applications
   - ## Contemporary Relevance
   - ## Summary & Key Takeaways

QUESTION: {question}

Provide a comprehensive, well-structured answer:"""
        else:
            system_prompt = f"""{base_prompt}

QUESTION: {question}

INSTRUCTIONS:
1. Provide a comprehensive answer using your deep knowledge of Jainism
2. Structure your answer with these typical sections:
   - ## Core Concept & Definition
   - ## Detailed Explanation  
   - ## Key Principles & Components
   - ## Scriptural References & Sources
   - ## Practical Applications
   - ## Contemporary Relevance
   - ## Summary & Key Takeaways

Provide a comprehensive, well-structured answer:"""

        # Add quality-based enhancements for good questions
        if quality_score >= 2:
            system_prompt += "\n\nADDITIONAL NOTE: This appears to be a well-structured question. Please provide an especially detailed and comprehensive answer with deeper insights and practical applications."

        # Prepare messages for the model
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": question
            }
        ]
        
        # Call Bytez model
        error, output = call_bytez_model(bytez_model, messages)
        
        if error:
            return f"Error: {error}", relevant_docs, suggestions
        elif output:
            # Refine the answer format
            refined_output = refine_answer_format(output)
            return refined_output, relevant_docs, suggestions
        else:
            return "No response received from the AI model.", relevant_docs, suggestions
        
    except Exception as e:
        return f"Error processing your question: {str(e)}", [], []

# --- Streamlit App UI ---

# Initialize
initialize_user_session()
check_and_reset_limit()

# --- Header ---
st.title("Welcome to JainQuest! 🙏")
st.markdown("""
**Embark on a journey through Jain philosophy**

I can help you explore:

**📚 Core Knowledge Areas:**
- **Jain Philosophy**: Six Substances, Nine Truths, Anekantavada
- **Ethical Framework**: Five Vows, Three Jewels, Spiritual Stages  
- **Cosmology**: Three Lokas, Jambudweep, Time Cycles
- **Spiritual Practices**: Meditation, Rituals, Path to Liberation
- **Scriptural Wisdom**: Agamas, Tattvartha Sutra, Kalpa Sutra
- **Historical Context**: Tirthankaras, Traditions, Modern Applications

**📄 Supported Repository Formats**: .txt, .md, .py, .rst, .json, .yaml, .yml

Ask me anything about Jain philosophy, concepts, or practices!
""")

# --- Initialize Bytez Model ---
if st.session_state.bytez_model is None:
    with st.spinner("🔌 Connecting to AI model..."):
        bytez_model = initialize_bytez_model()
        if bytez_model is not None:
            st.session_state.bytez_model = bytez_model
        else:
            st.error("❌ Failed to connect to AI models. The app cannot start.")
            st.stop()

# --- Load Repository Content ---
if st.session_state.repo_content is None:
    with st.spinner("📚 Loading knowledge base..."):
        repo_content = load_repo_content()
        if repo_content is not None:
            st.session_state.repo_content = repo_content
        else:
            st.error("❌ Failed to load the knowledge base.")
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
if prompt := st.chat_input("Ask your question about Jainism..."):
    
    if st.session_state.question_count >= DAILY_QUESTION_LIMIT:
        st.warning(f"🚫 You have reached your daily limit of {DAILY_QUESTION_LIMIT} questions. Please come back tomorrow!")
    else:
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in the container
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Show a spinner
        with st.spinner("🤔 JainQuest is thinking..."):
            try:
                # Get AI response using Bytez
                bot_response, source_docs, suggestions = get_ai_response(
                    prompt, 
                    st.session_state.repo_content, 
                    st.session_state.bytez_model
                )
                
                # Add bot response to session state
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                # Display bot response in the container
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(bot_response)
                        
                        # Show question quality feedback for good questions
                        if len(suggestions) == 0:
                            st.success("🌟 Great question! You received a comprehensive answer.")
                        
                        # Display sources if available
                        if source_docs:
                            with st.expander("📁 Sources from Knowledge Base"):
                                for doc in source_docs:
                                    st.info(f"**File:** `{doc['source']}` (Relevance: {doc['score']:.2f})")
                                    content_preview = doc['content']
                                    if len(content_preview) > 500:
                                        content_preview = content_preview[:500] + "..."
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
st.markdown("**Powered by Digital Jain Pathshala, made by Saumya Sanghvi: [https://linkedin.com/in/ssanghvi03](https://linkedin.com/in/ssanghvi03)**")
