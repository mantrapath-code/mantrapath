# MantraPath Multilingual Technical Specifications
## Detailed Implementation Requirements

**Document Version:** 1.0  
**Date:** January 2025  
**Related:** MULTILINGUAL_IMPLEMENTATION_PLAN.md  

---

## 🔧 Frontend Technical Specifications

### 1. **Required Dependencies & Versions**

```json
{
  "dependencies": {
    "i18next": "^23.7.6",
    "react-i18next": "^13.5.0",
    "i18next-browser-languagedetector": "^7.2.0",
    "i18next-http-backend": "^2.4.2",
    "i18next-icu": "^2.3.0",
    "i18next-parser": "^8.8.0",
    "date-fns": "^2.30.0",
    "date-fns-tz": "^2.0.0",
    "@formatjs/intl-pluralrules": "^5.2.2",
    "@formatjs/intl-relativetimeformat": "^11.2.2"
  }
}
```

### 2. **File Structure Changes**

```
frontend/src/
├── i18n/
│   ├── config.ts                    # i18next configuration
│   ├── resources.ts                 # Translation resource loader
│   ├── detector.ts                  # Custom language detector
│   └── formatters.ts                # Date/number formatters
├── contexts/
│   └── LanguageContext.tsx          # Language context provider
├── hooks/
│   ├── useLanguage.ts               # Language management hook
│   ├── useTranslation.ts            # Enhanced translation hook
│   └── useLocalization.ts           # Localization utilities
├── components/
│   ├── common/
│   │   ├── LanguageSelector.tsx     # Language selection component
│   │   ├── RTLProvider.tsx          # RTL layout provider
│   │   └── LocalizedText.tsx        # Text component with fallbacks
│   └── [existing components updated with i18n]
└── utils/
    ├── localization.ts              # Localization utilities
    ├── culturalAdaptation.ts        # Cultural adaptation logic
    └── rtlSupport.ts                # RTL support utilities

frontend/public/
└── locales/
    ├── en/
    │   ├── common.json
    │   ├── auth.json
    │   ├── mood.json
    │   ├── journal.json
    │   ├── chatbot.json
    │   ├── community.json
    │   ├── dashboard.json
    │   ├── notifications.json
    │   ├── profile.json
    │   ├── content.json
    │   └── errors.json
    ├── es/
    │   └── [same structure]
    └── [other languages]/
```

### 3. **Component Updates Required**

#### AuthScreen.tsx
```typescript
// Key changes needed
import { useTranslation } from 'react-i18next'
import { LanguageSelector } from '@/components/common/LanguageSelector'

// Replace hardcoded strings with:
const { t } = useTranslation('auth')

// Examples:
"MantraPath" → t('appName')
"Your AI-powered wellness companion" → t('tagline')
"Welcome" → t('welcome')
"Start your journey to better mental wellness" → t('welcomeDescription')
```

#### MoodTracker.tsx
```typescript
// Key changes needed
import { useTranslation } from 'react-i18next'
import { useLanguage } from '@/contexts/LanguageContext'

const { t } = useTranslation('mood')
const { formatDate, formatNumber } = useLanguage()

// Examples:
"Enhanced Mood Tracking" → t('enhancedMoodTracking')
"How are you feeling?" → t('howAreYouFeeling')
"Energy Level" → t('energyLevel')
"Stress Level" → t('stressLevel')
```

### 4. **Translation File Examples**

#### en/auth.json
```json
{
  "appName": "MantraPath",
  "tagline": "Your AI-powered wellness companion",
  "welcome": "Welcome",
  "welcomeDescription": "Start your journey to better mental wellness",
  "login": "Login",
  "register": "Register",
  "email": "Email",
  "password": "Password",
  "firstName": "First Name",
  "lastName": "Last Name",
  "username": "Username",
  "signIn": "Sign In",
  "createAccount": "Create Account",
  "forgotPassword": "Forgot Password?",
  "demoAccount": "Try Demo Account",
  "backendConnected": "Backend Connected",
  "demoMode": "Using Demo Mode",
  "passwordRequirements": {
    "title": "Password Requirements",
    "length": "At least 8 characters",
    "lowercase": "Lowercase letter",
    "uppercase": "Uppercase letter",
    "number": "Number",
    "special": "Special character"
  }
}
```

