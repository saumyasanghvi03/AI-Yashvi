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
st.set_page_config(page_title="JainQuest", page_icon="🙏", layout="wide")

# --- Hard-coded Repo URL ---
REPO_URL = "https://github.com/saumyasanghvi03/AI-Yashvi/"

# --- Bytez Configuration ---
BYTEZ_API_KEY = "90d252f09c55cacf3dcc914b5bb4ac01"

# --- Rate Limiting Logic ---
IST = pytz.timezone('Asia/Kolkata')
DAILY_QUESTION_LIMIT = 10
ADMIN_PASSWORD = "100370"

def initialize_user_session():
    """Initializes session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to JainQuest! 🙏\n\nI'm here to help you explore Jain philosophy and provide spiritual guidance. Ask me anything about Jain concepts, practices, or seek emotional support."}
        ]
    
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    
    if "last_reset_date" not in st.session_state:
        st.session_state.last_reset_date = datetime.now(IST).date()
    
    if "repo_content" not in st.session_state:
        st.session_state.repo_content = None
    
    if "bytez_model" not in st.session_state:
        st.session_state.bytez_model = None
    
    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False

def check_and_reset_limit():
    """Checks if the day has changed (midnight IST) and resets the limit."""
    today_ist = datetime.now(IST).date()
    
    if st.session_state.last_reset_date < today_ist:
        st.session_state.question_count = 0
        st.session_state.last_reset_date = today_ist
        st.success("🎉 Your daily question limit has been reset! You can ask up to 10 questions today.")

def get_remaining_questions():
    """Returns the number of questions remaining."""
    if st.session_state.admin_mode:
        return "∞ (Admin Mode)"
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

def detect_sensitive_topic(question):
    """
    Detects if the question involves sensitive topics that require careful handling.
    """
    sensitive_keywords = {
        'financial': ['debt', 'money', 'loan', 'bankrupt', 'financial', 'poverty', 'poor'],
        'medical': ['sick', 'illness', 'disease', 'pain', 'medicine', 'doctor', 'hospital'],
        'legal': ['lawyer', 'court', 'legal', 'sue', 'lawsuit', 'arrest'],
        'emotional': ['depressed', 'anxiety', 'stress', 'sad', 'hopeless', 'suicide', 'breakup', 'heartbreak'],
        'relationship': ['divorce', 'breakup', 'cheat', 'abuse', 'violence', 'girlfriend', 'boyfriend']
    }
    
    detected_topics = []
    question_lower = question.lower()
    
    for category, keywords in sensitive_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            detected_topics.append(category)
    
    return detected_topics

def detect_language(question):
    """
    Simple language detection for Gujarati and English.
    """
    gujarati_chars = set('અઆઇઈઉઊઋઌઍએઐઑઓઔકખગઘઙચછજઝઞટઠડઢણતથદધનપફબભમયરલવશષસહળ')
    if any(char in gujarati_chars for char in question):
        return 'gujarati'
    return 'english'

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

def get_ai_response(question, documents, bytez_model):
    """
    Gets relevant context and calls Bytez model for response.
    """
    try:
        # Analyze question quality and sensitivity
        quality_score, suggestions = detect_question_quality(question)
        sensitive_topics = detect_sensitive_topic(question)
        language = detect_language(question)
        
        # Search for relevant documents
        relevant_docs = search_in_repo(question, documents, max_results=3)
        
        # Combine context from relevant documents
        context = "\n\n".join([doc['content'] for doc in relevant_docs])
        
        # Enhanced system prompt for structured answers
        base_prompt = """You are JainQuest, an AI assistant with deep expertise in Jainism.

RESPONSE REQUIREMENTS:
- Structure answers with clear sections using ## headers
- Use bullet points (-) for lists and key points
- Be comprehensive but concise
- Provide practical applications
- Include Jain principles and scriptural references
- Be compassionate and supportive
- Use simple, clear language

ANSWER STRUCTURE:
## Core Concept
[Brief definition and overview]

## Key Principles
- Point 1
- Point 2  
- Point 3

## Practical Applications
- How to apply this in daily life
- Step-by-step guidance when relevant

## Jain Scriptural References
- Relevant texts and teachings

## Emotional & Spiritual Support
- Compassionate guidance
- Encouraging words

## Summary
- Key takeaways"""

        # Add language instruction
        language_instruction = ""
        if language == 'gujarati':
            language_instruction = "\n\nIMPORTANT: Respond in GUJARATI language. Use Gujarati script for the entire response."
        else:
            language_instruction = "\n\nIMPORTANT: Respond in ENGLISH language."

        # Add sensitive topic handling
        sensitive_handling = ""
        if sensitive_topics:
            sensitive_handling = f"""

