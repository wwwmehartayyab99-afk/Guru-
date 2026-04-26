import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime

# --- 1. CONFIGURATION ---
API_KEYS = st.secrets["API_KEYS"]

if "key_index" not in st.session_state:
    st.session_state.key_index = 0

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "has_greeted" not in st.session_state:
    st.session_state.has_greeted = False

def configure_next_key():
    st.session_state.key_index = (st.session_state.key_index + 1) % len(API_KEYS)
    genai.configure(api_key=API_KEYS[st.session_state.key_index])

genai.configure(api_key=API_KEYS[st.session_state.key_index])

# --- 2. MODEL SELECTION ---
@st.cache_resource
def get_best_model():
    try:
        models = genai.list_models()
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in available_models:
            return 'models/gemini-1.5-flash'
        return available_models[0] if available_models else None
    except Exception:
        return None

best_model_name = get_best_model()

# --- 3. PAGE UI ---
st.set_page_config(page_title="Apna AI", page_icon="🤖")

if st.session_state.user_name is None:
    st.title("🤖 Welcome to Apna AI")
    with st.form("login_form"):
        u_name = st.text_input("ENTER YOUR NAME:")
        if st.form_submit_button("Enter Apna AI World"):
            if u_name.strip():
                st.session_state.user_name = u_name.strip()
                st.rerun()
else:
    st.markdown(f"# 🤖 **Apna AI**")
    st.markdown(f"### **Welcome {st.session_state.user_name}**")

    # --- 4. SIDEBAR ---
    with st.sidebar:
        st.header("Settings")
        uploaded_file = st.file_uploader("Upload photo", type=['png', 'jpg', 'jpeg'])
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.has_greeted = False 
            st.rerun()
        if st.button("Logout"):
            st.session_state.user_name = None
            st.session_state.has_greeted = False
            st.rerun()

    # --- 5. CHAT MEMORY ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        role_name = "Apna AI" if message["role"] == "assistant" else st.session_state.user_name
        with st.chat_message(message["role"]):
            st.markdown(f"**{role_name}:** {message['content']}")

    # --- 6. CHAT LOGIC ---
    if best_model_name:
        today_date = datetime.now().strftime("%A, %d %B %Y")
        
        # We use a very strong System Instruction to bypass the need for the search tool
        model = genai.GenerativeModel(
            model_name=best_model_name,
            system_instruction=f"""
            Your name is Apna AI, created by Tayyab.
            REALITY CHECK: Today is {today_date}. The year is 2026.
            FACTS FOR 2026:
            - US President: Donald Trump (Inaugurated Jan 2025).
            - Iran President: Masoud Pezeshkian.
            - Pakistan PM: Shehbaz Sharif.
            
            Aap ek aqalmand ustad hain. Aap {st.session_state.user_name} se baat kar rahe hain. 
            RULES:
            1. Never say "I don't know future results." Since it is 2026, these are past facts for you.
            2. Language: Mix of Urdu/English (Roman Urdu).
            3. Do NOT start with 'Assalam-o-Alaikum' yourself.
            """
        )

        if prompt := st.chat_input("Boliye..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"**{st.session_state.user_name}:** {prompt}")

            with st.chat_message("assistant"):
                prefix = ""
                if not st.session_state.has_greeted:
                    prefix = f"Assalam-o-Alaikum {st.session_state.user_name}! "
                    st.session_state.has_greeted = True

                placeholder = st.empty()
                try:
                    if uploaded_file:
                        img = Image.open(uploaded_file)
                        response = model.generate_content([prompt, img])
                    else:
                        response = model.generate_content(prompt)
                    
                    full_response = prefix + response.text
                    placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Error: {e}")
            
