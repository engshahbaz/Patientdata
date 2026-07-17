import os
import subprocess
import time
import webbrowser

# 1. Path to your Streamlit script
STREAMLIT_SCRIPT = "xray_app.py"
PORT = "8501"
URL = f"http://localhost:{PORT}"

def launch_in_firefox():
    # Wait briefly for the Streamlit server to initialize
    time.sleep(2)
    try:
        # Force Python to look for Firefox specifically
        firefox = webbrowser.get('firefox')
        firefox.open(URL)
        print("🚀 Successfully launched X-Ray app in Firefox.")
    except Exception:
        # Fallback if the standard registry/path lookup fails
        print("⚠️ Direct Firefox lookup failed, attempting system path launch...")
        try:
            # Common paths for Firefox depending on OS
            if os.name == 'nt':  # Windows
                ff_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
            else:  # Linux / macOS
                ff_path = "firefox"
            
            subprocess.Popen([ff_path, URL])
        except Exception as e:
            print(f"Could not open Firefox automatically: {e}")
            print(f"Please open Firefox manually and go to: {URL}")

if __name__ == "__main__":
    # 2. Start the Streamlit server in the background without auto-opening the default browser
    print("🤖 Starting Local Chest X-Ray Analyzer server...")
    server_process = subprocess.Popen(
        ["streamlit", "run", STREAMLIT_SCRIPT, "--server.port", PORT, "--server.headless", "true"]
    )
    
    # 3. Trigger the Firefox launch thread/function
    launch_in_firefox()
    
    try:
        # Keep the main process alive so the server runs
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down X-Ray Analyzer server.")
        server_process.terminate()