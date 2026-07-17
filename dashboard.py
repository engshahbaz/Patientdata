import subprocess
import webbrowser
import time
import os

STREAMLIT_SCRIPT = "dashboard_app.py"
PORT = "8520"  # Dedicated network port for the dashboard app
URL = f"http://localhost:{PORT}"

def launch_in_firefox():
    time.sleep(3)  # Allows background system components to spin up safely
    try:
        firefox = webbrowser.get('firefox')
        firefox.open(URL)
        print(f"🚀 Dashboard launched successfully in Firefox on port {PORT}.")
    except Exception:
        print("⚠️ Direct Firefox path target failed, trying fallback configurations...")
        try:
            if os.name == 'nt':  # Windows environment default path
                ff_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
            else:  # Linux / macOS environment default command
                ff_path = "firefox"
            
            subprocess.Popen([ff_path, URL])
        except Exception as e:
            print(f"Could not open Firefox automatically: {e}")
            print(f"Please open Firefox manually and go to: {URL}")

if __name__ == "__main__":
    print("🤖 Launching Local Streamlit Healthcare Dashboard Server...")
    server_process = subprocess.Popen(
        ["streamlit", "run", STREAMLIT_SCRIPT, "--server.port", PORT, "--server.headless", "true"]
    )
    
    launch_in_firefox()
    
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Dashboard server.")
        server_process.terminate()