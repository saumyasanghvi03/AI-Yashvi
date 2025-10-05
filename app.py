# ==============================================================================
# AI SISTER YASHVI - LIGHTWEIGHT EDITION
# Sophisticated Jain Spiritual Companion with Local Intelligence
# ==============================================================================

import streamlit as st
import base64
from gtts import gTTS
import io
import speech_recognition as sr
import random
import re
from datetime import datetime
import pandas as pd

# ======================
# PREMIUM CONFIGURATION
# ======================

# Premium Color Scheme
COLORS = {
    "primary": "#2E7D32",      # Deep Jain Green
    "secondary": "#D4AF37",    # Gold
    "accent": "#8B0000",       # Deep Red
    "background": "#FAFDF7",   # Soft White
    "surface": "#FFFFFF",      # Pure White
    "text": "#1A1A1A",         # Dark Text
    "text_light": "#666666"    # Light Text
}

# Enhanced Language Support
LANG_MAP = {
    "English": "en",
    "Hindi": "hi", 
    "Gujarati": "gu",
    "Sanskrit": "sa"
}

# ======================
# ADVANCED JAIN KNOWLEDGE MEMORY SYSTEM
# ======================

class JainKnowledgeMemory:
    def __init__(self):
        self.knowledge_base = self._load_comprehensive_knowledge()
        self.conversation_memory = []
        
    def _load_comprehensive_knowledge(self):
        """Load comprehensive Jain knowledge"""
        return {
            "philosophy": {
                "six_dravyas": {
                    "title": "🪷 Six Dravyas (Substances)",
                    "content": """According to Jain philosophy, the universe consists of six eternal substances:

1. **Jiva** - Living souls (conscious beings)
2. **Ajiva** - Non-living substances:
   - Pudgala (Matter)
   - Dharma (Medium of motion)
   - Adharma (Medium of rest)  
   - Akasha (Space)
   - Kala (Time)

These six dravyas form the foundation of Jain metaphysics.""",
                    "keywords": ["dravya", "substance", "jiva", "ajiva", "soul", "matter"]
                },
                "nine_tattvas": {
                    "title": "📊 Nine Tattvas (Principles)",
                    "content": """The nine fundamental principles:

1. **Jiva** - Soul
2. **Ajiva** - Non-soul
3. **Asrava** - Influx of karma
4. **Bandha** - Bondage of karma
5. **Punya** - Virtuous karma
6. **Papa** - Sinful karma
7. **Samvara** - Stoppage of karma
8. **Nirjara** - Shedding of karma
9. **Moksha** - Liberation

Understanding these leads to spiritual progress.""",
                    "keywords": ["tattva", "principle", "karma", "moksha", "liberation"]
                },
                "anekantavada": {
                    "title": "🔶 Anekantavada (Multiple Viewpoints)",
                    "content": """The doctrine of manifold aspects:

**Core Concepts:**
- Reality is complex and multi-dimensional
- Avoid absolute statements and dogmatic thinking
- Respect all perspectives while maintaining your truth

**Practice:** When facing conflict, consider multiple viewpoints before forming conclusions.""",
                    "keywords": ["anekantavada", "viewpoints", "perspective", "truth"]
                }
            },
            "ethics": {
                "ahimsa": {
                    "title": "🕊️ Ahimsa (Non-violence)",
                    "content": """The supreme principle of Jainism:

**Three Dimensions:**
- **Physical** - Not harming any creature
- **Verbal** - Speaking gentle, truthful words  
- **Mental** - Cultivating compassionate thoughts

**Practice:** Before any action, ask: "Will this cause harm?"""",
                    "keywords": ["ahimsa", "non-violence", "harm", "compassion"]
                },
                "five_vows": {
                    "title": "📜 Five Mahavratas (Vows)",
                    "content": """The five great vows:

1. **Ahimsa** - Non-violence
2. **Satya** - Truthfulness
3. **Asteya** - Non-stealing
4. **Brahmacharya** - Chastity
5. **Aparigraha** - Non-possessiveness

These vows purify the soul and prevent karma bondage.""",
                    "keywords": ["vows", "mahavrata", "ahimsa", "satya", "asteya"]
                }
            },
            "practices": {
                "meditation": {
                    "title": "🧘‍♀️ Meditation Practices",
                    "content": """Jain meditation techniques:

**Preksha Meditation:**
- Focus on breath and body awareness
- 20-30 minutes daily practice

**Samayika:**
- 48-minute practice of equanimity
- Cultivates mental balance

**Kayotsarga:**
- Complete relaxation and detachment""",
                    "keywords": ["meditation", "samayika", "preksha", "mindfulness"]
                },
                "daily_routine": {
                    "title": "🌅 Daily Spiritual Routine",
                    "content": """Ideal daily practices:

**Morning:**
- Wake before sunrise
- Recite Navkar Mantra
- Practice meditation
- Set Ahimsa intentions

**Throughout Day:**
- Mindful eating with gratitude
- Conscious speech and actions

**Evening:**
- Review day's thoughts and actions
- Practice forgiveness and planning""",
                    "keywords": ["routine", "daily", "practice", "schedule"]
                }
            },
            "prayers": {
                "navkar_mantra": {
                    "title": "🕉️ Navkar Mantra",
                    "content": """The fundamental Jain prayer:

**Mantra:**
"Namo Arihantanam
Namo Siddhanam
Namo Ayariyanam
Nomo Uvajjhayanam
Namo Loe Savva Sahunam"

**Meaning:** I bow to the Arihants, Siddhas, Acharyas, Upadhyayas, and all Sadhus.""",
                    "keywords": ["navkar", "mantra", "prayer", "namokar"]
                }
            }
        }
    
    def search_knowledge(self, query):
        """Search through knowledge base for relevant information"""
        query_lower = query.lower()
        relevant_sections = []
        
        for category, topics in self.knowledge_base.items():
            for topic_key, topic_data in topics.items():
                # Check title and keywords
                title_match = topic_data['title'].lower() in query_lower
                keyword_match = any(keyword in query_lower for keyword in topic_data['keywords'])
                
                if title_match or keyword_match:
                    relevant_sections.append({
                        'category': category,
                        'title': topic_data['title'],
                        'content': topic_data['content'],
                        'relevance_score': self._calculate_relevance(query_lower, topic_data)
                    })
        
        # Sort by relevance and return top 3
        relevant_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_sections[:3]
    
    def _calculate_relevance(self, query, topic_data):
        """Calculate how relevant a topic is to the query"""
        score = 0
        query_words = set(query.split())
        
        # Check title words
        title_words = set(topic_data['title'].lower().split())
        score += len(query_words.intersection(title_words)) * 3
        
        # Check keywords
        keyword_matches = sum(1 for keyword in topic_data['keywords'] if keyword in query)
        score += keyword_matches * 2
        
        return score

