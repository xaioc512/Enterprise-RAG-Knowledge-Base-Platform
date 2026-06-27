# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] — 2026-06-27

### Added

- **MVP Core**: RAG-based enterprise knowledge Q&A platform
- **Backend**: FastAPI + SQLAlchemy 2.0 async + LangChain + Chroma
- **Frontend**: Vue 3 + Element Plus + Pinia + Dark theme design system
- **Authentication**: JWT + bcrypt + department-level access control
- **Document Management**: PDF/Word/Markdown/TXT upload, parse, chunk, vectorize
- **AI Chat**: DeepSeek Chat API + SSE streaming + source citations
- **Conversation History**: Multi-turn dialogue management + auto title generation
- **Feedback System**: Thumbs up/down on AI responses
- **Admin Dashboard**: User management, department CRUD, system stats
- **Agent System**: Built-in web search + tagging + audit logging tools
- **Docker**: Full containerization with docker-compose (MySQL + Redis + Backend + Frontend + Nginx)
- **Testing**: 26 pytest cases covering auth, departments, documents, health checks
- **CI/CD**: GitHub Actions for lint, test, and Docker build
- **Code Quality**: Ruff, Prettier, pre-commit hooks
