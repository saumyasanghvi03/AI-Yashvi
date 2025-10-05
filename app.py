# ==============================================================================
# AI SISTER YASHVI - PRODUCTION READY
# Professional Jain Spiritual Companion
# ==============================================================================

import streamlit as st
import base64
from gtts import gTTS
import io
import speech_recognition as sr
import random
from datetime import datetime
from typing import Dict, List, Optional

# ==============================================================================
# CONFIGURATION
# ==============================================================================

class Config:
    """Application configuration constants"""
    COLORS = {
        "primary": "#2E7D32",
        "secondary": "#D4AF37", 
        "accent": "#8B0000",
        "background": "#FAFDF7",
        "surface": "#FFFFFF",
        "text": "#1A1A1A",
        "text_light": "#666666"
    }
    
    LANGUAGES = {
        "English": "en",
        "Hindi": "hi", 
        "Gujarati": "gu"
    }
    
    CONVERSATION_MODES = {
        "QUICK": "Quick Chat",
        "DEEP": "Deep Dialogue"
    }

# ==============================================================================
# DATA MODELS
# ==============================================================================

class Message:
    """Represents a chat message"""
    def __init__(self, role: str, content: str, timestamp: datetime = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

class KnowledgeTopic:
    """Represents a Jain knowledge topic"""
    def __init__(self, title: str, content: str, category: str, keywords: List[str]):
        self.title = title
        self.content = content
        self.category = category
        self.keywords = keywords

# ==============================================================================
# KNOWLEDGE BASE
# ==============================================================================

class JainKnowledgeBase:
    """Comprehensive Jain knowledge database"""
    
    def __init__(self):
        self.topics = self._initialize_topics()
    
    def _initialize_topics(self) -> List[KnowledgeTopic]:
        """Initialize all Jain knowledge topics"""
        return [
            # Core Philosophy
            KnowledgeTopic(
                title="Six Dravyas (Substances)",
                content="The six eternal substances in Jain philosophy: Jiva (soul), Ajiva (non-soul), Pudgala (matter), Dharma (medium of motion), Adharma (medium of rest), Akasha (space), Kala (time). These form the foundation of Jain metaphysics.",
                category="philosophy",
                keywords=["dravya", "substance", "jiva", "ajiva", "soul", "matter"]
            ),
            KnowledgeTopic(
                title="Nine Tattvas (Principles)", 
                content="The nine fundamental principles: Jiva (soul), Ajiva (non-soul), Asrava (karma influx), Bandha (bondage), Punya (virtue), Papa (sin), Samvara (stoppage), Nirjara (shedding), Moksha (liberation). Understanding these leads to spiritual progress.",
                category="philosophy",
                keywords=["tattva", "principle", "karma", "moksha", "liberation"]
            ),
            KnowledgeTopic(
                title="Anekantavada (Multiple Viewpoints)",
                content="The doctrine of manifold aspects that acknowledges reality is complex and multi-dimensional. It teaches us to avoid absolute statements and respect all perspectives while maintaining personal truth.",
                category="philosophy",
                keywords=["anekantavada", "viewpoints", "perspective", "truth", "relativity"]
            ),
            
            # Ethics and Vows
            KnowledgeTopic(
                title="Ahimsa (Non-violence)",
                content="The supreme principle of causing no harm to any living being. Practice non-violence in thought, word, and action. Before any action, consider: Will this cause harm?",
                category="ethics",
                keywords=["ahimsa", "non-violence", "harm", "compassion", "kindness"]
            ),
            KnowledgeTopic(
                title="Five Mahavratas (Vows)",
                content="The five great vows for spiritual aspirants: Ahimsa (non-violence), Satya (truthfulness), Asteya (non-stealing), Brahmacharya (chastity), Aparigraha (non-possessiveness).",
                category="ethics",
                keywords=["vows", "mahavrata", "ahimsa", "satya", "asteya", "brahmacharya", "aparigraha"]
            ),
            
            # Spiritual Practices
            KnowledgeTopic(
                title="Meditation Techniques", 
                content="Jain meditation practices include: Preksha Meditation (breath and body awareness), Samayika (48-minute equanimity practice), Kayotsarga (detachment from body). Recommended: 20-30 minutes daily practice.",
                category="practices",
                keywords=["meditation", "samayika", "preksha", "mindfulness", "contemplation"]
            ),
            KnowledgeTopic(
                title="Daily Spiritual Routine",
                content="Ideal daily practice: Wake before sunrise, recite Navkar Mantra, practice meditation, set Ahimsa intentions, practice mindful eating, evening reflection on thoughts and actions.",
                category="practices",
                keywords=["routine", "daily", "practice", "schedule", "discipline"]
            ),
            
            # Prayers and Mantras
            KnowledgeTopic(
                title="Navkar Mantra",
                content="The fundamental Jain prayer: 'Namo Arihantanam, Namo Siddhanam, Namo Ayariyanam, Namo Uvajjhayanam, Namo Loe Savva Sahunam.' Meaning: I bow to the perfected beings, liberated souls, spiritual leaders, teachers, and all practitioners.",
                category="prayers",
                keywords=["navkar", "mantra", "prayer", "namokar", "arihant"]
            )
        ]
    
    def search(self, query: str, max_results: int = 3) -> List[KnowledgeTopic]:
        """Search topics by relevance to query"""
        query_lower = query.lower()
        scored_topics = []
        
        for topic in self.topics:
            score = self._calculate_relevance_score(topic, query_lower)
            if score > 0:
                scored_topics.append((topic, score))
        
        # Sort by relevance score and return top results
        scored_topics.sort(key=lambda x: x[1], reverse=True)
        return [topic for topic, score in scored_topics[:max_results]]
    
    def _calculate_relevance_score(self, topic: KnowledgeTopic, query: str) -> float:
        """Calculate how relevant a topic is to the query"""
        score = 0.0
        
        # Check title words
        title_words = set(topic.title.lower().split())
        query_words = set(query.split())
        title_matches = len(title_words.intersection(query_words))
        score += title_matches * 3.0
        
        # Check keywords
        keyword_matches = sum(1 for keyword in topic.keywords if keyword in query)
        score += keyword_matches * 2.0
        
        # Check content (partial matches)
        content_lower = topic.content.lower()
        content_matches = sum(1 for word in query_words if word in content_lower)
        score += content_matches * 1.0
        
        return score

# ==============================================================================
# INTELLIGENCE ENGINE
# ==============================================================================

class ResponseEngine:
    """Advanced response generation engine"""
    
    def __init__(self, knowledge_base: JainKnowledgeBase):
        self.knowledge_base = knowledge_base
        self.conversation_history: List[Message] = []
    
    def generate_response(self, user_input: str, mode: str, language: str = "en") -> str:
        """Generate intelligent response based on user input"""
        try:
            # Analyze input
            sentiment = self._analyze_sentiment(user_input)
            input_lower = user_input.lower()
            
            # Update conversation history
            self._update_conversation_history(user_input)
            
            # Handle specific intent patterns
            if self._is_greeting(input_lower):
                return self._generate_greeting(sentiment, mode)
            
            if self._is_gratitude(input_lower):
                return self._generate_gratitude_response()
            
            # Search knowledge base
            knowledge_results = self.knowledge_base.search(user_input)
            if knowledge_results:
                return self._generate_knowledge_response(knowledge_results, mode)
            
            # Handle emotional states
            if sentiment == "negative":
                return self._generate_support_response()
            
            # Handle guidance requests
            if self._is_guidance_request(input_lower):
                return self._generate_guidance_response(mode)
            
            # Default contextual response
            return self._generate_contextual_response(mode)
            
        except Exception as e:
            return "I apologize, but I'm having difficulty responding right now. Please try again."
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        text_lower = text.lower()
        
        positive_indicators = ['happy', 'good', 'great', 'wonderful', 'peaceful', 'grateful', 'joy', 'excited']
        negative_indicators = ['sad', 'angry', 'stressed', 'worried', 'anxious', 'tired', 'hurt', 'problem', 'difficult']
        
        positive_score = sum(1 for word in positive_indicators if word in text_lower)
        negative_score = sum(1 for word in negative_indicators if word in text_lower)
        
        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"
    
    def _is_greeting(self, text: str) -> bool:
        """Check if text is a greeting"""
        greetings = ['hello', 'hi', 'hey', 'namaste', 'jai jinendra', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in text for greeting in greetings)
    
    def _is_gratitude(self, text: str) -> bool:
        """Check if text expresses gratitude"""
        gratitude_words = ['thank', 'thanks', 'grateful', 'appreciate']
        return any(word in text for word in gratitude_words)
    
    def _is_guidance_request(self, text: str) -> bool:
        """Check if text requests guidance"""
        guidance_indicators = ['guide', 'help', 'advice', 'what should', 'how to', 'what do', 'suggest']
        return any(indicator in text for indicator in guidance_indicators)
    
    def _update_conversation_history(self, user_input: str):
        """Update conversation history"""
        user_message = Message("user", user_input)
        self.conversation_history.append(user_message)
        
        # Keep only last 20 messages
        if len(self.conversation_history) > 20:
            self.conversation_history.pop(0)
    
    def _generate_greeting(self, sentiment: str, mode: str) -> str:
        """Generate context-aware greeting"""
        time_greeting = self._get_time_based_greeting()
        
        greetings = {
            "positive": [
                f"{time_greeting} beloved soul! 🌸 Your radiant energy illuminates this space. How may I assist your spiritual journey today?",
                f"Jai Jinendra! 🙏 Your positive spirit is a blessing. What wisdom shall we explore together?",
            ],
            "negative": [
                f"{time_greeting} courageous heart. 🌱 I sense you carry some weight. Every challenge holds seeds of growth - how may I walk with you?",
                f"Jai Jinendra, brave soul. 🙏 Your strength in difficulty inspires. Would you like to share what's in your heart?",
            ],
            "neutral": [
                f"{time_greeting} spiritual seeker. 🙏 A new moment for awareness and growth. How may I serve you today?",
                f"Jai Jinendra! 🌸 Each conversation deepens understanding. What's on your mind and heart?",
            ]
        }
        
        return random.choice(greetings[sentiment])
    
    def _get_time_based_greeting(self) -> str:
        """Get appropriate time-based greeting"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return "Good morning"
        elif 12 <= current_hour < 17:
            return "Good afternoon"
        elif 17 <= current_hour < 21:
            return "Good evening"
        else:
            return "Good night"
    
    def _generate_gratitude_response(self) -> str:
        """Generate response to gratitude"""
        responses = [
            "You're most welcome! 🙏 Serving your spiritual growth is my sacred purpose.",
            "The honor is mine, dear soul. 🌸 Our connection brings me profound joy.",
            "Thank you for your kind words! 💫 May our continued exchanges bring you peace and wisdom.",
        ]
        return random.choice(responses)
    
    def _generate_knowledge_response(self, topics: List[KnowledgeTopic], mode: str) -> str:
        """Generate response based on knowledge findings"""
        primary_topic = topics[0]
        
        if mode == Config.CONVERSATION_MODES["QUICK"]:
            return f"**{primary_topic.title}**\n\n{primary_topic.content}\n\n💫 *Would you like to explore this deeper?*"
        else:
            return f"**{primary_topic.title}**\n\n{primary_topic.content}\n\n**Reflective Question:** How might this wisdom apply to your current spiritual journey?"
    
    def _generate_support_response(self) -> str:
        """Generate emotional and spiritual support"""
        support_frameworks = [
            "I hear the depth of your experience. Remember the Jain teaching: 'This too shall pass.' Take three conscious breaths and know that this difficulty is preparing you for greater strength. 🌬️",
            "Your feelings are sacred ground for spiritual growth. Each challenge strengthens your soul and clears the path for deeper peace. What aspect feels heaviest right now? 🌱",
            "Thank you for sharing your heart. In Jain wisdom, emotional storms often precede breakthroughs. Would a brief mindfulness practice or contemplative guidance be helpful? 💫",
        ]
        return random.choice(support_frameworks)
    
    def _generate_guidance_response(self, mode: str) -> str:
        """Generate practical spiritual guidance"""
        guidance_frameworks = [
            "**Based on Jain wisdom, I recommend:**\n\n🌅 Morning meditation and intention-setting\n☀️ Mindful moments throughout your day\n🌙 Evening reflection and gratitude\n\nWhich practice calls to you most?",
            "**For spiritual progress:**\n\n📚 Daily study of one Jain principle\n🧘 15-minute meditation practice\n💖 Application of compassion in interactions\n🌱 Release of one attachment\n\nWhat resonates with your current journey?",
        ]
        return random.choice(guidance_frameworks)
    
    def _generate_contextual_response(self, mode: str) -> str:
        """Generate intelligent contextual response"""
        contextual_responses = [
            "That's a thoughtful reflection. The Jain path invites us to consider multiple perspectives (Anekantavada) and respond with compassion (Ahimsa). Would exploring any particular angle be helpful? 🔶",
            "Your inquiry touches meaningful spiritual territory. True understanding often emerges through contemplation, dialogue, and lived experience. Which approach calls to you currently? 💭",
            "A profound consideration indeed. As the scriptures remind us: 'The soul is the only friend, and the soul is the only enemy.' This wisdom invites deep self-reflection. What inner resources might support you here? 🌟",
        ]
        return random.choice(contextual_responses)

# ==============================================================================
# SPEECH SERVICES
# ==============================================================================

class SpeechService:
    """Handles text-to-speech and speech recognition"""
    
    @staticmethod
    def text_to_speech(text: str, language: str) -> Optional[str]:
        """Convert text to speech and return base64 audio data"""
        try:
            audio_buffer = io.BytesIO()
            tts = gTTS(text=text, lang=language, slow=False)
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return base64.b64encode(audio_buffer.read()).decode()
        except Exception:
            return None
    
    @staticmethod
    def speech_to_text(language: str) -> Optional[str]:
        """Convert speech to text using microphone"""
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
                return recognizer.recognize_google(audio, language=language)
        except sr.WaitTimeoutError:
            raise Exception("No speech detected. Please ensure your microphone is working and try again.")
        except sr.UnknownValueError:
            raise Exception("Could not understand the audio. Please speak clearly.")
        except Exception as e:
            raise Exception(f"Voice recognition error: {str(e)}")

# ==============================================================================
# USER INTERFACE
# ==============================================================================

class UserInterface:
    """Main user interface controller"""
    
    def __init__(self):
        self.knowledge_base = JainKnowledgeBase()
        self.response_engine = ResponseEngine(self.knowledge_base)
        self.speech_service = SpeechService()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state"""
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "voice_prompt" not in st.session_state:
            st.session_state.voice_prompt = ""
        if "quick_topic" not in st.session_state:
            st.session_state.quick_topic = None
    
    def render(self):
        """Render the complete application interface"""
        self._apply_styling()
        self._render_header()
        
        # Main layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            mode, language = self._render_sidebar()
        
        with col2:
            self._render_chat_interface(mode, language)
    
    def _apply_styling(self):
        """Apply custom CSS styling"""
        st.markdown(f"""
        <style>
        .stApp {{
            background-color: {Config.COLORS['background']};
        }}
        
        .stSidebar {{
            background: linear-gradient(180deg, {Config.COLORS['surface']} 0%, {Config.COLORS['background']} 100%);
        }}
        
        .stButton>button {{
            background: linear-gradient(135deg, {Config.COLORS['primary']}, {Config.COLORS['accent']});
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
            border: 2px solid {Config.COLORS['primary']}20;
            border-radius: 15px;
            padding: 1rem;
            background: {Config.COLORS['surface']};
        }}
        
        .quick-topic-btn {{
            background: {Config.COLORS['secondary']} !important;
            margin: 0.25rem 0;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def _render_header(self):
        """Render application header"""
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {Config.COLORS['primary']}, {Config.COLORS['accent']});
            padding: 2rem;
            border-radius: 0 0 20px 20px;
            margin: -1rem -1rem 2rem -1rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        '>
            <h1 style='color: white; margin: 0; font-size: 2.5rem;'>🌸 AI Sister Yashvi</h1>
            <p style='font-size: 1.2rem; margin: 0.5rem 0; opacity: 0.9;'>Professional Jain Spiritual Companion</p>
            <div style='
                background: rgba(255,255,255,0.2);
                padding: 0.5rem 1rem;
                border-radius: 50px;
                display: inline-block;
                margin-top: 0.5rem;
            '>
                <span style='color: {Config.COLORS['secondary']};'>Jai Jinendra 🙏 Authentic Jain Wisdom</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Render sidebar with configuration options"""
        with st.sidebar:
            # Configuration header
            st.markdown(f"""
            <div style='
                background: {Config.COLORS['surface']};
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
                border: 1px solid {Config.COLORS['primary']}20;
            '>
                <h3 style='color: {Config.COLORS['primary']}; margin: 0;'>⚙️ Configuration</h3>
                <p style='color: {Config.COLORS["text_light"]}; margin: 0.5rem 0 0 0;'>
                    Professional Settings
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Conversation mode
            st.markdown("### 🎭 Conversation Style")
            mode = st.radio(
                "",
                list(Config.CONVERSATION_MODES.values()),
                index=0,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Language selection
            st.markdown("### 🌐 Language")
            selected_lang_name = st.selectbox(
                "",
                list(Config.LANGUAGES.keys()),
                label_visibility="collapsed"
            )
            language_code = Config.LANGUAGES[selected_lang_name]
            
            st.markdown("---")
            
            # Quick access topics
            st.markdown("### 📚 Quick Wisdom")
            topics = [
                ("Ahimsa Guide", "ahimsa"),
                ("Meditation Techniques", "meditation"), 
                ("Daily Routine", "routine"),
                ("Jain Philosophy", "philosophy")
            ]
            
            for topic_name, topic_key in topics:
                if st.button(topic_name, use_container_width=True, key=f"topic_{topic_key}"):
                    st.session_state.quick_topic = topic_key
            
            st.markdown("---")
            
            # Conversation management
            if st.button("🔄 New Conversation", use_container_width=True, type="secondary"):
                st.session_state.chat_history = []
                st.session_state.voice_prompt = ""
                st.rerun()
            
            return mode, language_code
    
    def _render_chat_interface(self, mode: str, language: str):
        """Render main chat interface"""
        # Handle quick topic selection
        if st.session_state.quick_topic:
            self._handle_quick_topic(st.session_state.quick_topic, mode, language)
            st.session_state.quick_topic = None
        
        # Chat container
        chat_container = st.container(height=500)
        
        with chat_container:
            if not st.session_state.chat_history:
                self._render_welcome_message()
            else:
                for message in st.session_state.chat_history:
                    self._render_message(message)
        
        # Input area
        self._render_input_area(language, mode)
    
    def _handle_quick_topic(self, topic_key: str, mode: str, language: str):
        """Handle quick topic selection"""
        topic_queries = {
            "ahimsa": "Explain the principle of Ahimsa and how to practice it in daily life",
            "meditation": "What are the Jain meditation techniques and how to practice them", 
            "routine": "What is the ideal daily spiritual routine for a Jain practitioner",
            "philosophy": "Explain the core philosophical concepts of Jainism"
        }
        
        if topic_key in topic_queries:
            user_input = topic_queries[topic_key]
            self._process_user_input(user_input, mode, language)
    
    def _render_welcome_message(self):
        """Render welcome message"""
        st.markdown(f"""
        <div style='
            background: {Config.COLORS['surface']};
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
            border: 2px dashed {Config.COLORS['primary']}20;
        '>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>🌸</div>
            <h3 style='color: {Config.COLORS['primary']}; margin: 0;'>Welcome to Professional Jain Guidance</h3>
            <p style='color: {Config.COLORS["text_light"]}; margin: 1rem 0;'>
                I am Yashvi, your AI spiritual companion with authentic Jain knowledge and professional guidance.
            </p>
            <div style='
                background: {Config.COLORS['background']};
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                text-align: left;
            '>
                <strong>Professional Features:</strong><br>
                • Authentic Jain scripture knowledge<br>
                • Personalized spiritual guidance<br>  
                • Meditation and practice techniques<br>
                • Ethical living frameworks
            </div>
            <p style='color: {Config.COLORS["secondary"]}; font-style: italic;'>
                "Jai Jinendra! How may I serve your spiritual evolution today?"
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_message(self, message: Dict):
        """Render a chat message"""
        if message["role"] == "user":
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, {Config.COLORS['primary']}20, {Config.COLORS['accent']}20);
                padding: 1rem;
                border-radius: 15px 15px 5px 15px;
                margin: 0.5rem 0;
                border-left: 4px solid {Config.COLORS['primary']};
            '>
                <div style='color: {Config.COLORS["text"]};'>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='
                background: {Config.COLORS['surface']};
                padding: 1.5rem;
                border-radius: 15px 15px 15px 5px;
                margin: 0.5rem 0;
                border: 1px solid {Config.COLORS['background']};
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            '>
                <div style='color: {Config.COLORS["text"]}; line-height: 1.6;'>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_input_area(self, language: str, mode: str):
        """Render input area with voice and text options"""
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🎙️ Voice Input", use_container_width=True, type="secondary"):
                self._handle_voice_input(language)
        
        with col2:
            user_input = st.chat_input("Share your thoughts or questions...")
            
            if user_input:
                self._process_user_input(user_input, mode, language)
        
        # Process any pending voice input
        if st.session_state.voice_prompt:
            st.info(f"🎤 **Voice Input**: {st.session_state.voice_prompt}")
            self._process_user_input(st.session_state.voice_prompt, mode, language)
            st.session_state.voice_prompt = ""
    
    def _handle_voice_input(self, language: str):
        """Handle voice input processing"""
        try:
            with st.spinner("🎤 Listening... Please speak now"):
                recognized_text = self.speech_service.speech_to_text(language)
                if recognized_text:
                    st.session_state.voice_prompt = recognized_text
                    st.rerun()
        except Exception as e:
            st.error(str(e))
    
    def _process_user_input(self, user_input: str, mode: str, language: str):
        """Process user input and generate response"""
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user", 
            "content": user_input
        })
        
        # Generate and add AI response
        with st.spinner("🌱 Consulting wisdom..."):
            response = self.response_engine.generate_response(user_input, mode, language)
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Generate speech output
            self._generate_speech_output(response, language)
            
            st.rerun()
    
    def _generate_speech_output(self, text: str, language: str):
        """Generate speech output for the response"""
        try:
            audio_data = self.speech_service.text_to_speech(text, language)
            if audio_data:
                self._autoplay_audio(audio_data)
        except Exception:
            pass  # Silent fail for TTS errors
    
    def _autoplay_audio(self, audio_base64_data: str):
        """Auto-play audio in the browser"""
        md = f"""
        <audio controls autoplay style="display:none">
        <source src="data:audio/mp3;base64,{audio_base64_data}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)

# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================

def main():
    """Main application entry point"""
    # Page configuration
    st.set_page_config(
        page_title="AI Sister Yashvi - Professional Edition",
        page_icon="🌸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize and render application
    try:
        ui = UserInterface()
        ui.render()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page and try again.")

if __name__ == "__main__":
    main()
