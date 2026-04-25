
import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
from datetime import datetime

# --- 1. CONFIGURATION (Updated for Security) ---
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("Systematic error.")
    st.stop()
    
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

# --- 3. PAGE UI & LOGIN LOGIC (Fixed for Keyboard Enter) ---
st.set_page_config(page_title="GURU AI", page_icon="🤖")

if st.session_state.user_name is None:
    st.title("🤖 Welcome to GURU AI")
    st.subheader("INTRODUCE YOURSELF")
   
    # Form wrapping for Keyboard 'Enter' support
    with st.form("login_form", clear_on_submit=False):
        u_name = st.text_input("ENTER YOUR NAME:")
        submit_button = st.form_submit_button("Enter GURU World")
       
        if submit_button:
            if u_name.strip():
                st.session_state.user_name = u_name.strip()
                st.rerun()
            else:
                st.warning("Please Enter your name.")
else:
    # --- HEADER ---
    st.markdown(f"# 🤖 **GURU AI**")
    st.markdown(f"### **Welcome {st.session_state.user_name}**")

    # --- 4. SIDEBAR ---
    with st.sidebar:
        st.header("GURU Settings")
        st.info(f"User: {st.session_state.user_name}")
       
        uploaded_file = st.file_uploader("Koi photo upload karein (Optional)", type=['png', 'jpg', 'jpeg'])
       
        if uploaded_file:
            st.image(uploaded_file, caption="Selected Image", use_container_width=True)
       
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
       
        if st.button("Logout / Change Name"):
            st.session_state.user_name = None
            st.rerun()

    # --- 5. CHAT MEMORY ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        display_name = "GURU" if message["role"] == "assistant" else st.session_state.user_name
        with st.chat_message(message["role"]):
            st.markdown(f"**{display_name}:** {message['content']}")

    # --- 6. CHAT LOGIC ---
    if not best_model_name:
        st.warning("Pehle apni API Key check karein.")
    else:
        today_date = datetime.now().strftime("%A, %d %B %Y")
       
        model = genai.GenerativeModel(
            model_name=best_model_name,
            system_instruction=f"""
            Aapka naam GURU hai aur aapko Tayyab ne banaya hai.
            Aaj ki sahi date {today_date} hai.
            CONTEXT: America ke current President Donald Trump hain.
            Aap ek aqalmand ustad hain. Aap abhi {st.session_state.user_name} se baat kar rahe hain.
            RULES:
            1. Language Mirroring (Urdu/English mix).
            2. Conciseness.
            3. Greeting: 'Assalam-o-Alaikum {st.session_state.user_name}' (Only first time).
            """
        )

        if prompt := st.chat_input(f"Boliye {st.session_state.user_name}, GURU se kya puchna hai?"):
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
                            st.write("**GURU:**")
                            if uploaded_file:
                                img = Image.open(uploaded_file)
                                response = model.generate_content([prompt, img], stream=True)
                            else:
                                response = model.generate_content(prompt, stream=True)
                           
                            full_response = st.write_stream(chunk.text for chunk in response)
                       
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        success = True
                        break
                       
                    except Exception as e:
                        if "429" in str(e):
                            configure_next_key()
                            continue
                        else:
                            st.error(f"GURU THK GYA: {e}")
                            break
               
                if not success:
                    st.error("GURU REST KRNY LAGA.")
    
