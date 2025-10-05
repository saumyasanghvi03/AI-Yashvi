# =============================================================================
# AI SISTER YASHVI - PROFESSIONAL GRADE
# Production-Ready Jain Spiritual Assistant
# =============================================================================

import streamlit as st
import base64
from gtts import gTTS
import io
import speech_recognition as sr
from datetime import datetime
import json

# =============================================================================
# CORE ENGINE
# =============================================================================

class JainWisdomEngine:
    """Professional-grade Jain knowledge and response engine"""
    
    def __init__(self):
        self.knowledge_base = self._build_knowledge_base()
    
    def _build_knowledge_base(self):
        """Comprehensive, structured Jain knowledge"""
        return {
            "philosophy": {
                "six_dravyas": {
                    "question": "What are the six dravyas in Jainism?",
                    "answer": "The six eternal substances are: Jiva (soul), Pudgala (matter), Dharma (medium of motion), Adharma (medium of rest), Akasha (space), and Kala (time). These form the foundation of Jain metaphysics.",
                    "keywords": ["dravya", "substance", "jiva", "matter", "space", "time"]
                },
                "nine_tattvas": {
                    "question": "What are the nine tattvas?",
                    "answer": "The nine fundamental principles are: Jiva (soul), Ajiva (non-soul), Asrava (influx of karma), Bandha (bondage), Punya (virtue), Papa (sin), Samvara (stoppage), Nirjara (shedding), and Moksha (liberation).",
                    "keywords": ["tattva", "principle", "karma", "liberation", "moksha"]
                }
            },
            "ethics": {
                "ahimsa": {
                    "question": "What is Ahimsa and how to practice it?",
                    "answer": "Ahimsa means non-violence in thought, word, and action. Practice by: 1) Being mindful of your actions 2) Speaking truthfully without harm 3) Cultivating compassionate thoughts 4) Choosing vegetarian food 5) Respecting all life forms.",
                    "keywords": ["ahimsa", "non-violence", "compassion", "vegetarian"]
                },
                "five_vows": {
                    "question": "What are the five Mahavratas?",
                    "answer": "The five great vows are: 1) Ahimsa (non-violence) 2) Satya (truthfulness) 3) Asteya (non-stealing) 4) Brahmacharya (chastity) 5) Aparigraha (non-possessiveness).",
                    "keywords": ["vows", "mahavrata", "truth", "non-stealing", "chastity"]
                }
            },
            "practices": {
                "meditation": {
                    "question": "What are Jain meditation techniques?",
                    "answer": "Key techniques: 1) Preksha Meditation (mindfulness) 2) Samayika (48-minute equanimity) 3) Kayotsarga (body detachment) 4) Anupreksha (contemplation). Practice 20-30 minutes daily.",
                    "keywords": ["meditation", "samayika", "preksha", "mindfulness"]
                },
                "daily_routine": {
                    "question": "What is the ideal daily routine?",
                    "answer": "Morning: Wake early, recite Navkar Mantra, meditate. Day: Mindful eating, compassionate actions. Evening: Reflect on thoughts/actions, plan improvements. Key: Consistency in small practices.",
                    "keywords": ["routine", "daily", "schedule", "practice"]
                }
            },
            "prayers": {
                "navkar_mantra": {
                    "question": "What is the Navkar Mantra?",
                    "answer": "The fundamental Jain prayer: 'Namo Arihantanam, Namo Siddhanam, Namo Ayariyanam, Namo Uvajjhayanam, Namo Loe Savva Sahunam.' It means: I bow to the perfected beings, liberated souls, spiritual leaders, teachers, and all practitioners.",
                    "keywords": ["navkar", "mantra", "prayer", "arihant"]
                }
            }
        }
    
    def find_answer(self, user_question):
        """Find the most relevant answer for user's question"""
        user_question_lower = user_question.lower()
        
        # Direct keyword matching
        for category, topics in self.knowledge_base.items():
            for topic_id, topic in topics.items():
                # Check if any keyword matches
                if any(keyword in user_question_lower for keyword in topic["keywords"]):
                    return {
                        "answer": topic["answer"],
                        "question": topic["question"],
                        "category": category
                    }
        
        # Fallback responses
        fallbacks = [
            "That's an insightful question about Jain spirituality. While I focus on core principles like Ahimsa, Anekantavada, and spiritual practices, I'd be happy to discuss specific aspects that interest you.",
            "Your question touches on deeper spiritual concepts. I specialize in practical Jain wisdom - daily practices, ethical living, and philosophical foundations. Could you clarify what aspect you'd like to explore?",
            "I appreciate your curiosity about Jain teachings. My knowledge covers the Six Dravyas, Five Vows, meditation techniques, and daily spiritual practices. What specific area can I help with?"
        ]
        
        import random
        return {
            "answer": random.choice(fallbacks),
            "question": user_question,
            "category": "general"
        }

