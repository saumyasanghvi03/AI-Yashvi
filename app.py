import streamlit as st
from datetime import datetime
import pytz
import tempfile
import os
import shutil
from git import Repo
import glob
import re

# Add this at the top of your app as a temporary fix
import subprocess
import sys

def install_missing_packages():
    missing_packages = []
    try:
        import transformers
    except ImportError:
        missing_packages.append("transformers==4.33.0")
    
    try:
        import torch
    except ImportError:
        missing_packages.append("torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu")
    
    if missing_packages:
        print(f"Installing missing packages: {missing_packages}")
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Call this function (comment out after first run if needed)
# install_missing_packages()

# --- Bytez SDK Import ---
try:
    from bytez import Bytez
    BYTEZ_AVAILABLE = True
except ImportError:
    st.error("Bytez package not installed. Please install it with: pip install bytez")
    BYTEZ_AVAILABLE = False

# --- Hugging Face Fallback Imports ---
try:
    from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
    from transformers import GenerationConfig
    import torch
    HF_AVAILABLE = True
except ImportError:
    st.warning("Hugging Face transformers not available. Install with: pip install transformers torch accelerate")
    HF_AVAILABLE = False

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
    
    if "repo_content" not in st.session_state:
        st.session_state.repo_content = None
    
    if "ai_models" not in st.session_state:
        st.session_state.ai_models = None
    
    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Chat"
    
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    
    if "show_fallback_ui" not in st.session_state:
        st.session_state.show_fallback_ui = False

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

# --- UPGRADE: Cached Functions ---
@st.cache_resource
def cached_initialize_ai_models():
    """Initialize AI models with fallback hierarchy."""
    models = {}
    
    # Try Bytez models first
    if BYTEZ_AVAILABLE:
        try:
            sdk = Bytez(BYTEZ_API_KEY)
            # Try Qwen model first
            try:
                models['bytez_qwen'] = sdk.model("Qwen/Qwen3-4B-Instruct-2507")
                st.success("✓ Bytez Qwen model loaded")
            except Exception as qwen_error:
                # Fallback to Gemma model
                try:
                    models['bytez_gemma'] = sdk.model("google/gemma-3-4b-it")
                    st.success("✓ Bytez Gemma model loaded")
                except Exception as gemma_error:
                    st.warning("Bytez models unavailable, using Hugging Face fallback")
        except Exception as e:
            st.warning(f"Bytez SDK initialization failed: {e}")
    
    # Hugging Face fallback models
    if HF_AVAILABLE and not models:  # Only load HF if Bytez failed
        try:
            # Load a small, efficient model for chat
            st.info("Loading Hugging Face fallback model...")
            
            # Option 1: Try a small instruct model first
            try:
                models['hf_chat'] = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-medium",
                    torch_dtype=torch.float16,
                    device_map="auto" if torch.cuda.is_available() else None,
                    max_length=1024
                )
                st.success("✓ Hugging Face DialoGPT model loaded")
            except Exception as dialo_error:
                # Option 2: Fallback to a distilled model
                try:
                    models['hf_chat'] = pipeline(
                        "text-generation", 
                        model="distilgpt2",
                        torch_dtype=torch.float16,
                        device_map="auto" if torch.cuda.is_available() else None,
                        max_length=1024
                    )
                    st.success("✓ Hugging Face DistilGPT2 model loaded")
                except Exception as distil_error:
                    st.error("All AI models failed to load")
        
        except Exception as e:
            st.error(f"Hugging Face model loading failed: {e}")
    
    return models

@st.cache_resource
def cached_load_repo_content():
    """
    Clones the GitHub repo and loads text files.
    Returns a list of documents with metadata.
    """
    try:
        with st.spinner("Loading knowledge base (one-time setup)..."):
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
                
                st.success("✓ Knowledge base loaded")
                return documents

    except Exception as e:
        st.error(f"Error loading repository: {e}")
        return None
# --- END UPGRADE ---

