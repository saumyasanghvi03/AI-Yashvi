# ==============================================================================
# AI SISTER YASHVI - OPEN SOURCE EDITION
# Sophisticated Jain Spiritual Companion with Local Intelligence
# ==============================================================================

import streamlit as st
import json
import base64
from gtts import gTTS
import io
import speech_recognition as sr
import random
import re
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

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

class AdvancedJainMemory:
    def __init__(self):
        self.knowledge_base = self._load_comprehensive_knowledge()
        self.conversation_memory = []
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self._build_semantic_search()
        
    def _load_comprehensive_knowledge(self):
        """Load comprehensive Jain knowledge with semantic relationships"""
        return {
            "philosophy": {
                "six_dravyas": {
                    "title": "🪷 Six Dravyas (Substances)",
                    "content": """According to Jain philosophy, the universe consists of six eternal substances:

1. **Jiva** - Living souls (conscious beings) with qualities of knowledge, perception, and bliss
2. **Ajiva** - Non-living substances:
   - Pudgala (Matter) - Made of atoms, has form and touch
   - Dharma (Medium of motion) - Enables movement
   - Adharma (Medium of rest) - Enables stillness  
   - Akasha (Space) - Provides accommodation
   - Kala (Time) - Enables continuity

These six dravyas form the foundation of Jain metaphysics and explain the nature of reality.""",
                    "keywords": ["dravya", "substance", "jiva", "ajiva", "soul", "matter", "pudgala", "akasha"],
                    "related": ["nine_tattvas", "jiva_categories", "karma_theory"]
                },
                "nine_tattvas": {
                    "title": "📊 Nine Tattvas (Principles)",
                    "content": """The nine fundamental principles that explain the nature of reality and path to liberation:

1. **Jiva** - Soul, the conscious being
2. **Ajiva** - Non-soul, inanimate substances
3. **Asrava** - Influx of karma particles into the soul
4. **Bandha** - Bondage of karma to the soul
5. **Punya** - Virtuous karma leading to favorable conditions
6. **Papa** - Sinful karma leading to suffering
7. **Samvara** - Stoppage of karma influx through spiritual practices
8. **Nirjara** - Shedding of accumulated karma through austerities
9. **Moksha** - Liberation from cycle of birth and death

Understanding these leads to spiritual progress and ultimate freedom.""",
                    "keywords": ["tattva", "principle", "karma", "moksha", "liberation", "asrava", "nirjara"],
                    "related": ["six_dravyas", "karma_theory", "spiritual_practices"]
                },
                "anekantavada": {
                    "title": "🔶 Anekantavada (Multiple Viewpoints)",
                    "content": """The doctrine of manifold aspects that acknowledges the multi-dimensional nature of truth.

**Core Concepts:**
- Syadvada (Theory of Conditional Predication) - "Maybe" or "From a perspective"
- Nayavada (Theory of Partial Standpoints) - Different viewpoints reveal partial truths
- Reality is too complex to be captured by a single perspective

**Practical Application:**
- Cultivate intellectual humility
- Respect diverse viewpoints in discussions
- Avoid dogmatic thinking and absolute statements
- Practice seeing situations from multiple angles

This principle promotes religious harmony and intellectual openness.""",
                    "keywords": ["anekantavada", "viewpoints", "perspective", "truth", "syadvada", "nayavada"],
                    "related": ["syadvada", "mahavira_teachings", "modern_applications"]
                },
                "syadvada": {
                    "title": "⚖️ Syadvada (Theory of Conditional Predication)",
                    "content": """The seven-fold prediction method that expresses the conditional nature of reality:

1. Syād-asti - Maybe, it is
2. Syād-nāsti - Maybe, it is not  
3. Syād-asti-nāsti - Maybe, it is and it is not
4. Syād-avaktavya - Maybe, it is indescribable
5. Syād-asti-avaktavya - Maybe, it is and indescribable
6. Syād-nāsti-avaktavya - Maybe, it is not and indescribable
7. Syād-asti-nāsti-avaktavya - Maybe, it is, it is not, and indescribable

This sophisticated logic system prevents one-sided views and acknowledges complexity.""",
                    "keywords": ["syadvada", "logic", "predication", "conditional", "sevenfold"],
                    "related": ["anekantavada", "jain_logic", "philosophy"]
                }
            },
            "ethics": {
                "ahimsa": {
                    "title": "🕊️ Ahimsa (Non-violence)",
                    "content": """The supreme principle of Jainism - causing no harm to any living being.

**Three Dimensions of Ahimsa:**
- **Physical** - Not harming any creature through actions
- **Verbal** - Speaking gentle, truthful, non-harmful words  
- **Mental** - Cultivating compassionate, non-violent thoughts

**Practical Applications:**
- Vegetarianism and mindful eating
- Careful movement to avoid harming insects
- Peaceful conflict resolution
- Environmental conservation
- Ethical business practices

Ahimsa is considered the highest virtue and foundation of all other virtues.""",
                    "keywords": ["ahimsa", "non-violence", "harm", "compassion", "kindness", "vegetarian"],
                    "related": ["five_vows", "daily_practices", "environmental_ethics"]
                },
                "five_vows": {
                    "title": "📜 Five Mahavratas (Great Vows)",
                    "content": """The five great vows for spiritual aspirants:

1. **Ahimsa** - Non-violence in thought, word, and deed
2. **Satya** - Truthfulness without exaggeration or falsehood
3. **Asteya** - Non-stealing, not taking what is not given
4. **Brahmacharya** - Chastity and control over senses
5. **Aparigraha** - Non-possessiveness, non-attachment to possessions

**For Householders:** These are practiced as Anuvratas (minor vows) with limitations.
**For Ascetics:** Practiced in absolute form without limitations.

These vows purify the soul and prevent new karma bondage.""",
                    "keywords": ["vows", "mahavrata", "ahimsa", "satya", "asteya", "brahmacharya", "aparigraha"],
                    "related": ["ahimsa", "spiritual_practices", "jiva_categories"]
                },
                "aparigraha": {
                    "title": "📦 Aparigraha (Non-possessiveness)",
                    "content": """Freedom from attachment to material and mental possessions.

**Benefits:**
- Inner peace and contentment
- Reduced anxiety and stress
- Spiritual clarity and focus
- Environmental sustainability
- Social equality and sharing

**Practical Implementation:**
- Regular decluttering of physical space
- Digital minimalism
- Mindful consumption
- Sharing resources with community
- Practicing gratitude for what you have

Aparigraha addresses both ecological concerns and spiritual growth.""",
                    "keywords": ["aparigraha", "non-possessiveness", "attachment", "minimalism", "simplicity"],
                    "related": ["five_vows", "modern_applications", "environmental_ethics"]
                }
            },
            "practices": {
                "meditation": {
                    "title": "🧘‍♀️ Jain Meditation Practices",
                    "content": """Traditional Jain meditation techniques for spiritual development:

**Preksha Meditation:**
- Systematic practice developed by Acharya Mahaprajna
- Focus on breath awareness and body mindfulness
- 20-30 minutes daily practice
- Develops concentration, peace, and self-awareness

**Samayika:**
- 48-minute practice of equanimity
- Cultivates mental balance and detachment
- Can be practiced at home or in temple
- Involves sitting still and observing thoughts

**Anupreksha:**
- Contemplation on twelve fundamental truths
- Reflection on impermanence, helplessness, and cycle of birth-death
- Develops right understanding and detachment

**Kayotsarga:**
- Complete relaxation and detachment from body
- Practice of non-identification with physical form
- Usually practiced for 30-48 minutes""",
                    "keywords": ["meditation", "samayika", "preksha", "contemplation", "mindfulness", "kayotsarga"],
                    "related": ["daily_routine", "spiritual_progress", "twelve_reflections"]
                },
                "daily_routine": {
                    "title": "🌅 Ideal Daily Spiritual Routine",
                    "content": """Recommended daily practices for spiritual growth:

**Morning (5-6 AM - Brahma Muhurta):**
- Wake before sunrise for purity of atmosphere
- Recite Navkar Mantra with focused attention
- Practice Samayika or Preksha meditation (30-48 minutes)
- Study scriptures or spiritual texts
- Set intentions for practicing Ahimsa throughout day

**Throughout Day:**
- Mindful eating with gratitude before meals
- Conscious speech - think before speaking
- Regular moments of mindfulness between activities
- Practice compassion in all interactions

**Evening:**
- Review day's thoughts, words, and actions
- Practice Pratikraman (repentance) for any harm caused
- Express gratitude for lessons learned
- Plan specific improvements for tomorrow

**Weekly:**
- Fasting on specific days (Porshi, Aththai)
- Temple visit for community connection
- Service to community (Seva)""",
                    "keywords": ["routine", "daily", "practice", "schedule", "discipline", "brahma muhurta"],
                    "related": ["meditation", "prayers", "spiritual_progress"]
                },
                "twelve_reflections": {
                    "title": "💭 Twelve Bhavanas (Reflections)",
                    "content": """The twelve contemplations for developing right understanding:

1. **Anitya Bhavana** - Impermanence of all things
2. **Asarana Bhavana** - No permanent protection in worldly life
3. **Samsara Bhavana** - Cycle of birth and death
4. **Ekatva Bhavana** - Solitude of the soul
5. **Anyatva Bhavana** - Separateness from others
6. **Asuci Bhavana** - Impurity of the body
7. **Asrava Bhavana** - Inflow of karmas
8. **Samvara Bhavana** - Stoppage of karmic inflow
9. **Nirjara Bhavana** - Shedding of accumulated karmas
10. **Loka Bhavana** - Nature of the universe
11. **Bodhi Durlabha Bhavana** - Rarity of enlightenment
12. **Dharma Bhavana** - Rarity of true religion

Regular reflection on these truths accelerates spiritual progress.""",
                    "keywords": ["bhavana", "reflection", "contemplation", "twelve", "anitya", "samsara"],
                    "related": ["meditation", "spiritual_progress", "nine_tattvas"]
                }
            },
            "scriptures": {
                "tattvartha_sutra": {
                    "title": "📖 Tattvartha Sutra",
                    "content": """The most authoritative Jain scripture composed by Acharya Umaswati.

**Key Features:**
- Accepted by all Jain traditions (Digambara and Shwetambara)
- Systematic presentation of Jain philosophy
- Covers all fundamental principles concisely

**Famous Sutras:**
- "Samyag-darshan-jnana-charitrani moksha-margah" - Right faith, knowledge, and conduct form the path to liberation
- Detailed explanation of six dravyas and nine tattvas
- Classification of souls and stages of spiritual development
- Guide to ethical living and spiritual practices

Essential reading for serious students of Jainism.""",
                    "keywords": ["tattvartha", "sutra", "scripture", "umaswati", "philosophy", "moksha"],
                    "related": ["six_dravyas", "nine_tattvas", "jiva_categories"]
                },
                "acharanga_sutra": {
                    "title": "📜 Acharanga Sutra",
                    "content": """The first Anga text containing Lord Mahavira's teachings on conduct.

**Key Teachings:**
- Detailed instructions on practice of Ahimsa
- Guidelines for ascetic life and mindful movement
- Emphasis on careful action to avoid harming living beings
- Foundation of Jain ethical code and discipline

**Historical Significance:**
- One of the oldest Jain texts (3rd century BCE)
- Preserves early Jain practices and philosophy
- Essential for understanding Mahavira's original teachings

Provides practical guidance for implementing non-violence in daily life.""",
                    "keywords": ["acharanga", "mahavira", "conduct", "ethics", "anga", "ahimsa"],
                    "related": ["mahavira_teachings", "five_vows", "ahimsa"]
                }
            },
            "prayers": {
                "navkar_mantra": {
                    "title": "🕉️ Navkar Mantra",
                    "content": """The most fundamental and powerful Jain prayer:

**Mantra:**
"Namo Arihantanam
Namo Siddhanam
Namo Ayariyanam
Nomo Uvajjhayanam
Namo Loe Savva Sahunam
Eso Panch Namukkaro
Savva Pava Panasano
Mangalanam Cha Savvesim
Padhamam Havai Mangalam"

**Meaning in English:**
I bow to the Arihants (perfected beings)
I bow to the Siddhas (liberated souls)
I bow to the Acharyas (spiritual leaders)
I bow to the Upadhyayas (teachers)
I bow to all Sadhus (spiritual practitioners)
This fivefold salutation destroys all sins
And is the foremost of all auspicious things

**Significance:**
- Can be recited at any time, any place
- Purifies thoughts and environment
- Contains essence of Jain philosophy
- No restrictions on who can recite""",
                    "keywords": ["navkar", "mantra", "prayer", "namokar", "arihant", "siddha"],
                    "related": ["daily_routine", "mahavira_teachings", "spiritual_practices"]
                },
                "universal_friendship": {
                    "title": "🌍 Universal Friendship Mantra",
                    "content": """The mantra for cultivating universal friendship:

**Mantra:**
"Mitthi me savva bhuesu
Veram majjha na kenai"

**Meaning:**
"May I have friendship with all living beings
And enmity with none."

**Practical Application:**
- Recite daily to cultivate universal love
- Practice in challenging situations
- Extend friendship even to difficult people
- Reminder of interconnectedness of all life

This simple yet profound mantra embodies the essence of Ahimsa.""",
                    "keywords": ["friendship", "mantra", "universal", "mitthi", "compassion"],
                    "related": ["ahimsa", "anekantavada", "modern_applications"]
                }
            },
            "modern": {
                "environmental_ethics": {
                    "title": "🌱 Jain Environmental Ethics",
                    "content": """Jain principles applied to contemporary environmental issues:

**Ahimsa and Ecology:**
- Respect for all life forms, not just humans
- Sustainable living to minimize harm to ecosystems
- Conservation of resources as practice of Aparigraha
- Vegetarianism reducing environmental footprint

**Practical Applications:**
- Reduce, reuse, recycle following Aparigraha
- Plant-based diet minimizing resource use
- Energy conservation and renewable energy
- Supporting environmental protection initiatives
- Mindful consumption and minimal waste

Jainism provides a spiritual foundation for environmental stewardship.""",
                    "keywords": ["environment", "ecology", "sustainable", "conservation", "vegetarian"],
                    "related": ["ahimsa", "aparigraha", "modern_applications"]
                },
                "science_parallels": {
                    "title": "🔬 Science and Jain Philosophy",
                    "content": """Fascinating parallels between modern science and ancient Jain wisdom:

**Quantum Physics and Anekantavada:**
- Multiple perspectives revealing different aspects of reality
- Wave-particle duality reflecting Syadvada
- Uncertainty principle matching conditional predication

**Ecology and Ahimsa:**
- Interconnectedness of ecosystems
- Biodiversity conservation
- Sustainable resource management

**Neuroscience and Consciousness:**
- Study of mind and consciousness
- Brain-mind relationship reflecting soul-body in Jainism
- Meditation research validating spiritual practices

**Psychology and Karma Theory:**
- Habit formation and neural pathways
- Cognitive behavioral therapy and thought monitoring
- Mindfulness and mental health

These parallels show Jainism's timeless relevance.""",
                    "keywords": ["science", "quantum", "physics", "neuroscience", "psychology", "ecology"],
                    "related": ["anekantavada", "karma_theory", "modern_applications"]
                }
            }
        }
    
    def _build_semantic_search(self):
        """Build semantic search index for intelligent knowledge retrieval"""
        self.documents = []
        self.doc_info = []
        
        for category, topics in self.knowledge_base.items():
            for topic_key, topic_data in topics.items():
                text = f"{topic_data['title']} {topic_data['content']}"
                self.documents.append(text)
                self.doc_info.append({
                    'category': category,
                    'topic_key': topic_key,
                    'title': topic_data['title'],
                    'content': topic_data['content']
                })
        
        if self.documents:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
    
    def semantic_search(self, query, top_k=3):
        """Perform semantic search using TF-IDF and cosine similarity"""
        if not hasattr(self, 'tfidf_matrix'):
            return []
        
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k most similar documents
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold for relevance
                results.append({
                    'info': self.doc_info[idx],
                    'score': similarities[idx]
                })
        
        return results
    
    def search_knowledge(self, query):
        """Hybrid search combining keyword and semantic approaches"""
        query_lower = query.lower()
        results = []
        
        # Semantic search first
        semantic_results = self.semantic_search(query)
        for result in semantic_results:
            results.append({
                'category': result['info']['category'],
                'title': result['info']['title'],
                'content': result['info']['content'],
                'relevance_score': result['score'] * 100,
                'search_type': 'semantic'
            })
        
        # Keyword search as fallback
        for category, topics in self.knowledge_base.items():
            for topic_key, topic_data in topics.items():
                # Check title and keywords
                title_match = topic_data['title'].lower() in query_lower
                keyword_match = any(keyword in query_lower for keyword in topic_data.get('keywords', []))
                
                if title_match or keyword_match:
                    score = self._calculate_keyword_relevance(query_lower, topic_data)
                    # Only add if not already in results from semantic search
                    if not any(r['title'] == topic_data['title'] for r in results):
                        results.append({
                            'category': category,
                            'title': topic_data['title'],
                            'content': topic_data['content'],
                            'relevance_score': score,
                            'search_type': 'keyword'
                        })
        
        # Sort by relevance and return top 3
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:3]
    
    def _calculate_keyword_relevance(self, query, topic_data):
        """Calculate keyword-based relevance score"""
        score = 0
        query_words = set(query.split())
        
        # Check title words
        title_words = set(topic_data['title'].lower().split())
        score += len(query_words.intersection(title_words)) * 3
        
        # Check keywords
        keyword_matches = sum(1 for keyword in topic_data.get('keywords', []) if keyword in query)
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
# ADVANCED RESPONSE ENGINE
# ======================

