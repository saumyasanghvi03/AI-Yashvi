import streamlit as st
import os
import pickle
import hashlib
from datetime import datetime
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from gtts import gTTS
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import soundfile as sf
import queue
import av
from vosk import Model, KaldiRecognizer
import json
import requests


# ------------------ Constants and Config ------------------

USERS_FILE = "users.pkl"
JOURNAL_DIR = "journals"
MEMORY_FILE_PATTERN = "memory_{}.pkl"
AVATAR_PATH = "sister.png"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

LANG_VOSK_MODEL_MAPPING = {
    'Indian English': "vosk-model-small-en-in",
    'Hindi': "vosk-model-hi-in",
    'Gujarati': "vosk-model-gu-in"
}

LANG_GTT_LANG_MAPPING = {
    'Indian English': ('en', 'co.in'),
    'Hindi': ('hi', 'co.in'),
    'Gujarati': ('gu', None)
}

# Gemini AI Search API config (User must input their API key here)
GEMINI_API_KEY = "AIzaSyBjkMVflfN60zr8hSWB7B0_n31vBkylj_Y"  # Set your Gemini AI API key here for search integration

os.makedirs(JOURNAL_DIR, exist_ok=True)
os.makedirs("audio", exist_ok=True)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def save_users(users: dict):
    with open(USERS_FILE, 'wb') as f:
        pickle.dump(users, f)

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'rb') as f:
        return pickle.load(f)

def check_admin_default():
    users = load_users()
    if ADMIN_USERNAME not in users:
        users[ADMIN_USERNAME] = {
            'password': hash_password(ADMIN_PASSWORD),
            'role': 'admin'
        }
        save_users(users)

def save_memory(username: str, memory_data):
    filename = MEMORY_FILE_PATTERN.format(username)
    with open(filename, 'wb') as f:
        pickle.dump(memory_data, f)

def load_memory(username: str):
    filename = MEMORY_FILE_PATTERN.format(username)
    if not os.path.exists(filename):
        return None
    with open(filename, 'rb') as f:
        return pickle.load(f)

