# 🧘♀️ Python Intern Assessment - Mental Health AI Platform

## 📋 Overview

**Time Limit:** 1 week  
**Difficulty:** High  
**Focus:** FastAPI, AI/ML, Crisis Detection, Real-time Systems

**Total Points:** 100

---

## 🎯 Challenge: Build a Crisis Detection System

Create a mental health platform with **crisis prediction** capabilities from scratch. No repository access required.

---

## 🚀 Task 1: FastAPI Crisis Detection Service (40 points)

### Build a complete service with these endpoints:

```python
from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

app = FastAPI(title="Crisis Detection Service")

class MoodEntry(BaseModel):
    user_id: str
    mood_score: int  # 1-10
    energy_level: int  # 1-10
    stress_level: int  # 1-10
    notes: Optional[str] = None
    timestamp: datetime

class CrisisAlert(BaseModel):
    user_id: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float
    risk_factors: List[str]
    recommended_actions: List[str]

# TODO: Implement these endpoints (40 points total)

@app.post("/mood/entry")
async def create_mood_entry(entry: MoodEntry):
    """Store mood entry and trigger crisis analysis"""
    pass

@app.get("/crisis/risk/{user_id}")
async def get_crisis_risk(user_id: str) -> CrisisAlert:
    """Get current crisis risk assessment"""
    pass

@app.websocket("/ws/alerts/{user_id}")
async def crisis_alerts_websocket(websocket: WebSocket, user_id: str):
    """Real-time crisis alerts via WebSocket"""
    pass

@app.get("/analytics/dashboard")
async def crisis_dashboard():
    """Crisis monitoring dashboard with anonymized stats"""
    pass
```

**Requirements:**
- **Database:** SQLAlchemy with PostgreSQL/SQLite
- **Real-time:** WebSocket connections for alerts
- **Validation:** Pydantic models with proper validation
- **Error Handling:** Comprehensive HTTP error responses
- **Documentation:** Auto-generated OpenAPI docs

---

## 🤖 Task 2: AI/ML Crisis Prediction Model (35 points)

### Implement a machine learning model for crisis detection:

```python
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple

class CrisisPredictionModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def extract_features(self, mood_history: List[Dict]) -> np.ndarray:
        """
        Extract features for crisis prediction:
        - Mood trend (7-day slope)
        - Volatility (standard deviation)
        - Consecutive low mood days
        - Stress-energy correlation
        - Time-based patterns
        """
        pass
    
    def train(self, training_data: List[Dict]) -> Dict[str, float]:
        """
        Train model with historical data:
        - Handle class imbalance (SMOTE)
        - Feature engineering
        - Cross-validation
        - Return accuracy metrics
        """
        pass
    
    def predict_crisis_risk(self, user_mood_history: List[Dict]) -> Dict[str, Any]:
        """
        Predict crisis risk:
        Returns: {
            "risk_probability": 0.23,
            "risk_level": "MEDIUM",
            "confidence": 0.87,
            "key_factors": ["mood_decline", "high_stress"],
            "time_estimate": "3-7 days"
        }
        """
        pass
    
    def generate_synthetic_data(self, n_samples: int = 1000) -> List[Dict]:
        """
        Generate realistic training data since no real data available
        Include crisis and non-crisis examples with realistic patterns
        """
        pass
```

**Requirements:**
- **Model Performance:** >80% accuracy on test data
- **Feature Engineering:** Extract meaningful patterns from mood data
- **Class Imbalance:** Handle rare crisis events properly
- **Real-time Inference:** <100ms prediction time
- **Explainability:** Identify key risk factors

---

## 🔍 Task 3: NLP Crisis Detection (15 points)

### Analyze text for crisis indicators:

