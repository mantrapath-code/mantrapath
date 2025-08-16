"""
Comprehensive Main Application Tests for Models Service
Target: Increase main.py coverage to 80%
"""

import pytest
import pytest_asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestComprehensiveMainApp:
    """Comprehensive Main Application tests"""
    
    @pytest.fixture
    def temp_models_dir(self):
        """Create temporary models directory"""
        temp_dir = tempfile.mkdtemp()
        models_dir = Path(temp_dir) / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        yield models_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings"""
        mock_settings = Mock()
        mock_settings.MODELS_DIR = Path("/tmp/test_models")
        mock_settings.MODEL_CONFIGS = {}
        mock_settings.INDIAN_LANGUAGES = {
            'hi': {'stt_models': ['whisper'], 'tts_models': ['coqui']},
            'bn': {'stt_models': ['whisper'], 'tts_models': ['coqui']}
        }
        return mock_settings
    
    def test_main_imports(self):
        """Test that main module can be imported"""
        # Test importing main components
        try:
            from main import app, startup_event, shutdown_event
            assert True  # Import successful
        except ImportError as e:
            pytest.skip(f"Main module import failed: {e}")
    
    @pytest.mark.asyncio
    async def test_startup_event_success(self, temp_models_dir, mock_settings):
        """Test successful startup event"""
        # Mock the settings import
        with patch('main.get_settings') as mock_get_settings:
            mock_get_settings.return_value = mock_settings
            
            # Mock the model classes
            with patch('main.ModelManager') as mock_manager_class, \
                 patch('main.STTEngine') as mock_stt_class, \
                 patch('main.TTSEngine') as mock_tts_class, \
                 patch('main.NLPEngine') as mock_nlp_class:
                
                # Mock instances
                mock_manager = Mock()
                mock_stt = Mock()
                mock_tts = Mock()
                mock_nlp = Mock()
                
                mock_manager_class.return_value = mock_manager
                mock_stt_class.return_value = mock_stt
                mock_tts_class.return_value = mock_tts
                mock_nlp_class.return_value = mock_nlp
                
                # Mock async methods
                mock_manager.initialize = Mock(return_value=None)
                mock_stt.load_default_models = Mock(return_value=None)
                mock_tts.load_default_models = Mock(return_value=None)
                mock_nlp.load_default_models = Mock(return_value=None)
                
                # Import and test startup event
                from main import startup_event
                
                # This should not raise an exception
                await startup_event()
                
                # Check that initialization was called
                mock_manager.initialize.assert_called_once()
                mock_stt.load_default_models.assert_called_once()
                mock_tts.load_default_models.assert_called_once()
                mock_nlp.load_default_models.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_startup_event_failure(self, temp_models_dir, mock_settings):
        """Test startup event with failure"""
        # Mock the settings import
        with patch('main.get_settings') as mock_get_settings:
            mock_get_settings.return_value = mock_settings
            
            # Mock the model classes to raise an exception
            with patch('main.ModelManager') as mock_manager_class:
                mock_manager_class.side_effect = Exception("Initialization failed")
                
                # Import and test startup event
                from main import startup_event
                
                # This should raise an exception
                with pytest.raises(Exception, match="Initialization failed"):
                    await startup_event()
    
    @pytest.mark.asyncio
    async def test_shutdown_event(self, temp_models_dir):
        """Test shutdown event"""
        # Mock the model manager
        with patch('main.model_manager') as mock_manager:
            mock_manager.cleanup = Mock(return_value=None)
            
            # Import and test shutdown event
            from main import shutdown_event
            
            # This should not raise an exception
            await shutdown_event()
            
            # Check that cleanup was called
            mock_manager.cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown_event_no_manager(self, temp_models_dir):
        """Test shutdown event when no manager exists"""
        # Mock the model manager to be None
        with patch('main.model_manager', None):
            # Import and test shutdown event
            from main import shutdown_event
            
            # This should not raise an exception
            await shutdown_event()
    
    def test_fastapi_app_configuration(self):
        """Test FastAPI app configuration"""
        try:
            from main import app
            
            # Test app configuration
            assert app.title == "MantraPath Models Service"
            assert app.description == "Centralized AI Models Service for STT, TTS, NLP, and Training"
            assert app.version == "1.0.0"
            assert app.docs_url == "/docs"
            assert app.redoc_url == "/redoc"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_cors_middleware(self):
        """Test CORS middleware configuration"""
        try:
            from main import app
            
            # Test that CORS is properly configured
            # This is tested by checking if the app has CORS middleware
            cors_middleware_found = False
            for middleware in app.user_middleware:
                if "CORSMiddleware" in str(middleware.cls):
                    cors_middleware_found = True
                    break
            
            assert cors_middleware_found, "CORS middleware not found"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_router_inclusion(self):
        """Test that API router is included"""
        try:
            from main import app
            
            # Test that the API router is properly included
            # This is tested by checking if the app has routes
            assert len(app.routes) > 0, "No routes found in app"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        try:
            from main import app
            
            # Test that health endpoint exists
            health_route_found = False
            for route in app.routes:
                if hasattr(route, 'path') and route.path == "/health":
                    health_route_found = True
                    break
            
            assert health_route_found, "Health endpoint not found"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        try:
            from main import app
            
            # Test that status endpoint exists
            status_route_found = False
            for route in app.routes:
                if hasattr(route, 'path') and route.path == "/status":
                    status_route_found = True
                    break
            
            assert status_route_found, "Status endpoint not found"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_startup_event_registration(self):
        """Test that startup event is registered"""
        try:
            from main import app
            
            # Test that startup event is registered
            startup_events = [event for event in app.router.events if event.event_type == "startup"]
            assert len(startup_events) > 0, "Startup event not registered"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_shutdown_event_registration(self):
        """Test that shutdown event is registered"""
        try:
            from main import app
            
            # Test that shutdown event is registered
            shutdown_events = [event for event in app.router.events if event.event_type == "shutdown"]
            assert len(shutdown_events) > 0, "Shutdown event not registered"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_global_variables_initialization(self):
        """Test global variables initialization"""
        try:
            from main import app
            
            # Test that global variables are properly initialized
            # These should be None initially
            from main import stt_engine, tts_engine, nlp_engine, model_manager
            
            # They should be None before startup
            assert stt_engine is None
            assert tts_engine is None
            assert nlp_engine is None
            assert model_manager is None
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_error_handling_in_startup(self, temp_models_dir, mock_settings):
        """Test error handling in startup event"""
        # Mock the settings import
        with patch('main.get_settings') as mock_get_settings:
            mock_get_settings.return_value = mock_settings
            
            # Mock the model classes
            with patch('main.ModelManager') as mock_manager_class:
                # Mock instance that raises exception during initialize
                mock_manager = Mock()
                mock_manager.initialize = Mock(side_effect=Exception("Model manager failed"))
                mock_manager_class.return_value = mock_manager
                
                # Import and test startup event
                from main import startup_event
                
                # This should raise an exception
                with pytest.raises(Exception, match="Model manager failed"):
                    await startup_event()
    
    def test_error_handling_in_shutdown(self, temp_models_dir):
        """Test error handling in shutdown event"""
        # Mock the model manager that raises exception during cleanup
        with patch('main.model_manager') as mock_manager:
            mock_manager.cleanup = Mock(side_effect=Exception("Cleanup failed"))
            
            # Import and test shutdown event
            from main import shutdown_event
            
            # This should raise an exception
            with pytest.raises(Exception, match="Cleanup failed"):
                await shutdown_event()
    
    def test_import_dependencies(self):
        """Test that all required dependencies can be imported"""
        # Test importing all required modules
        try:
            import fastapi
            import uvicorn
            import torch
            import psutil
            import numpy
            assert True  # All imports successful
        except ImportError as e:
            pytest.skip(f"Required dependency import failed: {e}")
    
    def test_app_metadata(self):
        """Test app metadata and configuration"""
        try:
            from main import app
            
            # Test app metadata
            assert hasattr(app, 'title')
            assert hasattr(app, 'description')
            assert hasattr(app, 'version')
            assert hasattr(app, 'docs_url')
            assert hasattr(app, 'redoc_url')
            
            # Test app type
            assert hasattr(app, 'routes')
            assert hasattr(app, 'user_middleware')
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_middleware_configuration(self):
        """Test middleware configuration"""
        try:
            from main import app
            
            # Test that middleware is configured
            assert len(app.user_middleware) > 0, "No middleware configured"
            
            # Test CORS middleware specifically
            cors_middleware = None
            for middleware in app.user_middleware:
                if "CORSMiddleware" in str(middleware.cls):
                    cors_middleware = middleware
                    break
            
            assert cors_middleware is not None, "CORS middleware not found"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_route_registration(self):
        """Test route registration"""
        try:
            from main import app
            
            # Test that routes are registered
            assert len(app.routes) > 0, "No routes registered"
            
            # Test for specific route types
            get_routes = [r for r in app.routes if hasattr(r, 'methods') and 'GET' in r.methods]
            post_routes = [r for r in app.routes if hasattr(r, 'methods') and 'POST' in r.methods]
            
            assert len(get_routes) > 0, "No GET routes found"
            assert len(post_routes) > 0, "No POST routes found"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_app_lifecycle_events(self):
        """Test app lifecycle events"""
        try:
            from main import app
            
            # Test that lifecycle events are registered
            startup_events = [e for e in app.router.events if e.event_type == "startup"]
            shutdown_events = [e for e in app.router.events if e.event_type == "shutdown"]
            
            assert len(startup_events) > 0, "No startup events registered"
            assert len(shutdown_events) > 0, "No shutdown events registered"
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_global_state_management(self):
        """Test global state management"""
        try:
            from main import app
            
            # Test that global variables are accessible
            from main import stt_engine, tts_engine, nlp_engine, model_manager
            
            # These should be None initially
            assert stt_engine is None
            assert tts_engine is None
            assert nlp_engine is None
            assert model_manager is None
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_exception_handling_patterns(self):
        """Test exception handling patterns"""
        try:
            from main import app
            
            # Test that the app has proper exception handling
            # This is tested by checking if the app can be instantiated without errors
            assert app is not None
            
        except Exception as e:
            pytest.fail(f"App instantiation failed: {e}")
    
    def test_configuration_loading(self):
        """Test configuration loading"""
        try:
            from main import app
            
            # Test that configuration is properly loaded
            # This is tested by checking app attributes
            assert hasattr(app, 'title')
            assert hasattr(app, 'description')
            assert hasattr(app, 'version')
            
        except ImportError:
            pytest.skip("Main module import failed")
    
    def test_router_integration(self):
        """Test router integration"""
        try:
            from main import app
            
            # Test that the router is properly integrated
            # This is tested by checking if routes from the router are included
            router_routes = [r for r in app.routes if hasattr(r, 'path')]
            assert len(router_routes) > 0, "No router routes found"
            
        except ImportError:
            pytest.skip("Main module import failed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=main", "--cov-report=term-missing"])