# ======================
# ADVANCED RESPONSE ENGINE
# ======================

class AdvancedResponseEngine:
    def __init__(self, knowledge_memory):
        self.knowledge_memory = knowledge_memory
        self.conversation_context = []
        
    def analyze_sentiment(self, text):
        """Basic sentiment analysis"""
        text_lower = text.lower()
        
        positive_indicators = ['happy', 'good', 'great', 'wonderful', 'peaceful', 'grateful', 'joy']
        negative_indicators = ['sad', 'angry', 'stressed', 'worried', 'anxious', 'tired', 'hurt', 'problem']
        
        positive_score = sum(1 for word in positive_indicators if word in text_lower)
        negative_score = sum(1 for word in negative_indicators if word in text_lower)
        
        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"
    
    def generate_intelligent_response(self, user_input, mode, lang="en"):
        """Generate sophisticated responses using knowledge memory"""
        
        sentiment = self.analyze_sentiment(user_input)
        input_lower = user_input.lower()
        
        # Update conversation context
        self.conversation_context.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "sentiment": sentiment
        })
        
        # Keep only last 10 interactions
        self.conversation_context = self.conversation_context[-10:]
        
        # Search knowledge base
        knowledge_results = self.knowledge_memory.search_knowledge(user_input)
        
        # Handle greetings
        if any(word in input_lower for word in ["hello", "hi", "hey", "namaste", "jai jinendra"]):
            return self._generate_greeting(sentiment, mode)
        
        # If knowledge found, use it
        if knowledge_results:
            return self._generate_knowledge_response(knowledge_results, user_input, mode)
            
        # Emotional support
        if sentiment == "negative":
            return self._generate_spiritual_support(user_input, mode)
            
        # Spiritual guidance
        if any(word in input_lower for word in ["guide", "help", "advice", "what should", "how to"]):
            return self._generate_practical_guidance(user_input, mode)
            
        # Default intelligent response
        return self._generate_contextual_response(user_input, mode)
    
    def _generate_greeting(self, sentiment, mode):
        """Generate context-aware greetings"""
        time_of_day = self._get_time_based_greeting()
        
        base_greetings = {
            "positive": [
                f"{time_of_day} beloved soul! 🌸 How may I assist your spiritual journey today?",
                f"Jai Jinendra! 🙏 Your positive spirit shines. What wisdom shall we explore?",
            ],
            "negative": [
                f"{time_of_day} courageous heart. 🌱 Every challenge holds growth. How may I walk with you?",
                f"Jai Jinendra, brave soul. 🙏 I sense the weight you carry. Would you like to share?",
            ],
            "neutral": [
                f"{time_of_day} spiritual seeker. 🙏 A new moment for awareness. How may I assist?",
                f"Jai Jinendra! 🌸 Each conversation deepens understanding. What's on your mind?",
            ]
        }
        
        return random.choice(base_greetings[sentiment])
    
    def _get_time_based_greeting(self):
        """Get appropriate greeting based on time of day"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "Good night"
    
    def _generate_knowledge_response(self, knowledge_results, user_input, mode):
        """Generate responses based on knowledge findings"""
        primary_topic = knowledge_results[0]
        
        if mode == "Quick Chat":
            # Smart summary extraction
            content = primary_topic['content']
            sentences = content.split('.')
            summary = '. '.join(sentences[:2]) + '.'
            
            response = f"""**{primary_topic['title']}**

