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
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Hard-coded Repo URL ---
REPO_URL = "https://github.com/saumyasanghvi03/AI-Yashvi/"

# --- Bytez Configuration ---
BYTEZ_API_KEY = "90d252f09c55cacf3dcc914b5bb4ac01"

# --- Rate Limiting Logic ---
IST = pytz.timezone('Asia/Kolkata')
DAILY_QUESTION_LIMIT = 10
ADMIN_PASSWORD = "100370"

# --- Additional Jain Knowledge Sources ---
JAIN_KNOWLEDGE_SOURCES = {
    "Digital Jain Pathshala Blogs": "https://digitaljainpathshala.org/blogs",
    "Jain eLibrary": "https://www.jainelibrary.org",
    "JainQQ": "https://www.jainqq.org",
    "JainWorld": "https://www.jainworld.com",
    "HereNow4U": "https://www.herenow4u.net",
    "Jainpedia": "https://www.jainpedia.org",
    "Jain Philosophy": "https://www.jainphilosophy.com",
    "Jain Study": "https://www.jainstudy.org",
    "Jain Heritage": "https://www.jainheritage.org",
    "Jain Scriptures": "https://www.jainscriptures.com",
    "Jain Meditation": "https://www.jainmeditation.org"
}

# --- Digital Jain Pathshala Specific Content ---
DIGITAL_JAIN_PATHSHALA_CONTENT = """
Digital Jain Pathshala - Key Spiritual Topics:

• Ayambil and Spiritual Fasting:
  - Ayambil is a Jain spiritual practice of eating only one meal per day
  - Food consists of boiled grains without salt, spices, oil, or any tasty ingredients
  - Practice of Ras Parityag (renunciation of taste)
  - Performed during Navpad Oli festivals

• Navpad Oli:
  - Nine-day festival occurring twice yearly in Chaitra and Ashwin months
  - Each day dedicated to one of the nine supreme posts (Navpad)
  - Spiritual focus on self-discipline and purification

• Jain Meditation Techniques:
  - Preksha Meditation for self-awareness
  - Samayik for equanimity
  - Kayotsarg for relaxation and detachment

• Daily Spiritual Practices:
  - Navkar Mantra chanting
  - Pratikraman for introspection
  - Fasting for spiritual purification

• Core Jain Principles:
  - Ahimsa (Non-violence) in thought, word, and action
  - Anekantavada (Multiple viewpoints)
  - Aparigraha (Non-possessiveness)
"""

# --- Enhanced Quick Learning Topics ---
QUICK_LEARNING_TOPICS = {
    "basic_principles": {
        "icon": "🔰",
        "title": "Basic Principles",
        "question": "What are the basic principles of Jainism?",
        "description": "Learn the core foundations of Jain philosophy",
        "color": "#4CAF50"
    },
    "three_jewels": {
        "icon": "💎",
        "title": "Three Jewels",
        "question": "Explain the Three Jewels of Jainism",
        "description": "Right faith, knowledge, and conduct",
        "color": "#2196F3"
    },
    "ahimsa": {
        "icon": "🕊️",
        "title": "Ahimsa",
        "question": "What is Ahimsa and how to practice it daily?",
        "description": "Non-violence in thought, word, and action",
        "color": "#4CAF50"
    },
    "meditation": {
        "icon": "🧘",
        "title": "Meditation",
        "question": "Simple meditation techniques in Jainism",
        "description": "Preksha, Samayik, and Kayotsarg",
        "color": "#9C27B0"
    },
    "navkar_mantra": {
        "icon": "📿",
        "title": "Navkar Mantra",
        "question": "What is the significance of Navkar Mantra?",
        "description": "The most important Jain mantra",
        "color": "#FF9800"
    },
    "ayambil": {
        "icon": "🎯",
        "title": "Ayambil",
        "question": "What is Ayambil and its spiritual benefits?",
        "description": "Spiritual fasting practice",
        "color": "#F44336"
    },
    "tattvartha_sutra": {
        "icon": "📚",
        "title": "Tattvartha Sutra",
        "question": "Explain the key teachings of Tattvartha Sutra",
        "description": "Fundamental Jain scripture",
        "color": "#607D8B"
    },
    "anekantavada": {
        "icon": "🌿",
        "title": "Anekantavada",
        "question": "What is Anekantavada and its importance?",
        "description": "Doctrine of multiple viewpoints",
        "color": "#4CAF50"
    },
    "karma": {
        "icon": "🔄",
        "title": "Karma Theory",
        "question": "Explain the Jain concept of Karma",
        "description": "Understanding karmic bondage and liberation",
        "color": "#FF5722"
    },
    "vegetarianism": {
        "icon": "🌱",
        "title": "Vegetarianism",
        "question": "Why is vegetarianism important in Jainism?",
        "description": "Dietary principles and spiritual benefits",
        "color": "#4CAF50"
    },
    "navpad_oli": {
        "icon": "🕉️",
        "title": "Navpad Oli",
        "question": "What is Navpad Oli and how to observe it?",
        "description": "Nine-day spiritual festival",
        "color": "#9C27B0"
    },
    "daily_practices": {
        "icon": "🌅",
        "title": "Daily Practices",
        "question": "What are essential daily spiritual practices in Jainism?",
        "description": "Routine for spiritual growth",
        "color": "#2196F3"
    }
}

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
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Chat"
    
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    
    if "show_quick_topics" not in st.session_state:
        st.session_state.show_quick_topics = True

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

