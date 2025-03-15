"""
Run NBA PrizePicks Predictor with CloudflareBypass for improved scraping.
This will install and start the CloudflareBypass server automatically.
"""

import os
import sys
import time
import subprocess
import requests

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARE_DIR = os.path.join(PROJECT_ROOT, "CloudflareBypassForScraping")

def verify_setup():
    """Verify the CloudflareBypass setup."""
    if not os.path.exists(CLOUDFLARE_DIR):
        print(f"CloudflareBypassForScraping not found at: {CLOUDFLARE_DIR}")
        return False
    
    server_script = os.path.join(CLOUDFLARE_DIR, "server.py")
    if not os.path.exists(server_script):
        print(f"Server script not found at: {server_script}")
        return False
    
    return True

def check_server_running():
    """Check if the CloudflareBypass server is already running."""
    try:
        response = requests.get("http://localhost:8000/cookies?url=https://google.com", timeout=2)
        if response.status_code == 200:
            print("CloudflareBypass server is already running!")
            return True
    except:
        pass
    return False

# Step 1: Setup CloudflareBypass if not already installed
print("Step 1: Setting up CloudflareBypass...")
try:
    # Try to import the setup script, install if not found
    try:
        from setup_cloudflare_bypass import setup_cloudflare_bypass, start_server_thread
    except ImportError:
        print("CloudflareBypass setup script not found, creating it...")
        # Clone the repository directly to make sure it exists
        if not os.path.exists(CLOUDFLARE_DIR):
            subprocess.run(["git", "clone", "https://github.com/sarperavci/CloudflareBypassForScraping.git", CLOUDFLARE_DIR], check=True)
            print(f"Repository cloned to {CLOUDFLARE_DIR}")
        
        # Try importing again after cloning
        try:
            from setup_cloudflare_bypass import setup_cloudflare_bypass, start_server_thread
        except ImportError:
            # If still can't import, we'll need to exit
            print("Error: Could not import setup_cloudflare_bypass even after cloning the repository.")
            print("Please run setup_cloudflare_bypass.py separately and then try again.")
            sys.exit(1)
    
    # Run the setup
    setup_success = setup_cloudflare_bypass()
    if not setup_success:
        print("CloudflareBypass setup failed.")
        # Continue anyway but the server likely won't work
    else:
        print("CloudflareBypass setup complete!")
    
except Exception as e:
    print(f"Error setting up CloudflareBypass: {e}")
    print("Try running 'python setup_cloudflare_bypass.py' separately to fix any issues.")
    print("Continuing without CloudflareBypass...")

# Step 2: Start the CloudflareBypass server if it's not already running
print("\nStep 2: Starting CloudflareBypass server...")
server_running = check_server_running()

if not server_running:
    try:
        if verify_setup():
            server_thread = start_server_thread()
            print("Waiting for server to start...")
            
            # Try to verify server is running
            for _ in range(5):  # Try 5 times
                try:
                    response = requests.get("http://localhost:8000/cookies?url=https://google.com", timeout=2)
                    if response.status_code == 200:
                        print("CloudflareBypass server is now running!")
                        server_running = True
                        break
                except:
                    pass
                time.sleep(2)
                
            if not server_running:
                print("Warning: Could not verify if server is running. Will continue anyway.")
        else:
            print("Server verification failed. Cannot start CloudflareBypass server.")
    except Exception as e:
        print(f"Error starting CloudflareBypass server: {e}")
        print("Continuing without CloudflareBypass...")
else:
    print("CloudflareBypass server is already running. No need to start it again.")

# Step 3: Run the NBA PrizePicks Predictor with CloudflareBypass enabled
print("\nStep 3: Starting NBA PrizePicks Predictor...")
print("The application will now use CloudflareBypass to help scrape PrizePicks data.")
if server_running:
    print("CloudflareBypass is active and should reduce the number of CAPTCHAs you encounter.")
else:
    print("Warning: CloudflareBypass server is not running. You may still encounter CAPTCHAs.")
print("")

# Run the application with the compare flag to enable PrizePicks comparisons
os.system("python run.py run --compare") 