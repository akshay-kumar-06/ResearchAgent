<<<<<<< HEAD
# 🔬 Multi-Agent Research Assistant

A production-ready, multi-agent AI research assistant that autonomously researches topics and generates comprehensive reports with citations.

Built with **LangGraph** to orchestrate multiple specialized agents working together in a coordinated workflow.

## ✨ Features

- **🧠 Intelligent Planning**: Automatically breaks down complex research topics into focused sub-questions
- **🔍 Web Search**: Uses Tavily API to search for relevant information
- **📊 Analysis**: Synthesizes search results into key insights with citations
- 📝 **Report Generation**: Creates comprehensive markdown reports with proper citations
- 🔄 **Real-time Updates**: Track research progress through the modern React UI
- 📚 **History Tracking**: SQLite database stores all research results

## 🏗️ Architecture

```
User Query → Planner Agent → Web Search Agent → Analyzer Agent → Report Writer → Markdown Report
                ↓                    ↓                  ↓                 ↓
              [State]            [State]            [State]         [State]
```

### Agents

| Agent | Responsibility |
|-------|---------------|
| **Planner** | Breaks research topic into 3-5 focused sub-questions |
| **Searcher** | Performs web searches for each sub-question using Tavily |
| **Analyzer** | Synthesizes results, extracts insights, tracks citations |
| **Writer** | Generates structured markdown report with citations |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Gemini API Key](https://makersuite.google.com/app/apikey)
- [Tavily API Key](https://tavily.com/)

### Installation

1. **Clone the repository**
   ```bash
   cd multi_agent_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

### Running the Application

1. **Start FastAPI Backend**
   ```bash
   uvicorn app.main:app --reload
   ```
   API available at: http://localhost:8000

2. **Start React UI** (new terminal)
   ```bash
   cd ui-react
   npm run dev
   ```
   UI available at: http://localhost:5173

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/research` | Start new research |
| `GET` | `/research/{id}/status` | Get research status |
| `GET` | `/research/{id}` | Get completed result |
| `GET` | `/research` | List research history |

### Example API Usage

```bash
# Start research
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare AI regulations in EU vs US"}'

# Check status
curl http://localhost:8000/research/{research_id}/status

# Get result
curl http://localhost:8000/research/{research_id}
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ -v --cov=app
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📁 Project Structure

```
multi_agent_project/
├── app/
│   ├── core/           # Config, logging, database
│   ├── agents/         # LangGraph agents
│   ├── tools/          # Web search, citation tracker
│   ├── models/         # Pydantic schemas
│   ├── utils/          # Text processing, markdown
│   └── main.py         # FastAPI application
├── ui-react/           # React Frontend Application
│   ├── src/            # React components and API services
│   └── package.json    # Frontend dependencies
├── tests/              # Internal tests
├── examples/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## ⚙️ Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | Required |
| `TAVILY_API_KEY` | Tavily API key | Required |
| `LLM_MODEL` | Gemini model | `gemini-2.0-flash-exp` |
| `LLM_TEMPERATURE` | LLM creativity | `0.3` |
| `TAVILY_MAX_RESULTS` | Results per search | `5` |
| `DATABASE_PATH` | SQLite path | `./data/research.db` |

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Tavily](https://tavily.com/) - Web search API
- [FastAPI](https://fastapi.tiangolo.com/) - Process API backend
- [React](https://react.dev/) - Frontend framework
- [Vite](https://vitejs.dev/) - Frontend build tool
=======
# ResearchAgent
>>>>>>> 84ac30d1ce4dada7d931c001d2cc9a9da7724bc7
