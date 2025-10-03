# AI Newsroom Collaboration Tool

A collaborative AI-powered content generation platform for journalists and writers.

## Features

- **Collaborative Article Editor**: Rich text editor with real-time collaboration
- **AI Content Generation**: GPT-4 powered article drafting and writing assistance
- **Fact-Checking**: Automated fact verification and citation management
- **Image Integration**: AI-generated images with caption suggestions
- **Multi-Agent Workflow**: Research, writing, editing, and verification agents
- **Editorial Management**: Version control, review workflows, and publication pipeline

## Tech Stack

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- TipTap editor for rich text editing
- React Query for data fetching
- React Router for navigation

### Backend
- FastAPI (Python) REST API
- PostgreSQL database with SQLAlchemy ORM
- JWT authentication with OAuth integration
- OpenAI GPT integration
- News API integration for fact-checking

### AI & Services
- OpenAI GPT-4 for content generation
- DALL-E for image generation
- News API for fact verification
- Custom fact-checking pipeline

## Project Structure

```
news-mania/
├── frontend/          # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service functions
│   │   ├── hooks/         # Custom React hooks
│   │   └── context/       # React context providers
├── backend/           # FastAPI backend application
│   ├── app/
│   │   ├── models/        # SQLAlchemy database models
│   │   ├── routers/       # API route handlers
│   │   ├── services/      # Business logic services
│   │   └── utils/         # Utility functions
└── docker-compose.yml    # Development environment setup
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL 14+
- OpenAI API key
- News API key

### Environment Setup

1. Clone the repository
2. Copy environment files:
   ```bash
   cp frontend/.env.example frontend/.env
   cp backend/.env.example backend/.env
   ```
3. Update environment variables with your API keys

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Database Setup
```bash
# Run database migrations
cd backend
alembic upgrade head
```

## Development Workflow

1. **Setup Phase**: Project structure, authentication, basic CRUD
2. **Editor Phase**: Rich text editor, article management, version control
3. **AI Integration**: Content generation, fact-checking, image generation
4. **Collaboration**: Real-time editing, comments, workflow management
5. **Deployment**: Docker containerization, cloud deployment

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License