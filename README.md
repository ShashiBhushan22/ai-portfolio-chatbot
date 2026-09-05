# 🤖 AI Portfolio Chatbot

This conversational assistant lives on my portfolio website ([shashibhushanjha.me](https://shashibhushanjha.me)) and answers questions about my education, research, projects, and technical experience.

The implementation includes:
- **LLM Integration** - A configurable Groq production model with automatic fallback
- **RAG (Retrieval Augmented Generation)** - Context-aware responses from my knowledge base
- **Full-Stack Development** - FastAPI backend + embeddable JavaScript widget
- **Cloud Deployment** - Deployed on Render's free tier with optimized memory usage

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![Groq](https://img.shields.io/badge/Groq-GPT--OSS-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Why I Built This

As an M.Tech graduate in Communication and Signal Processing, I wanted a project that:
1. Makes my research profile easier for visitors to explore
2. Provides an interactive way for visitors to learn about my work
3. Showcases end-to-end development from concept to deployment

## ✨ Features

- **🧠 RAG-Powered Responses** - The chatbot retrieves relevant context from my resume, projects, and about page before generating responses
- **⚡ Fast Responses** - Powered by Groq's lightning-fast inference API
- **💬 Conversation Memory** - Maintains context across messages in a session
- **🎨 Clean Widget UI** - Modern, responsive chat interface that can be embedded on any website
- **🔒 Rate Limiting** - Built-in protection against API abuse
- **💰 Cost-Effective** - Runs on Groq's free tier + Render's free tier

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Chat Widget    │────▶│  FastAPI Server │────▶│   Groq API      │
│  (JavaScript)   │     │  + RAG Pipeline │     │  (GPT-OSS)      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   TF-IDF Index  │
                        │   (Knowledge    │
                        │     Base)       │
                        └─────────────────┘
```

## 📁 Project Structure

```
ai-portfolio-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── chat_lightweight.py  # Chat engine with Groq API
│   │   ├── rag_lightweight.py   # TF-IDF based retrieval
│   │   └── prompts.py           # System prompts & personality
│   ├── data/
│   │   ├── resume.md             # CV facts
│   │   ├── projects.md           # Project descriptions
│   │   └── about.md              # Research profile
│   └── requirements.txt
├── frontend/
│   ├── chat-widget.js           # Embeddable chat widget
│   └── chat-widget.css          # Widget styles
└── README.md
```

## 🛠️ Tech Stack

| Component | Technology | Why I Chose It |
|-----------|------------|----------------|
| **Backend** | FastAPI | Async support, automatic docs, type hints |
| **LLM** | Groq (configurable production model) | Fast inference and model flexibility |
| **Retrieval** | TF-IDF (scikit-learn) | Lightweight, works within 512MB RAM |
| **Hosting** | Render | Free tier, auto-deploys from GitHub |
| **Frontend** | Vanilla JS | No build step, easy to embed anywhere |

## 🚀 Running Locally

```bash
# Clone the repo
git clone https://github.com/ShashiBhushan22/ai-portfolio-chatbot.git
cd ai-portfolio-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set your Groq API key (get free at https://console.groq.com)
export GROQ_API_KEY=your_key_here

# Optional model overrides
export GROQ_MODEL=openai/gpt-oss-120b
export GROQ_FALLBACK_MODELS=openai/gpt-oss-20b

# Run the server
uvicorn app.main:app --reload --port 8000
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health status |
| `/chat` | POST | Send message, get response |
| `/chat/stream` | POST | Streaming response (SSE) |

### Example Request

```bash
curl -X POST https://ai-portfolio-chatbot-apme.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your skills?"}'
```

## 🎨 Embedding on Your Website

```html
<link rel="stylesheet" href="path/to/chat-widget.css">
<div id="chat-widget-container"></div>
<script src="path/to/chat-widget.js"></script>
<script>
    ChatWidget.init({
        apiUrl: 'https://your-backend-url.com',
        theme: 'dark'
    });
</script>
```

## 💡 Technical Decisions

### Why TF-IDF instead of Vector Embeddings?
Originally I used sentence-transformers with FAISS, but it required PyTorch (~900MB) which exceeded Render's free tier limit of 512MB. TF-IDF with scikit-learn achieves similar results for my small knowledge base while using only ~50MB.

### Why Groq instead of OpenAI?
Groq provides low-latency inference and an OpenAI-compatible chat interface. The model IDs are environment-configurable so provider migrations do not require code changes.

## 📈 Future Improvements

- [ ] Add conversation persistence with a database
- [ ] Implement streaming responses in the widget
- [ ] Add analytics to track common questions
- [ ] Support multiple languages
- [ ] Add voice input/output

## 📄 License

MIT License - feel free to use this as a template for your own portfolio chatbot!

## � Acknowledgments

This project was built with significant help from **Claude (Anthropic)** - an AI assistant that helped with architecture decisions, code implementation, debugging deployment issues, and writing this documentation. It's a great example of human-AI collaboration in software development.

## 👤 About Me

**Shashi Bhushan Jha**
- 🎓 M.Tech in Electrical Engineering, IIT Ropar (2024-2026)
- 🔬 Completed research: analytical and simulated performance evaluation of generalized N-user NOMA systems
- 🌱 Prospective interests: quantum communication, 6G, optical, ISAC, NTN, and satellite communication
- 🌐 Website: [shashibhushanjha.me](https://shashibhushanjha.me)
- 📧 Email: bhushan.gate2022@gmail.com
- 💻 GitHub: [@ShashiBhushan22](https://github.com/ShashiBhushan22)

---

*This chatbot demonstrates how AI tools can help developers build and deploy projects efficiently. Built with human creativity + AI assistance.* 🤝

