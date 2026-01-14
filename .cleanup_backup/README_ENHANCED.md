# Migru - Privacy-First AI Companion for Migraine & Stress Relief

Migru is a **local-first**, personal, and private AI-powered companion designed to support you through migraines and stress with empathy and research-backed relief strategies. It combines ultra-fast local responses with optional web search for complete privacy control.

## 🌟 Key Features

- **🔒 Privacy-First Local LLM Integration**: Complete local AI processing with FunctionGemma, Qwen2.5, and other models
- **🧠 Smart Agent Routing**: FunctionGemma-powered router for intelligent agent selection
- **🌿 Empathetic Conversations**: Local models optimized for therapeutic support
- **🔍 Optional Web Search**: Privacy-aware search tools only when you want them
- **⚡ Ultra-Fast Responses**: Local inference eliminates network latency
- **🎨 Beautiful CLI**: Rich themes and accessibility features
- **📊 Real-time Analytics**: Pattern detection and wellness insights

## 🛠️ Installation

### Quick Setup with Local LLM Support

```bash
# Clone the repository
git clone <repository-url>
cd migru

# Run the enhanced setup script
./setup_local.sh
```

The setup script will:
- ✅ Check Python 3.12+ and install dependencies
- ✅ Set up llama.cpp server with FunctionGemma
- ✅ Download optimized local models (Qwen2.5:3B, FunctionGemma:7B)
- ✅ Configure privacy-first environment
- ✅ Create startup scripts and test tools

### Manual Setup

```bash
# Install dependencies
uv sync --dev

# Install llama.cpp (recommended for local models)
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make LLAMA_OPENBLAS=1

# Download FunctionGemma model
mkdir -p models
cd models
wget https://huggingface.co/google/gemma-7b-it/resolve/main/gemma-7b-it.gguf -O function-gemma-7b.gguf

# Configure environment
cp .env.example .env
```

## 🚀 Usage

### Start Local LLM Server

```bash
# Start the llama.cpp server
./start_local_server.sh
```

### Run Migru

```bash
# Start with local models
uv run -m app.main_enhanced

# Or with custom user
uv run -m app.main_enhanced --user YourName
```

## 🔒 Privacy Modes

### Local Mode (100% Private)
- **AI Processing**: 100% local, no external APIs
- **Web Search**: Disabled completely
- **Data**: Never leaves your device
- **Recommended**: For sensitive conversations and complete privacy

### Hybrid Mode (Local AI + Optional Search)
- **AI Processing**: Local models for conversations
- **Web Search**: Available when explicitly needed
- **Control**: You choose when to use external services
- **Recommended**: Balance of privacy and functionality

### Flexible Mode (User Choice)
- **AI Processing**: Local or cloud based on preference
- **Web Search**: Always available
- **Control**: Full flexibility per session
- **Recommended**: Power users who want options

## 🧠 Local Models

### Recommended Models

| Model | Size | Best For | Privacy Mode |
|--------|-------|-----------|--------------|
| **FunctionGemma 7B** | 7B | Routing, Tool Calling, Research | All |
| **Qwen2.5 3B** | 3B | Empathetic Support, Speed | All |
| **Phi3.5 3.8B** | 3.8B | Balanced Reasoning, Advice | All |
| **Gemma2 2B** | 2B | Lightweight, Fallback | All |

### Model Selection

Migru automatically selects the optimal model based on your conversation type:

- **Emotional Support** → Qwen2.5:3B (warm, empathetic)
- **Research & Tool Calling** → FunctionGemma:7B (reliable, structured)
- **Practical Advice** → Phi3.5:3.8B (balanced reasoning)
- **General Conversation** → Qwen2.5:3B (fast, natural)

## 🎮 Commands

### Privacy & Model Management

```bash
# Check current privacy settings
/privacy status

# Switch privacy mode
/privacy local      # 100% private
/privacy hybrid     # Local AI + optional search  
/privacy flexible   # User choice

# Manage local models
/local status        # Show current model
/local models        # List available models
/local switch qwen2.5:3b    # Switch models
/local test         # Test connection
```

### Conversation & Search

```bash
# Natural conversation
I'm feeling anxious today
Help me understand my migraines

# Search (when allowed)
/search latest migraine research
/weather New York
/research natural remedies for headaches
```

### Wellness Features

```bash
/patterns             # View your wellness patterns
/insights             # Get personalized insights  
/nudges               # Show wellness suggestions
/theme ocean           # Switch UI theme
```

### System Controls

