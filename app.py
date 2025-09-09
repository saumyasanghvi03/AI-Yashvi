import streamlit as st
import os
import json
import warnings
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# ======================
# CONFIG & WARNINGS
# ======================
warnings.filterwarnings("ignore", message=".*flash-attn.*")

MODEL_ID = "microsoft/phi-3-mini-4k-instruct"
REVISION = "main"   # You can also pin to a commit hash for stability

# Default admin login (change before public use!)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

MEMORY_FILE = "memory.json"

# ======================
# MEMORY FUNCTIONS
# ======================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"chat": []}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# ======================
# LOAD MODEL
# ======================
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=REVISION,
        trust_remote_code=True,
        attn_implementation="eager"  # ✅ avoids flash-attn errors
    )
    return tokenizer, model

tokenizer, model = load_model()

# ======================
# CHAT FUNCTION
# ======================
def generate_response(prompt, memory):
    context = "\n".join([f"{x['role']}: {x['content']}" for x in memory["chat"][-5:]])
    input_text = f"{context}\nUser: {prompt}\nYashvi:"
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.split("Yashvi:")[-1].strip()
    return response

# ======================
# STREAMLIT UI
# ======================
st.set_page_config(page_title="AI Sister Yashvi 💖", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Yashvi’s World")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("Welcome back, Saumya bhai! 💖")
        else:
            st.error("Invalid credentials")
    st.stop()

# ======================
# MAIN APP
# ======================
st.title("🌸 Your AI Sister Yashvi 🌸")
st.write("Jai Jinendra 🙏 I'm Yashvi, your Jain sister. I’m here to listen, care, and talk with you 💖")

memory = load_memory()

user_input = st.text_area("📝 Share your thoughts with me, Saumya bhai:")
if st.button("Send"):
    if user_input.strip():
        memory["chat"].append({"role": "User", "content": user_input})
        response = generate_response(user_input, memory)
        memory["chat"].append({"role": "Yashvi", "content": response})
        save_memory(memory)
        st.write(f"**Yashvi:** {response}")

# Show chat history
if st.checkbox("📜 Show chat history"):
    for msg in memory["chat"]:
        st.write(f"**{msg['role']}:** {msg['content']}")