#### es/auth.json
```json
{
  "appName": "MantraPath",
  "tagline": "Tu compañero de bienestar impulsado por IA",
  "welcome": "Bienvenido",
  "welcomeDescription": "Comienza tu viaje hacia un mejor bienestar mental",
  "login": "Iniciar Sesión",
  "register": "Registrarse",
  "email": "Correo Electrónico",
  "password": "Contraseña",
  "firstName": "Nombre",
  "lastName": "Apellido",
  "username": "Nombre de Usuario",
  "signIn": "Iniciar Sesión",
  "createAccount": "Crear Cuenta",
  "forgotPassword": "¿Olvidaste tu contraseña?",
  "demoAccount": "Probar Cuenta Demo",
  "backendConnected": "Backend Conectado",
  "demoMode": "Usando Modo Demo",
  "passwordRequirements": {
    "title": "Requisitos de Contraseña",
    "length": "Al menos 8 caracteres",
    "lowercase": "Letra minúscula",
    "uppercase": "Letra mayúscula",
    "number": "Número",
    "special": "Carácter especial"
  }
}
```

### 5. **RTL Support Implementation**

#### CSS Updates Required
```css
/* Add to main.css */
[dir="rtl"] {
  text-align: right;
}

[dir="rtl"] .flex {
  flex-direction: row-reverse;
}

[dir="rtl"] .ml-2 {
  margin-left: 0;
  margin-right: 0.5rem;
}

[dir="rtl"] .mr-2 {
  margin-right: 0;
  margin-left: 0.5rem;
}

/* Tailwind RTL plugin configuration */
/* tailwind.config.js */
module.exports = {
  plugins: [
    require('@tailwindcss/rtl'),
  ],
}
```

---

## 🔧 Backend Technical Specifications

### 1. **Database Schema Changes**

#### User Table Extensions
```sql
-- Add to existing users table
ALTER TABLE users ADD COLUMN preferred_language VARCHAR(5) DEFAULT 'en';
ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';
ALTER TABLE users ADD COLUMN date_format VARCHAR(20) DEFAULT 'MM/DD/YYYY';
ALTER TABLE users ADD COLUMN number_format VARCHAR(20) DEFAULT 'en-US';
ALTER TABLE users ADD COLUMN cultural_preferences JSONB DEFAULT '{}';

-- Index for performance
CREATE INDEX idx_users_preferred_language ON users(preferred_language);
```

#### New Translation Tables
```sql
-- Content translations
CREATE TABLE content_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    tags JSONB DEFAULT '[]',
    translated_by VARCHAR(255),
    translation_quality FLOAT DEFAULT 0.0,
    is_machine_translated BOOLEAN DEFAULT false,
    cultural_adaptations JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(content_id, language_code)
);

-- Affirmation translations
CREATE TABLE affirmation_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    affirmation_id UUID REFERENCES affirmations(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL,
    text TEXT NOT NULL,
    cultural_context JSONB DEFAULT '{}',
    mood_context JSONB DEFAULT '[]',
    translated_by VARCHAR(255),
    translation_quality FLOAT DEFAULT 0.0,
    is_machine_translated BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(affirmation_id, language_code)
);

-- UI translations management
CREATE TABLE ui_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    translation_key VARCHAR(255) NOT NULL,
    namespace VARCHAR(50) NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    context TEXT,
    translated_by VARCHAR(255),
    translation_quality FLOAT DEFAULT 0.0,
    is_machine_translated BOOLEAN DEFAULT false,
    needs_review BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(translation_key, namespace, language_code)
);

-- ML model language support
CREATE TABLE ml_model_languages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    model_path TEXT NOT NULL,
    model_version VARCHAR(20),
    accuracy_score FLOAT,
    cultural_adaptation_score FLOAT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_name, language_code)
);

-- Performance indexes
CREATE INDEX idx_content_translations_lang ON content_translations(language_code);
CREATE INDEX idx_content_translations_quality ON content_translations(translation_quality);
CREATE INDEX idx_affirmation_translations_lang ON affirmation_translations(language_code);
CREATE INDEX idx_ui_translations_key_lang ON ui_translations(translation_key, language_code);
CREATE INDEX idx_ml_model_languages_active ON ml_model_languages(language_code, is_active);
```

