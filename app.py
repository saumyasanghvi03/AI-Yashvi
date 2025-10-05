# ==============================================================================
# AI SISTER YASHVI - PREMIUM EDITION
# Sophisticated Jain Spiritual Companion with Knowledge Memory
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

# ======================
# JAIN KNOWLEDGE MEMORY SYSTEM
# ======================

class JainKnowledgeMemory:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_memory = []
        
    def _load_knowledge_base(self):
        """Load Jain knowledge from embedded memory"""
        return {
            "core_principles": {
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
                    "content": """The nine fundamental principles that explain the nature of reality:

1. **Jiva** - Soul
2. **Ajiva** - Non-soul
3. **Asrava** - Influx of karma
4. **Bandha** - Bondage of karma
5. **Punya** - Virtuous karma
6. **Papa** - Sinful karma
7. **Samvara** - Stoppage of karma influx
8. **Nirjara** - Shedding of accumulated karma
9. **Moksha** - Liberation

Understanding these leads to spiritual progress.""",
                    "keywords": ["tattva", "principle", "karma", "moksha", "liberation"]
                },
                "ahimsa": {
                    "title": "🕊️ Ahimsa (Non-violence)",
                    "content": """The supreme principle of Jainism - causing no harm to any living being.

**Three Forms of Ahimsa:**
- **Physical** - Not harming any creature
- **Verbal** - Speaking gentle, truthful words
- **Mental** - Cultivating compassionate thoughts

**Practice:** Before any action, ask: "Will this cause harm to any living being?"""",
                    "keywords": ["ahimsa", "non-violence", "harm", "compassion", "kindness"]
                },
                "anekantavada": {
                    "title": "🔶 Anekantavada (Multiple Viewpoints)",
                    "content": """The doctrine of manifold aspects that acknowledges truth is multi-dimensional.

**Key Aspects:**
- Reality can be expressed in many ways
- Avoid absolute statements and dogmatic thinking
- Respect all perspectives while maintaining your truth

**Practice:** When facing conflict, consider at least three different viewpoints before forming conclusions.""",
                    "keywords": ["anekantavada", "viewpoints", "perspective", "truth", "relativity"]
                },
                "aparigraha": {
                    "title": "📦 Aparigraha (Non-possessiveness)",
                    "content": """Freedom from attachment to material and mental possessions.

**Benefits:**
- Inner peace and contentment
- Reduced anxiety and stress
- Spiritual clarity
- Environmental sustainability

**Practice:** Regularly give away things you haven't used in 6 months. Practice gratitude for what you have.""",
                    "keywords": ["aparigraha", "non-possessiveness", "attachment", "minimalism", "simplicity"]
                }
            },
            "spiritual_practices": {
                "meditation": {
                    "title": "🧘‍♀️ Meditation Practices",
                    "content": """Jain meditation techniques for spiritual development:

**Preksha Meditation:**
- Focus on breath and body awareness
- 20-30 minutes daily practice
- Develops concentration and mindfulness

**Samayika:**
- 48-minute practice of equanimity
- Cultivates mental balance
- Can be done at home or temple

**Anupreksha:**
- Contemplation on fundamental truths
- Reflection on impermanence and non-attachment""",
                    "keywords": ["meditation", "samayika", "preksha", "contemplation", "mindfulness"]
                },
                "daily_routine": {
                    "title": "🌅 Daily Spiritual Routine",
                    "content": """Ideal daily practices for spiritual growth:

**Morning (5-6 AM):**
- Wake before sunrise
- Recite Navkar Mantra
- Practice Samayika meditation
- Set intentions for practicing Ahimsa

**Throughout Day:**
- Mindful eating with gratitude
- Conscious speech and actions
- Regular moments of mindfulness

**Evening:**
- Review day's thoughts and actions
- Practice Pratikraman (repentance)
- Plan improvements for tomorrow""",
                    "keywords": ["routine", "daily", "practice", "schedule", "discipline"]
                }
            },
            "scriptures": {
                "tattvartha_sutra": {
                    "title": "📖 Tattvartha Sutra",
                    "content": """The foundational text of Jain philosophy composed by Acharya Umaswati.

**Key Teachings:**
- "Samyag-darshan-jnana-charitrani moksha-margah" - Right faith, knowledge, and conduct form the path to liberation
- Detailed explanation of six dravyas and nine tattvas
- Guide to spiritual progress and ethical living

Considered the most authoritative Jain scripture accepted by all traditions.""",
                    "keywords": ["tattvartha", "sutra", "scripture", "umaswati", "philosophy"]
                },
                "acharanga_sutra": {
                    "title": "📜 Acharanga Sutra",
                    "content": """The first Anga text containing Lord Mahavira's teachings on conduct.

**Key Principles:**
- Detailed instructions on Ahimsa
- Guidelines for ascetic life
- Emphasis on mindful movement and action
- Foundation of Jain ethical code

One of the oldest Jain texts, essential for understanding early Jain practices.""",
                    "keywords": ["acharanga", "mahavira", "conduct", "ethics", "anga"]
                }
            },
            "prayers": {
                "navkar_mantra": {
                    "title": "🕉️ Navkar Mantra",
                    "content": """The most fundamental Jain prayer:

**Mantra:**
"Namo Arihantanam
Namo Siddhanam
Namo Ayariyanam
Namo Uvajjhayanam
Namo Loe Savva Sahunam
Eso Panch Namukkaro
Savva Pava Panasano
Mangalanam Cha Savvesim
Padhamam Havai Mangalam"

**Meaning:** I bow to the Arihants, I bow to the Siddhas, I bow to the Acharyas, I bow to the Upadhyayas, I bow to all Sadhus. This fivefold salutation destroys all sins and is the foremost of all auspicious things.""",
                    "keywords": ["navkar", "mantra", "prayer", "namokar", "arihant"]
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
        
        # Check content (first 100 chars)
        content_preview = topic_data['content'][:100].lower()
        content_matches = sum(1 for word in query_words if word in content_preview)
        score += content_matches
        
        return score
    
    def add_conversation_memory(self, user_input, response):
        """Store important conversations for context"""
        self.conversation_memory.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'response': response
        })
        
        # Keep only last 20 conversations
        if len(self.conversation_memory) > 20:
            self.conversation_memory.pop(0)