{summary}

💫 *Want to explore this deeper?*"""
            
        else:
            # Deep, comprehensive response
            response = f"""**{primary_topic['title']}**

{primary_topic['content']}

**Reflection:** How does this wisdom resonate with your journey?"""

        return response
    
    def _generate_spiritual_support(self, user_input, mode):
        """Provide spiritual support with practical wisdom"""
        
        support_responses = [
            """I hear your difficulty. Remember: "This too shall pass."

**Immediate Practice:**
1. Take three conscious breaths 🌬️
2. Repeat: "I am the soul, not this difficulty"
3. Find one small act of kindness

Would you like a specific meditation practice?""",
            
            """Your feelings are sacred ground for growth.

**Perspective Shift:**
- See this as soul-strengthening
- Each challenge prepares you for higher consciousness
- Your resilience builds spiritual muscle

What aspect feels heaviest? Let's address it.""",
        ]
        
        return random.choice(support_responses)
    
    def _generate_practical_guidance(self, user_input, mode):
        """Provide actionable spiritual guidance"""
        
        guidance_responses = [
            """**Based on Jain Wisdom:**

🌅 **Morning** (20-30 mins)
- Navkar Mantra with meditation
- Set Ahimsa intention

☀️ **Daily Integration**
- Mindful eating with gratitude
- Three conscious breathing breaks

🌙 **Evening** (10-15 mins)
- Review thoughts, words, actions
- Practice forgiveness

Which area to develop first?""",
            
            """**For Spiritual Progress:**

📚 **Study** - One Jain principle daily
🧘 **Practice** - 15-min meditation  
💖 **Application** - Practice compassion
🌱 **Growth** - Identify one attachment to release

**Weekly Check-in:** What insights emerged?""",
        ]
        
        return random.choice(guidance_responses)
    
    def _generate_contextual_response(self, user_input, mode):
        """Generate intelligent contextual responses"""
        
        contextual_responses = [
            """That's thoughtful. The Jain path invites us to consider:

• **Anekantavada** - Multiple perspectives reveal truths
• **Ahimsa** - Respond with compassion
• **Self-Study** - What can this teach about your journey

Would exploring any angle be helpful?""",
            
            """Your inquiry touches meaningful territory. Ancient wisdom suggests:

Understanding emerges through:
1. **Contemplation** of truths
2. **Dialogue** with perspectives  
3. **Experience** of practice

Which approach calls to you?""",
        ]
        
        return random.choice(contextual_responses)

