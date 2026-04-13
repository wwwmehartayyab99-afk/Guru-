import streamlit as st

import google.generativeai as genai

from PIL import Image  # Tasveer parhne ke liye zaroori hai



# --- 1. CONFIGURATION ---

GOOGLE_API_KEY = "AIzaSyDRLw82kbZmh5HdaXLKuo-UejHcngqWuRc"

genai.configure(api_key=GOOGLE_API_KEY)



# --- 2. MODEL SELECTION ---

@st.cache_resource

def get_best_model():

    try:

        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

        if 'models/gemini-1.5-flash' in available_models:

            return 'models/gemini-1.5-flash'

        elif 'models/gemini-pro' in available_models:

            return 'models/gemini-pro'

        return available_models[0] if available_models else None

    except:

        return None



best_model_name = get_best_model()



# --- 3. PAGE UI ---

st.set_page_config(page_title="GURU AI", page_icon="⭐")

st.title("⭐ GURU AI")



# --- 4. SIDEBAR (Image Upload Feature) ---

with st.sidebar:

    st.header("GURU Settings")

    

    # Image Upload Option

    uploaded_file = st.file_uploader("Koi photo upload karein (Optional)", type=['png', 'jpg', 'jpeg'])

    

    if uploaded_file:

        st.image(uploaded_file, caption="Selected Image", use_container_width=True)

    

    if st.button("Clear Chat History"):

        st.session_state.messages = []

        st.rerun()

    

    st.write("---")

    st.success("GURU is Online")



# --- 5. CHAT MEMORY ---

if "messages" not in st.session_state:

    st.session_state.messages = []



for message in st.session_state.messages:

    name = "GURU" if message["role"] == "assistant" else "Tayyab"

    with st.chat_message(message["role"]):

        st.markdown(f"**{name}:** {message['content']}")



# --- 6. CHAT LOGIC ---

if prompt := st.chat_input("GURU se kuch puchiye..."):

    

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):

        st.markdown(f"**Tayyab:** {prompt}")



    with st.chat_message("assistant"):

        try:

            model = genai.GenerativeModel(

                model_name=best_model_name,

                system_instruction="Aapka naam GURU hai. Aap ek aqalmand ustad hain.Hamesha 'Assalam-o-Alaikum' se baat shuru karein aur 'Namaste' hargiz na kahein. Kahein. Agar koi puche 'Who are you' to hamesha kahein 'Main GURU hoon Mujy Tayyab ny bnaya hai'."

            )

            

            st.write("**GURU:**")

            

            # Agar image hai to image + text dono bhejain, warna sirf text

            if uploaded_file:

                img = Image.open(uploaded_file)

                # Dono cheezein list mein jati hain

                response = model.generate_content([prompt, img], stream=True)

            else:

                response = model.generate_content(prompt, stream=True)

            

            full_response = st.write_stream((chunk.text for chunk in response))

            st.session_state.messages.append({"role": "assistant", "content": full_response})

                    

        except Exception as e:

            st.error(f"GURU ko masla aya: {e}")

