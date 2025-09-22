# MantraPath Low-Level Design

## 🔧 Detailed Component Design

### **1. API Gateway Implementation**

#### **Core Components**
```python
# src/core/config.py
class GatewayConfig:
    services: Dict[str, ServiceConfig]
    rate_limits: Dict[str, RateLimitConfig]
    auth_config: AuthConfig
    cors_config: CORSConfig

class ServiceConfig:
    name: str
    url: str
    health_check: str
    timeout: int
    retry_attempts: int
    circuit_breaker: CircuitBreakerConfig
```

#### **Request Routing Logic**
```python
# src/routing/request_router.py
class RequestRouter:
    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry
        self.load_balancer = LoadBalancerFactory.create()
    
    async def route_request(self, request: ProxyRequest) -> Response:
        # 1. Extract service name from path
        service_name = self.extract_service_name(request.path)
        
        # 2. Get service instance from registry
        service_instance = self.service_registry.get_service(service_name)
        
        # 3. Apply load balancing
        target_url = self.load_balancer.select_instance(service_instance)
        
        # 4. Forward request
        return await self.forward_request(request, target_url)
```

#### **Authentication Middleware**
```python
# src/middleware/auth.py
class AuthMiddleware:
    def __init__(self, jwt_secret: str):
        self.jwt_secret = jwt_secret
        self.token_validator = JWTValidator(jwt_secret)
    
    async def authenticate_request(self, request: Request) -> UserContext:
        # 1. Extract token from headers
        token = self.extract_token(request.headers)
        
        # 2. Validate JWT token
        payload = self.token_validator.validate(token)
        
        # 3. Extract user context
        return UserContext(
            user_id=payload.get("sub"),
            email=payload.get("email"),
            role=payload.get("role"),
            permissions=self.get_permissions(payload.get("role"))
        )
```

### **2. Authentication Service Implementation**

#### **User Model**
```python
# shared/models.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String, default="user")
    verification_token = Column(String)
    verification_token_expires = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
```

#### **Password Security**
```python
# shared/auth.py
class PasswordManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        # Password strength validation logic
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
```

#### **JWT Token Management**
```python
# shared/auth.py
class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None
```

### **3. Mood Service Implementation**

#### **Mood Entry Model**
```python
# shared/models.py
class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    mood_score = Column(Integer, nullable=False)  # 1-10 scale
    energy_level = Column(Integer)  # 1-10 scale
    stress_level = Column(Integer)  # 1-10 scale
    activities = Column(JSON)  # List of activities
    notes = Column(Text)
    emotions = Column(JSON)  # List of emotions
    weather = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### **Mood Analytics Engine**
```python
# mood_service/analytics.py
class MoodAnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_mood_trend(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        # Get mood entries for the specified period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        entries = self.db.query(MoodEntry).filter(
            and_(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= cutoff_date
            )
        ).order_by(MoodEntry.created_at).all()
        
        if not entries:
            return {"trend": "insufficient_data", "entries_count": 0}
        
        # Calculate trend
        scores = [entry.mood_score for entry in entries]
        if len(scores) < 3:
            return {"trend": "insufficient_data", "entries_count": len(scores)}
        
        # Simple linear regression for trend calculation
        x = list(range(len(scores)))
        slope = self._calculate_slope(x, scores)
        
        if slope > 0.1:
            trend = "improving"
        elif slope < -0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "slope": slope,
            "average_score": sum(scores) / len(scores),
            "entries_count": len(scores),
            "latest_score": scores[-1],
            "score_range": {"min": min(scores), "max": max(scores)}
        }
    
    def detect_patterns(self, user_id: str) -> Dict[str, Any]:
        # Pattern detection logic
        entries = self.db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at).all()
        
        patterns = {
            "weekly_patterns": self._analyze_weekly_patterns(entries),
            "time_patterns": self._analyze_time_patterns(entries),
            "activity_correlations": self._analyze_activity_correlations(entries),
            "weather_correlations": self._analyze_weather_correlations(entries)
        }
        
        return patterns
