# 🤖 Adaptive AI Chatbot with Persistent SQLite Memory

A full-stack conversational AI application built with Python, Groq, and Streamlit. The system features persistent session storage via SQLite and an adaptive prompt refinement engine that learns user preferences across sessions.

---

## 🌟 Key Features
- **Low-Latency LLM Inference**: Powered by Groq's high-throughput LPU inference engine.
- **Persistent Database Storage**: Uses SQLite to store chat history (`messages` table) and user instructions (`improvement_notes` table).
- **Adaptive Memory & Preference Learning**: Custom prompt-engineering feedback loop injecting stored user rules into system context across sessions.
- **Interactive Web Interface**: Streamlit UI featuring chat components, responsive feedback controls, and live rule inspection.
- **Production-Grade Secret Management**: Credentials isolated via environment variables (`.env`) and excluded from version control (`.gitignore`).

---

## 🛠️ Tech Stack
- **Language**: Python 3.14
- **LLM Provider**: Groq API
- **Web Framework**: Streamlit
- **Database**: SQLite3
- **Configuration**: `python-dotenv`
- **Version Control**: Git & GitHub

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/chatbot.git](https://github.com/yathinms122007/chatbot.git)
cd chatbot