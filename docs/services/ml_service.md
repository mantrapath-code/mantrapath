# ML Service

## Description

The ML Service is the artificial intelligence and machine learning powerhouse of the MantraPath platform, providing sophisticated predictive analytics, personalized content recommendations, and crisis prediction capabilities. This service uses advanced machine learning models to analyze mood patterns, predict optimal timing for interventions, generate personalized notification content, and provide early warning systems for mental health crises.

This service solves the critical challenge of making mental health support truly personalized and proactive. By analyzing user data patterns, it enables predictive interventions, personalized timing of support messages, and early identification of potential mental health crises, transforming reactive mental health support into proactive, intelligent care.

## Table of Contents

- [Installation / Setup](#installation--setup)
- [Usage](#usage)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)
- [Contact / Author Info](#contact--author-info)
- [FAQ / Troubleshooting](#faq--troubleshooting)
- [Future Implementation](#future-implementation)

## Installation / Setup

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- PostgreSQL database
- Redis (for ML model caching)
- Sufficient computational resources (CPU/GPU for ML processing)
- Access to shared event bus system

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/ml_service
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download required NLP models:**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
   ```

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include `DATABASE_URL`, `REDIS_URL`, ML model parameters, crisis prediction thresholds, and computational resource settings.

## Usage

The ML Service provides machine learning capabilities through REST API endpoints and event-driven processing.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8008 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d ml_service
  ```

- **Analyze mood patterns:**
  ```bash
  curl -X POST "http://localhost:8008/ml/analyze-patterns" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"user_id":"user123","timeframe_days":30}'
  ```

- **Get optimal notification timing:**
  ```bash
  curl -X POST "http://localhost:8008/ml/optimal-timing" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"user_id":"user123","notification_type":"mood_check"}'
  ```

- **Get crisis prediction assessment:**
  ```bash
  curl -X POST "http://localhost:8008/ml/crisis-prediction" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"user_id":"user123"}'
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8008/docs`

## Features

- **Mood Pattern Analysis:** Advanced analysis of mood trends, cycles, and behavioral patterns
- **Optimal Timing Prediction:** ML-powered prediction of optimal times for notifications and interventions
- **Personalized Content Engine:** AI-generated personalized notification content and recommendations
- **Crisis Prediction System:** Early warning system for potential mental health crises
- **Effectiveness Tracking:** Analysis of intervention effectiveness and outcome prediction
- **Real-time Insight Processing:** Real-time analysis of user events for immediate insights
- **Early Warning System:** Proactive identification of concerning behavioral patterns
- **Smart Notification Scheduling:** Intelligent scheduling based on user behavior and preferences
- **Behavioral Clustering:** User segmentation based on behavioral patterns and needs
- **Intervention Recommendation:** AI-powered recommendations for therapeutic interventions
- **Predictive Analytics:** Long-term trend prediction and outcome forecasting
- **A/B Testing Integration:** ML-powered optimization of intervention strategies

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Machine Learning:** Scikit-learn 1.3.2, NumPy 1.24.3, Pandas 2.1.4, SciPy 1.11.4
- **Statistical Analysis:** Statsmodels 0.14.1, Joblib 1.3.2
- **Natural Language Processing:** NLTK 3.8.1, TextBlob 0.17.1, WordCloud 1.9.2
- **Database:** PostgreSQL with SQLAlchemy 2.0.23
- **Caching:** Redis 5.0.1 for ML model and prediction caching
- **Authentication:** JWT token validation through shared auth system
- **HTTP Client:** HTTPX 0.25.2 for service integration
- **Event System:** Enhanced Event Bus V3 for real-time ML processing
- **Testing:** Pytest with asyncio support for ML model testing
- **Containerization:** Docker

## Contributing

Contributions to enhance machine learning capabilities are crucial:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/advanced-crisis-prediction`)
3. Focus on ML model improvements and ethical AI practices
4. Add comprehensive tests for ML algorithms and predictions
5. Ensure responsible AI practices and bias detection
6. Update ML model documentation and validation metrics
7. Submit a pull request with detailed ML performance analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"ML predictions are inaccurate"**: Verify sufficient training data quality and quantity. Check model validation metrics and retrain if necessary.
- **"Crisis prediction too sensitive/not sensitive enough"**: Adjust crisis prediction thresholds based on validation data and clinical feedback.
- **"Slow ML processing"**: Optimize model parameters, consider model caching, and ensure adequate computational resources.
- **"Pattern analysis not finding patterns"**: Check data quality, ensure sufficient historical data, and review feature engineering.

## Future Implementation

- **Deep Learning Models:** Advanced neural networks for complex pattern recognition and prediction
- **Federated Learning:** Privacy-preserving distributed ML training across user data
- **Explainable AI:** Model interpretability features for transparent AI decision-making
- **Real-time Learning:** Online learning algorithms that adapt to user behavior in real-time
- **Advanced NLP:** Transformer-based models for sophisticated text analysis and generation
- **Clinical Integration:** ML models validated with clinical outcomes and professional oversight