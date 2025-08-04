# MantraPath Test Data Generation Scripts

This directory contains comprehensive test data generation scripts for all MantraPath services. Each script uses proper authentication and creates realistic, segregated data for testing the insights and analytics features.

## 🏗️ Structure

```
scripts/test-data/
├── auth_helper.py                          # Centralized authentication for all scripts
├── master_data_generator.py                # Orchestrates all data generation
├── mood-service/
│   └── generate_mood_data.py              # Realistic mood entries with patterns
├── journal-service/
│   └── generate_journal_data.py           # Mood-correlated journal entries
├── community-service/
│   └── generate_community_data.py         # Community posts and interactions
├── ml-service/
│   └── test_ml_insights.py                # ML endpoint testing and validation
└── README.md                              # This file
```

## 🔐 Authentication

All scripts use the `auth_helper.py` module which handles:
- User registration (if needed)
- JWT authentication 
- Session management
- API request authentication

### Test Users
- **Primary**: Uses your actual email/password credentials
- **Secondary**: `test.user@example.com` / `test123456`

## 🚀 Quick Start

### Option 1: Master Script (Recommended)
```bash
cd /Users/sachin/Documents/GitHub/mantrapath/scripts/test-data
python3 master_data_generator.py
```

### Option 2: Automated Comprehensive Generation
```bash
python3 master_data_generator.py --auto
```

### Option 3: Individual Service Scripts
```bash
# Mood data
python3 mood-service/generate_mood_data.py

# Journal data  
python3 journal-service/generate_journal_data.py

# Community data
python3 community-service/generate_community_data.py

# ML testing
python3 ml-service/test_ml_insights.py
```

## 📊 Data Types Generated

### Mood Service (`mood-service/generate_mood_data.py`)
- **Realistic mood patterns**: stable, improving, declining, volatile, weekend_boost
- **Diverse data**: 30+ days of varied mood entries
- **Streak data**: Consecutive good mood days for testing streak features
- **Context data**: Activities, locations, weather correlations

### Journal Service (`journal-service/generate_journal_data.py`)  
- **Mood-correlated entries**: Journal content that matches mood levels
- **Themed entries**: Gratitude, growth, reflection themes
- **Before/after moods**: Track mood changes from journaling
- **Smart tagging**: Automatic tag generation based on content

### Community Service (`community-service/generate_community_data.py`)
- **Post categories**: Motivation, support, gratitude, tips, milestones
- **Engagement**: Comments, reactions, discussions
- **Themed discussions**: Mental health awareness, motivation Monday, wellness Wednesday
- **Anonymous options**: Mix of identified and anonymous posts

### ML Service (`ml-service/test_ml_insights.py`)
- **Endpoint testing**: All ML API endpoints
- **Data validation**: Ensures real data vs fallbacks
- **Integration testing**: Frontend to backend data flow
- **Comprehensive reports**: JSON test reports with metrics

## 🎯 Specific Use Cases

### Testing "Best Moments" Feature
```bash
# Generate mood data with clear patterns
python3 mood-service/generate_mood_data.py
# Choose option 6 (comprehensive) or 4 (weekend boost pattern)

# Test the insights
python3 ml-service/test_ml_insights.py  
# Choose option 2 (validate insights data flow)
```

### Testing Community Features
```bash
# Generate community activity
python3 community-service/generate_community_data.py
# Choose option 5 (comprehensive)
```

### Testing Journal Correlations
```bash
# Generate mood data first
python3 mood-service/generate_mood_data.py

# Then generate correlated journal entries
python3 journal-service/generate_journal_data.py
# Choose option 1 (mood-correlated entries)
```

## 🔧 Configuration

### Update Credentials
Edit `auth_helper.py` to use your actual credentials:
```python
self.test_users = {
    "primary": {
        "email": "your-actual-email@example.com",
        "password": "your-actual-password", 
        "name": "Your Name"
    }
}
```

### Service URLs
Default configuration assumes:
- API Gateway: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- All backend services running via Docker Compose

## 📋 Prerequisites

1. **Backend services running**:
   ```bash
   cd /path/to/mantrapath/backend
   docker-compose up -d
   ```

2. **Frontend running**:
   ```bash
   cd /path/to/mantrapath/frontend  
   npm run dev
   ```

3. **Python dependencies**:
   ```bash
   pip install requests
   ```

## 🧪 Testing Workflow

1. **Check prerequisites**:
   ```bash
   python3 master_data_generator.py
   # Choose option 0
   ```

2. **Generate base data**:
   ```bash
   # Run mood data first (provides foundation)
   python3 mood-service/generate_mood_data.py
   ```

3. **Add correlated data**:
   ```bash
   # Journal entries that correlate with moods
   python3 journal-service/generate_journal_data.py
   ```

4. **Test insights**:
   ```bash
   # Validate that insights show real data
   python3 ml-service/test_ml_insights.py
   ```

5. **Verify in browser**:
   - Visit `http://localhost:5173`
   - Navigate to Insights section
   - Check "Best Moments" for populated data:
     - 🌟 Best day: Should show actual day
     - ⚡ Energy peak: Should show time/activity  
     - 🔥 Mood streak: Should show number > 0

## 📈 Expected Results

After running comprehensive data generation:

### Insights Dashboard Should Show:
- ✅ Real mood statistics instead of zeros
- ✅ Actual best day calculations  
- ✅ Energy peak times and activities
- ✅ Mood streak counters > 0 days
- ✅ Pattern-based recommendations
- ✅ Data quality scores > 0%

### Community Feed Should Show:
- ✅ Diverse post types and themes
- ✅ Realistic engagement (comments, reactions)
- ✅ Tagged and categorized content

### Journal Section Should Show:
- ✅ Mood-correlated entries
- ✅ Before/after mood tracking
- ✅ Thematic content variety

## 🐛 Troubleshooting

### "Authentication Failed"
- Check credentials in `auth_helper.py`
- Ensure auth service is running
- Try registering user first

### "Service Unavailable"  
- Verify Docker Compose services: `docker-compose ps`
- Check service health endpoints
- Restart specific service: `docker-compose restart <service>`

### "Empty Insights Data"
- Run mood data generation first
- Ensure ML service is healthy
- Check ML service logs: `docker-compose logs ml-service`

### "Scripts Not Found"
- Ensure you're in the correct directory
- Check file permissions: `chmod +x *.py`
- Verify Python 3 installation

## 🔄 Data Cleanup

To reset test data:
```bash
# Connect to database and truncate tables
# (Add specific cleanup scripts if needed)
```

## 📝 Logs and Reports

- ML test reports saved to: `ml_insights_test_report_YYYYMMDD_HHMMSS.json`
- Console output provides real-time status
- Check Docker logs for service-specific issues

---

**💡 Pro Tips:**
1. Always run mood data generation first - it provides the foundation for all other insights
2. Use the master script for consistent, comprehensive datasets
3. Check the ML test validation to ensure insights show real data instead of fallbacks
4. Monitor Docker service health if endpoints fail
5. The scripts are designed to be idempotent - safe to run multiple times
