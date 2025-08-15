"""
Voice Service Custom Exceptions
Comprehensive exception handling for enterprise-grade error management
"""

class VoiceServiceError(Exception):
    """Base exception for all voice service errors"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "VOICE_SERVICE_ERROR"
        self.details = details or {}

class AudioProcessingError(VoiceServiceError):
    """Raised when audio processing fails"""
    
    def __init__(self, message: str, audio_format: str = None, **kwargs):
        super().__init__(message, "AUDIO_PROCESSING_ERROR", kwargs)
        self.audio_format = audio_format

class EngineError(VoiceServiceError):
    """Raised when voice engine processing fails"""
    
    def __init__(self, message: str, engine_name: str = None, **kwargs):
        super().__init__(message, "ENGINE_ERROR", kwargs)
        self.engine_name = engine_name

class STTEngineError(EngineError):
    """Raised when Speech-to-Text engine fails"""
    
    def __init__(self, message: str, engine_name: str = None, **kwargs):
        super().__init__(message, engine_name, **kwargs)
        self.error_code = "STT_ENGINE_ERROR"

class TTSEngineError(EngineError):
    """Raised when Text-to-Speech engine fails"""
    
    def __init__(self, message: str, engine_name: str = None, **kwargs):
        super().__init__(message, engine_name, **kwargs)
        self.error_code = "TTS_ENGINE_ERROR"

class EmotionAnalysisError(EngineError):
    """Raised when emotion analysis fails"""
    
    def __init__(self, message: str, engine_name: str = None, **kwargs):
        super().__init__(message, engine_name, **kwargs)
        self.error_code = "EMOTION_ANALYSIS_ERROR"

class UnsupportedLanguageError(VoiceServiceError):
    """Raised when requested language is not supported"""
    
    def __init__(self, language_code: str, supported_languages: list = None):
        message = f"Language '{language_code}' is not supported"
        if supported_languages:
            message += f". Supported languages: {', '.join(supported_languages)}"
        
        super().__init__(message, "UNSUPPORTED_LANGUAGE_ERROR")
        self.language_code = language_code
        self.supported_languages = supported_languages or []

class AudioValidationError(VoiceServiceError):
    """Raised when audio validation fails"""
    
    def __init__(self, message: str, validation_type: str = None, **kwargs):
        super().__init__(message, "AUDIO_VALIDATION_ERROR", kwargs)
        self.validation_type = validation_type

class FileSizeError(AudioValidationError):
    """Raised when audio file size exceeds limits"""
    
    def __init__(self, file_size: int, max_size: int):
        message = f"File size {file_size} bytes exceeds maximum allowed {max_size} bytes"
        super().__init__(message, "file_size_validation")
        self.file_size = file_size
        self.max_size = max_size

class AudioDurationError(AudioValidationError):
    """Raised when audio duration exceeds limits"""
    
    def __init__(self, duration: float, max_duration: float):
        message = f"Audio duration {duration}s exceeds maximum allowed {max_duration}s"
        super().__init__(message, "duration_validation")
        self.duration = duration
        self.max_duration = max_duration

class UnsupportedFormatError(AudioValidationError):
    """Raised when audio format is not supported"""
    
    def __init__(self, format: str, supported_formats: list = None):
        message = f"Audio format '{format}' is not supported"
        if supported_formats:
            message += f". Supported formats: {', '.join(supported_formats)}"
        
        super().__init__(message, "format_validation")
        self.format = format
        self.supported_formats = supported_formats or []

class VoiceProfileError(VoiceServiceError):
    """Raised when voice profile operations fail"""
    
    def __init__(self, message: str, profile_id: str = None, **kwargs):
        super().__init__(message, "VOICE_PROFILE_ERROR", kwargs)
        self.profile_id = profile_id

class VoiceCommandError(VoiceServiceError):
    """Raised when voice command processing fails"""
    
    def __init__(self, message: str, command: str = None, **kwargs):
        super().__init__(message, "VOICE_COMMAND_ERROR", kwargs)
        self.command = command

class UnsupportedCommandError(VoiceCommandError):
    """Raised when voice command is not supported"""
    
    def __init__(self, command: str, supported_commands: list = None):
        message = f"Command '{command}' is not supported"
        if supported_commands:
            message += f". Supported commands: {', '.join(supported_commands)}"
        
        super().__init__(message, command)
        self.error_code = "UNSUPPORTED_COMMAND_ERROR"
        self.supported_commands = supported_commands or []

class VoiceProfileNotFoundError(VoiceProfileError):
    """Raised when voice profile is not found"""
    
    def __init__(self, profile_id: str):
        message = f"Voice profile '{profile_id}' not found"
        super().__init__(message, profile_id)
        self.error_code = "VOICE_PROFILE_NOT_FOUND"

class VoiceProfileCreationError(VoiceProfileError):
    """Raised when voice profile creation fails"""
    
    def __init__(self, message: str, user_id: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.error_code = "VOICE_PROFILE_CREATION_ERROR"
        self.user_id = user_id

class AuthenticationError(VoiceServiceError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(message, "AUTHENTICATION_ERROR", kwargs)

class AuthorizationError(VoiceServiceError):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, "AUTHORIZATION_ERROR", kwargs)

class RateLimitExceededError(VoiceServiceError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, reset_time: float = None, **kwargs):
        message = f"Rate limit of {limit} requests exceeded"
        if reset_time:
            message += f". Resets at {reset_time}"
        
        super().__init__(message, "RATE_LIMIT_EXCEEDED", kwargs)
        self.limit = limit
        self.reset_time = reset_time

# Alias for backward compatibility
RateLimitError = RateLimitExceededError

class WebSocketError(VoiceServiceError):
    """Raised when WebSocket operations fail"""
    
    def __init__(self, message: str, connection_id: str = None, **kwargs):
        super().__init__(message, "WEBSOCKET_ERROR", kwargs)
        self.connection_id = connection_id

class ServiceIntegrationError(VoiceServiceError):
    """Raised when service integration fails"""
    
    def __init__(self, message: str, service_name: str = None, **kwargs):
        super().__init__(message, "SERVICE_INTEGRATION_ERROR", kwargs)
        self.service_name = service_name

class ConfigurationError(VoiceServiceError):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(message, "CONFIGURATION_ERROR", kwargs)
        self.config_key = config_key

class VoiceCommandError(VoiceServiceError):
    """Raised when voice command processing fails"""
    
    def __init__(self, message: str, command_text: str = None, **kwargs):
        super().__init__(message, "VOICE_COMMAND_ERROR", kwargs)
        self.command_text = command_text

class StreamingError(VoiceServiceError):
    """Raised when real-time streaming fails"""
    
    def __init__(self, message: str, stream_id: str = None, **kwargs):
        super().__init__(message, "STREAMING_ERROR", kwargs)
        self.stream_id = stream_id

def handle_engine_exception(func):
    """Decorator to handle and transform engine-specific exceptions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Transform common exceptions to voice service exceptions
            if "authentication" in str(e).lower():
                raise AuthenticationError(f"Engine authentication failed: {str(e)}")
            elif "rate limit" in str(e).lower():
                raise RateLimitExceededError(0, message=str(e))
            elif "unsupported" in str(e).lower() and "language" in str(e).lower():
                raise UnsupportedLanguageError("unknown")
            elif "timeout" in str(e).lower():
                raise EngineError(f"Engine timeout: {str(e)}")
            else:
                raise EngineError(f"Engine processing failed: {str(e)}")
    
    return wrapper

