# AdaptaLearn

An AI-powered adaptive Learning Management System with personalized learning paths, gamification, and comprehensive user management.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Create Python Virtual Environment**:
```bash
python3 -m venv adapt_learn
source adapt_learn/bin/activate  # On Windows: adapt_learn\Scripts\activate
```

2. **Install Python Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run Backend Server**:
```bash
PYTHONPATH=. ./adapt_learn/bin/python3 backend/main_server.py
```

### Frontend Setup

1. **Install Node Dependencies**:
```bash
npm install
```

2. **Start Development Server**:
```bash
npm run dev
```

## � Project Structure

```
adapta-learn/
├── backend/                 # Flask API server
├── src/                     # React frontend
├── data/                    # JSON data files
├── agent/                   # AI/ML components
├── tests/                   # Test scripts
└── scripts/                 # Utility scripts
```

## 🔧 Available Scripts

### Backend
- `python backend/run.py` - Start the Flask server
- `python run_all_tests.py` - Run all backend tests

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 🧪 Testing

Run the test suite:
```bash
python run_all_tests.py
```

## 📊 Sample Data

The application comes with pre-generated sample data including:
- 25+ users across multiple departments
- Learning paths for different roles
- Progress tracking and sessions

### Login Credentials
- **Admin**: admin@adapta.com / Admin123!
- **HR Admin**: hr.admin@adapta.com / HRAdmin123!
- **Regular Users**: Use any user email with password `Pass123!`

## 🆘 Support

For issues or questions, check the test scripts and existing API implementations for usage examples.