```bash
/status               # System status
/help                 # Show all commands
/quit                 # Exit
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your preferences:

```bash
# Local LLM Configuration
LOCAL_LLM_ENABLED=true
LOCAL_LLM_HOST=http://localhost:8080
LOCAL_LLM_MODEL=function-gemma:7b
PRIVACY_MODE=hybrid
ENABLE_SEARCH_IN_LOCAL_MODE=false

# Local Server Settings
LLAMACPP_HOST=http://localhost:8080
OLLAMA_HOST=http://localhost:11434
LOCAL_SERVER_TYPE=llamacpp

# Cloud Fallbacks (optional)
MISTRAL_API_KEY=your_key_here
CEREBRAS_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Search & Weather (optional)
FIRECRAWL_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here

# Database
REDIS_URL=redis://localhost:6379
```

## 🏗️ Architecture

### Smart Router System

```
User Message → FunctionGemma Router → Task Analysis → Optimal Agent Selection
                                     ↓
                    Emotional Support → Qwen2.5:3B → Companion Agent
                    Research         → FunctionGemma:7B → Researcher Agent  
                    Practical Advice  → Phi3.5:3.8B → Advisor Agent
```

### Privacy-Aware Tools

```
Privacy Mode Controls:
├── Local Mode     → No external APIs, 100% private
├── Hybrid Mode    → Local AI + optional search tools
└── Flexible Mode  → User choice per interaction

Search Tools:
├── DuckDuckGo     → Fast, private search
├── Firecrawl       → Deep web scraping
└── OpenWeather     → Weather data (optional)
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest tests/

# Run local LLM tests
pytest tests/unit/test_local_integration.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing

# Test specific components
pytest tests/unit/test_local_integration.py::TestLocalLlamaModel -v
```

### Local Setup Test

```bash
# Test your local LLM setup
python3 test_local_setup.py
```

## 🌿 Benefits

### Privacy Benefits
- **Complete Data Control**: All conversations processed locally
- **No Data Leakage**: Optional external calls only with consent
- **Offline Capability**: Works without internet connection
- **User Sovereignty**: Full control over AI model and data

### Performance Benefits  
- **Ultra-Fast Responses**: Local inference eliminates network latency
- **Cost Efficiency**: No API calls for basic conversations
- **Reliability**: Works even when cloud services are down
- **Resource Optimized**: Small models for efficient memory usage

### Flexibility Benefits
- **Gradual Migration**: Start hybrid, move to fully local
- **Model Choice**: Support for multiple local LLM servers
- **Runtime Control**: Switch privacy modes without restarting
- **Optional Features**: Search available when needed, disabled by default

## 🔧 Troubleshooting

### Local Model Issues

```bash
# Check model files
ls -la ~/llama.cpp/models/

# Test connection
curl http://localhost:8080/health

# Check server logs
./start_local_server.sh
```

### Performance Optimization

```bash
# Use smaller models for faster responses
export LOCAL_LLM_MODEL=qwen2.5:3b

# Reduce context for speed
export NUM_HISTORY_RUNS=1

# Disable tools for simplicity
export ENABLE_SEARCH_IN_LOCAL_MODE=false
```

### Common Issues

1. **Model not found**: Ensure models are downloaded correctly
2. **Server won't start**: Check GPU drivers and system resources
3. **Slow responses**: Try smaller models or check system memory
4. **Search disabled**: Switch to hybrid/flexible privacy mode

## 📚 Development

### Project Structure

```
app/
├── models/                # Local LLM integration
│   └── local_llm.py    # Local model management
├── agents/               # Smart routing system
│   └── smart_router.py   # FunctionGemma router
├── core.py               # Enhanced Migru core
├── tools/                # Privacy-aware tools
│   └── privacy_tools.py # Search with privacy controls
├── main_enhanced.py     # Updated CLI interface
└── config_enhanced.py   # Enhanced configuration
```

### Adding New Local Models

```python
# Add to model_manager.model_configs
"new-model:4b": {
    "description": "New model description",
    "best_for": ["specific_task"],
    "temperature": 0.7,
    "max_tokens": 2048
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure privacy-first approach
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **FunctionGemma**: Google for tool calling capabilities
- **Qwen2.5**: Alibaba for efficient empathetic models  
- **llama.cpp**: Georgi Gerganov for fast local inference
- **Agno Framework**: For agent orchestration and tools

---

🌸 **Enjoy your private AI companion!** 

For questions, issues, or feature requests, please open an issue on GitHub.