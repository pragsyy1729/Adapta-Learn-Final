Link to the Architecture Overview - [Technical Architecture](adaptalearn_architecture_modern.png)
## **FRONTEND (React/TypeScript)**

### **Core Application Structure**

- **Main Entry Point** : Simple React 18 setup with root rendering
- **App Component** : React Router setup with 15+ routes including authentication, dashboard, admin, and learning paths
- **Navigation** : Responsive navigation with role-based menu items, authentication state management, and sign-out functionality

### **Page Components**

1. **Index.tsx** - Landing page with hero section and conditional dashboard display
2. **SignIn.tsx** - Authentication form with email/password validation and role-based redirects
3. **Dashboard.tsx** - Main dashboard with tabbed interface (Home, Learning Paths, Achievements, Recommendations, Profile, Collaboration)
4. **VARKQuiz.tsx** - 12-question learning style assessment with 4 learning styles (Visual, Aural, Read/Write, Kinesthetic)
5. **OnboardingWorkflow.tsx** - Multi-step onboarding with resume upload, skill analysis, and learning path assignment
6. **AdminView.tsx** - Administrative dashboard for system management
7. **ManagerView.tsx** - Manager-specific dashboard for team oversight
8. **HiringManagerView.tsx** - Department-level management interface

### **UI Components**

- **ConversationAgent.tsx** - AI-powered chat interface with department-specific knowledge
- **Dashboard.tsx** - Reusable dashboard layout component
- **Hero.tsx** - Landing page hero section with feature highlights
- **Notifications.tsx** - User notification system
- **GamificationDashboard.tsx** - Achievement and points tracking
- **RecommendationsPanel.tsx** - AI and HR-driven learning recommendations
- **LiveTimer.tsx** - Session tracking with activity monitoring
- **ProgressIndicator.tsx** - Learning progress visualization

### **Key Features**

- **Authentication System**: JWT-based with role management (Admin, Manager, Hiring Manager, Associate)
- **Learning Style Assessment**: VARK questionnaire with personalized recommendations
- **AI Conversation Agent**: Department-specific Q&A with vector search
- **Gamification**: Points, badges, and achievement system
- **Session Tracking**: Real-time activity monitoring and analytics
- **Responsive Design**: Mobile-first with Tailwind CSS and Radix UI components

## **BACKEND (Flask/Python)**

### **Core Application Structure**

- **Main Server** : Multi-process server managing authentication, session tracking, and main API
- **Flask App Factory** : Application initialization with CORS and route registration
- **Route Registration** : Blueprint registration for all API endpoints

### **API Routes (15+ Blueprints)**

1. **User Authentication** : Sign-in/sign-up, session management, rate limiting
2. **Dashboard** : Role-based dashboard data (Admin, Manager, Hiring Manager, Learner)
3. **Learning Paths** : Course management, module tracking, progress updates
4. **Onboarding** ([onboarding.py](vscode-file://vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-browser/workbench/workbench.html)): AI-powered resume analysis, skill gap detection, auto-enrollment
5. **Conversation** : AI chat interface with department-specific knowledge
6. **Assessment** : Quiz engine and evaluation system
7. **Gamification**: Points, badges, and achievement tracking
8. **Admin** : Administrative functions and system management

### **AI/ML Agent System**

- **Onboarding Agent** : Complete AI-powered onboarding orchestration
- **Resume Analyzer** : Document parsing and skill extraction
- **Conversation Agent** : NLP-powered Q&A system
- **Dynamic Role Manager** : Role-skill management system
- **Department Mapping** : Department-specific learning path assignment

### **Services Layer**

- **Data Access** : JSON file operations and data persistence
- **Document Processor** : PDF/DOCX processing and vector store management
- **Conversation Agent** : AI chat processing with FAISS vector search
- **Job Queue** : Asynchronous document processing with threading

### **Key Features**

- **Multi-Role Authentication**: JWT-based with role-based access control
- **AI-Powered Onboarding**: Resume analysis, skill gap detection, personalized learning paths
- **Vector Search**: FAISS-based semantic search for department knowledge
- **Asynchronous Processing**: Job queue for document processing and AI tasks
- **Session Management**: Real-time activity tracking and analytics
- **Rate Limiting**: Protection against brute force attacks
- **CORS Support**: Cross-origin resource sharing for frontend integration

## **TECHNOLOGY STACK**

### **Frontend**

- React 18.3.1 with TypeScript
- Vite for build tooling
- Tailwind CSS + Radix UI for styling
- React Query for state management
- React Router for navigation
- Axios for HTTP requests
- Lucide React for icons

### **Backend**

- Python 3.8+ with Flask
- Flask-CORS for cross-origin support
- Groq API for LLM integration
- LangChain for AI workflows
- FAISS for vector search
- PyPDF2 and python-docx for document processing

### **AI/ML Integration**

- Google Gemini for embeddings
- Groq LLaMA models for text generation
- FAISS vector database
- LangChain for AI orchestration
- Custom NLP pipelines

### **Data Storage**

- JSON-based persistence
- File system for assets
- FAISS vector stores per department
- In-memory caching for performance

## **ARCHITECTURAL PATTERNS**

1. **Layered Architecture**: Presentation → Application → Domain → Infrastructure
2. **Microservices Pattern**: Separate services for auth, learning, AI, admin
3. **Repository Pattern**: Data access abstraction for JSON operations
4. **Observer Pattern**: Event-driven updates for progress tracking
5. **Factory Pattern**: Flask app factory for testability

## **SECURITY MEASURES**

- JWT token authentication
- Password hashing with Werkzeug
- Rate limiting on authentication
- Input sanitization and validation
- CORS configuration
- Session management
- File upload validation

## **PERFORMANCE OPTIMIZATIONS**

- Asynchronous job processing
- Vector store caching
- Lazy loading of components
- Debounced search queries
- Optimized bundle splitting
- Background task processing

This comprehensive system provides an AI-powered adaptive learning management platform with personalized onboarding, intelligent content recommendations, and real-time progress tracking across multiple user roles and departments.


## **MAJOR IMPROVEMENTS**

1. Functional Manager View & HR View
2. Make the collaboration possible by communication through servers
3. Make AI Rate the user based on the questions asked to the Conversation Agent


## UNIQUE COMPONENTS IN THIS SOLUTION


##### Graph RAG for Conversational AI (Tailored to each department)- [Graph RAG Architecture](graph_rag_architecture_modern.png)
The AdaptaLearn system implements a sophisticated Graph RAG (Retrieval-Augmented Generation) architecture that combines vector embeddings, knowledge graphs, and large language models to provide intelligent, context-aware responses for department-specific onboarding and learning assistance.
#### AI Recommendation Engine

### Powered by Groq LLaMA 3.1-8B Instant

The AI recommendations use language models to analyze:

- **Learning Progress**: Completion rates, time invested, stalled paths
- **Skill Gaps**: Current vs. required proficiency levels
- **Deadline Management**: Upcoming due dates and time pressure
- **Learning Patterns**: Study habits and engagement metrics
- **Department Context**: Role-specific requirements and priorities