### 2. **API Endpoint Changes**

#### Enhanced User Profile Service
```python
# backend/services/profile_service/main.py

@app.put("/profile/language-preferences")
async def update_language_preferences(
    preferences: LanguagePreferencesUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's language and cultural preferences"""
    
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update language preferences
    user.preferred_language = preferences.language
    user.timezone = preferences.timezone
    user.date_format = preferences.date_format
    user.number_format = preferences.number_format
    user.cultural_preferences = preferences.cultural_preferences
    
    db.commit()
    
    return {
        "message": "Language preferences updated successfully",
        "preferences": {
            "language": user.preferred_language,
            "timezone": user.timezone,
            "date_format": user.date_format,
            "number_format": user.number_format,
            "cultural_preferences": user.cultural_preferences
        }
    }

class LanguagePreferencesUpdate(BaseModel):
    language: str = Field(..., pattern="^[a-z]{2}$")
    timezone: str = "UTC"
    date_format: str = "MM/DD/YYYY"
    number_format: str = "en-US"
    cultural_preferences: Dict[str, Any] = {}
```

#### Enhanced Content Service
```python
# backend/services/content_service/main.py

@app.get("/content/localized")
async def get_localized_content(
    request: Request,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get content in user's preferred language"""
    
    # Detect language
    language = detect_user_language(request, current_user)
    
    # Query content with translations
    query = db.query(Content).filter(Content.is_published == True)
    
    if category:
        query = query.filter(Content.category == category)
    
    content_items = query.offset(skip).limit(limit).all()
    
    # Get translations for each content item
    localized_content = []
    for content in content_items:
        translation = db.query(ContentTranslation).filter(
            and_(
                ContentTranslation.content_id == content.id,
                ContentTranslation.language_code == language
            )
        ).first()
        
        if translation:
            localized_content.append({
                "id": content.id,
                "title": translation.title,
                "content": translation.content,
                "excerpt": translation.excerpt,
                "category": content.category,
                "language": language,
                "is_translated": True,
                "translation_quality": translation.translation_quality,
                "cultural_adaptations": translation.cultural_adaptations
            })
        else:
            # Fallback to original content
            localized_content.append({
                "id": content.id,
                "title": content.title,
                "content": content.content,
                "excerpt": content.excerpt,
                "category": content.category,
                "language": "en",
                "is_translated": False,
                "needs_translation": language != "en"
            })
    
    return localized_content

def detect_user_language(request: Request, user: Optional[Dict] = None) -> str:
    """Detect user's preferred language"""
    # Priority: user preference > Accept-Language header > default
    if user and user.get('preferred_language'):
        return user['preferred_language']
    
    accept_language = request.headers.get('Accept-Language', '')
    supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar', 'he', 'hi', 'bn', 'ur']
    
    for lang in supported_languages:
        if lang in accept_language.lower():
            return lang
    
    return 'en'  # Default fallback
```

### 3. **ML Service Enhancements**

