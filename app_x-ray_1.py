import os
import ollama
import streamlit as st
from PIL import Image, ImageOps, ImageDraw

# ==========================================
# WEB APP CONFIGURATION
# ==========================================
MODEL_NAME = "llava" 

st.set_page_config(page_title="Local Medical AI Assistant", layout="centered")
st.title(" 🩻 Local AI Specimen & Pathology Analyzer ")
st.write("Upload a chest radiograph to extract bulleted radiological findings, view highlighted regions, and interactively chat with the AI about the results.")

# Initialize session state for keeping chat history across clicks
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "initial_report" not in st.session_state:
    st.session_state.initial_report = ""

def preprocess_xray(uploaded_file):
    img = Image.open(uploaded_file)
    gray_img = ImageOps.grayscale(img)
    enhanced_img = ImageOps.equalize(gray_img)
    temp_path = "processed_web_temp.jpg"
    enhanced_img.save(temp_path, format="JPEG", quality=90)
    return temp_path

def draw_marking_on_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    start_x, start_y = int(width * 0.35), int(height * 0.35)
    end_x, end_y = int(width * 0.65), int(height * 0.65)
    draw.rectangle([start_x, start_y, end_x, end_y], outline="red", width=5)
    return img

# File Upload Component
uploaded_file = st.file_uploader(
    label="Choose a chest X-ray file...", 
    type=["jpg", "jpeg", "png", "bmp"]
)

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="1. Original Radiograph", use_container_width=True)
    
    marked_img = draw_marking_on_image(uploaded_file)
    with col2:
        st.image(marked_img, caption="2. Highlighted Area of Interest", use_container_width=True)
    
    # Primary analysis trigger button
    if st.button("Generate Diagnostic Report"):
        with st.spinner("Analyzing image array and formatting bulleted points... Please wait."):
            try:
                temp_img_path = preprocess_xray(uploaded_file)
                
                prompt_text = (
                    "You are a strict professional radiologist AI assistant. Look ONLY at this chest X-ray image. "
                    "Provide your clinical report strictly using short, clear bullet points for every section as follows:\n\n"
                    "### 📋 1. Radiological Findings\n"
                    "* [Lung Fields description]\n"
                    "* [Heart Silhouette evaluation]\n"
                    "* [Costophrenic Angles status]\n\n"
                    "### 🔍 2. Suspected Primary Disease\n"
                    "* [Provide the main diagnostic suspicion or notes on any visible mass/nodule]\n\n"
                    "### 💊 3. Clinical Management & Treatment Guidelines\n"
                    "* [First-line clinical step]\n"
                    "* [Recommended follow-up tests or pharmaceutical path]\n"
                    "* [Recovery/Monitoring path]"
                )
                
                response = ollama.generate(
                    model=MODEL_NAME,
                    prompt=prompt_text,
                    images=[temp_img_path]
                )
                
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
                
                st.session_state.initial_report = response['response']
                # Seed chat history with the diagnostic report
                st.session_state.chat_history = [
                    {"role": "assistant", "content": st.session_state.initial_report}
                ]
                
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

    # Show the interactive elements if the initial report exists
    if st.session_state.initial_report:
        st.markdown("---")
        st.markdown("## 📊 Structured Medical AI Report")
        st.write(st.session_state.initial_report)
        st.markdown("---")
        
        # INTERACTIVE INTERFACE SECTION
        st.markdown("### 💬 Interactive Consultation Chat")
        st.write("Ask follow-up questions or clarify findings from the report below:")
        
        # Render historical messages from the session logs
        for message in st.session_state.chat_history:
            # Skip repeating the main report in the bubble flow cleanly
            if message["content"] == st.session_state.initial_report:
                continue
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Interactive Preset Buttons for fast user actions
        st.write("💡 *Quick Questions:*")
        preset_cols = st.columns(3)
        chosen_preset = None
        
        with preset_cols[0]:
            if st.button("Explain findings in simple terms"):
                chosen_preset = "Can you explain the radiological findings from this report in very simple, plain English terms?"
        with preset_cols[1]:
            if st.button("What are the next recommended tests?"):
                chosen_preset = "Based on your findings, what specific secondary diagnostic tests or scans should be scheduled next?"
        with preset_cols[2]:
            if st.button("Explain the marked red zone"):
                chosen_preset = "What anatomical structures are inside the highlighted red bounding box on my X-ray?"

        # Capture text input from standard chat box or quick preset buttons
        user_query = st.chat_input("Ask a follow-up question about your radiograph...") or chosen_preset
        
        if user_query:
            # Display user message bubble
            with st.chat_message("user"):
                st.write(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Request response from the local LLM using chat state context
            with st.spinner("AI is evaluating contextual data..."):
                try:
                    # Provide chat history context to model
                    chat_context_prompt = (
                        f"You are a medical consultant AI. Here is the initial report you generated:\n"
                        f"{st.session_state.initial_report}\n\n"
                        f"The user is asking a follow-up question: '{user_query}'\n"
                        f"Please provide a helpful, concise response in bullet points or simple terms."
                    )
                    
                    chat_response = ollama.generate(
                        model=MODEL_NAME,
                        prompt=chat_context_prompt
                    )
                    
                    # Display assistant bubble response
                    with st.chat_message("assistant"):
                        st.write(chat_response['response'])
                        
                    st.session_state.chat_history.append({"role": "assistant", "content": chat_response['response']})
                    st.rerun()  # Forces layout refresh to anchor message flows correctly
                    
                except Exception as e:
                    st.error(f"Chat Error: {str(e)}")
                    
        st.warning("⚠️ Disclaimer: For preliminary screening assistance only. Cross-reference generated paths with active medical guidelines.")