import streamlit as st
from datetime import datetime
import pytz
import requests
import json

# --- Configuration ---
st.set_page_config(
    page_title="JainQuest - Spiritual Guide", 
    page_icon="🙏", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# --- Comprehensive Quick Questions Database ---
QUICK_QUESTIONS_DATABASE = {
    "navkar_mantra": {
        "question": "What is the Navkar Mantra and its significance?",
        "answer": """**મુખ્ય વિચાર / Main Concept**
• Navkar Mantra is the most fundamental mantra in Jainism that honors the five supreme beings

**મુખ્ય મુદ્દાઓ / Key Points**
• Also known as Namokar Mantra or Panch Namaskar Mantra
• Contains salutations to Arihants, Siddhas, Acharyas, Upadhyayas, and Sadhus
• Considered the essence of Jain philosophy
• Can be chanted at any time without restrictions

**જૈન સિદ્ધાંતો / Jain Principles**
• Respect for all enlightened souls - fundamental Jain value
• Non-attachment - mantra focuses on spiritual qualities, not material gains
• Equality - honors all levels of spiritual achievement

**વ્યવહારુ સલાહ / Practical Advice**
• Chant 5-10 times daily morning after waking up
• Recite before meals as gratitude practice
• Use for meditation focusing on each of the five beings
• Teach children as their first spiritual practice

**ભાવનાત્મક સહાય / Emotional Support**
• This mantra connects you with centuries of spiritual wisdom and peace

**સારાંશ / Summary**
• Navkar Mantra is your daily connection to Jain spiritual heritage"""
    },
    "jainism_basics": {
        "question": "What are the basic principles of Jainism?",
        "answer": """**મુખ્ય વિચાર / Main Concept**
• Jainism is built on three core principles: Right Faith, Right Knowledge, Right Conduct

**મુખ્ય મુદ્દાઓ / Key Points**
• Ahimsa (Non-violence) - fundamental principle governing all actions
• Anekantavada (Multiple viewpoints) - respect for different perspectives
• Aparigraha (Non-possessiveness) - detachment from material things
• Five Mahavratas - great vows for spiritual progress

**જૈન સિદ્ધાંતો / Jain Principles**
• Every soul has potential for liberation (Moksha)
• Karma theory - actions determine spiritual progress
• Self-effort is essential for spiritual growth
• Compassion for all living beings

**વ્યવહારુ સલાહ / Practical Advice**
• Practice vegetarianism to minimize harm
• Be mindful of your thoughts, words, and actions
• Limit possessions to what you truly need
• Practice forgiveness daily

**ભાવનાત્મક સહાય / Emotional Support**
• These principles guide you toward lasting inner peace

**સારાંશ / Summary**
• Jain principles provide a complete roadmap for spiritual living"""
    },
    "ahimsa": {
        "question": "What is Ahimsa and how to practice it daily?",
        "answer": """**મુખ્ય વિચાર / Main Concept**
• Ahimsa means non-violence in thought, speech, and action toward all living beings

**મુખ્ય મુદ્દાઓ / Key Points**
• Includes mental non-violence - avoiding harmful thoughts
• Extends to all creatures, big and small
• More than just not killing - includes not causing mental pain
• Basis for vegetarianism in Jainism

**જૈન સિદ્ધાંતો / Jain Principles**
• Foundation of all other Jain principles
• Essential for spiritual progress
• Reduces karmic bondage
• Develops compassion and empathy

**વ્યવહારુ સલાહ / Practical Advice**
• Check food for small insects before cooking
• Speak gently without hurting others' feelings
• Walk carefully to avoid stepping on insects
• Practice forgiveness when others hurt you
• Use natural cleaning methods instead of insecticides

**ભાવનાત્મક સહાય / Emotional Support**
• Practicing Ahimsa brings profound peace and connection with all life

**સારાંશ / Summary**
• Ahimsa is the heart of Jain practice - start with small daily actions"""
    },
    "three_jewels": {
        "question": "Explain the Three Jewels of Jainism",
        "answer": """**મુખ્ય વિચાર / Main Concept**
• The Three Jewels (Ratnatraya) are Right Faith, Right Knowledge, and Right Conduct - the path to liberation

**મુખ્ય મુદ્દાઓ / Key Points**
• Right Faith (Samyak Darshan) - belief in Jain principles
• Right Knowledge (Samyak Gyan) - understanding true nature of reality
• Right Conduct (Samyak Charitra) - living according to Jain ethics
• All three are interconnected and essential

**જૈન સિદ્ધાંતો / Jain Principles**
• Foundation of spiritual practice
• Path to Moksha (liberation)
• Progressive development - one leads to another
• Applicable to both householders and monks

**વ્યવહારુ સલાહ / Practical Advice**
• Start with Right Faith - study basic Jain principles
• Develop Right Knowledge - read Jain scriptures regularly
• Practice Right Conduct - follow five minor vows daily
• Attend spiritual discourses for guidance
• Practice self-reflection regularly

**ભાવનાત્મક સહાય / Emotional Support**
• The Three Jewels provide clear guidance for your spiritual journey

**સારાંશ / Summary**
• Follow the Three Jewels step by step for steady spiritual progress"""
    },
    "ayambil": {
        "question": "What is Ayambil and its spiritual benefits?",
        "answer": """**મુખ્ય વિચાર / Main Concept**
• Ayambil is a Jain spiritual fasting practice involving one meal of boiled grains without spices or flavorings

**મુખ્ય મુદ્દાઓ / Key Points**
• Single meal during daytime only
• Boiled grains without salt, oil, spices, or dairy
• Practice of taste renunciation (Ras Parityag)
• Often observed during Navpad Oli

**જૈન સિદ્ધાંતો / Jain Principles**
• Control over sense of taste
• Reduction of karmic bondage
• Development of self-discipline
• Spiritual purification

**વ્યવહારુ સલાહ / Practical Advice**
• Start with one day Ayambil if new to fasting
• Choose simple grains like rice or wheat
• Maintain hydration with boiled water
• Combine with meditation and chanting
• Consult elders for proper procedure

**ભાવનાત્મક સહાય / Emotional Support**
• Ayambil strengthens your willpower and spiritual determination

**સારાંશ / Summary**
• Ayambil is powerful spiritual practice for self-purification"""
    },
    "meditation": {
        "question": "What are the main meditation techniques in Jainism?",
        "answer": """**મુખ્ય વિચાર / Main Concept**
• Jain meditation focuses on self-realization, peace, and spiritual purification

**મુખ્ય મુદ્દાઓ / Key Points**
• Preksha Meditation - for self-awareness and perception
• Samayik - practice of equanimity for 48 minutes
• Kayotsarg - complete relaxation and detachment
• Anupreksha - contemplation on fundamental truths

**જૈન સિદ્ધાંતો / Jain Principles**
• Meditation purifies soul from karmic particles
• Develops non-attachment and equanimity
• Enhances spiritual understanding
• Prepares for higher spiritual states

**વ્યવહારુ સલાહ / Practical Advice**
• Start with 10 minutes Preksha Meditation daily
• Practice Samayik on weekends initially
• Learn Kayotsarg for stress relief
• Join meditation classes for proper guidance
• Create peaceful meditation space at home

**ભાવનાત્મક સહાય / Emotional Support**
• Regular meditation brings deep peace and mental clarity

**સારાંશ / Summary**
• Jain meditation offers practical tools for inner transformation"""
    },
    "karma_theory": {
        "question": "Explain the Jain concept of Karma",
        "answer": """**મુખ્ય વિચાર / Main Concept**
• Karma in Jainism is subtle matter that binds to soul based on actions, determining spiritual progress

**મુખ્ય મુદ્દાઓ / Key Points**
• Karma is physical substance, not just philosophical concept
• Eight main types of Karma that affect soul
• Karma binds through actions driven by passions
• Liberation achieved by stopping influx and shedding existing Karma

**જૈન સિદ્ધાંતો / Jain Principles**
• Every action has consequences
• Self-effort can change karmic destiny
• Right knowledge and conduct destroy Karma
• Ultimate goal is complete freedom from Karma

**વ્યવહારુ સલાહ / Practical Advice**
• Practice mindfulness in daily actions
• Cultivate detachment from results
• Regular meditation to purify thoughts
• Study scriptures to understand karmic laws
• Perform Pratikraman for introspection

**ભાવનાત્મક સહાય / Emotional Support**
• Understanding Karma empowers you to shape your spiritual destiny

**સારાંશ / Summary**
• Jain Karma theory provides scientific approach to spiritual progress"""
    },
    "vegetarianism": {
        "question": "Why is vegetarianism important in Jainism?",
        "answer": """**મુખ્ય વિચાર / Main Concept**
• Vegetarianism is essential in Jainism as practical expression of Ahimsa (non-violence)

**મુખ્ય મુદ્દાઓ / Key Points**
• Minimizes harm to living beings
• Supports spiritual purity
• Traditional Jain diet excludes root vegetables
• Many Jains also avoid after-sunset eating

**જૈન સિદ્ધાંતો / Jain Principles**
• All living beings have soul and desire to live
• Causing unnecessary harm creates bad Karma
• Pure food leads to pure thoughts
• Diet affects spiritual progress directly

**વ્યવહારુ સલાહ / Practical Advice**
• Choose fresh, seasonal vegetables and fruits
• Avoid root vegetables if possible
• Check food for insects before cooking
• Practice gratitude before meals
• Consider lacto-vegetarian diet

**ભાવનાત્મક સહાય / Emotional Support**
• Vegetarian living brings harmony with all life forms

**સારાંશ / Summary**
• Vegetarianism is practical spirituality that benefits all beings"""
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
    
    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Chat"
    
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""

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

def detect_language(question):
    """
    Simple language detection for Gujarati and English.
    """
    gujarati_chars = set('અઆઇઈઉઊઋઌઍએઐઑઓઔકખગઘઙચછજઝઞટઠડઢણતથદધનપફબભમયરલવશષસહળ')
    if any(char in gujarati_chars for char in question):
        return 'gujarati'
    return 'english'

def get_fallback_response(question):
    """Get response from quick questions database."""
    question_lower = question.lower().strip()
    
    # Improved keyword-based matching for common questions
    question_keywords = {
        "jainism": "jainism_basics",
        "what is jain": "jainism_basics", 
        "basic principle": "jainism_basics",
        "navkar": "navkar_mantra",
        "namokar": "navkar_mantra",
        "mantra": "navkar_mantra",
        "ahimsa": "ahimsa",
        "non violence": "ahimsa",
        "non-violence": "ahimsa",
        "three jewel": "three_jewels",
        "ratnatraya": "three_jewels",
        "ayambil": "ayambil",
        "fasting": "ayambil",
        "meditation": "meditation",
        "karma": "karma_theory",
        "vegetarian": "vegetarianism",
        "diet": "vegetarianism"
    }
    
    # Check for direct keyword matches first
    for keyword, response_key in question_keywords.items():
        if keyword in question_lower:
            return QUICK_QUESTIONS_DATABASE[response_key]["answer"]
    
    # If no keyword match, use a generic response
    language = detect_language(question)
    
    if language == 'gujarati':
        return """**મુખ્ય વિચાર / Main Concept**
• હું હાલમાં આ પ્રશ્નનો સીધો જવાબ આપવામાં અસમર્થ છું

**મુખ્ય મુદ્દાઓ / Key Points**
• કૃપા કરીને તમારો પ્રશ્ન ફરીથી લખવાનો પ્રયાસ કરો
• તમે 'Quick Questions' વિભાગમાં સામાન્ય પ્રશ્નોના જવાબ મેળવી શકો છો
• અથવા તમારો પ્રશ્ન વિવિધ શબ્દોમાં રજૂ કરો

**વ્યવહારુ સલાહ / Practical Advice**
• જૈન ધર્મના સિદ્ધાંતો વિશે વાંચો
• ધાર્મિક સ્રોતોનો અભ્યાસ કરો
• સ્થાનિક જૈન સમુદાય સાથે જોડાવો

**ભાવનાત્મક સહાય / Emotional Support**
• તમારી આધ્યાત્મિક શોધ મહત્વપૂર્ણ છે - ચાલુ રાખો

**સારાંશ / Summary**
• કૃપા કરીને પ્રશ્ન ફરીથી લખો અથવા Quick Questions વિભાગ અજમાવો"""
    else:
        return """**મુખ્ય વિચાર / Main Concept**
• I'm currently unable to provide a direct answer to this specific question

**મુખ્ય મુદ્દાઓ / Key Points**
• Please try rephrasing your question
• You can find answers to common questions in the 'Quick Questions' section
• Or try asking your question using different words

**વ્યવહારુ સલાહ / Practical Advice**
• Read about Jain principles and philosophy
• Study religious texts and resources
• Connect with local Jain community

**ભાવનાત્મક સહાય / Emotional Support**
• Your spiritual quest is important - please continue

**સારાંશ / Summary**
• Please rephrase your question or try the Quick Questions section"""

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
        
        nav_options = ["💬 Chat", "❓ Quick Questions", "📚 Learn", "🛠️ Settings"]
        for option in nav_options:
            if st.button(option, use_container_width=True, key=f"nav_{option}"):
                st.session_state.current_page = option.replace("💬 ", "").replace("❓ ", "").replace("📚 ", "").replace("🛠️ ", "")
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

def render_quick_questions_page():
    """Renders the comprehensive quick questions page."""
    st.markdown("## ❓ Quick Questions - Instant Spiritual Guidance")
    
    st.markdown("""
    <div style='background: #E8F5E8; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;'>
        <h3 style='color: #2E7D32; margin: 0;'>🌟 Instant Answers to Common Questions</h3>
        <p style='margin: 0.5rem 0 0 0;'>Click any question below to get immediate, well-structured answers based on authentic Jain teachings.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Questions in organized sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📿 Mantras & Practices")
        
        # Navkar Mantra
        with st.expander("📿 Navkar Mantra - The Fundamental Mantra", expanded=True):
            st.markdown("**What is the Navkar Mantra and its significance?**")
            if st.button("Get Answer", key="navkar_answer"):
                st.session_state.messages.append({"role": "user", "content": QUICK_QUESTIONS_DATABASE["navkar_mantra"]["question"]})
                st.session_state.messages.append({"role": "assistant", "content": QUICK_QUESTIONS_DATABASE["navkar_mantra"]["answer"]})
                st.session_state.question_count += 1
                st.session_state.current_page = "Chat"
                st.rerun()
        
        # Meditation
        with st.expander("🧘 Jain Meditation Techniques"):
            st.markdown("**What are the main meditation techniques in Jainism?**")
            if st.button("Get Answer", key="meditation_answer"):
                st.session_state.messages.append({"role": "user", "content": QUICK_QUESTIONS_DATABASE["meditation"]["question"]})
                st.session_state.messages.append({"role": "assistant", "content": QUICK_QUESTIONS_DATABASE["meditation"]["answer"]})
                st.session_state.question_count += 1
                st.session_state.current_page = "Chat"
                st.rerun()
        
        # Ayambil
        with st.expander("🎯 Ayambil & Spiritual Fasting"):
            st.markdown("**What is Ayambil and its spiritual benefits?**")
            if st.button("Get Answer", key="ayambil_answer"):
                st.session_state.messages.append({"role": "user", "content": QUICK_QUESTIONS_DATABASE["ayambil"]["question"]})
                st.session_state.messages.append({"role": "assistant", "content": QUICK_QUESTIONS_DATABASE["ayambil"]["answer"]})
                st.session_state.question_count += 1
                st.session_state.current_page = "Chat"
                st.rerun()
    
    with col2:
        st.markdown("### 🔰 Core Principles")
        
        # Jainism Basics
        with st.expander("🔰 Basic Principles of Jainism", expanded=True):
            st.markdown("**What are the basic principles of Jainism?**")
            if st.button("Get Answer", key="basics_answer"):
                st.session_state.messages.append({"role": "user", "content": QUICK_QUESTIONS_DATABASE["jainism_basics"]["question"]})
                st.session_state.messages.append({"role": "assistant", "content": QUICK_QUESTIONS_DATABASE["jainism_basics"]["answer"]})
                st.session_state.question_count += 1
                st.session_state.current_page = "Chat"
                st.rerun()
        
        # Ahimsa
        with st.expander("🕊️ Ahimsa - Non-violence"):
            st.markdown("**What is Ahimsa and how to practice it daily?**")
            if st.button("Get Answer", key="ahimsa_answer"):
                st.session_state.messages.append({"role": "user", "content": QUICK_QUESTIONS_DATABASE["ahimsa"]["question"]})
                st.session_state.messages.append({"role": "assistant", "content": QUICK_QUESTIONS_DATABASE["ahimsa"]["answer"]})
                st.session_state.question_count += 1
                st.session_state.current_page = "Chat"
                st.rerun()
        
        # Three Jewels
        with st.expander("💎 Three Jewels of Jainism"):
            st.markdown("**Explain the Three Jewels of Jainism**")
            if st.button("Get Answer", key="three_jewels_answer"):
                st.session_state.messages.append({"role": "user", "content": QUICK_QUESTIONS_DATABASE["three_jewels"]["question"]})
                st.session_state.messages.append({"role": "assistant", "content": QUICK_QUESTIONS_DATABASE["three_jewels"]["answer"]})
                st.session_state.question_count += 1
                st.session_state.current_page = "Chat"
                st.rerun()
    
    # Second row of questions
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 📚 Philosophy & Concepts")
        
        # Karma Theory
        with st.expander("🔄 Karma Theory in Jainism"):
            st.markdown("**Explain the Jain concept of Karma**")
            if st.button("Get Answer", key="karma_answer"):
                st.session_state.messages.append({"role": "user", "content": QUICK_QUESTIONS_DATABASE["karma_theory"]["question"]})
                st.session_state.messages.append({"role": "assistant", "content": QUICK_QUESTIONS_DATABASE["karma_theory"]["answer"]})
                st.session_state.question_count += 1
                st.session_state.current_page = "Chat"
                st.rerun()
    
    with col4:
        st.markdown("### 🌱 Lifestyle & Diet")
        
        # Vegetarianism
        with st.expander("🌱 Vegetarianism in Jainism"):
            st.markdown("**Why is vegetarianism important in Jainism?**")
            if st.button("Get Answer", key="vegetarianism_answer"):
                st.session_state.messages.append({"role": "user", "content": QUICK_QUESTIONS_DATABASE["vegetarianism"]["question"]})
                st.session_state.messages.append({"role": "assistant", "content": QUICK_QUESTIONS_DATABASE["vegetarianism"]["answer"]})
                st.session_state.question_count += 1
                st.session_state.current_page = "Chat"
                st.rerun()
    
    # Information about the answers
    st.markdown("---")
    st.markdown("""
    <div style='background: #E3F2FD; padding: 1rem; border-radius: 10px;'>
        <h4 style='color: #1565C0; margin: 0;'>💡 About These Answers</h4>
        <p style='margin: 0.5rem 0 0 0;'>
        • All answers are pre-written based on authentic Jain sources<br>
        • Structured in easy-to-understand bullet points<br>
        • Include practical advice for daily life<br>
        • Available in both English and Gujarati formats<br>
        • Count toward your daily question limit
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_chat_page():
    """Renders the main chat interface."""
    # Header with quick actions
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 💭 Ask Your Spiritual Questions")
    with col2:
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "Chat cleared! How can I help you with Jain philosophy today? 🌟"}
            ]
            st.rerun()
    
    # Simple guidance section
    st.markdown("---")
    st.markdown("""
    <div style='background: #E8F5E8; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;'>
        <h4 style='color: #2E7D32; margin: 0;'>💡 How to Get the Best Answers</h4>
        <p style='margin: 0.5rem 0 0 0;'>
        • Ask specific questions about Jain philosophy, principles, or practices<br>
        • You can type in English or Gujarati<br>
        • Get clear, pointwise answers based on authentic sources<br>
        • Visit <strong>Quick Questions</strong> in sidebar for instant answers to common topics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
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
        ❓ Quick Questions for instant learning
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
    """Processes user question and generates response."""
    # Check limits
    if not st.session_state.admin_mode and st.session_state.question_count >= DAILY_QUESTION_LIMIT:
        st.error(f"❌ Daily limit reached. You've asked {DAILY_QUESTION_LIMIT} questions today.")
        return
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Show thinking indicator
    with st.spinner("🤔 Consulting Jain wisdom..."):
        try:
            # Get response from quick questions database
            bot_response = get_fallback_response(question)
            
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
    </style>
    """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    st.markdown(f"""
    <div class="header">
        <h1>🙏 Welcome to JainQuest</h1>
        <p>Your Spiritual Guide for Jain Philosophy and Daily Practice</p>
        {f"<h3>Namaste, {st.session_state.user_name}! 🌟</h3>" if st.session_state.user_name else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Render current page based on navigation
    if st.session_state.current_page == "Chat":
        render_chat_page()
    elif st.session_state.current_page == "Quick Questions":
        render_quick_questions_page()
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

if __name__ == "__main__":
    main()
