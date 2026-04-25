
import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION (Updated for Security) ---
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("Secrets mein API Key nahi mili! Settings check karein.")
    st.stop()
    
# --- 2. MODEL SELECTION (Fixed Error Handling) ---
@st.cache_resource
def get_best_model():
    try:
        # Models ki list mangwai
        models = genai.list_models()
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            return None
            
        # Preference order: Flash -> Pro -> Any available
        if 'models/gemini-1.5-flash' in available_models:
            return 'models/gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            return 'models/gemini-pro'
        return available_models[0]
    except Exception as e:
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
        st.rerun()
    
    st.write("---")
    if best_model_name:
        st.success(f"GURU is Online ({best_model_name.split('/')[-1]})")
    else:
        st.error("GURU Offline hai (Model issue)")

# --- 5. CHAT MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    name = "GURU" if message["role"] == "assistant" else "Tayyab"
    with st.chat_message(message["role"]):
        st.markdown(f"**{name}:** {message['content']}")

# --- 6. CHAT LOGIC ---
if not best_model_name:
    st.warning("Pehle apni API Key check karein, model load nahi ho saka.")
else:
    if prompt := st.chat_input("GURU se kuch puchiye..."):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"**Tayyab:** {prompt}")

        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel(
                    model_name=best_model_name,
                    system_instruction="Aapka naam GURU hai. Aap ek aqalmand ustad hain. Hamesha 'Assalam-o-Alaikum' se baat shuru karein. Agar koi puche 'Who are you' to kahein 'Main GURU hoon Mujy Tayyab ny bnaya hai'."
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
                st.error(f"GURU ko masla aya: {e}")

        
