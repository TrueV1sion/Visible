# Battlecard Platform

An AI-powered competitive intelligence platform for generating and managing sales battlecards. This application enables sales and marketing teams to create, maintain, and share competitive intelligence through structured and dynamically generated battlecards.

## 🚀 Core Features

- **AI-Powered Battlecard Generation**: Create comprehensive battlecards using advanced AI in minutes
- **Competitor Intelligence Tracking**: Automatically monitor competitors and receive updates
- **Interactive Battlecard Editing**: Collaboratively enhance AI-generated content
- **Objection Handling Library**: Access a database of effective objection responses
- **Real-Time Competitive Updates**: Get alerts when competitors make significant changes
- **Analytics Dashboard**: Track usage and effectiveness of battlecards

## 🏗️ Technology Stack

### Frontend
- **React**: Component-based UI development
- **Material UI**: Modern, responsive component library
- **React Query**: Data fetching and state management
- **Lucide React**: Beautiful, consistent iconography

### Backend
- **Python/FastAPI**: High-performance API framework
- **AI Orchestration Layer**: Modular agent-based architecture
- **PostgreSQL**: Relational database for structured data
- **Vector Database**: For semantic search capabilities
- **Anthropic/OpenAI Integration**: LLM services for content generation

## 🧠 AI Architecture

The platform uses a sophisticated multi-agent system to provide intelligent battlecard generation:

### Agent Components
1. **Prompt Management System**: Template-based approach with versioning
2. **Enhanced Battlecard Generation Agent**: Orchestrates specialized generation tasks
3. **Contextual Tagger Agent**: Analyzes and tags competitor content
4. **Objection Handling Agent**: Generates responses to common sales objections
5. **Expert System Agent**: Makes strategic recommendations

### Prompt Engineering
- Version controlled, componentized prompt templates
- A/B testing capabilities for prompt optimization
- Context-aware prompt selection based on task complexity

## 🔧 Getting Started

### Prerequisites
```
Node.js >= 16.0.0
npm >= 8.0.0
Python >= 3.9
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/battlecard-platform.git
cd battlecard-platform
```

2. **Install frontend dependencies**
```bash
cd frontend
npm install
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
# Edit .env files with your configuration
```

5. **Initialize the database**
```bash
cd backend
python -m scripts.init_db
```

6. **Start the development servers**

Backend:
```bash
cd backend
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm start
```

The application will be available at http://localhost:3000

## 🌐 API Documentation

The backend API is documented using OpenAPI/Swagger. When running the backend server, access the documentation at `http://localhost:8000/docs`.

### Key Endpoints

- `/api/v1/battlecards`: CRUD operations for battlecards
- `/api/v1/competitors`: Competitor data and updates
- `/api/v1/ai/`: AI-powered generation endpoints
- `/api/v1/objections`: Objection handling database
- `/api/v1/analytics`: Usage and performance statistics

## 🧩 Project Structure

```
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── battlecards/
│   │   │   ├── dashboard/
│   │   │   ├── insights/
│   │   │   └── layout/
│   │   ├── contexts/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── agents/
│   │   │   ├── prompts/
│   │   │   └── base.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   └── schemas/
│   ├── config/
│   ├── tests/
│   └── ai_orchestration/
│       ├── src/
│       │   ├── base_agent.py
│       │   ├── battlecard_generation.py
│       │   ├── contextual_tagger.py
│       │   ├── expert_system.py
│       │   ├── prompt_management.py
│       │   └── orchestration.py
├── docker/
└── docs/
```

## 🎯 Deployment

### Docker Deployment

1. Build the images
```bash
docker-compose build
```

2. Start the containers
```bash
docker-compose up -d
```

### Cloud Deployment

Deployment templates are available for:
- AWS (CloudFormation)
- Azure (ARM templates)
- Google Cloud (Terraform)

See the `/deployment` directory for specific instructions.

## 💡 Usage Examples

### Generating a New Battlecard

1. Navigate to the Battlecards section
2. Click "Create New Battlecard"
3. Enter competitor information
4. Select product segments and focus areas
5. Click "Generate Battlecard"

### Editing AI-Generated Content

1. Open a battlecard
2. Click the edit icon on any section
3. Modify the content
4. Click save to update

### Setting up Competitor Monitoring

1. Navigate to the Competitors section
2. Select a competitor
3. Click "Enable Monitoring"
4. Configure update frequency and alert settings

## 🤝 Contributing

We welcome contributions to the Battlecard Platform! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions, please contact:
- Email: support@battlecardplatform.com
- Issue Tracker: GitHub Issues

## 🙏 Acknowledgements

- [Anthropic Claude](https://www.anthropic.com/claude) for advanced AI capabilities
- [Material UI](https://mui.com/) for the component library
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Lucide](https://lucide.dev/) for the beautiful icons