```

#### **Emotional Weather Forecasting**
```python
# mood_service/emotional_weather.py
class EmotionalWeatherForecaster:
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    async def generate_forecast(self, user_id: str) -> Dict[str, Any]:
        # Get recent mood data
        recent_entries = self._get_recent_mood_entries(user_id, days=14)
        
        if len(recent_entries) < 7:
            return {"forecast": "insufficient_data", "confidence": 0.0}
        
        # Analyze patterns
        patterns = self._analyze_mood_patterns(recent_entries)
        
        # Generate forecast
        forecast = self._predict_next_week_mood(patterns)
        
        # Store forecast in cache
        cache_key = f"mood_forecast:{user_id}"
        self.redis_client.setex(cache_key, 3600, json.dumps(forecast))
        
        return forecast
    
    def _predict_next_week_mood(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        # Machine learning-based prediction
        # This would integrate with the ML service
        base_score = patterns.get("average_score", 5.0)
        trend = patterns.get("trend", "stable")
        
        # Adjust for trend
        if trend == "improving":
            trend_adjustment = 0.5
        elif trend == "declining":
            trend_adjustment = -0.5
        else:
            trend_adjustment = 0.0
        
        # Generate daily predictions
        daily_predictions = []
        for day in range(7):
            # Apply day-of-week patterns
            day_of_week = (datetime.utcnow().weekday() + day) % 7
            day_adjustment = patterns.get("weekly_patterns", {}).get(f"day_{day_of_week}", 0)
            
            predicted_score = max(1, min(10, base_score + trend_adjustment + day_adjustment))
            confidence = max(0.3, 1.0 - (day * 0.1))  # Confidence decreases over time
            
            daily_predictions.append({
                "day": day,
                "predicted_score": round(predicted_score, 1),
                "confidence": round(confidence, 2),
                "factors": self._identify_influencing_factors(patterns, day)
            })
        
        return {
            "forecast": daily_predictions,
            "overall_trend": trend,
            "confidence": round(sum(p["confidence"] for p in daily_predictions) / 7, 2),
            "generated_at": datetime.utcnow().isoformat()
        }
```

### **4. AI Event Processor Implementation**

#### **Event Processing Pipeline**
```python
# core/ai_processor.py
class AIEventProcessor:
    def __init__(self):
        self.event_bus = None
        self.redis_client = None
        self.emotion_analyzer = None
        self.cultural_processor = None
        self.predictive_engine = None
        self.metrics = AIMetrics()
    
    async def process_event(self, event: AIProcessingEvent) -> ProcessingResult:
        start_time = time.time()
        
        try:
            # 1. Validate event
            if not self._validate_event(event):
                return ProcessingResult(success=False, error="Invalid event")
            
            # 2. Extract context
            context = await self._extract_context(event)
            
            # 3. Process based on event type
            if event.event_type == AIEventType.MOOD_ENTRY:
                result = await self._process_mood_event(event, context)
            elif event.event_type == AIEventType.JOURNAL_ENTRY:
                result = await self._process_journal_event(event, context)
            elif event.event_type == AIEventType.VOICE_ACTIVITY:
                result = await self._process_voice_event(event, context)
            else:
                result = await self._process_generic_event(event, context)
            
            # 4. Update metrics
            processing_time = time.time() - start_time
            self.metrics.update_processing_time(processing_time)
            self.metrics.increment_processed_events()
            
            return ProcessingResult(
                success=True,
                result=result,
                processing_time_ms=processing_time * 1000
            )
            
        except Exception as e:
            self.metrics.increment_errors()
            logger.error(f"Error processing event: {e}")
            return ProcessingResult(success=False, error=str(e))
```

#### **Emotion Analysis Engine**
```python
# core/emotion_analyzer.py
class EmotionAnalyzer:
    def __init__(self):
        self.models = {}
        self.models_service_client = ModelsServiceClient()
        self.supported_languages = ['en', 'hi', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'zh', 'ko', 'ar', 'bn', 'ta', 'te']
        self.emotion_labels = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust', 'neutral']
    
    async def analyze(self, text: str, language: str = "en", user_id: str = None) -> EmotionResult:
        start_time = time.time()
        
        try:
            # 1. Detect language if not provided
            if not language or language == "auto":
                language = self._detect_language(text)
            
            # 2. Try Models Service first
            if self.models_service_client.is_available():
                result = await self._analyze_with_models_service(text, language, user_id)
                if result:
                    return result
            
            # 3. Fallback to local models
            result = await self._analyze_with_local_models(text, language, user_id)
            
            # 4. Apply cultural adaptation
            if language in self.supported_languages:
                result = await self._apply_cultural_adaptation(result, language, user_id)
            
            # 5. Update processing time
            processing_time = time.time() - start_time
            result.processing_time_ms = processing_time * 1000
            
            return result
            
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return self._create_fallback_result(text, language)
    
    async def _analyze_with_models_service(self, text: str, language: str, user_id: str) -> Optional[EmotionResult]:
        try:
            response = await self.models_service_client.analyze_emotion(text, language)
            if response and response.get("success"):
                data = response["data"]
                return EmotionResult(
                    emotion=data["primary_emotion"],
                    confidence=data["confidence"],
                    emotions=data["emotion_scores"],
                    language=language,
                    has_cultural_adaptation=False,
                    analysis_metadata={"source": "models_service"}
                )
        except Exception as e:
            logger.warning(f"Models Service emotion analysis failed: {e}")
        return None
```

### **5. Database Design**

#### **Core Tables Schema**
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'user',
    verification_token VARCHAR(255),
    verification_token_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- User profiles table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'UTC',
    theme VARCHAR(20) DEFAULT 'light',
    privacy_level VARCHAR(20) DEFAULT 'private',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    daily_reminder_enabled BOOLEAN DEFAULT TRUE,
    daily_reminder_time TIME DEFAULT '09:00',
    weekly_report_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mood entries table
CREATE TABLE mood_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    mood_score INTEGER NOT NULL CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    activities JSONB,
    notes TEXT,
    emotions JSONB,
    weather VARCHAR(100),
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Journal entries table
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT NOT NULL,
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    tags JSONB,
    is_private BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Community posts table
CREATE TABLE community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    forum_id UUID REFERENCES community_forums(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    post_type VARCHAR(50) DEFAULT 'discussion',
    is_anonymous BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    action_url VARCHAR(500),
    priority VARCHAR(20) DEFAULT 'normal',
    is_read BOOLEAN DEFAULT FALSE,
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Indexes for Performance**
```sql
-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Mood entry indexes
CREATE INDEX idx_mood_entries_user_id ON mood_entries(user_id);
CREATE INDEX idx_mood_entries_created_at ON mood_entries(created_at);
CREATE INDEX idx_mood_entries_user_created ON mood_entries(user_id, created_at);

-- Journal entry indexes
CREATE INDEX idx_journal_entries_user_id ON journal_entries(user_id);
CREATE INDEX idx_journal_entries_created_at ON journal_entries(created_at);
CREATE INDEX idx_journal_entries_user_created ON journal_entries(user_id, created_at);

-- Community post indexes
CREATE INDEX idx_community_posts_forum_id ON community_posts(forum_id);
CREATE INDEX idx_community_posts_created_at ON community_posts(created_at);
CREATE INDEX idx_community_posts_user_id ON community_posts(user_id);

-- Notification indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
```

### **6. Caching Strategy**

#### **Redis Cache Implementation**
```python
# shared/cache.py
class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def get_or_set(self, key: str, factory: Callable, ttl: int = None) -> Any:
        value = await self.get(key)
        if value is None:
            value = await factory()
            await self.set(key, value, ttl)
        return value
```

#### **Cache Key Patterns**
```python
# Cache key patterns
CACHE_KEYS = {
    "user_profile": "profile:{user_id}",
    "mood_analytics": "mood_analytics:{user_id}:{days}",
    "mood_forecast": "mood_forecast:{user_id}",
    "ai_context": "ai_context:{user_id}",
    "content_feed": "content_feed:{user_id}:{page}",
    "community_posts": "community_posts:{forum_id}:{page}",
    "notification_preferences": "notif_prefs:{user_id}",
    "language_preferences": "lang_prefs:{user_id}",
    "ai_insights": "ai_insights:{user_id}:{type}",
    "emotion_analysis": "emotion:{text_hash}:{language}"
}
```

### **7. Event Bus Implementation**

#### **NATS JetStream Configuration**
```python
# shared/events/nats_config.py
class NATSConfig:
    def __init__(self):
        self.server_url = os.getenv("NATS_URL", "nats://localhost:4222")
        self.jetstream_enabled = True
        self.streams = {
            "mantrapath_events": {
                "subjects": ["mantrapath.*"],
                "retention": "24h",
                "max_age": "24h",
                "storage": "file"
            }
        }
    
    async def create_streams(self, js: JetStreamContext):
        for stream_name, config in self.streams.items():
            try:
                await js.add_stream(
                    name=stream_name,
                    subjects=config["subjects"],
                    retention=config["retention"],
                    max_age=config["max_age"],
                    storage=config["storage"]
                )
                logger.info(f"Created stream: {stream_name}")
            except Exception as e:
                logger.error(f"Error creating stream {stream_name}: {e}")
```

#### **Event Publishing**
```python
# shared/events/publisher.py
class EventPublisher:
    def __init__(self, js: JetStreamContext):
        self.js = js
    
    async def publish_event(self, subject: str, data: dict, user_id: str = None):
        try:
            event = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "data": data,
                "version": "1.0"
            }
            
            await self.js.publish(subject, json.dumps(event).encode())
            logger.info(f"Published event to {subject}")
            
        except Exception as e:
            logger.error(f"Error publishing event to {subject}: {e}")
            raise
```

### **8. Error Handling and Resilience**

#### **Circuit Breaker Pattern**
```python
# shared/resilience/circuit_breaker.py
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (datetime.utcnow() - self.last_failure_time).seconds >= self.timeout
    
    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

#### **Retry Mechanism**
```python
# shared/resilience/retry.py
class RetryManager:
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
    
    async def retry_async(self, func: Callable, *args, **kwargs):
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                    logger.warning(f"Retry attempt {attempt + 1} for {func.__name__}")
                else:
                    logger.error(f"All retry attempts failed for {func.__name__}")
        
        raise last_exception
```

This low-level design provides the detailed implementation patterns and code structures that form the foundation of the MantraPath platform, ensuring robust, scalable, and maintainable mental health services.
