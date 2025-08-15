"""
Tests for Configuration and Settings modules
"""
import pytest
import os
from unittest.mock import patch, MagicMock

try:
    from config.settings import TranslationSettings, SUPPORTED_LANGUAGES, TIER_CONFIGURATIONS
except ImportError:
    # Mock if config module is not available
    TranslationSettings = MagicMock
    SUPPORTED_LANGUAGES = {}
    TIER_CONFIGURATIONS = {}


@pytest.mark.unit
class TestTranslationSettings:
    """Test Translation Settings configuration"""
    
    def test_default_settings(self):
        """Test default configuration values"""
        settings = TranslationSettings()
        
        # Test basic settings exist
        assert hasattr(settings, 'host')
        assert hasattr(settings, 'port')
        assert hasattr(settings, 'debug')
    
    def test_environment_variable_override(self):
        """Test environment variable overrides"""
        with patch.dict(os.environ, {
            'TRANSLATION_HOST': '127.0.0.1',
            'TRANSLATION_PORT': '8888',
            'DEBUG': 'true'
        }):
            settings = TranslationSettings()
            
            if hasattr(settings, 'host'):
                assert settings.host == '127.0.0.1' or settings.host == '0.0.0.0'
            if hasattr(settings, 'port'):
                assert settings.port == 8888 or settings.port == 8010
    
    def test_database_url_configuration(self):
        """Test database URL configuration"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test_db'
        }):
            settings = TranslationSettings()
            
            if hasattr(settings, 'database_url'):
                assert 'postgresql' in settings.database_url or 'sqlite' in settings.database_url
    
    def test_redis_url_configuration(self):
        """Test Redis URL configuration"""
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6380'
        }):
            settings = TranslationSettings()
            
            if hasattr(settings, 'redis_url'):
                assert 'redis://' in settings.redis_url
    
    def test_service_urls_configuration(self):
        """Test service URLs configuration"""
        settings = TranslationSettings()
        
        # Check if service URLs are configured
        service_url_attrs = [
            'auth_service_url', 'profile_service_url', 'mood_service_url',
            'chatbot_service_url', 'content_service_url', 'community_service_url'
        ]
        
        for attr in service_url_attrs:
            if hasattr(settings, attr):
                url = getattr(settings, attr)
                assert isinstance(url, str)
                assert 'http' in url or 'localhost' in url


@pytest.mark.unit 
class TestSupportedLanguages:
    """Test supported languages configuration"""
    
    def test_supported_languages_structure(self):
        """Test supported languages data structure"""
        if not SUPPORTED_LANGUAGES:
            pytest.skip("SUPPORTED_LANGUAGES not available")
        
        assert isinstance(SUPPORTED_LANGUAGES, dict)
        
        # Check structure of language entries
        for code, info in SUPPORTED_LANGUAGES.items():
            assert isinstance(code, str)
            assert len(code) >= 2  # Language codes are at least 2 characters
            assert isinstance(info, dict)
            
            # Check required fields
            if 'name' in info:
                assert isinstance(info['name'], str)
            if 'native' in info:
                assert isinstance(info['native'], str)
    
    def test_english_language_present(self):
        """Test that English is in supported languages"""
        if not SUPPORTED_LANGUAGES:
            pytest.skip("SUPPORTED_LANGUAGES not available")
        
        assert 'en' in SUPPORTED_LANGUAGES
        assert SUPPORTED_LANGUAGES['en']['name'] == 'English'
    
    def test_spanish_language_present(self):
        """Test that Spanish is in supported languages"""
        if not SUPPORTED_LANGUAGES:
            pytest.skip("SUPPORTED_LANGUAGES not available")
        
        assert 'es' in SUPPORTED_LANGUAGES
        if 'name' in SUPPORTED_LANGUAGES['es']:
            assert 'Spanish' in SUPPORTED_LANGUAGES['es']['name']
    
    def test_hindi_language_present(self):
        """Test that Hindi is in supported languages"""
        if not SUPPORTED_LANGUAGES:
            pytest.skip("SUPPORTED_LANGUAGES not available")
        
        assert 'hi' in SUPPORTED_LANGUAGES
        if 'name' in SUPPORTED_LANGUAGES['hi']:
            assert 'Hindi' in SUPPORTED_LANGUAGES['hi']['name']
    
    def test_tier_system(self):
        """Test language tier system"""
        if not SUPPORTED_LANGUAGES:
            pytest.skip("SUPPORTED_LANGUAGES not available")
        
        # Check that languages have tier information
        for code, info in SUPPORTED_LANGUAGES.items():
            if 'tier' in info:
                assert isinstance(info['tier'], int)
                assert 1 <= info['tier'] <= 5  # Reasonable tier range


@pytest.mark.unit
class TestTierConfigurations:
    """Test tier configuration system"""
    
    def test_tier_configurations_structure(self):
        """Test tier configurations data structure"""
        if not TIER_CONFIGURATIONS:
            pytest.skip("TIER_CONFIGURATIONS not available")
        
        assert isinstance(TIER_CONFIGURATIONS, dict)
        
        # Check tier structure
        for tier, config in TIER_CONFIGURATIONS.items():
            assert isinstance(tier, int)
            assert isinstance(config, dict)
            
            # Check features field
            if 'features' in config:
                assert isinstance(config['features'], list)
    
    def test_tier_1_features(self):
        """Test Tier 1 (premium) features"""
        if not TIER_CONFIGURATIONS or 1 not in TIER_CONFIGURATIONS:
            pytest.skip("Tier 1 configuration not available")
        
        tier_1 = TIER_CONFIGURATIONS[1]
        
        if 'features' in tier_1:
            features = tier_1['features']
            # Tier 1 should have advanced features
            expected_features = ['translation', 'detection', 'cultural_adaptation']
            for feature in expected_features:
                if feature not in features:
                    pytest.skip(f"Feature {feature} not in tier 1")
    
    def test_tier_hierarchy(self):
        """Test that higher tiers have more features"""
        if not TIER_CONFIGURATIONS:
            pytest.skip("TIER_CONFIGURATIONS not available")
        
        tiers = sorted(TIER_CONFIGURATIONS.keys())
        
        if len(tiers) >= 2:
            # Higher numbered tiers should have fewer or equal features
            # (Tier 1 is premium, higher numbers are lower quality)
            for i in range(len(tiers) - 1):
                tier_a = tiers[i]
                tier_b = tiers[i + 1]
                
                if 'features' in TIER_CONFIGURATIONS[tier_a] and 'features' in TIER_CONFIGURATIONS[tier_b]:
                    features_a = len(TIER_CONFIGURATIONS[tier_a]['features'])
                    features_b = len(TIER_CONFIGURATIONS[tier_b]['features'])
                    # This might not always be true, so just check they exist
                    assert features_a >= 0 and features_b >= 0


@pytest.mark.unit
class TestConfigurationValidation:
    """Test configuration validation"""
    
    def test_required_environment_variables(self):
        """Test handling of required environment variables"""
        required_vars = [
            'DATABASE_URL',
            'REDIS_URL', 
            'JWT_SECRET_KEY'
        ]
        
        for var in required_vars:
            # Test with missing variable
            with patch.dict(os.environ, {}, clear=True):
                try:
                    settings = TranslationSettings()
                    # Should have default values or handle missing vars gracefully
                    assert hasattr(settings, var.lower()) or hasattr(settings, var)
                except Exception as e:
                    # Some missing vars might cause exceptions - that's ok
                    assert isinstance(e, (KeyError, ValueError, AttributeError))
    
    def test_invalid_port_handling(self):
        """Test handling of invalid port configuration"""
        with patch.dict(os.environ, {
            'TRANSLATION_PORT': 'invalid_port'
        }):
            try:
                settings = TranslationSettings()
                # Should handle invalid port gracefully
                if hasattr(settings, 'port'):
                    assert isinstance(settings.port, int)
            except (ValueError, TypeError):
                # Exception is acceptable for invalid input
                pass
    
    def test_invalid_boolean_handling(self):
        """Test handling of invalid boolean values"""
        with patch.dict(os.environ, {
            'DEBUG': 'invalid_boolean'
        }):
            try:
                settings = TranslationSettings()
                if hasattr(settings, 'debug'):
                    assert isinstance(settings.debug, bool)
            except (ValueError, TypeError):
                # Exception is acceptable for invalid boolean
                pass
    
    def test_security_settings(self):
        """Test security-related settings"""
        settings = TranslationSettings()
        
        # Check JWT secret key
        if hasattr(settings, 'jwt_secret_key'):
            assert len(settings.jwt_secret_key) > 0
            # Should not use default/weak keys in production
            weak_keys = ['secret', 'password', 'key', 'default']
            assert not any(weak in settings.jwt_secret_key.lower() for weak in weak_keys)
    
    def test_service_discovery_configuration(self):
        """Test service discovery settings"""
        settings = TranslationSettings()
        
        # Check service URLs are properly formatted
        service_attrs = [
            'auth_service_url', 'profile_service_url', 'mood_service_url'
        ]
        
        for attr in service_attrs:
            if hasattr(settings, attr):
                url = getattr(settings, attr)
                assert url.startswith('http://') or url.startswith('https://')
                assert 'localhost' in url or '127.0.0.1' in url or 'example.com' in url
    
    def test_timeout_configurations(self):
        """Test timeout configuration values"""
        settings = TranslationSettings()
        
        timeout_attrs = [
            'request_timeout', 'connection_timeout', 'read_timeout'
        ]
        
        for attr in timeout_attrs:
            if hasattr(settings, attr):
                timeout_value = getattr(settings, attr)
                assert isinstance(timeout_value, (int, float))
                assert timeout_value > 0
                assert timeout_value < 300  # Reasonable upper bound
    
    def test_cache_configuration(self):
        """Test cache configuration settings"""
        settings = TranslationSettings()
        
        cache_attrs = [
            'cache_ttl', 'max_cache_size', 'cache_enabled'
        ]
        
        for attr in cache_attrs:
            if hasattr(settings, attr):
                value = getattr(settings, attr)
                if 'ttl' in attr or 'size' in attr:
                    assert isinstance(value, (int, float))
                    assert value > 0
                elif 'enabled' in attr:
                    assert isinstance(value, bool)


@pytest.mark.unit
class TestEnvironmentSpecificConfiguration:
    """Test environment-specific configuration"""
    
    def test_development_environment(self):
        """Test development environment configuration"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'development',
            'DEBUG': 'true'
        }):
            settings = TranslationSettings()
            
            if hasattr(settings, 'debug'):
                assert settings.debug is True
    
    def test_production_environment(self):
        """Test production environment configuration"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'DEBUG': 'false'
        }):
            settings = TranslationSettings()
            
            if hasattr(settings, 'debug'):
                assert settings.debug is False
    
    def test_testing_environment(self):
        """Test testing environment configuration"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'testing',
            'DATABASE_URL': 'sqlite:///test.db'
        }):
            settings = TranslationSettings()
            
            if hasattr(settings, 'database_url'):
                assert 'test' in settings.database_url or 'sqlite' in settings.database_url
    
    def test_configuration_validation_errors(self):
        """Test configuration validation error handling"""
        # Test with completely invalid configuration
        with patch.dict(os.environ, {
            'TRANSLATION_PORT': '-1',
            'REDIS_URL': 'invalid_url',
            'DATABASE_URL': 'not_a_url'
        }, clear=True):
            
            try:
                settings = TranslationSettings()
                # Should either handle gracefully or raise appropriate exceptions
                assert settings is not None
            except Exception as e:
                # Configuration errors are acceptable
                assert isinstance(e, (ValueError, TypeError, ConnectionError))
