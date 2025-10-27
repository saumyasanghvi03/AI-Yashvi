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
st.set_page_config(
    page_title="JainQuest - Spiritual Guide", 
    page_icon="🙏", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

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
            {"role": "assistant", "content": "Welcome! I'm here to help you learn about Jain philosophy and provide spiritual guidance. You can ask questions in English or Gujarati. 🌟"}
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
        with st.spinner("Loading knowledge base..."):
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
    if len(question.split()) >= 3:
        quality_score += 1
    
    # Check for specific question words
    question_words = ['what', 'how', 'why', 'explain', 'describe', 'compare', 'difference']
    if any(word in question.lower() for word in question_words):
        quality_score += 1
    
    return quality_score, suggestions

def detect_sensitive_topic(question):
    """
    Detects if the question involves sensitive topics that violate Jain principles.
    """
    prohibited_keywords = {
        'sexual': ['sex', 'masturbation', 'porn', 'sexual', 'intercourse', 'lust', 'desire', 'kama'],
        'nonveg': ['nonveg', 'non-veg', 'meat', 'chicken', 'fish', 'egg', 'eggs', 'mutton', 'beef', 'pork'],
        'alcohol': ['alcohol', 'beer', 'wine', 'whisky', 'drink', 'drunk', 'intoxication', 'smoking', 'cigarette'],
        'violence': ['violence', 'fight', 'attack', 'hurt', 'kill', 'war', 'weapon'],
        'inappropriate': ['drugs', 'weed', 'marijuana', 'cannabis', 'addiction']
    }
    
    detected_topics = []
    question_lower = question.lower()
    
    for category, keywords in prohibited_keywords.items():
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

def get_prohibited_response(language, topic):
    """
    Returns a standardized response for prohibited topics.
    """
    if language == 'gujarati':
        return f"""**મુખ્ય વિચાર / Main Concept**
• આ વિષય જૈન સિદ્ધાંતો સાથે સુસંગત નથી

**જૈન સિદ્ધાંતો / Jain Principles**
• અહિંસા - સર્વભૂત હિતેરતાઃ (સૌ પ્રાણીઓનું ભલું)
• સંયમ - ઇન્દ્રિયો પર નિયંત્રણ
• શુદ્ધતા - મન, વચન અને કાયાની પવિત્રતા

**ધાર્મિક સલાહ / Religious Advice**
• ભગવાન સાથે જોડાણ કરો નવકાર મંત્ર દ્વારા
• આ ટેવ છોડવા ભગવાનનાં આશીર્વાદ માંગો
• યાદ રાખો કે દરેક આત્મા પરિવર્તનની શક્તિ ધરાવે છે

**વ્યવહારુ સૂચનો / Practical Suggestions**
• પ્રલોભનોનો સામના કરવા 10 મિનિટ નવકાર મંત્ર જપો
• "તત્વાર્થ સૂત્ર" જેવા ધાર્મિક ગ્રંથો વાંચો
• જૈન સત્સંગ અથવા ઓનલાઈન સમુદાયમાં જોડાવો

**પ્રેરણા / Inspiration**
• અનેક મહાન આત્માઓએ ધાર્મિક સાધનાથી પરિવર્તન અનુભવ્યું છે
• તમારી શુદ્ધ આત્મા ફરી ચમકવા માટે રાહ જોઈ રહી છે

**સારાંશ / Summary**
• આંતરિક શાંતિ અને શક્તિ માટે ધાર્મિક સાધનાઓ તરફ વળો"""
    else:
        return f"""**મુખ્ય વિચાર / Main Concept**
• This topic is not aligned with Jain principles

**જૈન સિદ્ધાંતો / Jain Principles**
• Ahimsa - Non-violence towards all living beings
• Self-discipline - Control over senses and desires
• Purity - Maintaining physical and mental cleanliness

**ધાર્મિક સલાહ / Religious Advice**
• Connect with God through daily Navkar Mantra chanting
• Seek divine blessings to overcome challenging habits
• Remember every soul has the power to transform

**વ્યવહારુ સૂચનો / Practical Suggestions**
• Chant Navkar Mantra for 10 minutes when facing temptations
• Read spiritual texts like "Tattvartha Sutra" for guidance
• Join Jain satsangs or online spiritual communities

**પ્રેરણા / Inspiration**
• Many great souls have transformed through spiritual practice
• Your pure soul is waiting to shine brightly again

**સારાંશ / Summary**
• Turn to spiritual practices to find strength and inner peace"""

def get_ai_response(question, documents, bytez_model):
    """
    Gets relevant context and calls Bytez model for response.
    """
    try:
        # Check for prohibited topics first
        prohibited_topics = detect_sensitive_topic(question)
        if prohibited_topics:
            language = detect_language(question)
            return get_prohibited_response(language, prohibited_topics[0]), [], []

        # Analyze question quality and sensitivity
        quality_score, suggestions = detect_question_quality(question)
        language = detect_language(question)
        
        # Search for relevant documents
        relevant_docs = search_in_repo(question, documents, max_results=3)
        
        # Combine context from relevant documents
        context = "\n\n".join([doc['content'] for doc in relevant_docs])
        
        # STRICTLY POINTWISE system prompt with realistic suggestions
        base_prompt = """You are JainQuest, a helpful AI assistant for Jain philosophy.

CRITICAL FORMAT RULES - YOU MUST FOLLOW:
1. EVERY section must use ONLY bullet points (•)
2. NO paragraphs allowed - only short, clear bullet points
3. Keep each bullet point to 1-2 lines maximum
4. Be practical and realistic with advice
5. Include specific, actionable suggestions
6. Use simple language everyone can understand

REAL-WORLD JAIN TEACHER PRACTICES TO INCORPORATE:
• Satish Kumar's "Walk gently with eyes on ground" to practice mindfulness
• Acharya Shree Yogeesh's breathing techniques for stress relief
• Siddhayatan Tirth's meditation methods for emotional healing
• Listen to Jain bhajans like "Nemras" on Spotify/YouTube
• Practice 5-minute Navkar Mantra meditation daily
• Join online Jain satsangs for community support

REQUIRED SECTIONS (in this exact order):

**મુખ્ય વિચાર / Main Concept**
• [One clear bullet point explaining the core idea]

**મુખ્ય મુદ્દાઓ / Key Points**
• [Point 1 - short and clear]
• [Point 2 - short and clear]
• [Point 3 - short and clear]

**જૈન સિદ્ધાંતો / Jain Principles**
• [Relevant Jain principle 1]
• [Relevant Jain principle 2]

**વ્યવહારુ સલાહ / Practical Advice**
• [Include specific Jain teacher techniques when relevant]
• [Suggest Jain music like "Nemras" for emotional healing]
• [Recommend meditation apps or online resources]
• [Something easy to do today]

**ભાવનાત્મક સહાય / Emotional Support**
• [One compassionate, encouraging bullet point]

**સારાંશ / Summary**
• [One final takeaway bullet point]"""

        # Add language instruction
        if language == 'gujarati':
            language_instruction = "\n\nIMPORTANT: Write the CONTENT in GUJARATI language, but keep the section headings in both Gujarati and English as shown above."
        else:
            language_instruction = "\n\nIMPORTANT: Write the CONTENT in ENGLISH language, but keep the section headings in both Gujarati and English as shown above."

        # Add context if available
        context_part = ""
        if context.strip():
            context_part = f"\n\nRELEVANT CONTEXT:\n{context}\n\nBase your answer on this context when possible."

        system_prompt = base_prompt + language_instruction + context_part + f"\n\nQUESTION: {question}\n\nProvide your STRICTLY POINTWISE answer:"

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
            return output, relevant_docs, suggestions
        else:
            return "No response received from the AI model.", relevant_docs, suggestions
        
    except Exception as e:
        return f"Error processing your question: {str(e)}", [], []

# --- Universal UI Design ---

# Initialize
initialize_user_session()
check_and_reset_limit()

# Custom CSS for universal accessibility
st.markdown("""
<style>
    /* Large, readable fonts for all ages */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3 {
        color: #2E7D32;
        font-weight: 600;
    }
    
    .chat-user {
        background: #E3F2FD;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 5px solid #1976D2;
        font-size: 1.1rem;
    }
    
    .chat-bot {
        background: #F3E5F5;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 5px solid #7B1FA2;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .stButton button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
        border-radius: 10px;
    }
    
    .stTextInput textarea {
        font-size: 1.1rem;
        padding: 1rem;
    }
    
    .info-box {
        background: #E8F5E8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #FFEBEE;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #F44336;
        margin: 1rem 0;
    }
    
    /* High contrast for elders */
    .main {
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="font-size: 3rem; margin: 0;">🙏</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.title("JainQuest")
    st.markdown("**Spiritual Guide for Everyday Life**")

# --- Simple Stats ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Questions Asked", st.session_state.question_count)
with col2:
    remaining = get_remaining_questions()
    st.metric("Remaining Today", remaining)
with col3:
    status = "🌟 Unlimited" if st.session_state.admin_mode else "✅ Active"
    st.metric("Status", status)

# --- Content Guidelines ---
st.markdown("""
<div class="warning-box">
    <h4 style="margin: 0; color: #D32F2F;">📜 Content Guidelines</h4>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">
    • I provide spiritual guidance based on Jain principles<br>
    • I cannot answer questions about prohibited topics<br>
    • Always consult experts for medical/legal advice<br>
    • Focus on spiritual growth and inner peace
    </p>
</div>
""", unsafe_allow_html=True)

# --- Quick Action Buttons (Large & Clear) ---
st.markdown("### Quick Questions")
col1, col2, col3, col4 = st.columns(4)

quick_questions = {
    "Basic Jain Principles": "What are the basic principles of Jainism?",
    "Three Jewels": "Explain the Three Jewels of Jainism",
    "Ahimsa": "What is Ahimsa and how to practice it?",
    "Meditation": "Simple meditation techniques in Jainism"
}

if col1.button("🔰 Basic Principles", use_container_width=True):
    st.session_state.messages.append({"role": "user", "content": quick_questions["Basic Jain Principles"]})
if col2.button("💎 Three Jewels", use_container_width=True):
    st.session_state.messages.append({"role": "user", "content": quick_questions["Three Jewels"]})
if col3.button("🕊️ Ahimsa", use_container_width=True):
    st.session_state.messages.append({"role": "user", "content": quick_questions["Ahimsa"]})
if col4.button("🧘 Meditation", use_container_width=True):
    st.session_state.messages.append({"role": "user", "content": quick_questions["Meditation"]})

# --- Info Box ---
st.markdown("""
<div class="info-box">
    <h4 style="margin: 0; color: #2E7D32;">💡 How to Use</h4>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">
    • Ask any question about Jain philosophy<br>
    • Seek emotional or spiritual guidance<br>
    • Type in English or Gujarati<br>
    • Get clear, pointwise answers<br>
    • Based on authentic Jain teachings
    </p>
</div>
""", unsafe_allow_html=True)

# --- Admin Access (Simple & Discrete) ---
with st.expander("🔧 Admin Settings"):
    if not st.session_state.admin_mode:
        admin_pass = st.text_input("Enter Admin Password", type="password")
        if st.button("Enable Admin Mode"):
            if admin_pass == ADMIN_PASSWORD:
                st.session_state.admin_mode = True
                st.success("Admin mode activated! Unlimited questions.")
                st.rerun()
            else:
                st.error("Incorrect password")
    else:
        st.success("🛡️ Admin Mode: ACTIVE")
        if st.button("Disable Admin Mode"):
            st.session_state.admin_mode = False
            st.rerun()

# --- Initialize AI Model ---
if st.session_state.bytez_model is None:
    with st.spinner("Loading AI assistant..."):
        bytez_model = initialize_bytez_model()
        if bytez_model is not None:
            st.session_state.bytez_model = bytez_model
        else:
            st.error("Failed to connect to AI service.")
            st.stop()

# --- Load Knowledge Base ---
if st.session_state.repo_content is None:
    with st.spinner("Loading knowledge..."):
        repo_content = load_repo_content()
        if repo_content is not None:
            st.session_state.repo_content = repo_content
        else:
            st.error("Failed to load knowledge base.")
            st.stop()

# --- Chat Display ---
st.markdown("---")
st.markdown("## 💬 Conversation")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-user">
            <strong>You:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-bot">
            <strong>JainQuest:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)

# --- Chat Input ---
st.markdown("---")
st.markdown("### 💭 Ask Your Question")

# Simple language selector
lang_col1, lang_col2 = st.columns(2)
with lang_col1:
    st.info("💬 You can type in English or Gujarati")
with lang_col2:
    st.info("📱 Easy to read for all ages")

question = st.text_area(
    "Type your question here...", 
    height=100,
    placeholder="Example: What is Jainism? OR જૈન ધર્મ શું છે? OR I'm feeling sad, what should I do?"
)

col1, col2 = st.columns([3, 1])
with col2:
    send_clicked = st.button("🚀 Send Question", use_container_width=True)

if send_clicked and question.strip():
    # Check limits
    if not st.session_state.admin_mode and st.session_state.question_count >= DAILY_QUESTION_LIMIT:
        st.error(f"❌ Daily limit reached. You've asked {DAILY_QUESTION_LIMIT} questions today.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Show thinking indicator
        with st.spinner("🤔 Thinking..."):
            try:
                # Get AI response
                bot_response, source_docs, suggestions = get_ai_response(
                    question, 
                    st.session_state.repo_content, 
                    st.session_state.bytez_model
                )
                
                # Add bot response
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                # Update counter
                st.session_state.question_count += 1
                
                # Refresh
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "I encountered an error. Please try again."
                })
                st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 1rem;">
    <p><strong>Powered by Digital Jain Pathshala</strong></p>
    <p>Created with ❤️ by Saumya Sanghvi</p>
    <p><em>For spiritual guidance based on authentic Jain teachings</em></p>
</div>
""", unsafe_allow_html=True)