# ======================
# PREMIUM RESPONSE ENGINE
# ======================

class PremiumResponseEngine:
    def __init__(self, knowledge_memory):
        self.knowledge_memory = knowledge_memory
        self.conversation_context = []
        self.user_profile = {}
        
    def analyze_sentiment(self, text):
        """Basic sentiment analysis for empathetic responses"""
        positive_words = ['happy', 'good', 'great', 'wonderful', 'excited', 'peaceful', 'grateful', 'joy', 'bliss']
        negative_words = ['sad', 'angry', 'stressed', 'worried', 'anxious', 'tired', 'hurt', 'difficult', 'problem']
        
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
        """Generate sophisticated, context-aware responses using knowledge memory"""
        
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
        
        # Search knowledge base first
        knowledge_results = self.knowledge_memory.search_knowledge(user_input)
        
        # Greeting responses
        if any(word in input_lower for word in ["hello", "hi", "hey", "namaste", "jai jinendra"]):
            return self._generate_greeting(sentiment, mode, knowledge_results)
        
        # If knowledge found, use it
        if knowledge_results:
            return self._generate_knowledge_response(knowledge_results, user_input, mode)
            
        # Emotional support
        if sentiment == "negative":
            return self._generate_emotional_support(user_input, mode)
            
        # Spiritual guidance
        if any(word in input_lower for word in ["guide", "help", "advice", "what should", "how to"]):
            return self._generate_guidance(user_input, mode)
            
        # Default intelligent response
        return self._generate_contextual_response(user_input, mode)
    
    def _generate_greeting(self, sentiment, mode, knowledge_results):
        """Generate sophisticated greetings"""
        base_greetings = {
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
        
        greeting = random.choice(base_greetings[sentiment])
        
        # Add knowledge suggestion if available
        if knowledge_results and sentiment == "neutral":
            topic = knowledge_results[0]['title'].split(' ')[1]  # Get main topic
            greeting += f" I notice you might be interested in {topic}. Would you like to explore this?"
            
        return greeting
    
    def _generate_knowledge_response(self, knowledge_results, user_input, mode):
        """Generate response based on knowledge base findings"""
        primary_topic = knowledge_results[0]
        
        if mode == "Quick Chat":
            # Extract key points for quick response
            content = primary_topic['content']
            # Take first sentence or two for quick mode
            quick_summary = '. '.join(content.split('.')[:2]) + '.'
            return f"{primary_topic['title']}\n\n{quick_summary}\n\n💡 Want to explore this deeper?"
        else:
            # Full detailed response for deep mode
            return f"""**{primary_topic['title']}**

{primary_topic['content']}

**Reflection:** How does this wisdom resonate with your current journey?"""
    
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
        self.knowledge_memory = JainKnowledgeMemory()
        self.response_engine = PremiumResponseEngine(self.knowledge_memory)
        
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
                    Jain Knowledge Memory • Spiritual Analytics • Personalized Guidance
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
            
            # Knowledge Explorer
            st.markdown("### 📚 Wisdom Explorer")
            if st.button("Browse Jain Wisdom", use_container_width=True):
                self.show_knowledge_explorer()
                
            st.markdown("---")
            
            # Spiritual Dashboard
            st.markdown("### 📊 Your Journey")
            if st.button("View Spiritual Insights", use_container_width=True):
                self.show_spiritual_insights()
                
            st.markdown("---")
            
            # Clear History
            if st.button("🔄 New Conversation", use_container_width=True, type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
                
            return mode, LANG_MAP[selected_lang]
    
    def show_knowledge_explorer(self):
        """Show interactive knowledge explorer"""
        st.markdown("### 📖 Jain Wisdom Library")
        
        categories = self.knowledge_memory.knowledge_base.keys()
        selected_category = st.selectbox("Choose Category", list(categories))
        
        if selected_category:
            topics = self.knowledge_memory.knowledge_base[selected_category]
            topic_names = [topics[key]['title'] for key in topics.keys()]
            
            selected_topic_name = st.selectbox("Select Topic", topic_names)
            
            # Find the selected topic
            for topic_key, topic_data in topics.items():
                if topic_data['title'] == selected_topic_name:
                    st.markdown(f"### {topic_data['title']}")
                    st.markdown(topic_data['content'])
                    break
    
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
                I am Yashvi, your AI spiritual companion with authentic Jain knowledge. 
                Together, we'll explore timeless wisdom, practice mindfulness, and nurture your spiritual growth.
            </p>
            <div style='
                background: {COLORS['background']};
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                text-align: left;
            '>
                <strong>My knowledge includes:</strong><br>
                • Six Dravyas & Nine Tattvas<br>
                • Five Mahavratas and spiritual practices<br>  
                • Meditation techniques and daily routines<br>
                • Scriptures like Tattvartha Sutra
            </div>
            <p style='color: {COLORS["secondary"]}; font-style: italic;'>
                "May our conversation bring you peace and authentic wisdom"
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
        
        # Generate premium response using knowledge memory
        with st.spinner("🌱 Consulting wisdom..."):
            response = self.response_engine.generate_premium_response(
                user_input, mode, lang_code
            )
            
            # Add AI response to history
            st.session_state.chat_history.append({
                "role": "Yashvi",
                "content": response
            })
            
            # Store in conversation memory
            self.knowledge_memory.add_conversation_memory(user_input, response)
            
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