def format_response_to_bullet_points(response):
    """
    Converts paragraph responses to strict bullet point format.
    This is a fallback function to ensure proper formatting.
    """
    # If response already has proper bullet points, return as is
    if '•' in response or '- ' in response:
        return response
    
    # Split into sentences and convert to bullet points
    sentences = re.split(r'[.!?]+', response)
    bullet_points = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 10:  # Only meaningful sentences
            # Ensure it starts with a bullet point
            if not sentence.startswith('•'):
                sentence = '• ' + sentence
            bullet_points.append(sentence)
    
    return '\n'.join(bullet_points)

def get_jain_knowledge_context():
    """
    Returns context about additional Jain knowledge sources for the AI model.
    """
    sources_context = "ADDITIONAL JAIN KNOWLEDGE SOURCES FOR REFERENCE:\n\n"
    for source_name, source_url in JAIN_KNOWLEDGE_SOURCES.items():
        sources_context += f"• {source_name}: {source_url}\n"
    
    sources_context += f"\n\n{DIGITAL_JAIN_PATHSHALA_CONTENT}"
    
    sources_context += """
    
IMPORTANT JAIN CONCEPTS TO REFERENCE WHEN RELEVANT:

• Ayambil: A Jain spiritual practice combining intermittent fasting with controlled diet
• Navpad Oli: Nine-day festival dedicated to worshipping the nine supreme posts
• Ras parityag: Control of taste buds and renouncing desire for flavor
• Tattvartha Sutra: Fundamental Jain text covering all aspects of Jain philosophy
• Navkar Mantra: The most important mantra in Jainism
• Ahimsa: Non-violence towards all living beings
• Anekantavada: Doctrine of multiple viewpoints
• Aparigraha: Non-attachment to possessions
• Three Jewels: Right faith, right knowledge, right conduct
"""
    return sources_context

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

CRITICAL FORMAT RULES - YOU MUST FOLLOW EXACTLY:
1. EVERY section must use ONLY bullet points (•)
2. NO paragraphs allowed - only short, clear bullet points
3. Keep each bullet point to 1-2 lines maximum
4. Be practical and realistic with advice
5. Include specific, actionable suggestions
6. Use simple language everyone can understand
7. NEVER write paragraphs - only bullet points
8. ALWAYS use • for bullet points, not - or *

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
• [One final takeaway bullet point]

