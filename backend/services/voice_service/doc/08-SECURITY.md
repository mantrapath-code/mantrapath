# Voice Service Security

## Overview

The Voice Service implements enterprise-grade security measures to protect user voice data, ensure secure communication, and maintain privacy compliance. This document outlines the comprehensive security architecture and implementation details.

## 🔐 Authentication & Authorization

### JWT Token-Based Authentication
```python
# Token verification with Auth Service
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token with Auth Service"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Verify token with Auth Service
        auth_data = await integration_manager.verify_user_authentication(credentials.credentials)
        
        # Validate token structure and claims
        required_claims = ["user_id", "role", "permissions", "exp"]
        for claim in required_claims:
            if claim not in auth_data:
                raise AuthenticationError(f"Missing required claim: {claim}")
        
        # Check token expiration
        if auth_data.get("exp", 0) < time.time():
            raise AuthenticationError("Token expired")
        
        return auth_data
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
```

### Role-Based Access Control (RBAC)
```python
class VoiceServicePermissions:
    """Voice service specific permissions"""
    
    # Basic voice operations
    USE_STT = "voice:stt:use"
    USE_TTS = "voice:tts:use"
    USE_EMOTION_ANALYSIS = "voice:emotion:analyze"
    
    # Voice profile management
    CREATE_VOICE_PROFILE = "voice:profile:create"
    MANAGE_VOICE_PROFILE = "voice:profile:manage"
    DELETE_VOICE_PROFILE = "voice:profile:delete"
    
    # Voice commands
    USE_VOICE_COMMANDS = "voice:commands:use"
    CREATE_CUSTOM_COMMANDS = "voice:commands:create"
    
    # Administrative
    VIEW_SERVICE_STATS = "voice:admin:stats"
    MANAGE_SERVICE = "voice:admin:manage"
    CLEANUP_DATA = "voice:admin:cleanup"

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(*args, auth_data: dict = None, **kwargs):
            user_permissions = auth_data.get("permissions", [])
            user_role = auth_data.get("role", "user")
            
            # Admin role has all permissions
            if user_role == "admin":
                return await func(*args, **kwargs)
            
            # Check specific permission
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Insufficient permissions. Required: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### API Key Management
```python
class APIKeyManager:
    """Secure management of external service API keys"""
    
    def __init__(self):
        self.encryption_key = self._load_encryption_key()
        self.api_keys = {}
    
    def _load_encryption_key(self) -> bytes:
        """Load encryption key from secure storage"""
        key_path = os.getenv("API_KEY_ENCRYPTION_PATH", "/secrets/api_key.key")
        try:
            with open(key_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("API key encryption file not found, using environment key")
            return os.getenv("API_KEY_ENCRYPTION_KEY", "").encode()
    
    def store_api_key(self, service_name: str, api_key: str) -> None:
        """Store encrypted API key"""
        cipher = Fernet(self.encryption_key)
        encrypted_key = cipher.encrypt(api_key.encode())
        self.api_keys[service_name] = encrypted_key
    
    def get_api_key(self, service_name: str) -> str:
        """Retrieve and decrypt API key"""
        encrypted_key = self.api_keys.get(service_name)
        if not encrypted_key:
            raise VoiceServiceError(f"API key not found for service: {service_name}")
        
        cipher = Fernet(self.encryption_key)
        decrypted_key = cipher.decrypt(encrypted_key)
        return decrypted_key.decode()
```

## 🛡️ Voice Data Protection

### Audio Data Encryption
```python
class AudioDataProtector:
    """Protects audio data in transit and at rest"""
    
    def __init__(self):
        self.encryption_key = self._generate_session_key()
    
    def _generate_session_key(self) -> bytes:
        """Generate ephemeral encryption key for session"""
        return os.urandom(32)  # 256-bit key
    
    async def encrypt_audio_data(self, audio_data: bytes) -> EncryptedAudioData:
        """Encrypt audio data with session key"""
        cipher = Fernet(base64.urlsafe_b64encode(self.encryption_key))
        encrypted_data = cipher.encrypt(audio_data)
        
        return EncryptedAudioData(
            data=encrypted_data,
            encryption_metadata={
                "algorithm": "Fernet",
                "key_size": 256,
                "timestamp": time.time()
            }
        )
    
    async def decrypt_audio_data(self, encrypted_data: EncryptedAudioData) -> bytes:
        """Decrypt audio data"""
        cipher = Fernet(base64.urlsafe_b64encode(self.encryption_key))
        return cipher.decrypt(encrypted_data.data)
    
    async def secure_delete(self, audio_data: bytes) -> None:
        """Securely delete audio data from memory"""
        # Overwrite memory with random data
        for _ in range(3):
            audio_data = os.urandom(len(audio_data))
        del audio_data
```

### Voice Data Retention Policy
```python
class VoiceDataRetentionManager:
    """Manages voice data lifecycle and retention"""
    
    RETENTION_POLICIES = {
        "voice_samples": timedelta(days=30),  # Voice profile training data
        "processing_cache": timedelta(hours=2),  # Temporary processing data
        "error_logs": timedelta(days=90),  # Error diagnostics
        "user_audio": timedelta(minutes=0),  # Immediate deletion after processing
    }
    
    async def apply_retention_policy(self, data_type: str, data_id: str, created_at: datetime) -> bool:
        """Check if data should be retained based on policy"""
        policy = self.RETENTION_POLICIES.get(data_type)
        if not policy:
            # Default: delete immediately if no policy
            return False
        
        expiry_time = created_at + policy
        return datetime.now() < expiry_time
    
    async def cleanup_expired_data(self) -> CleanupReport:
        """Remove expired data according to retention policies"""
        cleanup_report = CleanupReport()
        
        for data_type, retention_period in self.RETENTION_POLICIES.items():
            cutoff_time = datetime.now() - retention_period
            
            # Find expired data
            expired_items = await self.find_expired_data(data_type, cutoff_time)
            
            # Securely delete expired data
            deleted_count = 0
            for item in expired_items:
                await self.secure_delete_data(item)
                deleted_count += 1
            
            cleanup_report.add_result(data_type, deleted_count)
        
        return cleanup_report
```

## 🔒 Privacy Compliance

### GDPR Compliance Implementation
```python
class VoiceDataGDPRCompliance:
    """GDPR compliance for voice data processing"""
    
    async def get_user_consent(self, user_id: str) -> VoiceProcessingConsent:
        """Retrieve user's voice processing consent"""
        consent = await self.consent_store.get_consent(user_id)
        return VoiceProcessingConsent(
            user_id=user_id,
            voice_processing_enabled=consent.get("voice_processing", False),
            voice_storage_enabled=consent.get("voice_storage", False),
            voice_analysis_enabled=consent.get("voice_analysis", False),
            consent_timestamp=consent.get("timestamp"),
            consent_version=consent.get("version", "1.0")
        )
    
    async def process_data_subject_request(self, user_id: str, request_type: str) -> DSRResponse:
        """Handle GDPR data subject requests"""
        if request_type == "access":
            return await self._handle_data_access_request(user_id)
        elif request_type == "portability":
            return await self._handle_data_portability_request(user_id)
        elif request_type == "deletion":
            return await self._handle_data_deletion_request(user_id)
        elif request_type == "rectification":
            return await self._handle_data_rectification_request(user_id)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    async def _handle_data_deletion_request(self, user_id: str) -> DSRResponse:
        """Delete all user voice data"""
        deletion_results = []
        
        # Delete voice profiles
        profile_result = await self.delete_voice_profiles(user_id)
        deletion_results.append(("voice_profiles", profile_result))
        
        # Delete processing history
        history_result = await self.delete_processing_history(user_id)
        deletion_results.append(("processing_history", history_result))
        
        # Delete cached data
        cache_result = await self.delete_cached_voice_data(user_id)
        deletion_results.append(("cached_data", cache_result))
        
        # Delete training data
        training_result = await self.delete_training_data(user_id)
        deletion_results.append(("training_data", training_result))
        
        return DSRResponse(
            request_type="deletion",
            user_id=user_id,
            status="completed",
            results=deletion_results,
            timestamp=datetime.now()
        )
```

### Consent Management
```python
class VoiceConsentManager:
    """Manages user consent for voice processing"""
    
    CONSENT_TYPES = {
        "basic_processing": "Basic voice processing (STT/TTS)",
        "emotion_analysis": "Emotion analysis from voice",
        "voice_storage": "Temporary voice data storage",
        "voice_profiling": "Voice profile creation and training",
        "voice_biometrics": "Voice-based authentication",
        "cross_service_sharing": "Sharing voice insights with other services"
    }
    
    async def record_consent(self, user_id: str, consent_data: ConsentData) -> ConsentRecord:
        """Record user consent with audit trail"""
        consent_record = ConsentRecord(
            user_id=user_id,
            consent_types=consent_data.consent_types,
            consent_version=consent_data.version,
            consent_timestamp=datetime.now(),
            ip_address=consent_data.ip_address,
            user_agent=consent_data.user_agent,
            explicit_consent=consent_data.explicit_consent
        )
        
        # Store consent record
        await self.consent_store.store_consent(consent_record)
        
        # Update user preferences
        await self.update_voice_preferences(user_id, consent_data.consent_types)
        
        # Audit log
        await self.audit_logger.log_consent_change(consent_record)
        
        return consent_record
    
    async def withdraw_consent(self, user_id: str, consent_types: List[str]) -> WithdrawalRecord:
        """Handle consent withdrawal"""
        withdrawal_record = WithdrawalRecord(
            user_id=user_id,
            withdrawn_types=consent_types,
            withdrawal_timestamp=datetime.now()
        )
        
        # Update consent status
        await self.consent_store.withdraw_consent(user_id, consent_types)
        
        # Trigger data cleanup for withdrawn consent
        for consent_type in consent_types:
            await self.cleanup_data_for_consent_type(user_id, consent_type)
        
        # Audit log
        await self.audit_logger.log_consent_withdrawal(withdrawal_record)
        
        return withdrawal_record
```

## 🚨 Security Monitoring

### Threat Detection System
```python
class VoiceSecurityMonitor:
    """Real-time security monitoring for voice service"""
    
    def __init__(self):
        self.threat_detector = ThreatDetector()
        self.rate_limiter = RateLimiter()
        self.anomaly_detector = AnomalyDetector()
    
    async def monitor_request(self, request: VoiceRequest, user_context: UserContext) -> SecurityAssessment:
        """Comprehensive security assessment of voice request"""
        assessment = SecurityAssessment()
        
        # Rate limiting check
        rate_limit_result = await self.rate_limiter.check_rate_limit(user_context.user_id)
        assessment.rate_limit_status = rate_limit_result
        
        # Anomaly detection
        anomaly_score = await self.anomaly_detector.analyze_request(request, user_context)
        assessment.anomaly_score = anomaly_score
        
        # Content analysis
        content_threats = await self.threat_detector.analyze_content(request.audio_data)
        assessment.content_threats = content_threats
        
        # Behavioral analysis
        behavior_anomalies = await self.analyze_user_behavior(user_context)
        assessment.behavior_anomalies = behavior_anomalies
        
        # Overall risk assessment
        assessment.risk_level = self.calculate_risk_level(assessment)
        
        return assessment
    
    async def handle_security_incident(self, assessment: SecurityAssessment, user_context: UserContext):
        """Handle detected security incidents"""
        if assessment.risk_level >= RiskLevel.HIGH:
            # Block request
            await self.block_request(user_context.session_id)
            
            # Alert security team
            await self.send_security_alert(assessment, user_context)
            
            # Log incident
            await self.log_security_incident(assessment, user_context)
        
        elif assessment.risk_level == RiskLevel.MEDIUM:
            # Additional verification
            await self.request_additional_verification(user_context.user_id)
            
            # Increased monitoring
            await self.increase_monitoring_level(user_context.user_id)
```

### Audit Logging
```python
class VoiceAuditLogger:
    """Comprehensive audit logging for voice service"""
    
    async def log_voice_request(self, request: VoiceRequest, user_id: str, result: VoiceResult):
        """Log voice processing request"""
        audit_entry = VoiceAuditEntry(
            event_type="voice_request",
            user_id=user_id,
            timestamp=datetime.now(),
            request_id=request.request_id,
            endpoint=request.endpoint,
            language=request.language,
            processing_time=result.processing_time,
            success=result.success,
            error_message=result.error_message if not result.success else None
        )
        
        # Exclude sensitive audio data from logs
        audit_entry.request_metadata = {
            "audio_format": request.audio_format,
            "audio_duration": request.audio_duration,
            "engine_used": result.engine_used,
            "confidence_score": result.confidence_score
        }
        
        await self.audit_store.store_audit_entry(audit_entry)
    
    async def log_security_event(self, event_type: str, user_id: str, details: dict):
        """Log security-related events"""
        security_entry = SecurityAuditEntry(
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.now(),
            details=details,
            severity=self.determine_severity(event_type),
            source_ip=details.get("ip_address"),
            user_agent=details.get("user_agent")
        )
        
        await self.security_audit_store.store_security_entry(security_entry)
        
        # Real-time alerting for critical events
        if security_entry.severity >= SeverityLevel.HIGH:
            await self.send_real_time_alert(security_entry)
```

## 🔧 Security Configuration

### Environment Security
```bash
# Voice Service Security Environment Variables

# Authentication
VOICE_JWT_SECRET_KEY=<strong-secret-key>
VOICE_JWT_ALGORITHM=HS256
VOICE_TOKEN_EXPIRY_HOURS=24

# API Key Encryption
API_KEY_ENCRYPTION_KEY=<encryption-key>
API_KEY_ENCRYPTION_PATH=/secrets/api_key.key

# Rate Limiting
VOICE_RATE_LIMIT_PER_MINUTE=60
VOICE_RATE_LIMIT_PER_HOUR=1000
VOICE_RATE_LIMIT_BURST=10

# Data Retention
VOICE_DATA_RETENTION_DAYS=30
VOICE_CACHE_RETENTION_HOURS=2
VOICE_ERROR_LOG_RETENTION_DAYS=90

# Security Monitoring
VOICE_ANOMALY_DETECTION_ENABLED=true
VOICE_THREAT_DETECTION_ENABLED=true
VOICE_SECURITY_ALERTS_ENABLED=true

# Privacy Compliance
VOICE_GDPR_COMPLIANCE_ENABLED=true
VOICE_DATA_ANONYMIZATION_ENABLED=true
VOICE_AUDIT_LOGGING_ENABLED=true
```

### Security Headers Configuration
```python
# Security middleware configuration
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "microphone=(self), camera=(), geolocation=()"
}

