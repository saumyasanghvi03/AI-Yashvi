# =============================================================================
# AI SISTER YASHVI - ENTERPRISE GRADE
# Professional Jain Assistant with Live Knowledge Base
# =============================================================================

import streamlit as st
import base64
from gtts import gTTS
import io
import speech_recognition as sr
from datetime import datetime
import requests
import re
from typing import Dict, List, Optional
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    KNOWLEDGE_BASE_URL = "https://raw.githubusercontent.com/saumyasanghvi03/AI-Yashvi/main/jain_knowledge_base.txt"
    COLORS = {
        "primary": "#2E7D32",
        "secondary": "#D4AF37", 
        "accent": "#8B0000",
        "background": "#FAFDF7",
        "surface": "#FFFFFF",
        "text": "#1A1A1A",
        "text_light": "#666666"
    }

# =============================================================================
# KNOWLEDGE MANAGER
# =============================================================================

class KnowledgeManager:
    """Professional knowledge base manager with live updates"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.last_update = None
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load knowledge base from GitHub with caching"""
        try:
            response = requests.get(Config.KNOWLEDGE_BASE_URL, timeout=10)
            if response.status_code == 200:
                self._parse_knowledge_base(response.text)
                self.last_update = datetime.now()
                return True
            else:
                st.error("❌ Failed to load knowledge base from GitHub")
                return False
        except Exception as e:
            st.error(f"❌ Error loading knowledge base: {str(e)}")
            # Load fallback knowledge
            self._load_fallback_knowledge()
            return False
    
    def _parse_knowledge_base(self, content: str):
        """Parse the knowledge base text file"""
        sections = content.split('## ')[1:]  # Skip first empty split
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.split('\n')
            section_title = lines[0].strip()
            self.knowledge_base[section_title] = {}
            
            current_subtopic = None
            content_lines = []
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for subtopic (lines starting with ###)
                if line.startswith('### '):
                    # Save previous subtopic
                    if current_subtopic and content_lines:
                        self.knowledge_base[section_title][current_subtopic] = '\n'.join(content_lines)
                    
                    # Start new subtopic
                    current_subtopic = line[4:].strip()
                    content_lines = []
                elif current_subtopic:
                    content_lines.append(line)
            
            # Save the last subtopic
            if current_subtopic and content_lines:
                self.knowledge_base[section_title][current_subtopic] = '\n'.join(content_lines)
    
    def _load_fallback_knowledge(self):
        """Load fallback knowledge when GitHub is unavailable"""
        self.knowledge_base = {
            "CORE PRINCIPLES": {
                "Ahimsa": "Non-violence in thought, word, and action. The supreme principle of Jainism.",
                "Anekantavada": "The doctrine of multiple viewpoints and relativity of truth.",
                "Aparigraha": "Non-possessiveness and non-attachment to material possessions."
            },
            "SPIRITUAL PRACTICES": {
                "Meditation": "Preksha meditation and Samayika for mental peace and spiritual growth.",
                "Daily Routine": "Morning prayers, mindful eating, and evening reflection.",
                "Fasting": "Periodic fasting for self-discipline and spiritual purification."
            }
        }
    
    def search(self, query: str) -> Dict:
        """Intelligent search through knowledge base"""
        query_lower = query.lower()
        results = []
        
        for category, topics in self.knowledge_base.items():
            for topic, content in topics.items():
                relevance_score = self._calculate_relevance(query_lower, topic, content)
                if relevance_score > 0:
                    results.append({
                        'category': category,
                        'topic': topic,
                        'content': content,
                        'score': relevance_score
                    })
        
        # Return best match
        if results:
            best_match = max(results, key=lambda x: x['score'])
            return best_match
        else:
            return self._get_fallback_response(query)
    
    def _calculate_relevance(self, query: str, topic: str, content: str) -> float:
        """Calculate relevance score for search"""
        score = 0.0
        
        # Topic matches
        topic_lower = topic.lower()
        if query in topic_lower:
            score += 10.0
        elif any(word in topic_lower for word in query.split()):
            score += 5.0
        
        # Content matches
        content_lower = content.lower()
        if query in content_lower:
            score += 8.0
        elif any(word in content_lower for word in query.split()):
            score += 3.0
        
        return score
    
    def _get_fallback_response(self, query: str) -> Dict:
        """Provide intelligent fallback responses"""
        fallbacks = [
            {
                'category': 'GENERAL',
                'topic': 'Jain Wisdom',
                'content': f"Your question about '{query}' shows deep curiosity. While I focus on core Jain principles like Ahimsa, Anekantavada, and spiritual practices, I'd be happy to discuss specific aspects of Jain philosophy or daily practices."
            },
            {
                'category': 'GUIDANCE', 
                'topic': 'Spiritual Direction',
                'content': f"That's a thoughtful inquiry. In Jain tradition, we emphasize practical wisdom. Would you like guidance on meditation, ethical living, or understanding specific Jain principles?"
            }
        ]
        
        import random
        response = random.choice(fallbacks)
        response['score'] = 1.0
        return response

# =============================================================================
# SPEECH ENGINE
# =============================================================================

class SpeechEngine:
    """Professional speech services"""
    
    @staticmethod
    def text_to_speech(text: str, language: str = 'en') -> Optional[str]:
        """Convert text to speech"""
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return base64.b64encode(audio_buffer.read()).decode()
        except Exception:
            return None
    
    @staticmethod
    def speech_to_text(language: str = 'en') -> str:
        """Convert speech to text"""
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            return recognizer.recognize_google(audio, language=language)
        except sr.WaitTimeoutError:
            raise Exception("🎤 No speech detected. Please ensure your microphone is working and try again.")
        except sr.UnknownValueError:
            raise Exception("🎤 Could not understand the audio. Please speak clearly.")
        except Exception as e:
            raise Exception(f"🎤 Voice input error: {str(e)}")

# =============================================================================
# USER INTERFACE
# =============================================================================

class ProfessionalUI:
    """Enterprise-grade user interface"""
    
    def __init__(self):
        self.knowledge_manager = KnowledgeManager()
        self.speech_engine = SpeechEngine()
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'knowledge_loaded' not in st.session_state:
            st.session_state.knowledge_loaded = False
        if 'voice_input' not in st.session_state:
            st.session_state.voice_input = ""
    
    def render(self):
        """Render complete application"""
        self._apply_professional_styles()
        self._render_header()
        
        # Main layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            self._render_sidebar()
        
        with col2:
            self._render_main_content()
    
    def _apply_professional_styles(self):
        """Apply enterprise-grade styling"""
        st.markdown(f"""
        <style>
        .main {{
            background-color: {Config.COLORS['background']};
        }}
        .header {{
            background: linear-gradient(135deg, {Config.COLORS['primary']}, {Config.COLORS['accent']});
            padding: 2rem;
            border-radius: 0 0 25px 25px;
            margin: -1rem -1rem 2rem -1rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .chat-user {{
            background: linear-gradient(135deg, {Config.COLORS['primary']}15, {Config.COLORS['accent']}15);
            padding: 1.2rem;
            border-radius: 18px 18px 5px 18px;
            margin: 0.8rem 0;
            border-left: 4px solid {Config.COLORS['primary']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        .chat-assistant {{
            background: {Config.COLORS['surface']};
            padding: 1.5rem;
            border-radius: 18px 18px 18px 5px;
            margin: 0.8rem 0;
            border: 1px solid {Config.COLORS['background']};
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .welcome-card {{
            background: {Config.COLORS['surface']};
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
            border: 2px dashed {Config.COLORS['primary']}30;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        .sidebar-card {{
            background: {Config.COLORS['surface']};
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            border: 1px solid {Config.COLORS['primary']}20;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .stButton button {{
            background: linear-gradient(135deg, {Config.COLORS['primary']}, {Config.COLORS['accent']});
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.8rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .stButton button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }}
        .quick-btn {{
            background: {Config.COLORS['secondary']} !important;
            margin: 0.3rem 0;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def _render_header(self):
        """Render professional header"""
        st.markdown("""
        <div class="header">
            <h1 style="color: white; margin: 0; font-size: 2.8rem;">🌸 AI Sister Yashvi</h1>
            <p style="font-size: 1.3rem; margin: 0.5rem 0; opacity: 0.95;">Enterprise-Grade Jain Spiritual Assistant</p>
            <div style="background: rgba(255,255,255,0.25); padding: 0.6rem 1.5rem; border-radius: 50px; display: inline-block; margin-top: 0.5rem;">
                <span style="color: #D4AF37; font-weight: 600;">🕊️ Live Knowledge Base • Professional UI/UX</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Render professional sidebar"""
        with st.sidebar:
            # Status Card
            st.markdown("""
            <div class="sidebar-card">
                <h3 style="color: #2E7D32; margin: 0 0 1rem 0;">⚡ System Status</h3>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>Knowledge Base:</span>
                    <span style="color: #2E7D32; font-weight: 600;">✅ Live</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span>Last Update:</span>
                    <span style="color: #666; font-size: 0.9em;">Just now</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Language Settings
            st.markdown("### 🌐 Language")
            self.language = st.radio(
                "Select Language:",
                ["English", "Hindi", "Gujarati"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Quick Access
            st.markdown("### 📚 Quick Wisdom")
            quick_topics = [
                ("🕊️ Ahimsa Guide", "ahimsa non-violence"),
                ("🔶 Anekantavada", "anekantavada multiple viewpoints"), 
                ("📦 Aparigraha", "aparigraha non-possessiveness"),
                ("🧘 Meditation", "meditation spiritual practice"),
                ("🌅 Daily Routine", "daily routine spiritual practice"),
                ("📜 Five Vows", "five vows mahavrata")
            ]
            
            for topic_text, search_query in quick_topics:
                if st.button(topic_text, use_container_width=True, key=f"quick_{search_query}"):
                    self._process_user_input(search_query)
            
            st.markdown("---")
            
            # Voice Input
            if st.button("🎙️ Voice Input", use_container_width=True, type="secondary"):
                self._handle_voice_input()
            
            # Management
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh", use_container_width=True):
                    if self.knowledge_manager.load_knowledge_base():
                        st.success("✅ Knowledge base updated!")
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
    
    def _render_main_content(self):
        """Render main chat interface"""
        # Handle any pending voice input
        if st.session_state.voice_input:
            self._process_user_input(st.session_state.voice_input)
            st.session_state.voice_input = ""
        
        # Chat container
        chat_container = st.container(height=600)
        
        with chat_container:
            if not st.session_state.chat_history:
                self._render_welcome_screen()
            else:
                for msg in st.session_state.chat_history:
                    self._render_chat_message(msg)
        
        # Input area
        self._render_input_area()
    
    def _render_welcome_screen(self):
        """Render professional welcome screen"""
        st.markdown("""
        <div class="welcome-card">
            <div style="font-size: 5rem; margin-bottom: 1.5rem;">🌸</div>
            <h2 style="color: #2E7D32; margin: 0 0 1rem 0;">Welcome to Professional Jain Guidance</h2>
            <p style="color: #666; font-size: 1.1rem; line-height: 1.6; margin-bottom: 2rem;">
                I'm Yashvi, your enterprise-grade AI spiritual assistant. I have access to a comprehensive 
                Jain knowledge base and can provide authentic, practical guidance for your spiritual journey.
            </p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 2rem 0;">
                <div style="background: #FAFDF7; padding: 1.2rem; border-radius: 12px; text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📚</div>
                    <div style="font-weight: 600; color: #2E7D32;">Live Knowledge</div>
                    <div style="font-size: 0.9rem; color: #666;">Updated from GitHub</div>
                </div>
                <div style="background: #FAFDF7; padding: 1.2rem; border-radius: 12px; text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎙️</div>
                    <div style="font-weight: 600; color: #2E7D32;">Voice Support</div>
                    <div style="font-size: 0.9rem; color: #666;">Multi-language</div>
                </div>
            </div>
            
            <p style="color: #D4AF37; font-style: italic; font-size: 1.1rem; margin-top: 1rem;">
                "Jai Jinendra! Ask me anything about Jain philosophy, practices, or daily spiritual living."
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_chat_message(self, msg: Dict):
        """Render professional chat message"""
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <div style="width: 32px; height: 32px; background: #2E7D32; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 0.8rem;">
                        <span style="color: white; font-weight: 600;">Y</span>
                    </div>
                    <strong style="color: #2E7D32;">You</strong>
                    <span style="margin-left: auto; color: #666; font-size: 0.8rem;">{msg.get('time', 'Now')}</span>
                </div>
                <div style="color: #1A1A1A; line-height: 1.5;">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-assistant">
                <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                    <div style="width: 32px; height: 32px; background: #D4AF37; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 0.8rem;">
                        <span style="color: white; font-weight: 600;">Y</span>
                    </div>
                    <strong style="color: #D4AF37;">Yashvi</strong>
                    <span style="margin-left: auto; color: #666; font-size: 0.8rem;">{msg.get('time', 'Now')}</span>
                </div>
                <div style="color: #1A1A1A; line-height: 1.6;">{msg["content"]}</div>
                {f'<div style="margin-top: 0.8rem; padding: 0.5rem 0.8rem; background: #FAFDF7; border-radius: 8px; border-left: 3px solid #2E7D32;"><small style="color: #666;"><strong>Source:</strong> {msg.get("category", "Jain Wisdom")} • {msg.get("topic", "General")}</small></div>' if msg.get("category") else ""}
            </div>
            """, unsafe_allow_html=True)
    
    def _render_input_area(self):
        """Render input area"""
        user_input = st.chat_input("💭 Ask about Jain philosophy, practices, or spiritual guidance...")
        
        if user_input:
            self._process_user_input(user_input)
    
    def _handle_voice_input(self):
        """Handle professional voice input"""
        try:
            language_map = {"English": "en", "Hindi": "hi", "Gujarati": "gu"}
            language_code = language_map.get(self.language, "en")
            
            with st.spinner("🎤 Listening... Speak now"):
                text = self.speech_engine.speech_to_text(language_code)
                if text:
                    st.session_state.voice_input = text
                    st.rerun()
                    
        except Exception as e:
            st.error(str(e))
    
    def _process_user_input(self, user_input: str):
        """Process user input professionally"""
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%H:%M")
        })
        
        # Generate response
        with st.spinner("🌱 Consulting knowledge base..."):
            result = self.knowledge_manager.search(user_input)
            
            # Add assistant response
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": result['content'],
                "category": result['category'],
                "topic": result['topic'],
                "time": datetime.now().strftime("%H:%M")
            })
            
            # Convert to speech
            self._speak_response(result['content'])
            
            st.rerun()
    
    def _speak_response(self, text: str):
        """Convert response to speech"""
        try:
            language_map = {"English": "en", "Hindi": "hi", "Gujarati": "gu"}
            language_code = language_map.get(self.language, "en")
            
            audio_data = self.speech_engine.text_to_speech(text, language_code)
            if audio_data:
                self._play_audio(audio_data)
        except Exception:
            pass  # Silent fail for audio errors
    
    def _play_audio(self, audio_base64: str):
        """Play audio professionally"""
        st.markdown(f"""
        <audio autoplay style="display: none">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)

# =============================================================================
# APPLICATION
# =============================================================================

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="AI Sister Yashvi - Enterprise",
        page_icon="🌸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    try:
        # Initialize and run application
        app = ProfessionalUI()
        app.render()
    except Exception as e:
        st.error(f"🚨 Application Error: {str(e)}")
        st.info("Please refresh the page to restart the application.")

if __name__ == "__main__":
    main()