REMEMBER: ONLY BULLET POINTS, NO PARAGRAPHS!"""

        # Add language instruction
        if language == 'gujarati':
            language_instruction = "\n\nIMPORTANT: Write the CONTENT in GUJARATI language, but keep the section headings in both Gujarati and English as shown above."
        else:
            language_instruction = "\n\nIMPORTANT: Write the CONTENT in ENGLISH language, but keep the section headings in both Gujarati and English as shown above."

        # Add context if available
        context_part = ""
        if context.strip():
            context_part = f"\n\nRELEVANT CONTEXT FROM KNOWLEDGE BASE:\n{context}\n\n"

        # Add Jain knowledge sources context
        jain_sources_context = get_jain_knowledge_context()

        system_prompt = base_prompt + language_instruction + context_part + jain_sources_context + f"\n\nQUESTION: {question}\n\nProvide your STRICTLY POINTWISE answer:"

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
            # Apply formatting to ensure bullet points
            formatted_output = format_response_to_bullet_points(output)
            return formatted_output, relevant_docs, suggestions
        else:
            return "No response received from the AI model.", relevant_docs, suggestions
        
    except Exception as e:
        return f"Error processing your question: {str(e)}", [], []

# --- Enhanced UI Components ---
def render_sidebar():
    """Renders the enhanced sidebar with navigation and user info."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1 style="font-size: 2.5rem; margin: 0;">🙏</h1>
            <h2 style="color: #2E7D32; margin: 0.5rem 0;">JainQuest</h2>
            <p style="color: #666; font-size: 0.9rem;">Spiritual Guide for Everyday Life</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User Profile Section
        st.markdown("---")
        st.subheader("👤 Your Profile")
        
        if not st.session_state.user_name:
            user_name = st.text_input("Enter your name:", placeholder="Your name...")
            if user_name:
                st.session_state.user_name = user_name
                st.rerun()
        else:
            st.success(f"Welcome, {st.session_state.user_name}!")
            if st.button("Change Name"):
                st.session_state.user_name = ""
                st.rerun()
        
        # Navigation
        st.markdown("---")
        st.subheader("🧭 Navigation")
        
        nav_options = ["💬 Chat", "📚 Learn", "🛠️ Settings"]
        for option in nav_options:
            if st.button(option, use_container_width=True, key=f"nav_{option}"):
                st.session_state.current_page = option.replace("💬 ", "").replace("📚 ", "").replace("🛠️ ", "")
                st.rerun()
        
        # Quick Stats
        st.markdown("---")
        st.subheader("📊 Today's Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Questions", st.session_state.question_count)
        with col2:
            remaining = get_remaining_questions()
            if isinstance(remaining, str):
                st.metric("Remaining", remaining)
            else:
                st.metric("Remaining", remaining)
        
        # Admin Section
        st.markdown("---")
        with st.expander("🔧 Admin Settings"):
            if not st.session_state.admin_mode:
                admin_pass = st.text_input("Admin Password", type="password")
                if st.button("Enable Admin Mode"):
                    if admin_pass == ADMIN_PASSWORD:
                        st.session_state.admin_mode = True
                        st.success("Admin mode activated!")
                        st.rerun()
                    else:
                        st.error("Incorrect password")
            else:
                st.success("🛡️ Admin Mode: ACTIVE")
                if st.button("Disable Admin Mode"):
                    st.session_state.admin_mode = False
                    st.rerun()
        
        # Resources
        st.markdown("---")
        st.subheader("📖 Resources")
        st.info("""
        **Authentic Jain Sources:**
        • Digital Jain Pathshala
        • Jain eLibrary
        • JainQQ
        • JainWorld
        """)

