# MantraPath - Holistic Mental Wellness Platform

A comprehensive mental wellness platform that combines mood tracking, journaling, community features, and AI-powered chatbot support.

## 🏗️ Project Structure

```
mantrapath-holistic/
├── README.md                 # Project documentation
├── LICENSE                   # License file
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
│
├── frontend/                # React/Vite frontend application
│   ├── src/                 # Source code
│   ├── package.json         # Frontend dependencies
│   ├── vite.config.ts       # Vite configuration
│   ├── tsconfig.json        # TypeScript configuration
│   └── index.html           # HTML entry point
│
├── backend/                 # FastAPI backend services
│   ├── services/            # Microservices
│   │   ├── api_gateway/     # API Gateway service
│   │   ├── auth_service/    # Authentication service
│   │   ├── mood_service/    # Mood tracking service
│   │   └── ...              # Other services
│   ├── shared/              # Shared utilities and models
│   ├── docker-compose.yml   # Docker orchestration
│   └── requirements.txt     # Python dependencies
│
├── config/                  # Configuration files
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   ├── components.json      # UI components configuration
│   ├── theme.json           # Theme customization
│   └── nginx.conf           # Nginx configuration
│
├── deployment/              # Deployment and infrastructure
│   ├── Dockerfile.frontend  # Frontend Docker image
│   └── deploy.sh            # Deployment script
│
├── scripts/                 # Utility scripts
│   ├── dev-setup.sh         # Development environment setup
│   ├── start-backend.sh     # Backend startup script
│   └── stop-backend.sh      # Backend shutdown script
│
├── tests/                   # Test files
│   ├── test-backend.py      # Backend tests
│   └── test-backend-connection.js # Connection tests
│
└── docs/                    # Documentation
    ├── PRD.md               # Product Requirements Document
    ├── SECURITY.md          # Security guidelines
    ├── BACKEND_SETUP.md     # Backend setup guide
    └── ...                  # Other documentation
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Docker and Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)

### 1. Clone the Repository

```bash
git clone https://github.com/ssharmasachin/mantrapath-holistic.git
cd mantrapath-holistic
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Start Backend Services

```bash
cd backend
docker-compose up --build
```

The backend services will start on:
- API Gateway: http://localhost:8000
- Auth Service: http://localhost:8001
- Mood Service: http://localhost:8003

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:5174

## 🛠️ Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev        # Start development server
npm run build      # Build for production
npm run preview    # Preview production build
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📖 Documentation

- [Product Requirements](docs/PRD.md)
- [Backend Setup Guide](docs/BACKEND_SETUP.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Guidelines](docs/SECURITY.md)

## 🔧 Configuration

Configuration files are located in the `config/` directory:

- `tailwind.config.js` - Tailwind CSS styling
- `components.json` - UI component library settings
- `theme.json` - Custom theme variables
- `nginx.conf` - Nginx reverse proxy configuration

## 🐳 Docker Deployment

```bash
# Build and start all services
cd backend
docker-compose up --build

# Stop all services
docker-compose down
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/ssharmasachin/mantrapath-holistic)
- [Documentation](docs/)
- [Issues](https://github.com/ssharmasachin/mantrapath-holistic/issues)
