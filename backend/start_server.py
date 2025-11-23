"""Start the FastAPI server"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set API key if not present (use environment variable or .env file)
# For security, do not hardcode API keys in source code
# Set HUGGINGFACE_API_KEY in .env file or environment variables

if __name__ == "__main__":
    import socket
    import sys
    import subprocess
    import platform
    
    def is_port_in_use(port):
        """Check if port is already in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0
    
    def kill_process_on_port(port):
        """Kill process using the specified port"""
        try:
            if platform.system() == "Windows":
                # Find process using port on Windows
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            try:
                                subprocess.run(
                                    f'taskkill /F /PID {pid}',
                                    shell=True,
                                    capture_output=True,
                                    text=True
                                )
                                print(f"✅ Stopped process {pid} on port {port}")
                            except:
                                pass
        except Exception as e:
            print(f"⚠️  Could not free port: {e}")
    
    port = 8006
    print("🚀 Starting Semiconductor Yield Prediction API Server...")
    
    # Check if port is in use and try to free it
    if is_port_in_use(port):
        print(f"⚠️  Port {port} is already in use. Attempting to free it...")
        kill_process_on_port(port)
        import time
        time.sleep(2)
        
        # Check again
        if is_port_in_use(port):
            print(f"❌ Port {port} is still in use.")
            print(f"💡 Please manually stop the process using port {port}")
            print(f"   Or change the port in start_server.py")
            sys.exit(1)
    
    print(f"📍 Server will be available at http://127.0.0.1:{port}")
    print(f"📖 API docs at http://127.0.0.1:{port}/docs")
    print()
    
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=port,
            reload=False,
            log_level="info"
        )
    except OSError as e:
        if "10048" in str(e) or "address already in use" in str(e).lower():
            print(f"\n❌ Error: Port {port} is still in use.")
            print("💡 Please close other instances or change the port")
            sys.exit(1)
        else:
            raise