def render_quick_learning_topics():
    """Renders the enhanced quick learning topics with modern UI/UX."""
    
    # Header with toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🚀 Quick Learning Topics")
    with col2:
        toggle_label = "🔽 Hide Topics" if st.session_state.show_quick_topics else "▶️ Show Topics"
        if st.button(toggle_label, use_container_width=True):
            st.session_state.show_quick_topics = not st.session_state.show_quick_topics
            st.rerun()
    
    if not st.session_state.show_quick_topics:
        return
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; 
                border-radius: 15px; 
                margin: 1rem 0;
                color: white;
                text-align: center;'>
        <h4 style='margin: 0; color: white;'>🌟 Click any topic to start learning instantly!</h4>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Choose from essential Jain spiritual topics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Category Tabs
    categories = {
        "🔰 Fundamentals": ["basic_principles", "three_jewels", "ahimsa", "anekantavada"],
        "🧘 Practices": ["meditation", "navkar_mantra", "daily_practices", "ayambil"],
        "📚 Scriptures": ["tattvartha_sutra", "karma"],
        "🌱 Lifestyle": ["vegetarianism", "navpad_oli"]
    }
    
    # Create tabs
    tabs = st.tabs(list(categories.keys()))
    
    for i, (category_name, topic_keys) in enumerate(categories.items()):
        with tabs[i]:
            # Create columns for this category
            cols = st.columns(2)
            
            for j, topic_key in enumerate(topic_keys):
                if topic_key in QUICK_LEARNING_TOPICS:
                    topic = QUICK_LEARNING_TOPICS[topic_key]
                    col_idx = j % 2
                    
                    with cols[col_idx]:
                        # Create a card-like container for each topic
                        st.markdown(f"""
                        <div style='
                            background: {topic["color"]}15;
                            border: 2px solid {topic["color"]}30;
                            border-radius: 12px;
                            padding: 1rem;
                            margin: 0.5rem 0;
                            transition: all 0.3s ease;
                            cursor: pointer;
                            height: 120px;
                            display: flex;
                            flex-direction: column;
                            justify-content: space-between;
                        '
                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px {topic["color"]}25';"
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';"
                        onclick="this.style.background='{topic["color"]}25';">
                            <div>
                                <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>{topic["icon"]}</div>
                                <h4 style='margin: 0; color: {topic["color"]}; font-weight: 600;'>{topic["title"]}</h4>
                                <p style='margin: 0.25rem 0 0 0; font-size: 0.85rem; color: #666; line-height: 1.3;'>{topic["description"]}</p>
                            </div>
                            <div style='text-align: right; font-size: 0.8rem; color: {topic["color"]};'>
                                Click to learn →
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add invisible button for functionality
                        if st.button("", key=f"topic_{topic_key}", help=f"Learn about {topic['title']}"):
                            st.session_state.messages.append({"role": "user", "content": topic["question"]})
                            st.rerun()

def render_chat_page():
    """Renders the main chat interface."""
    # Header with quick actions
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 💭 Ask Your Spiritual Questions")
    with col2:
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "Chat cleared! How can I help you with Jain philosophy today? 🌟"}
            ]
            st.rerun()
    with col3:
        if st.button("💫 Random Topic", use_container_width=True):
            import random
            random_topic = random.choice(list(QUICK_LEARNING_TOPICS.values()))
            st.session_state.messages.append({"role": "user", "content": random_topic["question"]})
            st.rerun()
    
    # Enhanced Quick Learning Topics
    render_quick_learning_topics()
    
    # Chat Container
    st.markdown("---")
    
    # Chat messages display
    chat_container = st.container(height=500, border=True)
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style='background: #E3F2FD; padding: 1rem; border-radius: 15px; margin: 0.5rem 0; border-left: 5px solid #1976D2;'>
                    <div style='font-weight: bold; color: #1565C0;'>👤 You</div>
                    <div style='margin-top: 0.5rem; font-size: 1.1rem;'>{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background: #F3E5F5; padding: 1rem; border-radius: 15px; margin: 0.5rem 0; border-left: 5px solid #7B1FA2;'>
                    <div style='font-weight: bold; color: #6A1B9A;'>🙏 JainQuest</div>
                    <div style='margin-top: 0.5rem; font-size: 1.1rem; line-height: 1.6;'>{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    question = st.text_area(
        "**Type your spiritual question here...**", 
        height=120,
        placeholder="Example: What is the meaning of life according to Jainism? OR જૈન ધર્મ મુજબ જીવનનો અર્થ શું છે? OR How can I find inner peace?",
        key="chat_input"
    )
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.info("💡 You can ask in English or Gujarati • 📚 Responses based on authentic Jain sources including Digital Jain Pathshala")
    with col2:
        send_clicked = st.button("🚀 Send Question", use_container_width=True, type="primary")
    
    if send_clicked and question.strip():
        process_user_question(question)

def render_learn_page():
    """Renders the learning resources page."""
    st.markdown("## 📚 Jain Learning Resources")
    
    st.markdown("""
    <div style='background: #E8F5E8; padding: 2rem; border-radius: 15px; margin: 1rem 0;'>
        <h3 style='color: #2E7D32;'>🌿 Deepen Your Spiritual Journey</h3>
        <p>Explore authentic Jain resources to enhance your understanding and practice.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Highlight Digital Jain Pathshala
    st.markdown("### 🌟 Featured Resource: Digital Jain Pathshala")
    
    with st.expander("📖 Digital Jain Pathshala Blogs - Complete Spiritual Guide", expanded=True):
        st.markdown(f"""
        **Website:** [https://digitaljainpathshala.org/blogs](https://digitaljainpathshala.org/blogs)
        
        **Key Spiritual Topics Covered:**
        
        • **Ayambil and Spiritual Fasting:**
          - Practice of eating one meal per day with boiled grains
          - No salt, spices, oil, or tasty ingredients
          - Ras Parityag (renunciation of taste)
          - Performed during Navpad Oli festivals
        
        • **Navpad Oli:**
          - Nine-day festivals in Chaitra and Ashwin months
          - Each day dedicated to one of nine supreme posts
          - Focus on self-discipline and purification
        
        • **Jain Meditation Techniques:**
          - Preksha Meditation for self-awareness
          - Samayik for equanimity
          - Kayotsarg for relaxation
        
        • **Daily Spiritual Practices:**
          - Navkar Mantra chanting
          - Pratikraman for introspection
          - Fasting for purification
        
        **Digital Jain Pathshala provides comprehensive guidance on:**
        - Jain philosophy and principles
        - Spiritual practices and rituals
        - Meditation techniques
        - Fasting methods and benefits
        - Daily spiritual routines
        """)
    
    # Other Jain Knowledge Sources
    st.markdown("### 🏛️ Additional Authentic Jain Sources")
    
    sources_col1, sources_col2 = st.columns(2)
    
    with sources_col1:
        for i, (source_name, source_url) in enumerate(list(JAIN_KNOWLEDGE_SOURCES.items())[1:6]):  # Skip first (Digital Jain Pathshala)
            with st.expander(f"📖 {source_name}", expanded=i==0):
                st.markdown(f"""
                **Website:** [{source_url}]({source_url})
                
                **Description:** Comprehensive Jain {source_name.split()[-1].lower()} resources including scriptures, articles, and teachings.
                """)
    
    with sources_col2:
        for i, (source_name, source_url) in enumerate(list(JAIN_KNOWLEDGE_SOURCES.items())[6:]):
            with st.expander(f"📖 {source_name}", expanded=i==0):
                st.markdown(f"""
                **Website:** [{source_url}]({source_url})
                
                **Description:** Authentic Jain {source_name.split()[-1].lower()} materials and spiritual guidance.
                """)
    
    # Key Concepts
    st.markdown("### 🔑 Key Jain Concepts")
    
    concepts = {
        "Ahimsa (Non-violence)": "The fundamental principle of causing no harm to any living being",
        "Anekantavada (Multiple Viewpoints)": "The doctrine of understanding truth from multiple perspectives",
        "Aparigraha (Non-attachment)": "Detachment from material possessions and desires",
        "Three Jewels": "Right faith, right knowledge, and right conduct - the path to liberation",
        "Karma Theory": "Understanding how actions affect the soul's journey",
        "Navkar Mantra": "The most important mantra honoring the five supreme beings"
    }
    
    for concept, description in concepts.items():
        with st.expander(f"🌟 {concept}"):
            st.markdown(f"**{description}**")
            st.info("Ask me about this concept in the chat for detailed explanation!")

def render_settings_page():
    """Renders the settings page."""
    st.markdown("## ⚙️ Settings & Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 App Settings")
        
        st.metric("Daily Question Limit", DAILY_QUESTION_LIMIT)
        st.metric("Questions Asked Today", st.session_state.question_count)
        remaining = get_remaining_questions()
        if isinstance(remaining, str):
            st.metric("Remaining Questions", remaining)
        else:
            st.metric("Remaining Questions", remaining)
        
        if st.button("🔄 Reset Today's Count (Admin Only)", disabled=not st.session_state.admin_mode):
            st.session_state.question_count = 0
            st.success("Question count reset!")
            st.rerun()
    
    with col2:
        st.markdown("### ℹ️ About JainQuest")
        
        st.markdown("""
        **JainQuest** is an AI-powered spiritual guide designed to:
        
        • Provide authentic Jain philosophy guidance
        • Support spiritual growth and learning
        • Offer practical advice for daily life
        • Connect users with traditional Jain teachings
        
        **Features:**
        🌟 Multi-language support (English & Gujarati)
        📚 Based on authentic Jain sources including Digital Jain Pathshala
        💬 Easy-to-understand pointwise answers
        🛡️ Content safety and appropriateness
        """)
    
    st.markdown("---")
    st.markdown("### 📞 Support & Feedback")
    
    feedback = st.text_area("Share your feedback or suggestions:", height=100)
    if st.button("Submit Feedback"):
        if feedback.strip():
            st.success("Thank you for your feedback! 🙏")
        else:
            st.warning("Please enter your feedback before submitting.")

def process_user_question(question):
    """Processes user question and generates AI response."""
    # Check limits
    if not st.session_state.admin_mode and st.session_state.question_count >= DAILY_QUESTION_LIMIT:
        st.error(f"❌ Daily limit reached. You've asked {DAILY_QUESTION_LIMIT} questions today.")
        return
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Show thinking indicator
    with st.spinner("🤔 Consulting Jain wisdom..."):
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
                "content": "I encountered an error while processing your question. Please try again."
            })
            st.rerun()