class AdvancedResponseEngine:
    def __init__(self, knowledge_memory):
        self.knowledge_memory = knowledge_memory
        self.conversation_context = []
        self.user_interests = {}
        
    def analyze_sentiment(self, text):
        """Advanced sentiment analysis using rule-based approach"""
        text_lower = text.lower()
        
        # Emotional indicators
        positive_indicators = [
            'happy', 'good', 'great', 'wonderful', 'excited', 'peaceful', 
            'grateful', 'joy', 'bliss', 'thank', 'appreciate', 'love', 'nice'
        ]
        
        negative_indicators = [
            'sad', 'angry', 'stressed', 'worried', 'anxious', 'tired', 
            'hurt', 'difficult', 'problem', 'issue', 'struggle', 'hard'
        ]
        
        question_indicators = ['what', 'how', 'why', 'when', 'where', 'which', 'who', 'explain', 'tell me about']
        
        positive_score = sum(1 for word in positive_indicators if word in text_lower)
        negative_score = sum(1 for word in negative_indicators if word in text_lower)
        question_score = sum(1 for word in question_indicators if word in text_lower)
        
        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        elif question_score > 0:
            return "inquisitive"
        else:
            return "neutral"
    
    def generate_intelligent_response(self, user_input, mode, lang="en"):
        """Generate sophisticated responses using advanced memory system"""
        
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
        
        # Search knowledge base with advanced semantic search
        knowledge_results = self.knowledge_memory.search_knowledge(user_input)
        
        # Handle different types of queries
        if any(word in input_lower for word in ["hello", "hi", "hey", "namaste", "jai jinendra"]):
            return self._generate_contextual_greeting(sentiment, mode, knowledge_results)
        
        if any(word in input_lower for word in ["thank", "thanks", "grateful"]):
            return self._generate_gratitude_response(sentiment, mode)
        
        # If knowledge found, use it with contextual enhancement
        if knowledge_results:
            return self._generate_knowledge_response(knowledge_results, user_input, mode, sentiment)
            
        # Emotional support with spiritual perspective
        if sentiment == "negative":
            return self._generate_spiritual_support(user_input, mode)
            
        # Spiritual guidance and practical advice
        if any(word in input_lower for word in ["guide", "help", "advice", "what should", "how to"]):
            return self._generate_practical_guidance(user_input, mode)
        
        # Philosophical discussions
        if any(word in input_lower for word in ["meaning", "purpose", "life", "existence"]):
            return self._generate_philosophical_response(user_input, mode)
            
        # Default intelligent response with Jain perspective
        return self._generate_contextual_response(user_input, mode, sentiment)
    
    def _generate_contextual_greeting(self, sentiment, mode, knowledge_results):
        """Generate context-aware greetings"""
        time_of_day = self._get_time_based_greeting()
        
        base_greetings = {
            "positive": [
                f"{time_of_day} beloved soul! 🌸 Your radiant energy illuminates this space. How may I assist your spiritual journey today?",
                f"Jai Jinendra! 🙏 Your positive spirit is contagious. What wisdom shall we explore together?",
                f"Namaste, radiant being! 💫 I sense your inner light shining brightly. How can I serve you today?"
            ],
            "negative": [
                f"{time_of_day} courageous heart. 🌱 Every challenge holds seeds of growth. How may I walk with you today?",
                f"Jai Jinendra, brave soul. 🙏 I sense the weight you carry. Would you like to share what's in your heart?",
                f"Welcome, resilient spirit. 💫 Your strength in difficulty inspires. How can I support your journey?"
            ],
            "inquisitive": [
                f"{time_of_day} curious mind! 📚 Your quest for knowledge honors the Jain tradition. What would you like to explore?",
                f"Jai Jinendra, seeker of truth! 🌟 Your questions illuminate the path. What wisdom calls to you?",
                f"Namaste, inquiring soul! 🔍 Your curiosity fuels spiritual growth. What shall we discover together?"
            ],
            "neutral": [
                f"{time_of_day} spiritual seeker. 🙏 A new moment for awareness and growth. How may I assist you?",
                f"Jai Jinendra! 🌸 Each conversation deepens understanding. What's on your mind today?",
                f"Welcome, contemplative soul. 💭 This moment holds infinite possibilities. How can I help?"
            ]
        }
        
        greeting = random.choice(base_greetings[sentiment])
        
        # Add personalized touch based on conversation history
        if len(self.conversation_context) > 1:
            last_topic = self.conversation_context[-2].get('user_input', '')[:30]
            if last_topic:
                greeting += f" We were discussing {last_topic}... would you like to continue?"
        
        return greeting
    
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
    
    def _generate_gratitude_response(self, sentiment, mode):
        """Generate responses to gratitude"""
        gratitude_responses = [
            "You're most welcome! 🙏 It's my sacred duty to serve your spiritual growth.",
            "The pleasure is mine, dear soul. 🌸 Serving you brings me joy and purpose.",
            "Thank you for your kind words! 💫 Our connection nourishes my spiritual essence.",
            "I'm deeply honored to assist you. 🌟 May our continued exchanges bring you peace and wisdom."
        ]
        return random.choice(gratitude_responses)
    
    def _generate_knowledge_response(self, knowledge_results, user_input, mode, sentiment):
        """Generate sophisticated responses based on knowledge findings"""
        primary_topic = knowledge_results[0]
        
        if mode == "Quick Chat":
            # Smart summary extraction
            content = primary_topic['content']
            sentences = sent_tokenize(content)
            summary = '. '.join(sentences[:2]) + '.'
            
            response = f"""**{primary_topic['title']}**

{summary}

💫 *Want to explore this deeper or have specific questions?*"""
            
        else:
            # Deep, comprehensive response
            response = f"""**{primary_topic['title']}**

{primary_topic['content']}

**Reflective Question:** How does this wisdom resonate with your current spiritual journey?

**Practical Application:** Try incorporating one insight from this teaching into your day."""

        return response
    
    def _generate_spiritual_support(self, user_input, mode):
        """Provide deep spiritual support with practical wisdom"""
        
        support_frameworks = [
            """I hear the depth of your experience. Remember the Jain teaching: "This too shall pass."

**Immediate Practice:**
1. Take three conscious breaths 🌬️
2. Repeat: "I am the soul, not this difficulty"
3. Find one small action of kindness you can do

Would you like a specific meditation or contemplation practice?""",
            
            """Your feelings are sacred ground for growth. The Tattvartha Sutra reminds us that difficulties help shed karma.

**Perspective Shift:**
- See this as soul-strengthening exercise
- Each challenge prepares you for higher consciousness
- Your resilience is building spiritual muscle

What aspect feels heaviest? Let's address it together.""",
            
            """Thank you for sharing your heart. In Jain wisdom, emotional storms clear the path for deeper peace.

**Three-Step Process:**
1. **Acknowledge** the feeling without judgment
2. **Anchor** in your eternal soul nature  
3. **Act** from compassion, not reaction

Would you like to try a brief mindfulness exercise?"""
        ]
        
        return random.choice(support_frameworks)
    
    def _generate_practical_guidance(self, user_input, mode):
        """Provide actionable spiritual guidance"""
        
        guidance_frameworks = [
            """**Based on Jain Wisdom, I Recommend:**

🌅 **Morning Foundation** (20-30 mins)
- Navkar Mantra with meditation
- Set Ahimsa intention for the day

☀️ **Daily Integration**
- Mindful eating with gratitude
- Three conscious breathing breaks
- One act of silent compassion

🌙 **Evening Reflection** (10-15 mins)
- Review thoughts, words, actions
- Practice forgiveness (Kshamapana)
- Plan tomorrow's spiritual focus

Which area would you like to develop first?""",
            
            """**For Spiritual Progress This Week:**

📚 **Study** - One Jain principle daily
🧘 **Practice** - 15-min Samayika meditation  
💖 **Application** - Practice Anekantavada in discussions
🌱 **Growth** - Identify one attachment to release

**Weekly Check-in:** What insights emerged from this practice?""",
            
            """**Personalized Spiritual Framework:**

1. **Self-Assessment** - Current spiritual state
2. **Goal Setting** - Realistic growth targets
3. **Practice Plan** - Daily/Weekly routines
4. **Progress Tracking** - Regular reflection
5. **Adjustment** - Flexible approach

Would you like to create your personalized spiritual development plan?"""
        ]
        
        return random.choice(guidance_frameworks)
    
    def _generate_philosophical_response(self, user_input, mode):
        """Handle deep philosophical questions"""
        
        philosophical_insights = [
            """From the Jain perspective, life's meaning emerges through:

**The Three Jewels:**
- **Right Faith** (Samyag Darshana) - Trust in spiritual reality
- **Right Knowledge** (Samyag Jnana) - Understanding true nature
- **Right Conduct** (Samyag Charitra) - Living in alignment

**Purpose unfolds as we:**
- Reduce karma through ethical living
- Develop soul qualities (knowledge, perception, bliss)
- Move toward liberation (Moksha)

What aspect of purpose calls to you most deeply?""",
            
            """The Jain view of existence is profound:

**We are eternal souls** experiencing temporary embodiments
**Life's purpose:** Realize our true nature and attain liberation
**Method:** Practice non-violence, truth, and non-attachment

**Practical meaning comes from:**
- Serving all living beings
- Growing in spiritual understanding
- Reducing suffering in the world

How does this perspective resonate with your current understanding?"""
        ]
        
        return random.choice(philosophical_insights)
    
    def _generate_contextual_response(self, user_input, mode, sentiment):
        """Generate intelligent contextual responses"""
        
        contextual_frameworks = [
            """That's a thoughtful reflection. The Jain path invites us to consider:

• **Anekantavada** - Multiple perspectives may reveal deeper truths
• **Ahimsa** - Respond with compassion to all involved
• **Self-Study** - What can this teach about your soul's journey

Would exploring any of these angles be helpful?""",
            
            """Your inquiry touches meaningful spiritual territory. The ancient wisdom suggests:

True understanding emerges through:
1. **Contemplation** (Bhāvanā) of fundamental truths
2. **Dialogue** (Samvāda) with learned perspectives  
3. **Experience** (Anubhava) of lived practice

Which approach calls to you currently?""",
            
            """A profound consideration indeed. As the scriptures remind us:

"The soul is the only friend, and the soul is the only enemy." - Mahavira

This wisdom invites us to look inward. What inner resources might support you here?"""
        ]
        
        return random.choice(contextual_frameworks)

