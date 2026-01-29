# 🤖 AI Portfolio Chatbot

I built this AI-powered chatbot to showcase my skills in AI engineering. It's a conversational assistant that lives on my portfolio website ([shashibhushanjha.me](https://shashibhushanjha.me)) and can answer questions about my background, projects, and skills.

This project demonstrates my expertise in:
- **LLM Integration** - Using Groq's Llama 3.3 70B model
- **RAG (Retrieval Augmented Generation)** - Context-aware responses from my knowledge base
- **Full-Stack Development** - FastAPI backend + embeddable JavaScript widget
- **Cloud Deployment** - Deployed on Render's free tier with optimized memory usage

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Why I Built This

As an M.Tech student at IIT Ropar specializing in AI/ML and Signal Processing, I wanted a project that:
1. Demonstrates practical AI engineering skills to potential employers
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
│  (JavaScript)   │     │  + RAG Pipeline │     │  (Llama 3.3)    │
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
│   └── requirements.txt
├── frontend/
│   ├── chat-widget.js           # Embeddable chat widget
│   └── chat-widget.css          # Widget styles
├── data/
│   ├── resume.md                # My resume
│   ├── projects.md              # My project descriptions
│   └── about.md                 # About me
└── README.md
```

## 🛠️ Tech Stack

| Component | Technology | Why I Chose It |
|-----------|------------|----------------|
| **Backend** | FastAPI | Async support, automatic docs, type hints |
| **LLM** | Groq (Llama 3.3 70B) | Free tier, incredibly fast inference |
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
Groq offers a generous free tier and their inference speed is remarkable. The Llama 3.3 70B model produces high-quality responses comparable to GPT-4.

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
- 🎓 M.Tech at IIT Ropar (2024-2026)
- 🔬 Research: 5G NOMA Receivers, Swarm Drones
- 🌐 Website: [shashibhushanjha.me](https://shashibhushanjha.me)
- 📧 Email: bhushan.gate2022@gmail.com
- 💻 GitHub: [@ShashiBhushan22](https://github.com/ShashiBhushan22)

---

*This chatbot demonstrates how AI tools can help developers build and deploy projects efficiently. Built with human creativity + AI assistance.* 🤝