#### Multilingual Sentiment Analysis
```python
# backend/services/ml_service/models/multilingual_sentiment.py

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, List, Optional

class MultilingualSentimentAnalyzer:
    def __init__(self):
        self.supported_languages = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 
            'ar', 'he', 'hi', 'bn', 'ur'
        ]
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """Load multilingual sentiment analysis models"""
        try:
            # Primary multilingual model
            self.multilingual_model = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                tokenizer="cardiffnlp/twitter-xlm-roberta-base-sentiment"
            )
            
            # Language-specific models for better accuracy
            self.language_specific_models = {
                'en': pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest"),
                'es': pipeline("sentiment-analysis", model="pysentimiento/robertuito-sentiment-analysis"),
                'fr': pipeline("sentiment-analysis", model="tblard/tf-allocine"),
                'de': pipeline("sentiment-analysis", model="oliverguhr/german-sentiment-bert"),
                'zh': pipeline("sentiment-analysis", model="uer/roberta-base-finetuned-chinanews-chinese"),
            }
            
            print("✅ Multilingual sentiment models loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading multilingual sentiment models: {e}")
    
    def analyze_sentiment(self, text: str, language: str) -> Dict:
        """Analyze sentiment in specified language"""
        try:
            # Use language-specific model if available, otherwise use multilingual
            if language in self.language_specific_models:
                result = self.language_specific_models[language](text)
            else:
                result = self.multilingual_model(text)
            
            return {
                "sentiment": result[0]['label'],
                "confidence": result[0]['score'],
                "language": language,
                "model_used": "language_specific" if language in self.language_specific_models else "multilingual"
            }
        except Exception as e:
            print(f"Error in sentiment analysis for {language}: {e}")
            return {
                "sentiment": "NEUTRAL",
                "confidence": 0.5,
                "language": language,
                "error": str(e)
            }
    
    def batch_analyze_sentiment(self, texts: List[str], language: str) -> List[Dict]:
        """Analyze sentiment for multiple texts"""
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text, language))
        return results
```

#### Cultural Content Adaptation
```python
# backend/services/ml_service/models/cultural_adapter.py

class CulturalContentAdapter:
    def __init__(self):
        self.cultural_contexts = {
            'collectivist': ['zh', 'ja', 'ko', 'hi', 'bn'],  # Family/community focused
            'individualist': ['en', 'de', 'fr'],             # Individual achievement focused
            'high_context': ['ar', 'ja', 'zh'],              # Indirect communication
            'low_context': ['en', 'de', 'fr'],               # Direct communication
            'religious_integrated': ['ar', 'ur', 'he'],      # Spiritual integration important
        }
        
        self.adaptation_templates = {
            'affirmations': {
                'collectivist': {
                    'family_support': "Remember that your family and community support you",
                    'collective_strength': "Draw strength from your connections with others",
                    'harmony': "Seek balance and harmony in your relationships"
                },
                'individualist': {
                    'personal_growth': "This is an opportunity for personal growth",
                    'self_reliance': "Trust in your ability to overcome challenges",
                    'achievement': "You have the power to achieve your goals"
                },
                'religious_integrated': {
                    'spiritual_strength': "Find strength in your faith and spiritual practices",
                    'divine_support': "You are supported by divine love and guidance",
                    'prayer_meditation': "Turn to prayer and meditation for peace"
                }
            }
        }
    
    def adapt_content(self, content: str, language: str, content_type: str) -> Dict:
        """Adapt content based on cultural context"""
        cultural_tags = []
        
        # Determine cultural context
        for context, languages in self.cultural_contexts.items():
            if language in languages:
                cultural_tags.append(context)
        
        # Apply adaptations
        adapted_content = content
        adaptations_applied = []
        
        if content_type in self.adaptation_templates:
            for cultural_tag in cultural_tags:
                if cultural_tag in self.adaptation_templates[content_type]:
                    # Apply cultural adaptations
                    adaptations = self.adaptation_templates[content_type][cultural_tag]
                    adaptations_applied.extend(list(adaptations.keys()))
        
        return {
            "original_content": content,
            "adapted_content": adapted_content,
            "cultural_contexts": cultural_tags,
            "adaptations_applied": adaptations_applied,
            "language": language
        }
```

### 4. **Translation Management System**

