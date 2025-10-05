# ==============================================================================
# AI SISTER YASHVI - PREMIUM EDITION
# Sophisticated Jain Spiritual Companion
# ==============================================================================

import streamlit as st
import json
import base64
from gtts import gTTS
import io
import requests
import speech_recognition as sr
import random
import re
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# Premium Jain Knowledge Graph
JAIN_WISDOM_DATABASE = {
    "core_principles": {
        "ahimsa": {
            "title": "🕊️ Ahimsa (Non-violence)",
            "description": "The fundamental principle of causing no harm to any living being",
            "practices": [
                "Practice mindful eating with gratitude",
                "Speak words that heal, not hurt", 
                "Cultivate compassion in thoughts and actions",
                "Choose products that minimize harm to nature"
            ],
            "quotes": [
                "Non-violence is the highest religion. - Mahavira",
                "In happiness and suffering, in joy and grief, we should regard all creatures as we regard our own self."
            ]
        },
        "anekantavada": {
            "title": "🔶 Anekantavada (Multiple Perspectives)",
            "description": "The doctrine of manifold aspects and relativity of truth",
            "practices": [
                "Consider multiple viewpoints before forming opinions",
                "Practice active listening without judgment",
                "Embrace diversity of thought and culture",
                "Avoid absolute statements about complex truths"
            ],
            "quotes": [
                "Truth is multifaceted; wisdom lies in understanding this multiplicity.",
                "The wise understand others' views without abandoning their own."
            ]
        },
        "aparigraha": {
            "title": "📦 Aparigraha (Non-possessiveness)",
            "description": "Non-attachment to material and mental possessions",
            "practices": [
                "Regularly declutter physical and digital spaces",
                "Practice gratitude for what you have",
                "Share resources with those in need",
                "Focus on experiences over possessions"
            ],
            "quotes": [
                "The more you possess, the more you are possessed.",
                "Contentment is the greatest wealth."
            ]
        }
    },
    "daily_practices": {
        "meditation": "Begin each day with 10 minutes of mindful breathing to center yourself",
        "prayer": "Offer prayers with sincere gratitude and reflection",
        "mindful_eating": "Eat with awareness, considering the journey of your food",
        "self_reflection": "End each day with honest self-assessment and learning"
    }
}

# ======================
# PREMIUM RESPONSE ENGINE
# ======================