# CORS configuration
CORS_SETTINGS = {
    "allow_origins": ["https://app.mantrapath.com"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["Authorization", "Content-Type"],
    "expose_headers": ["X-Request-ID"]
}
```

## 🧪 Security Testing

### Penetration Testing Checklist
```yaml
security_tests:
  authentication:
    - token_expiry_validation
    - token_forgery_attempts
    - authorization_bypass_tests
    - role_escalation_attempts
  
  data_protection:
    - audio_data_encryption_validation
    - data_transmission_security
    - data_at_rest_protection
    - secure_deletion_verification
  
  api_security:
    - input_validation_tests
    - injection_attack_tests
    - rate_limiting_validation
    - ddos_protection_tests
  
  privacy_compliance:
    - consent_management_validation
    - data_subject_rights_testing
    - data_retention_policy_tests
    - audit_trail_validation
```

### Automated Security Scans
```python
class VoiceSecurityScanner:
    """Automated security vulnerability scanning"""
    
    async def run_security_scan(self) -> SecurityScanReport:
        """Run comprehensive security scan"""
        report = SecurityScanReport()
        
        # Authentication vulnerabilities
        auth_results = await self.scan_authentication_vulnerabilities()
        report.add_results("authentication", auth_results)
        
        # API vulnerabilities
        api_results = await self.scan_api_vulnerabilities()
        report.add_results("api_security", api_results)
        
        # Data protection
        data_results = await self.scan_data_protection()
        report.add_results("data_protection", data_results)
        
        # Configuration security
        config_results = await self.scan_configuration_security()
        report.add_results("configuration", config_results)
        
        return report
```

## 🚀 Security Best Practices

### Development Guidelines
1. **Secure by Default**: All voice endpoints require authentication
2. **Principle of Least Privilege**: Grant minimum necessary permissions
3. **Data Minimization**: Process only necessary voice data
4. **Encryption Everywhere**: Encrypt data in transit and at rest
5. **Audit Everything**: Log all security-relevant events
6. **Regular Updates**: Keep dependencies and engines updated
7. **Security Reviews**: Regular code security reviews
8. **Incident Response**: Prepared incident response procedures

### Deployment Security
1. **Environment Isolation**: Separate dev/staging/prod environments
2. **Secret Management**: Use secure secret management systems
3. **Network Security**: Restrict network access with firewalls
4. **Container Security**: Scan container images for vulnerabilities
5. **Monitoring**: Real-time security monitoring and alerting
6. **Backup Security**: Secure and test backup procedures
7. **Access Control**: Strict access control to production systems

---

This security implementation ensures the Voice Service meets enterprise security requirements while maintaining usability and performance for voice processing operations.
