import os
import ollama
import streamlit as st
from PIL import Image, ImageOps

# ==========================================
# WEB APP CONFIGURATION
# ==========================================
MODEL_NAME = "moondream"

# Page layout styling
st.set_page_config(page_title="Local Medical AI Assistant", layout="centered")
st.title("🩻 Local Chest X-Ray Analyzer")
st.write("Upload a chest radiograph to extract radiological findings, suspected condition, and treatment guidelines on your local system.")

def preprocess_xray(uploaded_file):
    """
    Optimizes the uploaded image for the local vision model by enhancing grayscale contrast.
    """
    # Open the uploaded file object directly with Pillow
    img = Image.open(uploaded_file)
    
    # Convert to single-channel grayscale and maximize contrast
    gray_img = ImageOps.grayscale(img)
    enhanced_img = ImageOps.equalize(gray_img)
    
    # Save a temporary file for Ollama API validation
    temp_path = "processed_web_temp.jpg"
    enhanced_img.save(temp_path, format="JPEG", quality=90)
    return temp_path

# 1. Native HTTP Browser File Upload Component
uploaded_file = st.file_uploader(
    label="Choose a chest X-ray file...", 
    type=["jpg", "jpeg", "png", "bmp"]
)

if uploaded_file is not None:
    # Display the uploaded image cleanly in the browser layout
    st.image(uploaded_file, caption="Uploaded Radiograph Profile", use_container_width=True)
    
    # Button trigger to begin computation
    if st.button("Investigate Image Findings"):
        with st.spinner("Analyzing image array via local model... Please wait."):
            try:
                # Pre-process image matrix
                temp_img_path = preprocess_xray(uploaded_file)
                
                # Context prompt construction
                prompt_text = (
                    "You are an expert radiologist AI assistant. Analyze this chest X-ray image in detail. "
                    "Provide your report strictly structured as follows:\n\n"
                    "### 1. Radiological Findings\n(Describe lung fields, heart silhouette size, costophrenic angles)\n\n"
                    "### 2. Suspected Primary Disease\n(State your primary diagnostic suspicion)\n\n"
                    "### 3. Clinical Management & Treatment Guidelines\n(State standard clinical first-lines, pharmaceutical insights, and physical recovery tracks)"
                )
                
                # Execute inference pipeline with Ollama backend
                response = ollama.generate(
                    model=MODEL_NAME,
                    prompt=prompt_text,
                    images=[temp_img_path]
                )
                
                # Delete temp file cleanly from local storage
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
                
                # Render results on the web screen
                st.success("Analysis Complete!")
                st.markdown("---")
                st.markdown("## 📋 Medical AI Report")
                st.write(response['response'])
                st.markdown("---")
                st.warning("⚠️ Disclaimer: For preliminary screening assistance only. Cross-reference generated paths with active medical guidelines.")
                
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")