class ErrorHandler:
    """Centralized error handling utility"""
    
    @staticmethod
    def format_error_response(error: VoiceServiceError, request_id: str = None) -> dict:
        """Format error as standardized response"""
        return {
            "success": False,
            "error": {
                "code": error.error_code,
                "message": error.message,
                "details": error.details
            },
            "request_id": request_id,
            "timestamp": None  # Will be set by response model
        }
    
    @staticmethod
    def is_retryable_error(error: VoiceServiceError) -> bool:
        """Check if error is retryable"""
        retryable_codes = [
            "ENGINE_ERROR",
            "AUDIO_PROCESSING_ERROR", 
            "SERVICE_INTEGRATION_ERROR",
            "STREAMING_ERROR"
        ]
        return error.error_code in retryable_codes
    
    @staticmethod
    def get_user_friendly_message(error: VoiceServiceError) -> str:
        """Get user-friendly error message"""
        user_messages = {
            "UNSUPPORTED_LANGUAGE_ERROR": "The requested language is not currently supported.",
            "AUDIO_VALIDATION_ERROR": "There was an issue with the audio file. Please check the format and size.",
            "RATE_LIMIT_EXCEEDED": "Too many requests. Please wait a moment before trying again.",
            "AUTHENTICATION_ERROR": "Authentication is required to access this feature.",
            "VOICE_PROFILE_NOT_FOUND": "Voice profile not found. Please create a profile first."
        }
        
        return user_messages.get(error.error_code, "An unexpected error occurred. Please try again.")