```python
# backend/services/translation_service/main.py

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid
from googletrans import Translator
import json

app = FastAPI(title="Translation Management Service")

class TranslationService:
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 
            'ar', 'he', 'hi', 'bn', 'ur'
        ]
    
    async def auto_translate_content(self, content_id: str, target_languages: List[str], db: Session):
        """Automatically translate content to target languages"""
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return {"error": "Content not found"}
        
        results = []
        for lang in target_languages:
            if lang == 'en':  # Skip if already in English
                continue
                
            try:
                # Translate title and content
                translated_title = self.translator.translate(content.title, dest=lang).text
                translated_content = self.translator.translate(content.content, dest=lang).text
                translated_excerpt = self.translator.translate(content.excerpt or "", dest=lang).text if content.excerpt else None
                
                # Check if translation already exists
                existing = db.query(ContentTranslation).filter(
                    and_(
                        ContentTranslation.content_id == content_id,
                        ContentTranslation.language_code == lang
                    )
                ).first()
                
                if existing:
                    # Update existing translation
                    existing.title = translated_title
                    existing.content = translated_content
                    existing.excerpt = translated_excerpt
                    existing.is_machine_translated = True
                    existing.translation_quality = 0.7  # Machine translation quality score
                else:
                    # Create new translation
                    translation = ContentTranslation(
                        id=str(uuid.uuid4()),
                        content_id=content_id,
                        language_code=lang,
                        title=translated_title,
                        content=translated_content,
                        excerpt=translated_excerpt,
                        is_machine_translated=True,
                        translation_quality=0.7
                    )
                    db.add(translation)
                
                results.append({
                    "language": lang,
                    "status": "success",
                    "title": translated_title[:50] + "..." if len(translated_title) > 50 else translated_title
                })
                
            except Exception as e:
                results.append({
                    "language": lang,
                    "status": "error",
                    "error": str(e)
                })
        
        db.commit()
        return {"results": results}

@app.post("/translate/content/{content_id}")
async def translate_content(
    content_id: str,
    target_languages: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Translate content to multiple languages"""
    translation_service = TranslationService()
    
    # Run translation in background
    background_tasks.add_task(
        translation_service.auto_translate_content,
        content_id,
        target_languages,
        db
    )
    
    return {
        "message": "Translation job started",
        "content_id": content_id,
        "target_languages": target_languages
    }

@app.get("/translations/quality-report")
async def get_translation_quality_report(
    language: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get translation quality report"""
    query = db.query(ContentTranslation)
    
    if language:
        query = query.filter(ContentTranslation.language_code == language)
    
    translations = query.all()
    
    # Calculate quality metrics
    total_translations = len(translations)
    machine_translated = len([t for t in translations if t.is_machine_translated])
    human_translated = total_translations - machine_translated
    
    avg_quality = sum(t.translation_quality for t in translations) / total_translations if total_translations > 0 else 0
    
    quality_distribution = {
        "excellent": len([t for t in translations if t.translation_quality >= 0.9]),
        "good": len([t for t in translations if 0.7 <= t.translation_quality < 0.9]),
        "fair": len([t for t in translations if 0.5 <= t.translation_quality < 0.7]),
        "poor": len([t for t in translations if t.translation_quality < 0.5])
    }
    
    return {
        "total_translations": total_translations,
        "machine_translated": machine_translated,
        "human_translated": human_translated,
        "average_quality": round(avg_quality, 2),
        "quality_distribution": quality_distribution,
        "language": language or "all"
    }
```

---

## 🧪 Testing Specifications

### 1. **Frontend Testing Requirements**

```typescript
// tests/i18n/translation.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import i18n from '@/i18n/config'
import { AuthScreen } from '@/components/auth/AuthScreen'

describe('Internationalization', () => {
  beforeEach(() => {
    i18n.changeLanguage('en')
  })

  test('should display English content by default', () => {
    render(
      <I18nextProvider i18n={i18n}>
        <AuthScreen />
      </I18nextProvider>
    )
    
    expect(screen.getByText('Welcome')).toBeInTheDocument()
    expect(screen.getByText('MantraPath')).toBeInTheDocument()
  })

  test('should switch to Spanish when language is changed', async () => {
    render(
      <I18nextProvider i18n={i18n}>
        <AuthScreen />
      </I18nextProvider>
    )
    
    await i18n.changeLanguage('es')
    
    expect(screen.getByText('Bienvenido')).toBeInTheDocument()
  })

  test('should format dates according to locale', () => {
    const date = new Date('2024-01-15')
    
    // English format
    i18n.changeLanguage('en')
    expect(new Intl.DateTimeFormat('en').format(date)).toBe('1/15/2024')
    
    // German format
    i18n.changeLanguage('de')
    expect(new Intl.DateTimeFormat('de').format(date)).toBe('15.1.2024')
  })

  test('should handle RTL languages correctly', async () => {
    render(
      <I18nextProvider i18n={i18n}>
        <AuthScreen />
      </I18nextProvider>
    )
    
    await i18n.changeLanguage('ar')
    
    expect(document.documentElement.dir).toBe('rtl')
  })
})
```

