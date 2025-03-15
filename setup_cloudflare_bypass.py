import os
import subprocess
import sys
import time
import threading

# Get the absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARE_DIR = os.path.join(PROJECT_ROOT, "CloudflareBypassForScraping")

def clone_repository():
    """Clone the CloudflareBypassForScraping repository if not already present."""
    if not os.path.exists(CLOUDFLARE_DIR):
        print(f"Cloning CloudflareBypassForScraping repository to {CLOUDFLARE_DIR}...")
        subprocess.run(["git", "clone", "https://github.com/sarperavci/CloudflareBypassForScraping.git", CLOUDFLARE_DIR], check=True)
        print("Repository cloned successfully!")
    else:
        print(f"CloudflareBypassForScraping repository already exists at {CLOUDFLARE_DIR}.")

def install_requirements():
    """Install the requirements for the CloudflareBypassForScraping server."""
    current_dir = os.getcwd()
    try:
        if not os.path.exists(CLOUDFLARE_DIR):
            print(f"Error: {CLOUDFLARE_DIR} directory does not exist. Cannot install requirements.")
            return False
            
        os.chdir(CLOUDFLARE_DIR)
        print("Installing server requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "server_requirements.txt"], check=True)
        print("Requirements installed successfully!")
        return True
    except Exception as e:
        print(f"Error installing requirements: {e}")
        return False
    finally:
        os.chdir(current_dir)

def start_server_process():
    """Start the CloudflareBypass server in a separate process."""
    if not os.path.exists(CLOUDFLARE_DIR):
        print(f"Error: {CLOUDFLARE_DIR} directory does not exist. Cannot start server.")
        return None
        
    server_script = os.path.join(CLOUDFLARE_DIR, "server.py")
    if not os.path.exists(server_script):
        print(f"Error: Server script not found at {server_script}")
        return None
        
    process = subprocess.Popen([sys.executable, server_script], cwd=CLOUDFLARE_DIR)
    return process

def start_server_thread():
    """Start the CloudflareBypass server in a background thread."""
    def run_server():
        if not os.path.exists(CLOUDFLARE_DIR):
            print(f"Error: {CLOUDFLARE_DIR} directory does not exist. Cannot start server.")
            return
            
        server_script = os.path.join(CLOUDFLARE_DIR, "server.py")
        if not os.path.exists(server_script):
            print(f"Error: Server script not found at {server_script}")
            return
            
        subprocess.run([sys.executable, server_script], cwd=CLOUDFLARE_DIR)
        
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("CloudflareBypass server started in background thread!")
    
    # Give the server time to start
    time.sleep(5)
    
    # Verify the server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/cookies?url=https://google.com", timeout=5)
        if response.status_code == 200:
            print("Verified server is running successfully!")
        else:
            print(f"Server responded with status code {response.status_code}")
    except Exception as e:
        print(f"Warning: Could not verify if server is running: {e}")
    
    return server_thread

def setup_cloudflare_bypass():
    """Complete setup of the CloudflareBypass server."""
    try:
        clone_repository()
        success = install_requirements()
        if not success:
            print("Failed to install requirements. CloudflareBypass setup incomplete.")
            return False
            
        print("\nSetup complete! You can now start the server with:")
        print(f"python -c 'from setup_cloudflare_bypass import start_server_process; start_server_process()'")
        print("\nOr to start it in a background thread within your application:")
        print("from setup_cloudflare_bypass import start_server_thread; start_server_thread()")
        return True
    except Exception as e:
        print(f"Error setting up CloudflareBypass: {e}")
        return False

if __name__ == "__main__":
    setup_cloudflare_bypass() 