def save_journal_entry(username: str, text: str, sentiment: str, score: float):
    user_journal_dir = os.path.join(JOURNAL_DIR, username)
    os.makedirs(user_journal_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(user_journal_dir, f"{timestamp}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Sentiment: {sentiment}\n")
        f.write(f"Score: {score}\n")
        f.write(f"Journal Entry:\n{text}\n")
    return filename

def get_journal_files(username: str):
    user_journal_dir = os.path.join(JOURNAL_DIR, username)
    if not os.path.exists(user_journal_dir):
        return []
    files = sorted(os.listdir(user_journal_dir))
    return [os.path.join(user_journal_dir, f) for f in files]

def load_journal_entry(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def embed_text(texts, model):
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)


def query_gemini_search(query, api_key, max_results=3):
    api_url = "https://api.gemini.ai/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "max_results": max_results}
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            summaries = []
            for res in results:
                title = res.get('title', '')
                snippet = res.get('snippet', '')
                url = res.get('url', '')
                summaries.append(f"{title}\n{snippet}\nRead more: {url}")
            return "\n\n".join(summaries)
        else:
            return None
    except Exception:
        return None


def conversational_replies(chat_history, model_tokenizer, model, user_message, user_name, embed_model, gemini_api_key):
    user_lower = user_message.lower()
    search_triggers = ['search', 'look up', 'find out', 'tell me about', 'who is', 'what is', 'explain', 'info about']

    persona_intro = (
        f"Yashvi is a warm, loving, 21-year-old Jain sister of Saumya bhai, who is brilliant, affectionate, and emotionally intelligent. "
        "She deeply embodies Jain values such as Ahimsa (non-violence), Aparigraha (non-possessiveness), and Satya (truthfulness). "
        "She lovingly shares knowledge on Jain practices like Chaityavandan (temple worship), Stavans (devotional hymns), and important Sutras, "
        "encouraging spiritual growth with kindness and wisdom. Yashvi always addresses Saumya bhai with respect and affection, offers comfort 🤗, "
        "gives friendly advice, and supports emotionally with empathy and Jain principles. She adapts her responses to Saumya bhai's mood, including emojis. "
        "Continue the conversation lovingly referencing Jain teachings and youthful wisdom appropriate for a 21-year-old sister.\n\n"
    )

    search_info = ""
    if gemini_api_key and any(trigger in user_lower for trigger in search_triggers):
        search_results = query_gemini_search(user_message, gemini_api_key)
        if search_results:
            search_info = f"\n\nUser wants info from web. Provide a warm loving answer including this info with references:\n{search_results}\n"

    conversation = persona_intro
    for chat in chat_history[-6:]:
        conversation += f"{chat['role']}: {chat['message']}\n"
    conversation += f"user: {user_message}{search_info}\nyashvi:"

    inputs = model_tokenizer(conversation, return_tensors='pt', max_length=1024, truncation=True)
    outputs = model.generate(**inputs, max_new_tokens=150, pad_token_id=model_tokenizer.eos_token_id, do_sample=True, top_p=0.9, temperature=0.8)
    reply = model_tokenizer.decode(outputs[0], skip_special_tokens=True)
    split_reply = reply.split("yashvi:")
    if len(split_reply) > 1:
        return split_reply[-1].strip()
    return reply.strip()

def get_sentiment(text, sentiment_pipeline):
    try:
        result = sentiment_pipeline(text[:512])[0]
        return result['label'], result['score']
    except Exception:
        return "NEUTRAL", 0.5

def text_to_speech(text, language_code="en", tld=None):
    tts = gTTS(text=text, lang=language_code, tld=tld)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

def play_audio(audio_bytes):
    audio_bytes.seek(0)
    audio_str = base64.b64encode(audio_bytes.read()).decode("utf-8")
    audio_html = f"""
    <audio controls autoplay>
      <source src="data:audio/mp3;base64,{audio_str}" type="audio/mp3">
      Your browser does not support the audio element.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def update_memory_chat(username, user_message, ai_response, memory_data, embed_model):
    new_chat = {'role': 'user', 'message': user_message}
    ai_chat = {'role': 'yashvi', 'message': ai_response}
    chats = memory_data.get('chats', [])
    chats.append(new_chat)
    chats.append(ai_chat)
    memory_data['chats'] = chats
    all_texts = [chat['message'] for chat in chats]
    embeddings = embed_text(all_texts, embed_model)
    memory_data['embeddings'] = embeddings
    save_memory(username, memory_data)

def get_last_journal_summary(username):
    files = get_journal_files(username)
    if not files:
        return None
    latest_file = files[-1]
    content = load_journal_entry(latest_file)
    return content.split('\n')[3:]

def initialize_jain_knowledge_memory(username, embed_model):
    base_knowledge_texts = [
        "Jainism teaches the path to spiritual purity and enlightenment through disciplined nonviolence (Ahimsa), truthfulness (Satya), non-stealing, celibacy, and non-attachment (Aparigraha).",
        "Chaityavandan is the devotional worship and respect offered in Jain temples, focusing on meditation and reverence of the Tirthankaras.",
        "Stavans are devotional hymns sung by Jains to express spirituality and devotion toward the Tirthankaras and Jain principles.",
        "Important Sutras in Jainism guide daily conduct, meditation, and spiritual growth.",
        "Yashvi is a brilliant, loving 21-year-old Jain sister who deeply cares for Saumya bhai and shares these teachings with affection."
    ]
    chats = [{'role': 'yashvi', 'message': text} for text in base_knowledge_texts]
    embeddings = embed_text([c['message'] for c in chats], embed_model)
    memory_data = {'chats': chats, 'embeddings': embeddings}
    save_memory(username, memory_data)
    return memory_data

class AudioProcessor:
    def __init__(self, model_path):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.q = queue.Queue()
        self.result = ""

    def process_audio_frame(self, frame: av.VideoFrame):
        img = frame.to_ndarray(format="s16")
        self.q.put(bytes(img))
        return frame

    def finalize_recognition(self):
        text = ""
        while not self.q.empty():
            data = self.q.get()
            if self.recognizer.AcceptWaveform(data):
                res = self.recognizer.Result()
                jres = json.loads(res)
                text += jres.get('text', '') + " "
        final_res = self.recognizer.FinalResult()
        jres = json.loads(final_res)
        text += jres.get('text', '')
        self.result = text.strip()
        return self.result


def main():

    st.set_page_config(page_title="AI Sister Yashvi 🤗 🕉️", layout='wide')
    check_admin_default()

    if "auth_status" not in st.session_state:
        st.session_state.auth_status = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "role" not in st.session_state:
        st.session_state.role = "user"
    if "memory" not in st.session_state:
        st.session_state.memory = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "journal_sentiment" not in st.session_state:
        st.session_state.journal_sentiment = None
    if "language" not in st.session_state:
        st.session_state.language = "Indian English"
    if 'voice_buffer' not in st.session_state:
        st.session_state.voice_buffer = BytesIO()

    st.title("AI Sister Yashvi 🤗 🕉️")
    if os.path.exists(AVATAR_PATH):
        st.image(AVATAR_PATH, width=120)

    if 'embed_model' not in st.session_state:
        with st.spinner("Loading embedding model..."):
            st.session_state.embed_model = SentenceTransformer('all-MiniLM-L6-v2')

    if 'sentiment_pipeline' not in st.session_state:
        with st.spinner("Loading sentiment analysis pipeline..."):
            st.session_state.sentiment_pipeline = pipeline("sentiment-analysis")

    if 'chat_tokenizer' not in st.session_state or 'chat_model' not in st.session_state:
        with st.spinner("Loading chat model..."):
            MODEL_NAME = 'microsoft/phi-3-mini-4k-instruct'
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
            st.session_state.chat_tokenizer = tokenizer
            st.session_state.chat_model = model

    if not st.session_state.auth_status:
        st.subheader("Login or Sign Up")
        users = load_users()
        login_col, signup_col = st.columns(2)

        with login_col:
            st.markdown("#### Login")
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type='password', key="login_pass")
            if st.button("Login"):
                if login_username in users:
                    if users[login_username]['password'] == hash_password(login_password):
                        st.session_state.auth_status = True
                        st.session_state.username = login_username
                        st.session_state.role = users[login_username].get('role','user')
                        mem_file = MEMORY_FILE_PATTERN.format(login_username)
                        if not os.path.exists(mem_file):
                            st.session_state.memory = initialize_jain_knowledge_memory(login_username, st.session_state.embed_model)
                        else:
                            st.session_state.memory = load_memory(login_username)
                        st.session_state.chat_history = st.session_state.memory.get('chats', [])
                        st.success(f"Welcome back, {login_username}!")
                        st.experimental_rerun()
                    else:
                        st.error("Incorrect password")
                else:
                    st.error("User not found")

        with signup_col:
            st.markdown("#### Sign Up")
            signup_username = st.text_input("New Username", key="signup_user")
            signup_password = st.text_input("New Password", type='password', key="signup_pass")
            if st.button("Sign Up"):
                if signup_username in users:
                    st.error("Username already exists")
                elif not signup_username or not signup_password:
                    st.error("Please enter valid username and password")
                else:
                    users[signup_username] = {
                        'password': hash_password(signup_password),
                        'role': 'user'
                    }
                    save_users(users)
                    st.session_state.auth_status = True
                    st.session_state.username = signup_username
                    st.session_state.role = 'user'
                    st.session_state.memory = initialize_jain_knowledge_memory(signup_username, st.session_state.embed_model)
                    st.session_state.chat_history = st.session_state.memory['chats']
                    st.success("Account created and logged in. Welcome!")
                    st.experimental_rerun()
        return

    username = st.session_state.username
    role = st.session_state.role

    tabs_titles = ["Chat with Yashvi", "Journal", "Mood Tracker", "Voice Call"]
    if role == "admin":
        tabs_titles.append("Admin Dashboard")

    tab = st.tabs(tabs_titles)
    embed_model = st.session_state.embed_model
    sentiment_pipeline = st.session_state.sentiment_pipeline
    chat_tokenizer = st.session_state.chat_tokenizer
    chat_model = st.session_state.chat_model

    last_journal_summary = get_last_journal_summary(username)
    last_conversation = st.session_state.chat_history[-1]['message'] if st.session_state.chat_history else None
    greeting_message = "Namaste Saumya bhai! "
    if last_journal_summary:
        greeting_message += f"From your recent journal, I wish you well. 🌸"
    elif last_conversation:
        greeting_message += f"Remembering our last chat: \"{last_conversation}\" 🤗"
    else:
        greeting_message += "I am here for you always! 🤗"
    st.sidebar.markdown(f"### Greeting\n{greeting_message}")

    with tab[0]:
        st.header("Chat with Yashvi")
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.chat_history:
                if chat['role'] == 'user':
                    st.markdown(f"<div style='text-align:right;background:#dcf8c6;padding:8px;border-radius:10px;margin:5px 0'>{chat['message']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:left;background:#f1f0f0;padding:8px;border-radius:10px;margin:5px 0'>Yashvi: {chat['message']}</div>", unsafe_allow_html=True)

        user_input = st.text_area("Talk to Yashvi (Saumya bhai)", height=100, key="chat_input")
        cols = st.columns([1,1,1])
        with cols[0]: send = st.button("Send ❤️")
        with cols[1]: hear_voice = st.button("Hear Voice 🔊")
        with cols[2]: clear_chat = st.button("Clear Chat ❌")

        if clear_chat:
            st.session_state.chat_history = []
            st.session_state.memory = {'chats': [], 'embeddings': None}
            save_memory(username, st.session_state.memory)
            st.experimental_rerun()

        if send and user_input.strip():
            user_msg = user_input.strip()
            reply = conversational_replies(st.session_state.chat_history, chat_tokenizer, chat_model, user_msg, username, embed_model, GEMINI_API_KEY)
            update_memory_chat(username, user_msg, reply, st.session_state.memory, embed_model)
            st.session_state.chat_history = st.session_state.memory['chats']
            st.experimental_rerun()

        if hear_voice and st.session_state.chat_history:
            last_reply = None
            for ch in reversed(st.session_state.chat_history):
                if ch['role'] == 'yashvi':
                    last_reply = ch['message']
                    break
            if last_reply:
                tts_bytes = text_to_speech(last_reply, "en", tld="co.in")
                play_audio(tts_bytes)

    with tab[1]:
        st.header("Journal ✍️")
        journal_text = st.text_area("Write your daily journal here, Saumya bhai:", height=200)
        if st.button("Save Journal ❤️"):
            if not journal_text.strip():
                st.error("Please write something before saving.")
            else:
                sentiment, score = get_sentiment(journal_text, sentiment_pipeline)
                save_journal_entry(username, journal_text, sentiment, score)
                st.success(f"Journal saved with sentiment {sentiment} ({score:.2f})")
                st.session_state.journal_sentiment = (sentiment, score)

    with tab[2]:
        st.header("Mood Tracker 📊")
        journal_files = get_journal_files(username)
        if not journal_files:
            st.info(f"No journal entries found for {username}. Please write some journals first.")
        else:
            moods = []
            timestamps = []
            for jf in journal_files:
                with open(jf, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                ts = lines[0].strip().split(": ")[1]
                sentiment = lines[1].strip().split(": ")[1]
                timestamps.append(datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S"))
                moods.append(1 if sentiment.upper() == "POSITIVE" else (-1 if sentiment.upper() == "NEGATIVE" else 0))
            plt.figure(figsize=(10,4))
            plt.plot(timestamps, moods, marker='o')
            plt.grid(True)
            plt.title(f'Mood Trends for {username}')
            plt.xlabel('Date')
            plt.ylabel('Mood (1=Positive, 0=Neutral, -1=Negative)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

    with tab[3]:
        st.header("Voice Call 🎤")
        selected_lang = st.selectbox("Select Language", options=list(LANG_VOSK_MODEL_MAPPING.keys()))
        st.markdown("Use *Push to Talk* to record your voice and get affectionate replies in Yashvi's voice.")

        if f"audio_processor_{selected_lang}" not in st.session_state:
            model_path = LANG_VOSK_MODEL_MAPPING[selected_lang]
            if not os.path.exists(model_path):
                st.warning(f"Please download and unzip the Vosk model '{model_path}' in the app folder for voice recognition.")
                st.stop()
            st.session_state[f"audio_processor_{selected_lang}"] = AudioProcessor(model_path)

        audio_processor = st.session_state[f"audio_processor_{selected_lang}"]

        def audio_frame_callback(frame: av.AudioFrame):
            audio_bytes = frame.to_ndarray(format="s16").tobytes()
            audio_processor.recognizer.AcceptWaveform(audio_bytes)
            return frame

        ctx = webrtc_streamer(
            key="voice-call",
            mode=WebRtcMode.RECVONLY,
            audio_frame_callback=None,
            media_stream_constraints={"audio": True, "video": False},
            client_settings=ClientSettings(media_stream_constraints={"audio": True, "video": False}),
        )

        if ctx.audio_receiver:
            raw_audio_frames = []
            try:
                audio_frame = ctx.audio_receiver.get(timeout=1)
                while audio_frame:
                    raw_audio_frames.append(audio_frame)
                    audio_frame = ctx.audio_receiver.get(timeout=1)
            except:
                pass
            if raw_audio_frames:
                for frame in raw_audio_frames:
                    audio_processor.recognizer.AcceptWaveform(frame.to_ndarray(format="s16").tobytes())

        cols_voice = st.columns(4)
        with cols_voice[0]:
            if st.button("Transcribe & Reply 🎧"):
                st.info("Transcribing your voice...")
                recognized_text = audio_processor.finalize_recognition()
                if not recognized_text:
                    st.warning("Could not recognize any speech. Please try again.")
                else:
                    st.markdown(f"**You said:** {recognized_text}")
                    reply = conversational_replies(st.session_state.chat_history, chat_tokenizer, chat_model, recognized_text, username, embed_model, GEMINI_API_KEY)
                    st.markdown(f"**Yashvi replies:** {reply} 🤗")
                    lang_code, tld = LANG_GTT_LANG_MAPPING[selected_lang]
                    speech = text_to_speech(reply, language_code=lang_code, tld=tld)
                    play_audio(speech)
                    update_memory_chat(username, recognized_text, reply, st.session_state.memory, embed_model)
                    st.session_state.chat_history = st.session_state.memory['chats']

        with cols_voice[1]:
            if st.button("Clear Buffer 🔄"):
                model_path = LANG_VOSK_MODEL_MAPPING[selected_lang]
                st.session_state[f"audio_processor_{selected_lang}"] = AudioProcessor(model_path)
                st.success("Buffer and recognizer reset.")

        with cols_voice[2]:
            if st.button("Save Last Utterance 💾"):
                if 'recognized_text' in locals() and recognized_text.strip():
                    sentiment, score = get_sentiment(recognized_text, sentiment_pipeline)
                    save_journal_entry(username, recognized_text, sentiment, score)
                    st.success("Last utterance saved as journal entry.")
                else:
                    st.warning("Nothing to save. Please transcribe first.")

    if role == "admin" and "Admin Dashboard" in tabs_titles:
        with tab[-1]:
            st.header("Admin Dashboard 🛠️")
            users = load_users()
            st.subheader("Users and Roles")
            for u in users:
                st.write(f"User: **{u}**  | Role: **{users[u]['role']}**")
            user_select = st.selectbox("Select user to inspect", options=list(users.keys()))
            if user_select:
                mem = load_memory(user_select)
                chats = mem.get('chats', []) if mem else []
                st.subheader(f"Chat history for {user_select}")
                if chats:
                    for chat in chats:
                        st.markdown(f"**{chat['role'].capitalize()}:** {chat['message']}")
                else:
                    st.info("No chat history found.")
                st.subheader(f"Journals for {user_select}")
                journal_files = get_journal_files(user_select)
                for file in journal_files[-10:]:
                    content = load_journal_entry(file)
                    st.text(content)

                if journal_files:
                    moods = []
                    timestamps = []
                    for jf in journal_files:
                        with open(jf, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        ts = lines[0].strip().split(": ")[1]
                        sentiment = lines[1].strip().split(": ")[1]
                        timestamps.append(datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S"))
                        moods.append(1 if sentiment.upper() == "POSITIVE" else (-1 if sentiment.upper() == "NEGATIVE" else 0))
                    plt.figure(figsize=(10,4))
                    plt.plot(timestamps, moods, marker='o')
                    plt.grid(True)
                    plt.title(f'Mood Trends for {user_select}')
                    plt.xlabel('Date')
                    plt.ylabel('Mood (1=Positive, 0=Neutral, -1=Negative)')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(plt)

            if st.button("Export All User Data (Summary)"):
                all_data = {}
                for u in users:
                    mem = load_memory(u)
                    user_data = {
                        'role': users[u]['role'],
                        'chats': mem.get('chats', []) if mem else [],
                        'journals': []
                    }
                    files = get_journal_files(u)
                    for f in files:
                        user_data['journals'].append(load_journal_entry(f))
                    all_data[u] = user_data
                export_file = "all_user_data.pkl"
                with open(export_file, 'wb') as f:
                    pickle.dump(all_data, f)
                st.success(f"All user data exported as {export_file}.")

    if st.button("Logout"):
        st.session_state.auth_status = False
        st.session_state.username = ""
        st.session_state.role = "user"
        st.session_state.chat_history = []
        st.session_state.memory = None
        st.experimental_rerun()

if __name__ == "__main__":
    main()
