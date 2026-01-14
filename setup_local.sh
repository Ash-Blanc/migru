#!/bin/bash

# Migru Local LLM Setup Script
# Sets up local models and privacy-first configuration

set -e

echo "🌸 Migru Local LLM Setup"
echo "=========================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect system architecture
detect_arch() {
    if [[ "$(uname -m)" == "arm64" ]] || [[ "$(uname -m)" == "aarch64" ]]; then
        echo "arm64"
    else
        echo "amd64"
    fi
}

# Check Python version
echo "🐍 Checking Python version..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "Found Python $PYTHON_VERSION"
    
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 12) else 1)'; then
        echo "✅ Python 3.12+ satisfied"
    else
        echo "❌ Python 3.12+ required. Current version: $PYTHON_VERSION"
        exit 1
    fi
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check if uv is installed
echo "📦 Checking uv package manager..."
if command_exists uv; then
    echo "✅ uv found"
else
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command_exists uv; then
        echo "❌ Failed to install uv"
        exit 1
    fi
    echo "✅ uv installed successfully"
fi

# Install dependencies
echo "📚 Installing dependencies..."
uv sync --dev

# Setup local LLM server
echo "🧠 Setting up Local LLM Server..."

# Check if llama.cpp is available or install it
LLAMACPP_DIR="$HOME/llama.cpp"
if [ ! -d "$LLAMACPP_DIR" ]; then
    echo "📥 Cloning llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp.git "$LLAMACPP_DIR"
    cd "$LLAMACPP_DIR"
    
    echo "🔨 Building llama.cpp..."
    make LLAMA_OPENBLAS=1
    
    echo "✅ llama.cpp built successfully"
else
    echo "✅ llama.cpp already found"
fi

# Download FunctionGemma model for tool calling
echo "🔄 Downloading FunctionGemma model..."
cd "$LLAMACPP_DIR"

# FunctionGemma 7B model URL
FUNCTION_GEMMA_URL="https://huggingface.co/google/gemma-7b-it/resolve/main/gemma-7b-it.gguf?download=true"
MODEL_DIR="$LLAMACPP_DIR/models"
mkdir -p "$MODEL_DIR"

if [ ! -f "$MODEL_DIR/function-gemma-7b.gguf" ]; then
    echo "📥 Downloading FunctionGemma 7B model (this may take a while)..."
    curl -L -o "$MODEL_DIR/function-gemma-7b.gguf" "$FUNCTION_GEMMA_URL"
    echo "✅ FunctionGemma model downloaded"
else
    echo "✅ FunctionGemma model already exists"
fi

# Alternative: Download smaller models if user prefers
echo "📥 Downloading additional models..."

# Qwen2.5:3B (fast empathetic model)
QWEN_MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_0.gguf?download=true"
if [ ! -f "$MODEL_DIR/qwen2.5-3b.gguf" ]; then
    echo "📥 Downloading Qwen2.5:3B model..."
    curl -L -o "$MODEL_DIR/qwen2.5-3b.gguf" "$QWEN_MODEL_URL"
    echo "✅ Qwen2.5 model downloaded"
else
    echo "✅ Qwen2.5 model already exists"
fi

# Create environment configuration
echo "⚙️ Creating environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Add local LLM configuration to .env
cat >> .env << EOF

# Local LLM Configuration (Privacy-First)
LOCAL_LLM_ENABLED=true
LOCAL_LLM_HOST=http://localhost:8080
LOCAL_LLM_MODEL=function-gemma:7b
LOCAL_LLM_API_KEY=not-needed

# Privacy Mode Configuration
PRIVACY_MODE=hybrid
ENABLE_SEARCH_IN_LOCAL_MODE=false

# Local Server Configuration
LLAMACPP_HOST=http://localhost:8080
LOCAL_SERVER_TYPE=llamacpp

# Model Paths
LLAMACPP_MODELS_DIR=$MODEL_DIR
EOF

echo "✅ Environment configuration updated"

# Create startup script for llama.cpp server
echo "🚀 Creating startup script..."
cat > start_local_server.sh << 'EOF'
#!/bin/bash

# Migru Local LLM Server Startup Script

echo "🧠 Starting Local LLM Server..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LLAMACPP_DIR="$HOME/llama.cpp"
MODEL_DIR="$LLAMACPP_DIR/models"