SENSITIVE TOPIC NOTE: This question involves {', '.join(sensitive_topics)} concerns.
- Provide compassionate emotional and spiritual support
- Offer Jain philosophical perspectives
- Be understanding and supportive
- Focus on emotional resilience"""

        if context.strip():
            system_prompt = f"""{base_prompt}{language_instruction}{sensitive_handling}

CONTEXT FROM REPOSITORY:
{context}

QUESTION: {question}

Provide a structured, compassionate response:"""
        else:
            system_prompt = f"""{base_prompt}{language_instruction}{sensitive_handling}

QUESTION: {question}

Provide a structured, compassionate response:"""

        # Add quality-based enhancements for good questions
        if quality_score >= 2:
            system_prompt += "\n\nNOTE: This is a well-structured question. Provide detailed, comprehensive guidance."

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

# --- Sidebar for Admin Mode ---
with st.sidebar:
    st.header("🔧 Admin Settings")
    
    if not st.session_state.admin_mode:
        admin_password = st.text_input("Admin Password", type="password", placeholder="Enter admin password")
        if st.button("Enable Admin Mode"):
            if admin_password == ADMIN_PASSWORD:
                st.session_state.admin_mode = True
                st.success("✅ Admin mode activated! Unlimited questions enabled.")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    
    # Display current status
    st.subheader("📊 Session Info")
    remaining = get_remaining_questions()
    st.info(f"**Questions Today:** {st.session_state.question_count}")
    st.info(f"**Remaining Questions:** {remaining}")
    
    if st.session_state.admin_mode:
        st.success("**🛡️ Admin Mode: ACTIVE**")
        if st.button("Disable Admin Mode"):
            st.session_state.admin_mode = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📚 Quick Topics")
    if st.button("Jain Basic Principles"):
        st.session_state.messages.append({"role": "user", "content": "Explain the basic principles of Jainism"})
    if st.button("Three Jewels of Jainism"):
        st.session_state.messages.append({"role": "user", "content": "What are the Three Jewels of Jainism?"})
    if st.button("Concept of Ahimsa"):
        st.session_state.messages.append({"role": "user", "content": "Explain the concept of Ahimsa in Jainism"})
    if st.button("Path to Liberation"):
        st.session_state.messages.append({"role": "user", "content": "What is the path to liberation in Jainism?"})

# --- Main Content Area ---
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🕉️ JainQuest")
    st.markdown("**Your Guide to Jain Philosophy & Spiritual Wisdom**")

with col2:
    st.metric("Questions Used", st.session_state.question_count, get_remaining_questions())

# --- Hero Section ---
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white; margin: 1rem 0;">
    <h2 style="color: white; margin: 0;">🙏 Welcome to Spiritual Guidance</h2>
    <p style="color: white; margin: 0.5rem 0 0 0;">Explore Jain philosophy, find emotional support, and discover inner peace through ancient wisdom</p>
</div>
""", unsafe_allow_html=True)

# --- Features Grid ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea;">
        <h4>📖 Philosophical Guidance</h4>
        <p>Learn about Jain concepts, principles, and spiritual practices</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #28a745;">
        <h4>💫 Emotional Support</h4>
        <p>Find comfort and guidance during difficult times</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #ff6b6b;">
        <h4>🌍 Practical Wisdom</h4>
        <p>Apply Jain teachings to modern life challenges</p>
    </div>
    """, unsafe_allow_html=True)

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
st.markdown("## 💬 Chat with JainQuest")

chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #2196f3;">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #f3e5f5; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #9c27b0;">
                <strong>JainQuest:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)

# --- Chat Input ---
st.markdown("---")
col1, col2 = st.columns([4, 1])

with col1:
    prompt = st.text_area("Ask your question...", placeholder="Type your question about Jain philosophy, seek emotional support, or ask in Gujarati...", height=80)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_button = st.button("🚀 Send", use_container_width=True)

if send_button and prompt:
    # Check question limit (unless admin mode)
    if not st.session_state.admin_mode and st.session_state.question_count >= DAILY_QUESTION_LIMIT:
        st.warning(f"🚫 You have reached your daily limit of {DAILY_QUESTION_LIMIT} questions. Please come back tomorrow or enable admin mode!")
    else:
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
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
                
                # Increment the question count
                st.session_state.question_count += 1
                
                # Rerun to update the UI
                st.rerun()

            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": "I encountered an error while processing your question. Please try again."})
                st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p><strong>Powered by Digital Jain Pathshala</strong></p>
    <p>Made with ❤️ by <a href="https://linkedin.com/in/ssanghvi03" target="_blank">Saumya Sanghvi</a></p>
    <p><em>I provide philosophical guidance and emotional support. For professional advice, consult qualified experts.</em></p>
</div>
""", unsafe_allow_html=True)
