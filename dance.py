import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
API_KEYS = st.secrets["API_KEYS"]

if "key_index" not in st.session_state:
    st.session_state.key_index = 0

if "user_name" not in st.session_state:
    st.session_state.user_name = None

# Track if greeting has been sent
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
    st.subheader("INTRODUCE YOURSELF")
    
    with st.form("login_form", clear_on_submit=False):
        u_name = st.text_input("ENTER YOUR NAME:")
        submit_button = st.form_submit_button("Enter Apna AI World")
        
        if submit_button:
            if u_name.strip():
                st.session_state.user_name = u_name.strip()
                st.rerun()
            else:
                st.warning("Please Enter your name.")
else:
    st.markdown(f"# 🤖 **Apna AI**")
    st.markdown(f"### **Welcome {st.session_state.user_name}**")

    # --- 4. SIDEBAR ---
    with st.sidebar:
        st.header("Settings")
        st.info(f"User: {st.session_state.user_name}")
        uploaded_file = st.file_uploader("Koi photo upload karein (Optional)", type=['png', 'jpg', 'jpeg'])
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.has_greeted = False # Reset greeting too
            st.rerun()
        
        if st.button("Logout"):
            st.session_state.user_name = None
            st.session_state.has_greeted = False
            st.rerun()

    # --- 5. CHAT MEMORY ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        display_name = "Apna AI" if message["role"] == "assistant" else st.session_state.user_name
        with st.chat_message(message["role"]):
            st.markdown(f"**{display_name}:** {message['content']}")

    # --- 6. CHAT LOGIC ---
    if not best_model_name:
        st.warning("Pehle apni API Key check karein.")
    else:
        # Crucial for "Current Data" - Providing the specific context of 2026
        today_date = datetime.now().strftime("%A, %d %B %Y")
        
        model = genai.GenerativeModel(
            model_name=best_model_name,
            system_instruction=f"""
            Your name is Apna AI, created by Tayyab.
            CRITICAL INFO: Today is {today_date}. It is the year 2026.
            If asked about the US President or world leaders, use the data for the year 2026.
            Aap ek aqalmand ustad hain. Aap abhi {st.session_state.user_name} se baat kar rahe hain. 
            RULES:
            1. Language: Mix of Urdu/English (Roman Urdu).
            2. Be concise.
            3. Do NOT start with 'Assalam-o-Alaikum' yourself; the system will handle it if needed.
            """
        )

        if prompt := st.chat_input(f"Boliye {st.session_state.user_name}..."):
            # --- FIXED GREETING LOGIC ---
            final_prompt = prompt
            if not st.session_state.has_greeted:
                # Force the greeting only on the very first prompt
                final_prompt = f"Start your response with 'Assalam-o-Alaikum {st.session_state.user_name}!' and then answer this: {prompt}"
                st.session_state.has_greeted = True

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"**{st.session_state.user_name}:** {prompt}")

            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                success = False
                
                for attempt in range(len(API_KEYS)):
                    try:
                        with placeholder.container():
                            st.write("**Apna AI:**")
                            if uploaded_file:
                                img = Image.open(uploaded_file)
                                # Use final_prompt which contains greeting logic
                                response = model.generate_content([final_prompt, img], stream=True)
                            else:
                                response = model.generate_content(final_prompt, stream=True)
                            
                            full_response = st.write_stream(chunk.text for chunk in response)
                        
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        success = True
                        break 
                        
                    except Exception as e:
                        if "429" in str(e):
                            configure_next_key()
                            continue 
                        else:
                            st.error(f"Error: {e}")
                            break
                
                if not success:
                    st.error("Apna AI is currently resting.")
        