# --- Main App ---
def main():
    # Initialize session state
    initialize_user_session()
    check_and_reset_limit()
    
    # Custom CSS for enhanced UI
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Header styling */
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Metric card styling */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Chat message styling */
    .user-message {
        background: #E3F2FD;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 5px solid #1976D2;
    }
    
    .bot-message {
        background: #F3E5F5;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 5px solid #7B1FA2;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F8F9FA;
        border-radius: 8px 8px 0px 0px;
        gap: 8px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    
    /* Hide the default Streamlit button that appears on topic cards */
    div[data-testid="stButton"] button {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    st.markdown(f"""
    <div class="header">
        <h1>🙏 Welcome to JainQuest</h1>
        <p>Your AI Spiritual Guide for Jain Philosophy and Daily Practice</p>
        {f"<h3>Namaste, {st.session_state.user_name}! 🌟</h3>" if st.session_state.user_name else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Render current page based on navigation
    if st.session_state.current_page == "Chat":
        render_chat_page()
    elif st.session_state.current_page == "Learn":
        render_learn_page()
    elif st.session_state.current_page == "Settings":
        render_settings_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>Powered by Digital Jain Pathshala • Built with ❤️ for the Jain Community</strong></p>
        <p><em>For authentic spiritual guidance based on Jain teachings • Always consult human experts for critical decisions</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize AI Model if not already done
    if st.session_state.bytez_model is None:
        with st.spinner("🔄 Loading AI assistant..."):
            bytez_model = initialize_bytez_model()
            if bytez_model is not None:
                st.session_state.bytez_model = bytez_model
            else:
                st.error("Failed to connect to AI service. Please refresh the page.")
                st.stop()
    
    # Load Knowledge Base if not already done
    if st.session_state.repo_content is None:
        with st.spinner("📚 Loading knowledge base..."):
            repo_content = load_repo_content()
            if repo_content is not None:
                st.session_state.repo_content = repo_content
            else:
                st.error("Failed to load knowledge base. Some features may be limited.")

if __name__ == "__main__":
    main()
