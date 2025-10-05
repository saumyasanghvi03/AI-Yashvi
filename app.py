# ==============================================================================
# AI SISTER YASHVI - STABLE EDITION
# Jain Spiritual Companion with Local Intelligence
# ==============================================================================

import streamlit as st
import base64
from gtts import gTTS
import io
import speech_recognition as sr
import random
from datetime import datetime

# ======================
# CONFIGURATION
# ======================

COLORS = {
    "primary": "#2E7D32",
    "secondary": "#D4AF37", 
    "accent": "#8B0000",
    "background": "#FAFDF7",
    "surface": "#FFFFFF",
    "text": "#1A1A1A",
    "text_light": "#666666"
}

LANG_MAP = {
    "English": "en",
    "Hindi": "hi", 
    "Gujarati": "gu"
}

# ======================
# JAIN KNOWLEDGE MEMORY
# ======================

class JainKnowledgeMemory:
    def __init__(self):
        self.knowledge_base = self._load_knowledge()
        
    def _load_knowledge(self):
        return {
            "philosophy": {
                "six_dravyas": {
                    "title": "Six Dravyas (Substances)",
                    "content": "According to Jain philosophy, the universe consists of six eternal substances: Jiva (soul), Ajiva (non-soul), Pudgala (matter), Dharma (motion), Adharma (rest), Akasha (space), Kala (time).",
                    "keywords": ["dravya", "substance", "jiva", "ajiva", "soul"]
                },
                "nine_tattvas": {
                    "title": "Nine Tattvas (Principles)", 
                    "content": "The nine fundamental principles: Jiva (soul), Ajiva (non-soul), Asrava (karma influx), Bandha (bondage), Punya (virtue), Papa (sin), Samvara (stoppage), Nirjara (shedding), Moksha (liberation).",
                    "keywords": ["tattva", "principle", "karma", "moksha", "liberation"]
                },
                "anekantavada": {
                    "title": "Anekantavada (Multiple Viewpoints)",
                    "content": "The doctrine of manifold aspects. Reality is complex and multi-dimensional. Avoid absolute statements and respect all perspectives while maintaining your truth.",
                    "keywords": ["anekantavada", "viewpoints", "perspective", "truth"]
                }
            },
            "ethics": {
                "ahimsa": {
                    "title": "Ahimsa (Non-violence)",
                    "content": "The supreme principle of causing no harm to any living being. Practice non-violence in thought, word, and action. Before any action, ask: Will this cause harm?",
                    "keywords": ["ahimsa", "non-violence", "harm", "compassion"]
                },
                "five_vows": {
                    "title": "Five Mahavratas (Vows)",
                    "content": "The five great vows: Ahimsa (non-violence), Satya (truthfulness), Asteya (non-stealing), Brahmacharya (chastity), Aparigraha (non-possessiveness).",
                    "keywords": ["vows", "mahavrata", "ahimsa", "satya", "asteya"]
                }
            },
            "practices": {
                "meditation": {
                    "title": "Meditation Practices", 
                    "content": "Jain meditation techniques: Preksha Meditation (breath awareness), Samayika (48-minute equanimity), Kayotsarga (detachment from body). Practice 20-30 minutes daily.",
                    "keywords": ["meditation", "samayika", "preksha", "mindfulness"]
                },
                "daily_routine": {
                    "title": "Daily Spiritual Routine",
                    "content": "Ideal daily practice: Wake before sunrise, recite Navkar Mantra, practice meditation, set Ahimsa intentions, mindful eating, evening reflection on thoughts and actions.",
                    "keywords": ["routine", "daily", "practice", "schedule"]
                }
            },
            "prayers": {
                "navkar_mantra": {
                    "title": "Navkar Mantra",
                    "content": "The fundamental Jain prayer: Namo Arihantanam, Namo Siddhanam, Namo Ayariyanam, Namo Uvajjhayanam, Namo Loe Savva Sahunam. Meaning: I bow to the perfected beings, liberated souls, spiritual leaders, teachers, and all practitioners.",
                    "keywords": ["navkar", "mantra", "prayer", "namokar"]
                }
            }
        }
    
    def search_knowledge(self, query):
        query_lower = query.lower()
        relevant_sections = []
        
        for category, topics in self.knowledge_base.items():
            for topic_key, topic_data in topics.items():
                title_match = topic_data['title'].lower() in query_lower
                keyword_match = any(keyword in query_lower for keyword in topic_data['keywords'])
                
                if title_match or keyword_match:
                    score = self._calculate_relevance(query_lower, topic_data)
                    relevant_sections.append({
                        'category': category,
                        'title': topic_data['title'],
                        'content': topic_data['content'],
                        'relevance_score': score
                    })
        
        relevant_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_sections[:3]
    
    def _calculate_relevance(self, query, topic_data):
        score = 0
        query_words = set(query.split())
        
        title_words = set(topic_data['title'].lower().split())
        score += len(query_words.intersection(title_words)) * 3
        
        keyword_matches = sum(1 for keyword in topic_data['keywords'] if keyword in query)
        score += keyword_matches * 2
        
        return score

