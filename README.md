# 🤖 AI Portfolio Chatbot

An intelligent conversational AI assistant for your portfolio website. This chatbot demonstrates practical AI engineering skills including LLM integration, RAG (Retrieval Augmented Generation), and production deployment.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **🧠 RAG-Powered Responses**: Context-aware answers using your resume and projects
- **⚡ Streaming Responses**: Real-time token-by-token output
- **💬 Conversation Memory**: Maintains context across messages
- **🎨 Beautiful Widget**: Modern, responsive chat interface
- **🔒 Rate Limiting**: Protection against API abuse
- **🚀 Easy Deployment**: Docker-ready with Railway/Render configs
- **💰 Cost-Effective**: Works with free Groq API or OpenAI

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Chat Widget    │────▶│  FastAPI Server │────▶│   LLM (Groq/    │
│  (JavaScript)   │     │  + RAG Pipeline │     │   OpenAI)       │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   FAISS Vector  │
                        │     Store       │
                        │ (Your Knowledge │
                        │     Base)       │
                        └─────────────────┘
```

## 📁 Project Structure

```
ai-portfolio-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── chat.py          # Chat engine & LLM integration
│   │   ├── rag.py           # RAG pipeline
│   │   └── prompts.py       # System prompts
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── index.html           # Demo page
│   ├── chat-widget.js       # Embeddable widget
│   └── chat-widget.css      # Widget styles
├── data/
│   ├── resume.md            # Your resume
│   ├── projects.md          # Project descriptions
│   └── about.md             # About you
├── docker-compose.yml
├── railway.toml
├── render.yaml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Groq API key (free) or OpenAI API key

### 1. Clone and Setup

```bash
cd ai-portfolio-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# GROQ_API_KEY=your_key_here (recommended - free!)
# OR
# OPENAI_API_KEY=your_key_here
```

### 3. Customize Knowledge Base

Edit the files in `/data/` directory:
- `resume.md` - Your resume and skills
- `projects.md` - Your project descriptions
- `about.md` - Personal information

### 4. Run Locally

```bash
# From the backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Send a message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your skills?"}'
```

### 6. Test the Widget

Open `frontend/index.html` in your browser to see the chat widget in action.

## 🌐 Deployment

### Option A: Railway (Recommended)

1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables (`GROQ_API_KEY`)
4. Deploy! Railway will use `railway.toml` config

### Option B: Render

1. Create account at [render.com](https://render.com)
2. Create new Web Service from GitHub
3. It will use `render.yaml` config
4. Add environment variables
5. Deploy!

### Option C: Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
cd backend
docker build -t ai-chatbot .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key ai-chatbot
```

## 🔧 Embedding the Widget

Add this code to your website before `</body>`:

```html
<!-- AI Chatbot Widget -->
<link rel="stylesheet" href="https://your-domain.com/chat-widget.css">
<div id="chat-widget-container"></div>
<script src="https://your-domain.com/chat-widget.js"></script>
<script>
    ChatWidget.init({
        apiUrl: 'https://your-api-domain.com',
        theme: 'dark',  // or 'light'
        position: 'bottom-right',
        greeting: "Hi! I'm Shashi's AI Assistant. How can I help you?"
    });
</script>
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health status |
| `/chat` | POST | Send message, get response |
| `/chat/stream` | POST | Streaming response (SSE) |
| `/info` | GET | Chatbot info & suggestions |

### Chat Request Example

```json
{
    "message": "What are your key skills?",
    "conversation_history": [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello! How can I help?"}
    ]
}
```

### Chat Response Example

```json
{
    "response": "My key skills include...",
    "sources": ["resume.md", "projects.md"]
}
```

## ⚙️ Configuration

### LLM Providers

| Provider | Model | Cost | Setup |
|----------|-------|------|-------|
| **Groq** | Llama 3.1 70B | Free tier | [Get API key](https://console.groq.com) |
| **OpenAI** | GPT-4o-mini | $0.15/M tokens | [Get API key](https://platform.openai.com) |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key | Yes (or OpenAI) |
| `OPENAI_API_KEY` | OpenAI API key | Optional |

## 🎨 Customization

### Themes

The widget supports `dark` and `light` themes. Customize colors in `chat-widget.css`:

```css
:root {
    --chat-primary: #6366f1;
    --chat-bg-dark: #1f2937;
    /* ... */
}
```

### Prompts

Edit `backend/app/prompts.py` to customize:
- System personality
- Response style
- Knowledge base integration

## 🛡️ Security Considerations

- ✅ Rate limiting implemented
- ✅ Input sanitization
- ✅ CORS configuration
- ⚠️ Update `allow_origins` in production
- ⚠️ Use HTTPS in production
- ⚠️ Secure your API keys

## 📈 Future Enhancements

- [ ] Add user authentication
- [ ] Implement conversation persistence
- [ ] Add analytics dashboard
- [ ] Support multiple languages
- [ ] Add voice input/output
- [ ] Implement feedback system

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Shashi Bhushan Jha**
- Website: [shashibhushanjha.me](https://shashibhushanjha.me)
- GitHub: [@shashibhushanjha](https://github.com/shashibhushanjha)

---

Built with ❤️ and AI 🤖