### 2. **Backend Testing Requirements**

```python
# tests/test_localization.py
import pytest
from fastapi.testclient import TestClient
from backend.services.content_service.main import app

client = TestClient(app)

def test_language_detection():
    """Test language detection from Accept-Language header"""
    response = client.get(
        "/content/localized",
        headers={"Accept-Language": "es-ES,es;q=0.9,en;q=0.8"}
    )
    assert response.status_code == 200
    # Should detect Spanish as preferred language

def test_content_translation():
    """Test content translation endpoint"""
    response = client.get(
        "/content/localized",
        headers={"Accept-Language": "es"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check if Spanish translations are returned when available
    for item in data:
        if item.get('is_translated'):
            assert item['language'] == 'es'

def test_fallback_to_english():
    """Test fallback to English when translation not available"""
    response = client.get(
        "/content/localized",
        headers={"Accept-Language": "xyz"}  # Unsupported language
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should fallback to English
    for item in data:
        assert item['language'] == 'en'

@pytest.mark.asyncio
async def test_translation_quality():
    """Test translation quality scoring"""
    # Test with known good translation
    quality_score = calculate_translation_quality("Hello", "Hola", "es")
    assert quality_score > 0.8
    
    # Test with poor translation
    quality_score = calculate_translation_quality("Hello", "Bad translation", "es")
    assert quality_score < 0.5
```

---

## 📊 Performance Benchmarks

### Frontend Performance Targets
- **Initial Load Time:** <3 seconds (including i18n setup)
- **Language Switch Time:** <100ms
- **Translation File Load:** <50ms per namespace
- **Bundle Size Increase:** <15% per additional language
- **Memory Usage:** <10MB additional for i18n system

### Backend Performance Targets
- **Localized API Response:** <200ms
- **Translation Query Time:** <50ms
- **Content Translation:** <500ms per item
- **Database Query Performance:** <100ms for multilingual queries
- **Cache Hit Rate:** >90% for frequently accessed translations

### Monitoring Metrics
```typescript
// Performance monitoring setup
const performanceMonitor = {
  trackLanguageSwitch: (fromLang: string, toLang: string, duration: number) => {
    // Track language switching performance
    analytics.track('language_switch', {
      from_language: fromLang,
      to_language: toLang,
      duration_ms: duration,
      timestamp: Date.now()
    })
  },
  
  trackTranslationLoad: (namespace: string, language: string, duration: number) => {
    // Track translation file loading performance
    analytics.track('translation_load', {
      namespace,
      language,
      duration_ms: duration,
      timestamp: Date.now()
    })
  }
}
```

---

## 🔒 Security Considerations

### Translation Security
- **Input Sanitization:** All translated content must be sanitized
- **XSS Prevention:** Escape HTML in translations
- **Content Validation:** Validate translation quality and appropriateness
- **Access Control:** Restrict translation management to authorized users

### Data Privacy
- **User Language Preferences:** Encrypt sensitive preference data
- **Translation Logs:** Anonymize user content in translation logs
- **GDPR Compliance:** Handle EU user language preferences according to GDPR
- **Cultural Sensitivity:** Respect cultural and religious sensitivities

---

**Document Status:** Technical Specifications Complete  
**Next Review Date:** February 1, 2025  
**Document Owner:** Engineering Team  
**Related Documents:** MULTILINGUAL_IMPLEMENTATION_PLAN.md