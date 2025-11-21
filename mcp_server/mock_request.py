import subprocess
import sys
import time
import requests
import os
import signal

def run_mock_request():
    # Path to the local server runner
    server_script = "mcp_server/main.py"
    
    # Set environment variables
    env = os.environ.copy()
    env["GCS_BUCKET_NAME"] = "monte-carlo-mcp-assets"
    env["PORT"] = "8080"
    
    # Start the server process
    print("Starting server process...")
    process = subprocess.Popen(
        [sys.executable, server_script],
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True
    )

    # Wait for server to start
    print("Waiting for server to start...")
    server_url = "http://localhost:8080/sse"
    max_retries = 30
    
    try:
        for i in range(max_retries):
            try:
                response = requests.get(server_url, stream=True, timeout=1)
                if response.status_code == 200:
                    print("Server is up and running! (SSE endpoint accessible)")
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(2)
                print(f"Waiting... ({i+1}/{max_retries})")
        else:
            print("Server failed to start within timeout.")
            return

        print("Test passed: Server started and is listening on port 8080.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Terminating server process...")
        os.kill(process.pid, signal.SIGTERM)
        process.wait()
        print("Server process terminated.")

if __name__ == "__main__":
    run_mock_request()
