import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION (Multi-Key Support) ---
def configure_genai():
    if "GEMINI_KEYS" in st.secrets:
        api_keys = st.secrets["GEMINI_KEYS"]
        # Agar single string hai to list bana dein
        if isinstance(api_keys, str):
            api_keys = [api_keys]
            
        if "key_index" not in st.session_state:
            st.session_state.key_index = 0
            
        # Current key select karna
        current_key = api_keys[st.session_state.key_index]
        genai.configure(api_key=current_key)
        return api_keys
    else:
        st.error("Secrets mein 'GEMINI_KEYS' nahi mili! Please check your .toml file or Streamlit Cloud settings.")
        st.stop()

all_keys = configure_genai()

# --- 2. MODEL SELECTION ---
@st.cache_resource
def get_best_model():
    try:
        models = genai.list_models()
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        if 'models/gemini-1.5-flash' in available_models:
            return 'models/gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            return 'models/gemini-pro'
        return available_models[0] if available_models else None
    except Exception:
        return None

best_model_name = get_best_model()

# --- 3. PAGE UI ---
st.set_page_config(page_title="GURU AI", page_icon="⭐")
st.title("⭐ GURU AI")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("GURU Settings")
    uploaded_file = st.file_uploader("Koi photo upload karein (Optional)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Selected Image", use_container_width=True)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.key_index = 0 # Reset key to first one
        st.rerun()
    
    st.write("---")
    if best_model_name:
        st.success(f"GURU Online ({best_model_name.split('/')[-1]})")
        st.info(f"API Key #{st.session_state.key_index + 1} active")
    else:
        st.error("GURU Offline hai.")

# --- 5. CHAT MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    name = "GURU" if message["role"] == "assistant" else "Tayyab"
    with st.chat_message(message["role"]):
        st.markdown(f"**{name}:** {message['content']}")

# --- 6. CHAT LOGIC ---
if prompt := st.chat_input("GURU se kuch puchiye..."):
    
    # User ka message save aur show karein
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**Tayyab:** {prompt}")

    with st.chat_message("assistant"):
        try:
            # Check if it's the first message to handle "Assalam-o-Alaikum"
            # History check: user ka message append ho chuka hai, agar count 1 hai to ye pehla sawaal hai
            if len(st.session_state.messages) <= 1:
                greeting_instr = "Hamesha 'Assalam-o-Alaikum Dear. How are You How can i Help you' se baat shuru karein."
            else:
                greeting_instr = "Ab dubara Salam mat karein (already greeted), seedha jawab dein."

            model = genai.GenerativeModel(
                model_name=best_model_name,
                system_instruction=f"Aapka naam GURU hai. Aap ek bhtreen ustad hain. {greeting_instr} Agar koi puche 'Who are you' to kahein 'Main GURU hoon Mujy Tayyab ny bnaya hai'."
            )
            
            st.write("**GURU:**")
            
            if uploaded_file:
                img = Image.open(uploaded_file)
                response = model.generate_content([prompt, img], stream=True)
            else:
                response = model.generate_content(prompt, stream=True)
            
            full_response = st.write_stream((chunk.text for chunk in response))
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            # Key Switch Logic if limit reached
            if "429" in str(e) or "quota" in str(e).lower():
                if st.session_state.key_index < len(all_keys) - 1:
                    st.session_state.key_index += 1
                    st.warning(f"Key limit reached. Switching to Key #{st.session_state.key_index + 1}...")
                    st.rerun()
                else:
                    st.error("Please wait After some time you can ask me anything!")
            else:
                st.error(f"Some error found in Guru Coding: {e}")
        