# Check if models exist
if [ ! -f "$MODEL_DIR/function-gemma-7b.gguf" ]; then
    echo "❌ FunctionGemma model not found. Please run setup.sh first."
    exit 1
fi

# Start llama.cpp server with FunctionGemma
echo "🔄 Starting llama.cpp server on http://localhost:8080"
cd "$LLAMACPP_DIR"

./server \
    -m "$MODEL_DIR/function-gemma-7b.gguf" \
    --host 0.0.0.0 \
    --port 8080 \
    -c 2048 \
    --batch-size 2048 \
    --ctx-size 2048 \
    -ngl 33 \
    --threads 4 \
    --temp 0.7 \
    --repeat-penalty 1.1 \
    --log-format json \
    --verbose

echo "🛑 Local LLM server stopped"
EOF

chmod +x start_local_server.sh
echo "✅ Startup script created"

# Create systemd service (optional)
echo "🔧 Creating systemd service (optional)..."
if command_exists systemctl; then
    SERVICE_CONTENT="[Unit]
Description=Migru Local LLM Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$LLAMACPP_DIR
ExecStart=$LLAMACPP_DIR/server -m $MODEL_DIR/function-gemma-7b.gguf --host 0.0.0.0 --port 8080 -c 2048 --batch-size 2048 --ctx-size 2048 -ngl 33 --threads 4 --temp 0.7 --repeat-penalty 1.1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"

    echo "$SERVICE_CONTENT" | sudo tee /etc/systemd/system/migru-local-llm.service > /dev/null
    echo "✅ Systemd service created (use with: sudo systemctl enable migru-local-llm)"
fi

# Create test script
echo "🧪 Creating test script..."
cat > test_local_setup.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for local LLM setup
"""
import asyncio
import httpx
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_local_server():
    """Test local LLM server connection."""
    print("🧪 Testing Local LLM Server...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8080/health")
            if response.status_code == 200:
                print("✅ Local server is running!")
                return True
            else:
                print(f"❌ Server returned status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to local server: {e}")
        return False

async def test_model_response():
    """Test model response generation."""
    print("🧪 Testing Model Response...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "prompt": "Hello! How are you feeling today?",
                "max_tokens": 100,
                "temperature": 0.7,
                "stream": False
            }
            
            response = await client.post(
                "http://localhost:8080/completion",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Model generated response!")
                print(f"📝 Response: {result.get('content', 'No content')[:100]}...")
                return True
            else:
                print(f"❌ Model request failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🌸 Migru Local LLM Setup Test")
    print("==============================")
    
    # Test server connection
    server_ok = await test_local_server()
    
    if server_ok:
        # Test model response
        model_ok = await test_model_response()
        
        if model_ok:
            print("\n🎉 All tests passed! Your local LLM setup is working.")
            print("\nTo start Migru:")
            print("  1. Make sure the local server is running: ./start_local_server.sh")
            print("  2. Run Migru: uv run -m app.main")
        else:
            print("\n❌ Model test failed. Check server logs.")
    else:
        print("\n❌ Server not running. Start it with: ./start_local_server.sh")

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x test_local_setup.py
echo "✅ Test script created"

# Final instructions
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📋 Next Steps:"
echo "1. Start the local LLM server:"
echo "   ./start_local_server.sh"
echo ""
echo "2. Test the setup (in a new terminal):"
echo "   python3 test_local_setup.py"
echo ""
echo "3. Run Migru with local models:"
echo "   uv run -m app.main"
echo ""
echo "🔒 Privacy Features:"
echo "- Local AI processing (100% private)"
echo "- Optional web search (hybrid mode)"
echo "- Runtime privacy mode switching"
echo "- Multiple local model support"
echo ""
echo "📚 Available Models:"
echo "- FunctionGemma 7B (tool calling, routing)"
echo "- Qwen2.5 3B (empathetic, fast)"
echo ""
echo "⚙️ Configuration:"
echo "- Edit .env to change settings"
echo "- Use /privacy command in Migru to switch modes"
echo "- Use /local command to manage models"
echo ""
echo "🐛 Troubleshooting:"
echo "- If server fails: Check GPU drivers and model files"
echo "- If responses are slow: Try smaller models or check system resources"
echo "- For help: Check README.md or open an issue"
echo ""
echo "🌸 Enjoy your private AI companion!"