class PremiumResponseEngine:
    def __init__(self):
        self.conversation_context = []
        self.user_profile = {}
        
    def analyze_sentiment(self, text):
        """Basic sentiment analysis for empathetic responses"""
        positive_words = ['happy', 'good', 'great', 'wonderful', 'excited', 'peaceful', 'grateful']
        negative_words = ['sad', 'angry', 'stressed', 'worried', 'anxious', 'tired', 'hurt']
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"
    
    def generate_premium_response(self, user_input, mode, lang="en"):
        """Generate sophisticated, context-aware responses"""
        
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
        
        # Greeting responses
        if any(word in input_lower for word in ["hello", "hi", "hey", "namaste", "jai jinendra"]):
            return self._generate_greeting(sentiment, mode)
        
        # Principle-based queries
        principle_response = self._handle_jain_principles(input_lower, mode)
        if principle_response:
            return principle_response
            
        # Emotional support
        if sentiment == "negative":
            return self._generate_emotional_support(user_input, mode)
            
        # Spiritual guidance
        if any(word in input_lower for word in ["guide", "help", "advice", "what should"]):
            return self._generate_guidance(user_input, mode)
            
        # Default intelligent response
        return self._generate_contextual_response(user_input, mode)
    
    def _generate_greeting(self, sentiment, mode):
        """Generate sophisticated greetings"""
        greetings = {
            "positive": [
                "Jai Jinendra! 🙏 Your radiant energy brightens this space. How may I serve your spiritual journey today?",
                "Welcome, dear soul! 🌸 Your presence brings peace. What wisdom shall we explore together?",
                "Namaste! 🌟 I sense your positive spirit. How can I assist your growth today?"
            ],
            "negative": [
                "Jai Jinendra, beloved soul. 🙏 I sense some heaviness in your heart. Would you like to share what weighs upon you?",
                "Welcome, courageous one. 💫 Every challenge is an opportunity for growth. How may I walk with you today?",
                "Namaste, brave heart. 🌱 Your journey matters. Let's find peace together."
            ],
            "neutral": [
                "Jai Jinendra! 🙏 A new moment for growth and awareness. How may I assist you today?",
                "Welcome, seeker of truth. 🌟 Each conversation is a step toward enlightenment.",
                "Namaste! 🌸 May our exchange bring clarity and peace to your path."
            ]
        }
        
        return random.choice(greetings[sentiment])
    
    def _handle_jain_principles(self, user_input, mode):
        """Handle queries about Jain principles with depth"""
        
        if "ahimsa" in user_input:
            principle = JAIN_WISDOM_DATABASE["core_principles"]["ahimsa"]
            practice = random.choice(principle["practices"])
            quote = random.choice(principle["quotes"])
            
            if mode == "Quick Chat":
                return f"🕊️ **Ahimsa**: Non-violence in thought, word, action.\n\n💡 *Today*: {practice}\n\n📜 {quote}"
            else:
                return f"""**{principle['title']}**

{principle['description']}

**Practical Application:**
{practice}

**Wisdom Quote:**
*"{quote}"*

**Reflection Question:** How can you practice Ahimsa in your interactions today?"""
                
        elif "anekantavada" in user_input:
            principle = JAIN_WISDOM_DATABASE["core_principles"]["anekantavada"]
            practice = random.choice(principle["practices"])
            quote = random.choice(principle["quotes"])
            
            if mode == "Quick Chat":
                return f"🔶 **Anekantavada**: Multiple perspectives reveal truth.\n\n💡 *Practice*: {practice}\n\n📜 {quote}"
            else:
                return f"""**{principle['title']}**

{principle['description']}

**Practical Application:**
{practice}

**Wisdom Quote:**
*"{quote}"*

**Reflection:** Consider a current challenge from three different viewpoints."""
                
        elif "aparigraha" in user_input:
            principle = JAIN_WISDOM_DATABASE["core_principles"]["aparigraha"]
            practice = random.choice(principle["practices"])
            quote = random.choice(principle["quotes"])
            
            if mode == "Quick Chat":
                return f"📦 **Aparigraha**: Freedom through non-attachment.\n\n💡 *Try*: {practice}\n\n📜 {quote}"
            else:
                return f"""**{principle['title']}**

{principle['description']}

**Practical Application:**
{practice}

**Wisdom Quote:**
*"{quote}"*

**Exercise:** Identify one possession you can release this week."""
        
        return None
    
    def _generate_emotional_support(self, user_input, mode):
        """Provide deep emotional and spiritual support"""
        
        support_responses = [
            """I hear the weight in your words. Remember, even the mightiest rivers encounter rocks, yet they continue to flow. 

This moment of difficulty is preparing you for greater strength. Would you like to practice a brief mindfulness exercise together?""",
            
            """Your feelings are valid and honored. In Jain wisdom, we understand that suffering often precedes growth.

Let's breathe together: Inhale peace, exhale tension. Repeat three times. 🙏""",
            
            """Thank you for sharing your heart. The path of spiritual growth has both sunshine and shadow.

Would it help to discuss practical steps, or would you prefer contemplative guidance?"""
        ]
        
        return random.choice(support_responses)
    
    def _generate_guidance(self, user_input, mode):
        """Provide spiritual guidance"""
        
        guidance_responses = [
            """Based on Jain wisdom, I recommend:

1. **Morning Meditation** (5-10 minutes of mindful breathing)
2. **Mindful Action** throughout your day
3. **Evening Reflection** on your thoughts and actions

Which aspect would you like to explore deeper?""",
            
            """For spiritual progress today:

• Practice **active listening** in conversations
• Find **one opportunity** for silent compassion
• **Release judgment** of yourself and others

Each small step creates meaningful change.""",
            
            """Consider this daily practice framework:

🌅 **Morning**: Set intention with prayer
☀️ **Day**: Mindful moments between tasks  
🌙 **Evening**: Gratitude and self-review

Would you like a personalized schedule?"""
        ]
        
        return random.choice(guidance_responses)
    
    def _generate_contextual_response(self, user_input, mode):
        """Generate intelligent contextual responses"""
        
        contextual_responses = [
            """That's a profound reflection. From a Jain perspective, this invites us to consider:

• The principle of **Anekantavada** - multiple truths may coexist
• The practice of **mindful response** rather than reaction
• The opportunity for **spiritual learning**

Would you like to explore any of these aspects further?""",
            
            """Your inquiry touches deep spiritual questions. The Jain path suggests:

True understanding comes from:
1. **Right Knowledge** (Samyag Jnana)
2. **Right Faith** (Samyag Darshana) 
3. **Right Conduct** (Samyag Charitra)

Which element calls to you currently?""",
            
            """A thoughtful question indeed. The ancient wisdom reminds us:

"One who conquers oneself is greater than another who conquers a thousand times a thousand men on the battlefield." - Mahavira

How might this wisdom apply to your situation?"""
        ]
        
        return random.choice(contextual_responses)