# ======================
# SIMPLIFIED UI COMPONENTS
# ======================

class SimpleUI:
    def __init__(self):
        self.knowledge_memory = JainKnowledgeMemory()
        self.response_engine = AdvancedResponseEngine(self.knowledge_memory)
        
    def render_header(self):
        """Render beautiful header"""
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
            padding: 2rem;
            border-radius: 0 0 20px 20px;
            margin: -1rem -1rem 2rem -1rem;
            color: white;
            text-align: center;
        '>
            <h1 style='color: white; margin: 0; font-size: 2.5rem;'>🌸 AI Sister Yashvi</h1>
            <p style='font-size: 1.2rem; margin: 0.5rem 0; opacity: 0.9;'>Jain Spiritual Companion</p>
            <div style='
                background: rgba(255,255,255,0.2);
                padding: 0.5rem 1rem;
                border-radius: 50px;
                display: inline-block;
                margin-top: 0.5rem;
            '>
                <span style='color: {COLORS['secondary']};'>🕊️ 100% Open Source • No Dependencies</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render simplified sidebar"""
        with st.sidebar:
            st.markdown(f"""
            <div style='
                background: {COLORS['surface']};
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
                border: 1px solid {COLORS['primary']}20;
            '>
                <h3 style='color: {COLORS['primary']}; margin: 0;'>⚡ Features</h3>
                <p style='color: {COLORS["text_light"]}; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                    Jain Knowledge • Local AI • Voice Support
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Conversation Style
            st.markdown("### 🎭 Conversation Style")
            mode = st.radio(
                "",
                ["Quick Chat", "Deep Dialogue"],
                index=0,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Language Selection
            st.markdown("### 🌐 Language")
            selected_lang = st.selectbox(
                "Select Language",
                list(LANG_MAP.keys()),
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Quick Wisdom Access
            st.markdown("### 📚 Quick Wisdom")
            if st.button("Ahimsa Guide", use_container_width=True):
                st.session_state.quick_wisdom = "ahimsa"
            if st.button("Meditation Tips", use_container_width=True):
                st.session_state.quick_wisdom = "meditation"
            if st.button("Daily Routine", use_container_width=True):
                st.session_state.quick_wisdom = "daily_routine"
                
            st.markdown("---")
            
            # Clear History
            if st.button("🔄 New Conversation", use_container_width=True, type="secondary"):
                st.session_state.chat_history = []
                st.session_state.voice_prompt = ""
                st.rerun()
                
            return mode, LANG_MAP[selected_lang]
    
    def render_chat_interface(self, mode, lang_code):
        """Render chat interface"""
        
        # Initialize session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "voice_prompt" not in st.session_state:
            st.session_state.voice_prompt = ""
        if "quick_wisdom" not in st.session_state:
            st.session_state.quick_wisdom = None
            
        # Handle quick wisdom buttons
        if st.session_state.quick_wisdom:
            wisdom_map = {
                "ahimsa": "Tell me about Ahimsa and how to practice it",
                "meditation": "What are the Jain meditation techniques?",
                "daily_routine": "What is the ideal daily spiritual routine?"
            }
            user_input = wisdom_map[st.session_state.quick_wisdom]
            st.session_state.quick_wisdom = None
            self.process_user_input(user_input, mode, lang_code)
            
        # Chat container
        chat_container = st.container(height=500)
        
        with chat_container:
            if not st.session_state.chat_history:
                self.render_welcome_message()
            else:
                for msg in st.session_state.chat_history:
                    self.render_message(msg)
        
        # Input area
        self.render_input_area(lang_code, mode)
    
    def render_welcome_message(self):
        """Render beautiful welcome message"""
        st.markdown(f"""
        <div style='
            background: {COLORS['surface']};
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
            border: 2px dashed {COLORS['primary']}20;
        '>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>🌸</div>
            <h3 style='color: {COLORS['primary']}; margin: 0;'>Welcome to Jain Wisdom</h3>
            <p style='color: {COLORS["text_light"]}; margin: 1rem 0;'>
                I am Yashvi, your AI spiritual companion powered by authentic Jain knowledge.
            </p>
            <div style='
                background: {COLORS['background']};
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                text-align: left;
            '>
                <strong>Ask me about:</strong><br>
                • Jain philosophy and principles<br>
                • Meditation and spiritual practices<br>  
                • Daily routines and ethical living<br>
                • Scriptures and prayers
            </div>
            <p style='color: {COLORS["secondary"]}; font-style: italic;'>
                "Jai Jinendra! How may I serve your spiritual growth today?"
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_message(self, msg):
        """Render beautiful chat messages"""
        if msg["role"] == "User":
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, {COLORS['primary']}20, {COLORS['accent']}20);
                padding: 1rem;
                border-radius: 15px 15px 5px 15px;
                margin: 0.5rem 0;
                border-left: 4px solid {COLORS['primary']};
            '>
                <div style='color: {COLORS["text"]};'>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='
                background: {COLORS['surface']};
                padding: 1.5rem;
                border-radius: 15px 15px 15px 5px;
                margin: 0.5rem 0;
                border: 1px solid {COLORS['background']};
            '>
                <div style='color: {COLORS["text"]}; line-height: 1.6;'>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_input_area(self, lang_code, mode):
        """Render input area"""
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🎙️ Voice", use_container_width=True, type="secondary"):
                self.listen_for_speech(lang_code)
                
        with col2:
            user_input = st.chat_input("Ask about Jain wisdom...")
            
        # Process voice input
        if st.session_state.voice_prompt:
            user_input = st.session_state.voice_prompt
            st.info(f"🎤 **Voice**: {user_input}")
            st.session_state.voice_prompt = ""
            
        # Process input
        if user_input:
            self.process_user_input(user_input, mode, lang_code)
    
    def listen_for_speech(self, lang_code):
        """Voice input"""
        r = sr.Recognizer()
        
        with st.spinner("🎤 Listening..."):
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source, timeout=5, phrase_time_limit=15)
                
                recognized_text = r.recognize_google(audio, language=lang_code)
                st.session_state.voice_prompt = recognized_text
                st.rerun()
                
            except sr.WaitTimeoutError:
                st.warning("No speech detected")
            except Exception as e:
                st.error("Voice service unavailable")
    
    def process_user_input(self, user_input, mode, lang_code):
        """Process user input"""
        
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "User", 
            "content": user_input
        })
        
        # Generate intelligent response
        with st.spinner("🌱 Consulting wisdom..."):
            response = self.response_engine.generate_intelligent_response(
                user_input, mode, lang_code
            )
            
            # Add AI response to history
            st.session_state.chat_history.append({
                "role": "Yashvi",
                "content": response
            })
            
            # Generate speech
            self.generate_speech(response, lang_code)
            
            st.rerun()
    
    def generate_speech(self, text, lang_code):
        """Generate TTS"""
        try:
            audio_b64 = get_tts_base64(text, lang_code)
            if audio_b64:
                autoplay_audio(audio_b64)
        except:
            pass

# ======================
# HELPER FUNCTIONS  
# ======================

def get_tts_base64(text: str, lang_code: str) -> str:
    """Convert text to speech"""
    try:
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang=lang_code, tld="com", slow=False)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode()
    except:
        return ""

def autoplay_audio(audio_base64_data):
    """Auto-play audio"""
    md = f"""
    <audio controls autoplay style="display:none">
    <source src="data:audio/mp3;base64,{audio_base64_data}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# ======================
# STREAMLIT APP
# ======================

def main():
    # Page configuration
    st.set_page_config(
        page_title="AI Sister Yashvi",
        page_icon="🌸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLORS['background']};
    }}
    
    .stSidebar {{
        background: linear-gradient(180deg, {COLORS['surface']} 0%, {COLORS['background']} 100%);
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-weight: 500;
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(135deg, {COLORS['accent']}, {COLORS['primary']});
    }}
    
    .stTextInput>div>div>input {{
        border: 2px solid {COLORS['primary']}20;
        border-radius: 15px;
        padding: 1rem;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize UI
    simple_ui = SimpleUI()
    
    # Render interface
    simple_ui.render_header()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        mode, lang_code = simple_ui.render_sidebar()
        
    with col2:
        simple_ui.render_chat_interface(mode, lang_code)

if __name__ == "__main__":
    main()