# =============================================================================
# SPEECH ENGINE
# =============================================================================

class SpeechEngine:
    """Professional speech recognition and synthesis"""
    
    @staticmethod
    def text_to_speech(text, language='en'):
        """Convert text to speech with error handling"""
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return base64.b64encode(audio_buffer.read()).decode()
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    @staticmethod
    def speech_to_text(language='en'):
        """Convert speech to text with robust error handling"""
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎤 Listening... Speak now")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            text = recognizer.recognize_google(audio, language=language)
            return text
        except sr.WaitTimeoutError:
            raise Exception("No speech detected. Please ensure your microphone is working.")
        except sr.UnknownValueError:
            raise Exception("Could not understand the audio. Please speak clearly.")
        except Exception as e:
            raise Exception(f"Microphone error: {str(e)}")

# =============================================================================
# USER INTERFACE
# =============================================================================

class ProfessionalUI:
    """Production-grade user interface"""
    
    def __init__(self):
        self.wisdom_engine = JainWisdomEngine()
        self.speech_engine = SpeechEngine()
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session state"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'voice_input' not in st.session_state:
            st.session_state.voice_input = ""
    
    def render(self):
        """Render the complete application"""
        self._apply_styles()
        self._render_header()
        self._render_sidebar()
        self._render_chat_interface()
    
    def _apply_styles(self):
        """Apply professional CSS styles"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #2E7D32, #8B0000);
            padding: 2rem;
            border-radius: 0 0 20px 20px;
            margin: -1rem -1rem 2rem -1rem;
            color: white;
            text-align: center;
        }
        .chat-user {
            background: #E8F5E8;
            padding: 1rem;
            border-radius: 15px 15px 5px 15px;
            margin: 0.5rem 0;
            border-left: 4px solid #2E7D32;
        }
        .chat-assistant {
            background: white;
            padding: 1.5rem;
            border-radius: 15px 15px 15px 5px;
            margin: 0.5rem 0;
            border: 1px solid #f0f0f0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .welcome-box {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem 0;
            border: 2px dashed #2E7D32;
        }
        .quick-action-btn {
            width: 100%;
            margin: 0.25rem 0;
            background: #D4AF37 !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_header(self):
        """Render application header"""
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0;">🌸 AI Sister Yashvi</h1>
            <p style="margin: 0.5rem 0; font-size: 1.2rem;">Professional Jain Spiritual Assistant</p>
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 50px; display: inline-block;">
                <span style="color: #D4AF37;">Jai Jinendra 🙏 Production Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Render sidebar with controls"""
        with st.sidebar:
            st.markdown("## ⚙️ Controls")
            
            # Language selection
            self.language = st.selectbox(
                "Language",
                ["English", "Hindi", "Gujarati"],
                key="language_select"
            )
            
            st.markdown("---")
            st.markdown("## 📚 Quick Questions")
            
            # Quick action buttons
            quick_actions = [
                ("What is Ahimsa?", "ahimsa"),
                ("Explain Six Dravyas", "six_dravyas"),
                ("Daily Meditation", "meditation"),
                ("Five Vows", "five_vows"),
                ("Navkar Mantra", "navkar_mantra")
            ]
            
            for action_text, action_key in quick_actions:
                if st.button(action_text, key=action_key, use_container_width=True):
                    self._handle_quick_action(action_key)
            
            st.markdown("---")
            
            # Voice input
            if st.button("🎙️ Voice Input", use_container_width=True, type="secondary"):
                self._handle_voice_input()
            
            # Clear chat
            if st.button("🔄 Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    def _render_chat_interface(self):
        """Render main chat interface"""
        # Chat container
        chat_container = st.container(height=500)
        
        with chat_container:
            if not st.session_state.chat_history:
                self._render_welcome()
            else:
                for msg in st.session_state.chat_history:
                    self._render_message(msg)
        
        # Text input
        user_input = st.chat_input("Ask about Jain wisdom...")
        if user_input:
            self._process_user_input(user_input)
    
    def _render_welcome(self):
        """Render welcome message"""
        st.markdown("""
        <div class="welcome-box">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🌸</div>
            <h3 style="color: #2E7D32;">Welcome to Professional Jain Guidance</h3>
            <p>I'm Yashvi, your AI spiritual assistant with authentic Jain knowledge.</p>
            <div style="background: #FAFDF7; padding: 1rem; border-radius: 10px; margin: 1rem 0; text-align: left;">
                <strong>I can help with:</strong><br>
                • Jain philosophy & principles<br>
                • Spiritual practices & meditation<br>
                • Ethical living & daily routines<br>
                • Prayers & scriptures
            </div>
            <p style="color: #D4AF37; font-style: italic;">
                "Jai Jinendra! How may I assist your spiritual journey today?"
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_message(self, msg):
        """Render a chat message"""
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
                <strong>You:</strong> {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-assistant">
                <strong>Yashvi:</strong> {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    def _handle_quick_action(self, action_key):
        """Handle quick action button clicks"""
        action_map = {
            "ahimsa": "What is Ahimsa and how to practice it?",
            "six_dravyas": "What are the six dravyas in Jainism?",
            "meditation": "What are Jain meditation techniques?",
            "five_vows": "What are the five Mahavratas?",
            "navkar_mantra": "What is the Navkar Mantra?"
        }
        
        if action_key in action_map:
            self._process_user_input(action_map[action_key])
    
    def _handle_voice_input(self):
        """Handle voice input"""
        try:
            language_map = {"English": "en", "Hindi": "hi", "Gujarati": "gu"}
            language_code = language_map.get(self.language, "en")
            
            text = self.speech_engine.speech_to_text(language_code)
            if text:
                self._process_user_input(text)
                
        except Exception as e:
            st.error(str(e))
    
    def _process_user_input(self, user_input):
        """Process user input and generate response"""
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate response
        with st.spinner("🕊️ Consulting wisdom..."):
            result = self.wisdom_engine.find_answer(user_input)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result["answer"],
                "category": result["category"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Convert to speech
            self._speak_response(result["answer"])
            
            st.rerun()
    
    def _speak_response(self, text):
        """Convert response to speech"""
        try:
            language_map = {"English": "en", "Hindi": "hi", "Gujarati": "gu"}
            language_code = language_map.get(self.language, "en")
            
            audio_data = self.speech_engine.text_to_speech(text, language_code)
            if audio_data:
                self._play_audio(audio_data)
        except Exception:
            pass  # Silent fail for audio errors
    
    def _play_audio(self, audio_base64):
        """Play audio in browser"""
        st.markdown(f"""
        <audio autoplay style="display:none">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)

# =============================================================================
# APPLICATION
# =============================================================================

def main():
    """Main application entry point"""
    # Configure page
    st.set_page_config(
        page_title="AI Sister Yashvi - Professional",
        page_icon="🌸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize and run application
    try:
        app = ProfessionalUI()
        app.render()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page to restart the application.")

if __name__ == "__main__":
    main()