# ======================
# PREMIUM UI COMPONENTS
# ======================

class PremiumUI:
    def __init__(self):
        self.response_engine = PremiumResponseEngine()
        
    def render_header(self):
        """Render premium header"""
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
            padding: 2rem;
            border-radius: 0 0 20px 20px;
            margin: -1rem -1rem 2rem -1rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        '>
            <h1 style='color: white; margin: 0; font-size: 2.5rem;'>🌸 AI Sister Yashvi</h1>
            <p style='font-size: 1.2rem; margin: 0.5rem 0; opacity: 0.9;'>Premium Spiritual Companion</p>
            <div style='
                background: rgba(255,255,255,0.2);
                padding: 0.5rem 1rem;
                border-radius: 50px;
                display: inline-block;
                margin-top: 0.5rem;
            '>
                <span style='color: {COLORS['secondary']};'>Jai Jinendra 🙏</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render premium sidebar"""
        with st.sidebar:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, {COLORS['surface']}, {COLORS['background']});
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
                border: 1px solid rgba(0,0,0,0.1);
            '>
                <h3 style='color: {COLORS['primary']}; margin: 0;'>⚡ Premium Features</h3>
                <p style='color: {COLORS["text_light"]}; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                    Advanced AI • Spiritual Analytics • Personalized Guidance
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
            
            # Spiritual Dashboard
            st.markdown("### 📊 Your Spiritual Journey")
            if st.button("View Progress Insights", use_container_width=True):
                self.show_spiritual_insights()
                
            st.markdown("---")
            
            # Wisdom Library
            st.markdown("### 📚 Wisdom Library")
            with st.expander("Explore Jain Principles"):
                for principle_key, principle in JAIN_WISDOM_DATABASE["core_principles"].items():
                    st.markdown(f"**{principle['title']}**")
                    st.caption(principle['description'])
                    
            st.markdown("---")
            
            # Clear History
            if st.button("🔄 New Conversation", use_container_width=True, type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
                
            return mode, LANG_MAP[selected_lang]
    
    def show_spiritual_insights(self):
        """Show beautiful spiritual analytics"""
        st.markdown("### 📈 Your Spiritual Journey")
        
        # Sample data for demonstration
        data = {
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Mindfulness': [3, 4, 5, 4, 3, 6, 7],
            'Compassion': [4, 5, 4, 6, 5, 7, 8],
            'Learning': [2, 3, 4, 3, 5, 4, 6]
        }
        
        df = pd.DataFrame(data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Day'], y=df['Mindfulness'],
            mode='lines+markers',
            name='🧠 Mindfulness',
            line=dict(color=COLORS['primary'], width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Day'], y=df['Compassion'],
            mode='lines+markers', 
            name='💖 Compassion',
            line=dict(color=COLORS['accent'], width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Day'], y=df['Learning'],
            mode='lines+markers',
            name='📚 Learning',
            line=dict(color=COLORS['secondary'], width=3)
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Streak", "7 days", "2 days")
        with col2:
            st.metric("Wisdom Minutes", "45 min", "15 min")
        with col3:
            st.metric("Growth Score", "78%", "12%")
    
    def render_chat_interface(self, mode, lang_code):
        """Render premium chat interface"""
        
        # Initialize session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "voice_prompt" not in st.session_state:
            st.session_state.voice_prompt = ""
            
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
            <h3 style='color: {COLORS['primary']}; margin: 0;'>Welcome to Your Spiritual Sanctuary</h3>
            <p style='color: {COLORS["text_light"]}; margin: 1rem 0;'>
                I am Yashvi, your AI spiritual companion. Together, we'll explore Jain wisdom, 
                practice mindfulness, and nurture your spiritual growth.
            </p>
            <div style='
                background: {COLORS['background']};
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                text-align: left;
            '>
                <strong>Begin your journey:</strong><br>
                • Ask about Jain principles and practices<br>
                • Seek guidance for daily challenges<br>  
                • Explore meditation and mindfulness<br>
                • Discuss spiritual growth
            </div>
            <p style='color: {COLORS["secondary"]}; font-style: italic;'>
                "May our conversation bring you peace and clarity"
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
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            '>
                <div style='color: {COLORS["text"]}; line-height: 1.6;'>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_input_area(self, lang_code, mode):
        """Render premium input area"""
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🎙️ Voice", use_container_width=True, type="secondary"):
                self.listen_for_speech(lang_code)
                
        with col2:
            user_input = st.chat_input("Share your thoughts or questions...")
            
        # Process voice input
        if st.session_state.voice_prompt:
            user_input = st.session_state.voice_prompt
            st.info(f"🎤 **Voice**: {user_input}")
            st.session_state.voice_prompt = ""
            
        # Process input
        if user_input:
            self.process_user_input(user_input, mode, lang_code)
    
    def listen_for_speech(self, lang_code):
        """Premium voice input"""
        r = sr.Recognizer()
        
        with st.spinner("🎤 Listening deeply..."):
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source, timeout=8, phrase_time_limit=20)
                
                recognized_text = r.recognize_google(audio, language=lang_code)
                st.session_state.voice_prompt = recognized_text
                st.rerun()
                
            except sr.WaitTimeoutError:
                st.warning("No speech detected")
            except Exception as e:
                st.error("Voice service unavailable")
    
    def process_user_input(self, user_input, mode, lang_code):
        """Process user input with premium response"""
        
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "User", 
            "content": user_input
        })
        
        # Generate premium response
        with st.spinner("🌱 Connecting with wisdom..."):
            response = self.response_engine.generate_premium_response(
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
        """Generate premium TTS"""
        try:
            audio_b64 = get_tts_base64(text, lang_code)
            if audio_b64:
                autoplay_audio(audio_b64)
        except:
            pass

# ======================
# PREMIUM HELPER FUNCTIONS  
# ======================

@st.cache_data(show_spinner=False)
def get_tts_base64(text: str, lang_code: str) -> str:
    """Premium TTS with better quality"""
    try:
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang=lang_code, tld="com", slow=False)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode()
    except:
        return ""

def autoplay_audio(audio_base64_data):
    """Premium audio player"""
    md = f"""
    <audio controls autoplay style="display:none">
    <source src="data:audio/mp3;base64,{audio_base64_data}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# ======================
# PREMIUM STREAMLIT APP
# ======================

def main():
    # Page configuration
    st.set_page_config(
        page_title="AI Sister Yashvi - Premium",
        page_icon="🌸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Premium CSS
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
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    
    .stTextInput>div>div>input {{
        border: 2px solid {COLORS['primary']}20;
        border-radius: 15px;
        padding: 1rem;
        background: {COLORS['surface']};
    }}
    
    .stRadio > div {{
        background: {COLORS['surface']};
        padding: 1rem;
        border-radius: 15px;
        border: 1px solid {COLORS['primary']}20;
    }}
    
    .stSelectbox>div>div {{
        border: 2px solid {COLORS['primary']}20;
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize premium UI
    premium_ui = PremiumUI()
    
    # Render premium interface
    premium_ui.render_header()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        mode, lang_code = premium_ui.render_sidebar()
        
    with col2:
        premium_ui.render_chat_interface(mode, lang_code)

if __name__ == "__main__":
    main()