def call_ai_model(models, messages):
    """
    Calls available AI models with fallback hierarchy.
    Returns response and any error.
    """
    system_prompt = None
    user_question = None
    
    # Extract system prompt and user question from messages
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"]
        elif msg["role"] == "user":
            user_question = msg["content"]
    
    if not user_question:
        return "No question provided.", "No user question"
    
    full_prompt = f"{system_prompt}\n\nAnswer:"
    
    # Try Bytez models first
    if 'bytez_qwen' in models:
        try:
            output, error = models['bytez_qwen'].run(full_prompt)
            if not error:
                return output, None
        except Exception as e:
            st.warning(f"Bytez Qwen failed: {e}")
    
    if 'bytez_gemma' in models:
        try:
            output, error = models['bytez_gemma'].run(full_prompt)
            if not error:
                return output, None
        except Exception as e:
            st.warning(f"Bytez Gemma failed: {e}")
    
    # Hugging Face fallback
    if 'hf_chat' in models:
        try:
            # For DialoGPT or similar models
            if hasattr(models['hf_chat'], 'tokenizer'):
                # This is a pipeline
                response = models['hf_chat'](
                    full_prompt,
                    max_new_tokens=500,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=models['hf_chat'].tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
                if isinstance(response, list) and len(response) > 0:
                    generated_text = response[0]['generated_text']
                    # Extract only the new generated part
                    if generated_text.startswith(full_prompt):
                        answer = generated_text[len(full_prompt):].strip()
                    else:
                        answer = generated_text
                    return answer, None
            else:
                # Handle other model types
                return "Hugging Face model available but specific handling not implemented.", "Model handling error"
                
        except Exception as e:
            error_msg = f"Hugging Face model error: {str(e)}"
            st.error(error_msg)
            return None, error_msg
    
    return None, "All AI models failed"

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

def get_fallback_response(question):
    """Ultimate fallback when all AI models fail."""
    question_lower = question.lower()
    
    # --- BUG FIX ---
    # The original logic was matching any word from the question_data,
    # causing "What is Jainism?" to match "What is the Navkar Mantra?".
    # The new logic checks if the *primary topic word* from the key 
    # (e.g., "jainism", "navkar", "ahimsa") is in the user's question.
    
    # Try matching based on the primary topic word in the dictionary key
    for key, data in QUICK_QUESTIONS_DATABASE.items():
        # Get the main topic from the key (e.g., "jainism" from "jainism_basics")
        topic_word = key.split('_')[0]
        
        if topic_word in question_lower:
            # Special case: 'three' is too general, check for 'three jewels'
            if topic_word == 'three' and 'jewels' not in question_lower:
                continue
            return data['answer']
    # --- END OF BUG FIX ---

    # --- REPAIR: Check WHY we are falling back ---
    # If no AI models were loaded at all, show a specific error.
    if not st.session_state.ai_models:
        specific_error_message_eng = """**મુખ્ય વિચાર / Main Concept**
• The AI models are not available.

**મુખ્ય મુદ્દાઓ / Key Points**
• This app requires installing Python packages to function.
• The `bytez` and `transformers` packages could not be found.

**વ્યવહારુ સલાહ / Practical Advice**
• If you are running this locally, please install the dependencies:
• `pip install bytez transformers torch accelerate`

**સારાંશ / Summary**
• AI features are disabled. Using pre-written answers only."""
        
        specific_error_message_guj = """**મુખ્ય વિચાર / Main Concept**
• AI મોડલ ઉપલબ્ધ નથી.

**મુખ્ય મુદ્દાઓ / Key Points**
• આ એપ્લિકેશનને કાર્ય કરવા માટે પાઇથોન પેકેજો ઇન્સ્ટોલ કરવાની જરૂર છે.
• `bytez` અને `transformers` પેકેજો મળી શક્યા નથી.

**વ્યવહારુ સલાહ / Practical Advice**
• જો તમે આને સ્થાનિક રીતે ચલાવી રહ્યા છો, તો કૃપા કરીને ડિપેન્ડન્સી ઇન્સ્ટોલ કરો:
• `pip install bytez transformers torch accelerate`

**સારાંશ / Summary**
• AI સુવિધાઓ અક્ષમ છે. ફક્ત પૂર્વ-લેખિત જવાબોનો ઉપયોગ કરી રહ્યા છીએ."""
        
        if detect_language(question) == 'gujarati':
            return specific_error_message_guj
        else:
            return specific_error_message_eng
    # --- END REPAIR ---
    
    # Generic fallback responses (if models *are* loaded but just failed)
    # This message will be INTERCEPTED by process_user_question
    fallback_responses = {
        'english': """**મુખ્ય વિચાર / Main Concept**
• I'm currently experiencing technical difficulties with my AI models

**મુખ્ય મુદ્દાઓ / Key Points**
• Please try the 'Quick Questions' section for instant answers
• You can also explore the 'Learn' section for resources
• Try rephrasing your question

**વ્યવહારુ સલાહ / Practical Advice**
• Visit Digital Jain Pathshala: https://digitaljainpathshala.org/blogs
• Check Jain eLibrary: https://www.jainelibrary.org
• Explore JainQQ: https://www.jainqq.org

**ભાવનાત્મક સહાય / Emotional Support**
• Your spiritual journey is important - please try again soon

**સારાંશ / Summary**
• Technical issue detected - using fallback mode""",
        
        'gujarati': """**મુખ્ય વિચાર / Main Concept**
• હું હાલમાં મારી AI મોડલ્સ સાથે તકનીકી મુશ્કેલીઓનો સામનો કરી રહ્યો છું

**મુખ્ય મુદ્દાઓ / Key Points**
• કૃપા કરીને ત્વરિત જવાબો માટે 'Quick Questions' વિભાગ અજમાવો
• તમે સંસાધનો માટે 'Learn' વિભાગ પણ એક્સપ્લોર કરી શકો છો
• તમારો પ્રશ્ન ફરીથી લખવાનો પ્રયાસ કરો

**વ્યવહારુ સલાહ / Practical Advice**
• ડિજિટલ જૈન પાઠશાળા મુલાકાત લો: https://digitaljainpathshala.org/blogs
• જૈન ઈ-લાઈબ્રેરી તપાસો: https://www.jainelibrary.org
• જૈનQQ એક્સપ્લોર કરો: https://www.jainqq.org

**ભાવનાત્મક સહાય / Emotional Support**
• તમારી આધ્યાત્મિક યાત્રા મહત્વપૂર્ણ છે - કૃપા કરીને ફરી પ્રયાસ કરો

**સારાંશ / Summary**
• તકનીકી સમસ્યા શોધાઈ - ફોલબેક મોડનો ઉપયોગ કરી રહ્યા છીએ"""
    }
    
    language = detect_language(question)
    return fallback_responses.get(language, fallback_responses['english'])

def get_ai_response(question, documents, ai_models):
    """
    Gets relevant context and calls AI models for response with fallbacks.
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

        # --- UPGRADE: Conversational Memory ---
        # Build conversation history
        history_messages = st.session_state.messages[-6:] # Get last 6 messages (3 pairs)
        conversation_history = "\n\nPREVIOUS CONVERSATION CONTEXT:\n"
        if len(history_messages) > 1: # More than just the initial welcome
            for msg in history_messages:
                if msg["role"] == "user":
                    conversation_history += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    conversation_history += f"Assistant: {msg['content']}\n"
        else:
            conversation_history = "\n\nThis is the first question.\n"
        # --- END UPGRADE ---
        
        # SIMPLIFIED system prompt without complex practices
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
9. Use the PREVIOUS CONVERSATION CONTEXT to understand follow-up questions (e.g., "what about it?").

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
• [Suggest simple daily practices]
• [Recommend basic meditation techniques]
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

        # --- UPGRADE: Modified System Prompt ---
        system_prompt = (
            base_prompt + 
            language_instruction + 
            conversation_history +  # Add memory
            context_part + 
            jain_sources_context + 
            f"\n\nNEW QUESTION: {question}"
        )
        # --- END UPGRADE ---

        # Prepare messages for the model
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": question # The user's latest question
            }
        ]
        
        # Call AI models with fallback
        output, error = call_ai_model(ai_models, messages)
        
        if error:
            # Ultimate fallback - use quick questions database if AI fails
            return get_fallback_response(question), relevant_docs, suggestions
        elif output:
            # Apply formatting to ensure bullet points
            formatted_output = format_response_to_bullet_points(output)
            return formatted_output, relevant_docs, suggestions
        else:
            return get_fallback_response(question), relevant_docs, suggestions
        
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

    # --- REPAIR 1: Check if AI models are available before rendering chat ---
    if not st.session_state.ai_models:
        st.markdown("### 💭 Ask Your Spiritual Questions")
        st.markdown("---")
        
        st.error("""
        **AI Chat Disabled: Technical Issue**
        
        The core AI models for conversation are not available. This is likely because the required Python packages (`bytez` or `transformers`) are not installed in this environment.
        
        **You can still use the app's other features:**
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❓ Go to Quick Questions", use_container_width=True, type="primary"):
                st.session_state.current_page = "Quick Questions"
                st.rerun()
        with col2:
            if st.button("📚 Go to Learn", use_container_width=True, type="primary"):
                st.session_state.current_page = "Learn"
                st.rerun()
                
        st.markdown("---")
        st.warning("If you are the app developer, please install the missing packages: `pip install bytez transformers torch accelerate`")

    # --- REPAIR 2: Check if a runtime fallback occurred ---
    elif st.session_state.show_fallback_ui:
        st.markdown("### 💭 Ask Your Spiritual Questions")
        st.markdown("---")
        
        st.error("""
        **AI Chat Temporarily Unavailable**
        
        We are experiencing technical difficulties connecting to the AI models. This may be due to high traffic or an API service issue.
        
        **You can still use the app's other features:**
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❓ Go to Quick Questions", use_container_width=True, type="primary"):
                st.session_state.current_page = "Quick Questions"
                st.session_state.show_fallback_ui = False # Reset flag
                st.rerun()
        with col2:
            if st.button("📚 Go to Learn", use_container_width=True, type="primary"):
                st.session_state.current_page = "Learn"
                st.session_state.show_fallback_ui = False # Reset flag
                st.rerun()
                
        st.markdown("---")
        if st.button("🔄 Try Reconnecting to Chat"):
            st.session_state.show_fallback_ui = False
            st.rerun()
        
    else:
        # --- Original Chat Page Code ---
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
    # --- END REPAIR ---

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
            # --- UPGRADE: Save feedback to file ---
            try:
                with open("feedback.txt", "a", encoding="utf-8") as f:
                    f.write(f"--- {datetime.now(IST)} ---\n")
                    f.write(f"User: {st.session_state.user_name}\n")
                    f.write(f"Feedback: {feedback}\n\n")
                st.success("Thank you for your feedback! 🙏")
            except Exception as e:
                st.error(f"Could not save feedback: {e}")
            # --- END UPGRADE ---
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
                st.session_state.ai_models
            )
            
            # --- REPAIR: Intercept generic fallback message ---
            if "Technical issue detected - using fallback mode" in bot_response:
                # Don't append this message.
                # Instead, set a state to show the error UI.
                st.session_state.show_fallback_ui = True
                st.session_state.messages.pop() # Remove the user's message
                st.rerun()
                return # Stop processing
            # --- END REPAIR ---
                
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

    # --- UPGRADE: Load cached models and data at the START ---
    # This runs ONCE per session and is much faster on re-runs.
    try:
        if st.session_state.ai_models is None:
            st.session_state.ai_models = cached_initialize_ai_models()
    except Exception as e:
            st.error(f"Failed to load AI models: {e}")
            st.session_state.ai_models = {} # Set to empty dict to prevent re-load

    try:
        if st.session_state.repo_content is None:
            st.session_state.repo_content = cached_load_repo_content()
    except Exception as e:
            st.error(f"Failed to load knowledge base: {e}")
            st.session_state.repo_content = [] # Set to empty list to prevent re-load
    # --- END UPGRADE ---
    
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
        <p>Your AI Spiritual Guide for Jain Philosophy and Daily Practice</p>
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
    
    # --- UPGRADE: Removed the old loading blocks from here ---

if __name__ == "__main__":
    main()