```python
import re
from textblob import TextBlob
from typing import Dict, List

class CrisisTextAnalyzer:
    def __init__(self):
        self.crisis_keywords = {
            "critical": ["suicide", "kill myself", "end it all"],
            "high": ["hopeless", "worthless", "can't go on"],
            "medium": ["depressed", "anxious", "struggling"]
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for crisis indicators:
        1. Keyword detection with severity scoring
        2. Sentiment analysis (TextBlob)
        3. Linguistic patterns (finality, isolation)
        4. Urgency detection
        
        Returns risk assessment with confidence score
        """
        pass
    
    def generate_response(self, risk_level: str) -> str:
        """
        Generate appropriate response based on risk:
        - CRITICAL: Crisis hotline resources
        - HIGH: Immediate support suggestions
        - MEDIUM: Coping strategies
        - LOW: General wellness tips
        """
        pass
```

---

## 🏗️ Task 4: System Architecture (10 points)

### Design scalable architecture:

**Requirements:**
1. **Database Schema:** Design tables for users, mood_entries, crisis_assessments, alerts
2. **Caching Strategy:** Redis for real-time data and ML predictions
3. **Event System:** Async event handling for crisis alerts
4. **Security:** JWT authentication, data encryption, rate limiting
5. **Monitoring:** Health checks, metrics, logging

**Deliverable:** Architecture diagram + implementation

---

## 📋 Implementation Requirements

### **Core Features:**
- ✅ **FastAPI Service** with all endpoints working
- ✅ **Database Integration** with proper models
- ✅ **ML Model** trained and making predictions
- ✅ **WebSocket** real-time alerts
- ✅ **NLP Analysis** for text-based crisis detection
- ✅ **Crisis Dashboard** with anonymized metrics

### **Technical Standards:**
- **Code Quality:** Type hints, docstrings, PEP 8
- **Testing:** Unit tests for critical functions
- **Error Handling:** Graceful failure handling
- **Performance:** Async operations, efficient queries
- **Security:** Input validation, SQL injection prevention

### **Bonus Features (+10 points):**
- **Advanced ML:** Ensemble models, deep learning
- **Real-time Dashboard:** Interactive crisis monitoring
- **Multi-language:** Text analysis in multiple languages
- **Mobile API:** Optimized endpoints for mobile apps
- **Load Testing:** Performance benchmarks

---

## 🎯 Evaluation Criteria

| Component | Points | Key Factors |
|-----------|--------|-------------|
| **FastAPI Service** | 40 | Working endpoints, WebSocket, validation |
| **ML Model** | 35 | Accuracy >80%, feature engineering, real-time |
| **NLP Analysis** | 15 | Text analysis, risk classification |
| **Architecture** | 10 | Scalable design, security, monitoring |

---

## 🚀 Getting Started

### **Setup:**
```bash
# Create project
mkdir crisis-detection-service
cd crisis-detection-service

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary
pip install scikit-learn pandas numpy textblob
pip install redis pytest httpx
```

### **Project Structure:**
```
crisis-detection-service/
├── main.py              # FastAPI app
├── models.py            # Database models
├── ml_model.py          # Crisis prediction ML
├── nlp_analyzer.py      # Text analysis
├── database.py          # DB connection
├── websocket_manager.py # Real-time alerts
├── tests/               # Unit tests
└── requirements.txt     # Dependencies
```

### **Run Service:**
```bash
uvicorn main:app --reload --port 8000
# Access docs: http://localhost:8000/docs
```

---

## 📝 Submission

**Deliverables:**
1. **Complete Source Code** with all implementations
2. **README.md** with setup and usage instructions
3. **API Documentation** (auto-generated + examples)
4. **Test Results** showing model performance
5. **Architecture Diagram** of your system design

**Demo Requirements:**
- Working API endpoints with example requests
- Crisis detection demonstration
- Real-time WebSocket alerts
- ML model performance metrics

---

## 🎯 Success Tips

1. **Start Simple:** Get basic FastAPI service running first
2. **Generate Data:** Create realistic synthetic data for ML training
3. **Test Continuously:** Write tests as you develop
4. **Focus on Core:** Implement all required features before bonuses
5. **Document Well:** Clear code comments and API docs
6. **Handle Errors:** Robust error handling throughout
7. **Think Real-world:** Consider production deployment needs

---

**This assessment tests your ability to build production-ready mental health technology that could genuinely help detect and prevent crisis situations. Good luck! 🧘♀️**