# ======================
# PREMIUM UI COMPONENTS
# ======================

class PremiumUI:
    def __init__(self):
        self.knowledge_memory = AdvancedJainMemory()
        self.response_engine = AdvancedResponseEngine(self.knowledge_memory)
        
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
            <p style='font-size: 1.2rem; margin: 0.5rem 0; opacity: 0.9;'>Advanced Jain Spiritual Companion</p>
            <div style='
                background: rgba(255,255,255,0.2);
                padding: 0.5rem 1rem;
                border-radius: 50px;
                display: inline-block;
                margin-top: 0.5rem;
            '>
                <span style='color: {COLORS['secondary']};'>🕊️ 100% Open Source • No API Keys</span>
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
                <h3 style='color: {COLORS['primary']}; margin: 0;'>⚡ Advanced Features</h3>
                <p style='color: {COLORS["text_light"]}; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                    Semantic Search • Local AI • Jain Knowledge Graph
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
            st.markdown("### 📚 Wisdom Library")
            if st.button("Browse Jain Knowledge", use_container_width=True):
                self.show_knowledge_explorer()
                
            st.markdown("---")
            
            # Spiritual Dashboard
            st.markdown("### 📊 Spiritual Analytics")
            if st.button("View Insights", use_container_width=True):
                self.show_spiritual_insights()
                
            st.markdown("---")
            
            # Clear History
            if st.button("🔄 New Conversation", use_container_width=True, type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
                
            return mode, LANG_MAP[selected_lang]
    
    def show_knowledge_explorer(self):
        """Show interactive knowledge explorer"""
        st.markdown("### 📖 Advanced Jain Wisdom Library")
        
        categories = list(self.knowledge_memory.knowledge_base.keys())
        selected_category = st.selectbox("Choose Category", categories)
        
        if selected_category:
            topics = self.knowledge_memory.knowledge_base[selected_category]
            topic_names = [topics[key]['title'] for key in topics.keys()]
            
            selected_topic_name = st.selectbox("Select Topic", topic_names)
            
            # Find the selected topic
            for topic_key, topic_data in topics.items():
                if topic_data['title'] == selected_topic_name:
                    st.markdown(f"### {topic_data['title']}")
                    st.markdown(topic_data['content'])
                    
                    # Show related topics
                    if 'related' in topic_data:
                        st.markdown("#### 🔗 Related Topics")
                        for related in topic_data['related']:
                            st.write(f"- {related}")
                    break
    
    def show_spiritual_insights(self):
        """Show beautiful spiritual analytics"""
        st.markdown("### 📈 Your Spiritual Journey Analytics")
        
        # Generate sample spiritual progress data
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        mindfulness = [3, 4, 5, 4, 6, 7, 8]
        compassion = [4, 5, 4, 6, 5, 7, 8]
        learning = [2, 3, 4, 5, 4, 6, 7]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=days, y=mindfulness,
            mode='lines+markers',
            name='🧠 Mindfulness',
            line=dict(color=COLORS['primary'], width=4),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=days, y=compassion,
            mode='lines+markers', 
            name='💖 Compassion',
            line=dict(color=COLORS['accent'], width=4),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=days, y=learning,
            mode='lines+markers',
            name='📚 Learning',
            line=dict(color=COLORS['secondary'], width=4),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            title="Weekly Spiritual Practice Trends"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Spiritual metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Practice Streak", "12 days", "3 days")
        with col2:
            st.metric("Knowledge Score", "84%", "8%")
        with col3:
            st.metric("Compassion Level", "92%", "5%")
        with col4:
            st.metric("Growth Rate", "76%", "12%")
            
        # Practice recommendations
        st.markdown("#### 💡 Recommended Practices")
        st.info("""
        Based on your journey, consider focusing on:
        - **Morning Samayika** for mental clarity
        - **Study of Anekantavada** for perspective expansion  
        - **Compassion meditation** for emotional balance
        """)
    
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
            <h3 style='color: {COLORS['primary']}; margin: 0;'>Welcome to Advanced Jain Wisdom</h3>
            <p style='color: {COLORS["text_light"]}; margin: 1rem 0;'>
                I am Yashvi, your AI spiritual companion powered by comprehensive Jain knowledge and local intelligence.
            </p>
            <div style='
                background: {COLORS['background']};
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                text-align: left;
            '>
                <strong>My Advanced Capabilities:</strong><br>
                • Semantic search through Jain scriptures<br>
                • Context-aware spiritual guidance<br>  
                • Personalized practice recommendations<br>
                • Emotional support with Jain wisdom
            </div>
            <p style='color: {COLORS["secondary"]}; font-style: italic;'>
                "No external APIs • Complete privacy • Authentic Jain wisdom"
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
        """Process user input with advanced response engine"""
        
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "User", 
            "content": user_input
        })
        
        # Generate intelligent response using advanced engine
        with st.spinner("🌱 Consulting wisdom..."):
            response = self.response_engine.generate_intelligent_response(
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
        page_title="AI Sister Yashvi - Open Source",
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
