import os
import ollama
from PIL import Image, ImageOps
import tkinter as tk
from tkinter import filedialog

# ==========================================
# CONFIGURATION
# ==========================================
MODEL_NAME = "moondream"  # Optimized, lightweight local vision model

def get_image_path_via_dialog():
    """
    Opens a native Windows file dialog to let you select an X-ray image.
    """
    # Create a hidden root window so only the file picker shows up
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)  # Brings the file window to the front
    
    print("[*] Opening file explorer... Please select your X-ray image.")
    file_path = filedialog.askopenfilename(
        title="Select Chest X-Ray Image",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.dicom"), ("All Files", "*.*")]
    )
    
    return file_path

def preprocess_xray(image_path):
    """
    Optimizes the X-ray image for the vision model.
    Converts to grayscale and enhances contrast of lung fields.
    """
    print(f"[*] Pre-processing X-ray image: {image_path}")
    output_path = "processed_temp.jpg"
    
    with Image.open(image_path) as img:
        # Convert to single-channel grayscale and maximize contrast
        gray_img = ImageOps.grayscale(img)
        enhanced_img = ImageOps.equalize(gray_img)
        
        # Save a temporary copy for Ollama to read
        enhanced_img.save(output_path, format="JPEG", quality=90)
        return output_path

def analyze_chest_xray(image_path):
    if not image_path:
        print("[!] No file was selected. Exiting.")
        return None
        
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image '{image_path}' not found!")
        
    # Process image
    temp_processed_image = preprocess_xray(image_path)
    
    print(f"[*] Sending image to local {MODEL_NAME} engine...")
    
    # Construct an explicit clinical prompt
    prompt_text = (
        "You are an expert radiologist AI assistant. Analyze this chest X-ray image in detail. "
        "Provide: 1. Radiological Findings (lung fields, heart silhouette). "
        "2. Suspected Primary Disease. "
        "3. Standard Clinical Management/Prescription Guidelines."
    )
    
    # Generate response via Ollama
    response = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt_text,
        images=[temp_processed_image]
    )
    
    # Clean up the temporary file
    if os.path.exists(temp_processed_image):
        os.remove(temp_processed_image)
        
    return response['response']

if __name__ == "__main__":
    try:
        # 1. Pop up window to pick an image from your computer
        selected_file = get_image_path_via_dialog()
        
        if selected_file:
            # 2. Run the medical engine on the selected image
            analysis_report = analyze_chest_xray(selected_file)
            
            if analysis_report:
                print("\n==================================================================")
                print("                      MEDICAL AI ANALYSIS REPORT                 ")
                print("==================================================================")
                print(analysis_report)
                print("==================================================================")
        
    except Exception as e:
        print(f"\n[!] Execution Error: {str(e)}")