# ======================
# RESPONSE ENGINE
# ======================

class ResponseEngine:
    def __init__(self, knowledge_memory):
        self.knowledge_memory = knowledge_memory
        self.conversation_context = []
        
    def analyze_sentiment(self, text):
        text_lower = text.lower()
        
        positive_words = ['happy', 'good', 'great', 'wonderful', 'peaceful', 'grateful', 'joy']
        negative_words = ['sad', 'angry', 'stressed', 'worried', 'anxious', 'tired', 'hurt', 'problem']
        
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"
    
    def generate_response(self, user_input, mode, lang="en"):
        sentiment = self.analyze_sentiment(user_input)
        input_lower = user_input.lower()
        
        self.conversation_context.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "sentiment": sentiment
        })
        
        self.conversation_context = self.conversation_context[-10:]
        
        knowledge_results = self.knowledge_memory.search_knowledge(user_input)
        
        if any(word in input_lower for word in ["hello", "hi", "hey", "namaste", "jai jinendra"]):
            return self._generate_greeting(sentiment, mode)
        
        if knowledge_results:
            return self._generate_knowledge_response(knowledge_results, user_input, mode)
            
        if sentiment == "negative":
            return self._generate_support(user_input, mode)
            
        if any(word in input_lower for word in ["guide", "help", "advice", "what should", "how to"]):
            return self._generate_guidance(user_input, mode)
            
        return self._generate_contextual_response(user_input, mode)
    
    def _generate_greeting(self, sentiment, mode):
        time_of_day = self._get_time_based_greeting()
        
        greetings = {
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
        
        return random.choice(greetings[sentiment])
    
    def _get_time_based_greeting(self):
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
        primary_topic = knowledge_results[0]
        
        if mode == "Quick Chat":
            response = f"**{primary_topic['title']}**\n\n{primary_topic['content']}\n\n💫 *Want to explore deeper?*"
        else:
            response = f"**{primary_topic['title']}**\n\n{primary_topic['content']}\n\n**Reflection:** How does this wisdom resonate with your journey?"

        return response
    
    def _generate_support(self, user_input, mode):
        support_responses = [
            "I hear your difficulty. Remember: This too shall pass. Take three conscious breaths and find one small act of kindness today. 🌬️",
            "Your feelings are sacred ground for growth. See this challenge as soul-strengthening. What aspect feels heaviest? 🌱",
        ]
        return random.choice(support_responses)
    
    def _generate_guidance(self, user_input, mode):
        guidance_responses = [
            "**Daily Practice:** Morning meditation, mindful eating, evening reflection. Which area to develop first? 🌅",
            "**For Progress:** Study one principle daily, practice 15-min meditation, apply compassion. What calls to you? 📚",
        ]
        return random.choice(guidance_responses)
    
    def _generate_contextual_response(self, user_input, mode):
        contextual_responses = [
            "That's thoughtful. Consider multiple perspectives (Anekantavada) and respond with compassion (Ahimsa). Would exploring any angle help? 🔶",
            "Your inquiry touches meaningful territory. Understanding comes through contemplation, dialogue, and experience. Which approach calls to you? 💭",
        ]
        return random.choice(contextual_responses)

# ======================
# UI COMPONENTS
# ======================

class SimpleUI:
    def __init__(self):
        self.knowledge_memory = JainKnowledgeMemory()
        self.response_engine = ResponseEngine(self.knowledge_memory)
        
    def render_header(self):
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
            padding: 2rem;
            border-radius: 0 0 20px 20px;
            margin: -1rem -1rem 2rem -1rem;
            color: white;
            text-align: center;
        '>
            <h1 style='color: white; margin: 0;'>🌸 AI Sister Yashvi</h1>
            <p style='margin: 0.5rem 0;'>Jain Spiritual Companion</p>
            <div style='
                background: rgba(255,255,255,0.2);
                padding: 0.5rem 1rem;
                border-radius: 50px;
                display: inline-block;
            '>
                <span>🕊️ Open Source • No Dependencies</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        with st.sidebar:
            st.markdown("### ⚙️ Configuration")
            
            mode = st.radio(
                "Conversation Style:",
                ["Quick Chat", "Deep Dialogue"],
                index=0
            )
            
            st.markdown("---")
            
            selected_lang = st.selectbox(
                "Language:",
                list(LANG_MAP.keys())
            )
            
            st.markdown("---")
            
            st.markdown("### 📚 Quick Access")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Ahimsa"):
                    st.session_state.quick_topic = "ahimsa"
                if st.button("Meditation"):
                    st.session_state.quick_topic = "meditation"
            with col2:
                if st.button("Prayers"):
                    st.session_state.quick_topic = "prayers"
                if st.button("Daily Routine"):
                    st.session_state.quick_topic = "daily_routine"
            
            st.markdown("---")
            
            if st.button("🔄 Clear Chat"):
                st.session_state.chat_history = []
                st.session_state.voice_prompt = ""
                st.rerun()
                
            return mode, LANG_MAP[selected_lang]
    
    def render_chat_interface(self, mode, lang_code):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "voice_prompt" not in st.session_state:
            st.session_state.voice_prompt = ""
        if "quick_topic" not in st.session_state:
            st.session_state.quick_topic = None
            
        if st.session_state.quick_topic:
            topic_map = {
                "ahimsa": "Tell me about Ahimsa",
                "meditation": "What are Jain meditation techniques?",
                "prayers": "Teach me about Jain prayers",
                "daily_routine": "What is the ideal daily routine?"
            }
            user_input = topic_map[st.session_state.quick_topic]
            st.session_state.quick_topic = None
            self.process_user_input(user_input, mode, lang_code)
            
        chat_container = st.container(height=500)
        
        with chat_container:
            if not st.session_state.chat_history:
                self.render_welcome_message()
            else:
                for msg in st.session_state.chat_history:
                    self.render_message(msg)
        
        self.render_input_area(lang_code, mode)
    
    def render_welcome_message(self):
        st.markdown(f"""
        <div style='
            background: {COLORS['surface']};
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
        '>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>🌸</div>
            <h3 style='color: {COLORS['primary']};'>Welcome to Jain Wisdom</h3>
            <p>I am Yashvi, your AI spiritual companion with authentic Jain knowledge.</p>
            <div style='
                background: {COLORS['background']};
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
            '>
                <strong>Ask me about:</strong><br>
                • Jain philosophy and principles<br>
                • Meditation and spiritual practices<br>  
                • Daily routines and ethical living
            </div>
            <p style='color: {COLORS["secondary"]};'>"Jai Jinendra! How may I serve your spiritual growth?"</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_message(self, msg):
        if msg["role"] == "User":
            st.markdown(f"""
            <div style='
                background: {COLORS['primary']}20;
                padding: 1rem;
                border-radius: 15px 15px 5px 15px;
                margin: 0.5rem 0;
                border-left: 4px solid {COLORS['primary']};
            '>
                {msg["content"]}
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
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    def render_input_area(self, lang_code, mode):
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🎙️ Voice", use_container_width=True):
                self.listen_for_speech(lang_code)
                
        with col2:
            user_input = st.chat_input("Ask about Jain wisdom...")
            
        if st.session_state.voice_prompt:
            user_input = st.session_state.voice_prompt
            st.info(f"🎤 Voice: {user_input}")
            st.session_state.voice_prompt = ""
            
        if user_input:
            self.process_user_input(user_input, mode, lang_code)
    
    def listen_for_speech(self, lang_code):
        r = sr.Recognizer()
        
        with st.spinner("Listening..."):
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source, timeout=5, phrase_time_limit=15)
                
                recognized_text = r.recognize_google(audio, language=lang_code)
                st.session_state.voice_prompt = recognized_text
                st.rerun()
                
            except sr.WaitTimeoutError:
                st.warning("No speech detected")
            except Exception:
                st.error("Voice service unavailable")
    
    def process_user_input(self, user_input, mode, lang_code):
        st.session_state.chat_history.append({
            "role": "User", 
            "content": user_input
        })
        
        with st.spinner("Yashvi is thinking..."):
            response = self.response_engine.generate_response(
                user_input, mode, lang_code
            )
            
            st.session_state.chat_history.append({
                "role": "Yashvi",
                "content": response
            })
            
            self.generate_speech(response, lang_code)
            st.rerun()
    
    def generate_speech(self, text, lang_code):
        try:
            audio_b64 = get_tts_base64(text, lang_code)
            if audio_b64:
                autoplay_audio(audio_b64)
        except:
            pass

# ======================
# HELPER FUNCTIONS
# ======================

def get_tts_base64(text, lang_code):
    try:
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode()
    except:
        return ""

def autoplay_audio(audio_base64_data):
    md = f"""
    <audio controls autoplay style="display:none">
    <source src="data:audio/mp3;base64,{audio_base64_data}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# ======================
# MAIN APP
# ======================

def main():
    st.set_page_config(
        page_title="AI Sister Yashvi",
        page_icon="🌸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLORS['background']};
    }}
    .stSidebar {{
        background: {COLORS['surface']};
    }}
    .stButton>button {{
        background: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    ui = SimpleUI()
    ui.render_header()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        mode, lang_code = ui.render_sidebar()
        
    with col2:
        ui.render_chat_interface(mode, lang_code)

if __name__ == "__main__":
    main()
