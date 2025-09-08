"""
API Documentation Service for frontend engineers
"""

import asyncio
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class APIDocumentationService:
    """Service for providing API documentation to frontend engineers"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_update = 0
        
        # Service endpoints for documentation discovery
        self.services = {
            "voice_service": {
                "url": "http://localhost:8011",
                "name": "Voice Service",
                "description": "Speech-to-text and text-to-speech capabilities",
                "endpoints": [
                    {
                        "path": "/api/voice/stt",
                        "method": "POST",
                        "description": "Convert speech to text",
                        "parameters": {
                            "audio_file": "Audio file (WAV, MP3, etc.)",
                            "language": "Language code (en, hi, bn, etc.)",
                            "model": "STT model to use"
                        },
                        "response": {
                            "text": "Transcribed text",
                            "confidence": "Confidence score",
                            "language": "Detected language"
                        }
                    },
                    {
                        "path": "/api/voice/tts",
                        "method": "POST",
                        "description": "Convert text to speech",
                        "parameters": {
                            "text": "Text to convert",
                            "language": "Language code",
                            "voice": "Voice model to use",
                            "speed": "Speech speed (0.5-2.0)"
                        },
                        "response": {
                            "audio_url": "URL to generated audio",
                            "duration": "Audio duration in seconds",
                            "format": "Audio format (WAV, MP3)"
                        }
                    },
                    {
                        "path": "/api/voice/models",
                        "method": "GET",
                        "description": "Get available voice models",
                        "parameters": {},
                        "response": {
                            "stt_models": "List of STT models",
                            "tts_models": "List of TTS models",
                            "languages": "Supported languages"
                        }
                    }
                ]
            },
            "community_service": {
                "url": "http://localhost:8012",
                "name": "Community Service",
                "description": "Social features and community management",
                "endpoints": [
                    {
                        "path": "/api/community/challenges",
                        "method": "GET",
                        "description": "Get community challenges",
                        "parameters": {
                            "category": "Challenge category",
                            "status": "Challenge status",
                            "limit": "Number of challenges to return"
                        },
                        "response": {
                            "challenges": "List of challenges",
                            "total": "Total number of challenges",
                            "categories": "Available categories"
                        }
                    },
                    {
                        "path": "/api/community/events",
                        "method": "GET",
                        "description": "Get community events",
                        "parameters": {
                            "date_from": "Start date",
                            "date_to": "End date",
                            "type": "Event type"
                        },
                        "response": {
                            "events": "List of events",
                            "total": "Total number of events"
                        }
                    },
                    {
                        "path": "/api/community/leaderboard",
                        "method": "GET",
                        "description": "Get community leaderboard",
                        "parameters": {
                            "period": "Time period (daily, weekly, monthly)",
                            "category": "Leaderboard category"
                        },
                        "response": {
                            "leaderboard": "List of top users",
                            "period": "Current period",
                            "user_rank": "Current user's rank"
                        }
                    }
                ]
            },
            "ml_service": {
                "url": "http://localhost:8013",
                "name": "ML Service",
                "description": "Machine learning and AI model management",
                "endpoints": [
                    {
                        "path": "/api/ml/models",
                        "method": "GET",
                        "description": "Get available ML models",
                        "parameters": {
                            "type": "Model type",
                            "status": "Model status"
                        },
                        "response": {
                            "models": "List of models",
                            "types": "Available model types"
                        }
                    },
                    {
                        "path": "/api/ml/performance",
                        "method": "GET",
                        "description": "Get model performance metrics",
                        "parameters": {
                            "model_id": "Model identifier",
                            "metric": "Performance metric"
                        },
                        "response": {
                            "metrics": "Performance metrics",
                            "history": "Historical performance"
                        }
                    },
                    {
                        "path": "/api/ml/predict",
                        "method": "POST",
                        "description": "Make predictions using ML models",
                        "parameters": {
                            "model_id": "Model to use",
                            "input_data": "Input data for prediction"
                        },
                        "response": {
                            "prediction": "Model prediction",
                            "confidence": "Prediction confidence",
                            "model_info": "Model information"
                        }
                    }
                ]
            },
            "models_service": {
                "url": "http://localhost:8085",
                "name": "Models Service",
                "description": "AI model training and deployment management",
                "endpoints": [
                    {
                        "path": "/api/models/status",
                        "method": "GET",
                        "description": "Get model training status",
                        "parameters": {
                            "model_type": "Type of model",
                            "status": "Training status"
                        },
                        "response": {
                            "models": "List of models",
                            "training_status": "Overall training status"
                        }
                    },
                    {
                        "path": "/api/models/training",
                        "method": "GET",
                        "description": "Get training progress",
                        "parameters": {
                            "model_id": "Model identifier"
                        },
                        "response": {
                            "progress": "Training progress percentage",
                            "eta": "Estimated time to completion",
                            "metrics": "Training metrics"
                        }
                    },
                    {
                        "path": "/api/models/deployment",
                        "method": "GET",
                        "description": "Get deployment status",
                        "parameters": {
                            "model_id": "Model identifier"
                        },
                        "response": {
                            "status": "Deployment status",
                            "version": "Model version",
                            "endpoints": "Available endpoints"
                        }
                    }
                ]
            },
            "auth_service": {
                "url": "http://localhost:8001",
                "name": "Authentication Service",
                "description": "User authentication and authorization",
                "endpoints": [
                    {
                        "path": "/api/auth/login",
                        "method": "POST",
                        "description": "User login",
                        "parameters": {
                            "email": "User email",
                            "password": "User password"
                        },
                        "response": {
                            "access_token": "JWT access token",
                            "refresh_token": "JWT refresh token",
                            "user": "User information"
                        }
                    },
                    {
                        "path": "/api/auth/register",
                        "method": "POST",
                        "description": "User registration",
                        "parameters": {
                            "email": "User email",
                            "password": "User password",
                            "name": "User name"
                        },
                        "response": {
                            "user_id": "Created user ID",
                            "message": "Success message"
                        }
                    },
                    {
                        "path": "/api/auth/refresh",
                        "method": "POST",
                        "description": "Refresh access token",
                        "parameters": {
                            "refresh_token": "JWT refresh token"
                        },
                        "response": {
                            "access_token": "New JWT access token",
                            "expires_in": "Token expiration time"
                        }
                    }
                ]
            }
        }
    
    async def initialize(self):
        """Initialize the service"""
        await self.update_documentation()
    
    async def cleanup(self):
        """Cleanup resources"""
        self.cache.clear()
    
    async def get_all_documentation(self) -> Dict[str, Any]:
        """Get complete API documentation for all services"""
        try:
            # Check cache
            current_time = datetime.now(timezone.utc).timestamp()
            if current_time - self.last_update < self.cache_ttl and self.cache:
                return self.cache.get("all_docs", {})
            
            # Generate comprehensive documentation
            docs = {
                "overview": {
                    "title": "MantraPath API Documentation",
                    "description": "Complete API reference for frontend engineers",
                    "version": "1.0.0",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_services": len(self.services),
                    "total_endpoints": sum(len(service["endpoints"]) for service in self.services.values())
                },
                "services": {},
                "authentication": {
                    "type": "JWT Bearer Token",
                    "header": "Authorization: Bearer <token>",
                    "token_expiry": "60 minutes",
                    "refresh_endpoint": "/api/auth/refresh"
                },
                "rate_limiting": {
                    "basic": "100 requests per minute",
                    "enhanced": "500 requests per minute",
                    "premium": "1000 requests per minute"
                },
                "error_codes": {
                    "400": "Bad Request - Invalid parameters",
                    "401": "Unauthorized - Invalid or missing token",
                    "403": "Forbidden - Insufficient permissions",
                    "404": "Not Found - Resource not found",
                    "429": "Too Many Requests - Rate limit exceeded",
                    "500": "Internal Server Error - Server error"
                },
                "best_practices": [
                    "Always include Authorization header",
                    "Handle rate limiting gracefully",
                    "Implement proper error handling",
                    "Use appropriate HTTP methods",
                    "Validate input data",
                    "Cache responses when possible"
                ]
            }
            
            # Add service documentation
            for service_id, service in self.services.items():
                docs["services"][service_id] = {
                    "name": service["name"],
                    "description": service["description"],
                    "url": service["url"],
                    "endpoints": service["endpoints"],
                    "examples": await self._generate_examples(service)
                }
            
            # Cache the documentation
            self.cache["all_docs"] = docs
            self.last_update = current_time
            
            return docs
            
        except Exception as e:
            return {
                "error": f"Failed to generate documentation: {str(e)}",
                "services": self.services
            }
    
    async def get_service_documentation(self, service_name: str) -> Dict[str, Any]:
        """Get API documentation for a specific service"""
        try:
            if service_name not in self.services:
                return {
                    "error": f"Service '{service_name}' not found",
                    "available_services": list(self.services.keys())
                }
            
            service = self.services[service_name]
            
            docs = {
                "service": {
                    "id": service_name,
                    "name": service["name"],
                    "description": service["description"],
                    "url": service["url"]
                },
                "endpoints": service["endpoints"],
                "examples": await self._generate_examples(service),
                "authentication": "JWT Bearer Token required",
                "rate_limiting": "Subject to engineer's permission level",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            return docs
            
        except Exception as e:
            return {
                "error": f"Failed to get {service_name} documentation: {str(e)}"
            }
    
    async def _generate_examples(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example requests and responses for a service"""
        examples = {}
        
        for endpoint in service["endpoints"]:
            path = endpoint["path"]
            method = endpoint["method"]
            
            # Generate example request
            request_example = {
                "method": method,
                "url": f"{service['url']}{path}",
                "headers": {
                    "Authorization": "Bearer <your_jwt_token>",
                    "Content-Type": "application/json"
                }
            }
            
            # Add body for POST/PUT requests
            if method in ["POST", "PUT"]:
                request_example["body"] = self._generate_sample_body(endpoint)
            
            # Generate example response
            response_example = {
                "status": 200,
                "body": endpoint["response"]
            }
            
            examples[path] = {
                "request": request_example,
                "response": response_example
            }
        
        return examples
    
    def _generate_sample_body(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample request body based on endpoint parameters"""
        sample_body = {}
        
        for param_name, param_desc in endpoint["parameters"].items():
            if "file" in param_name.lower():
                sample_body[param_name] = "<file_data>"
            elif "language" in param_name.lower():
                sample_body[param_name] = "en"
            elif "model" in param_name.lower():
                sample_body[param_name] = "default"
            elif "limit" in param_name.lower():
                sample_body[param_name] = 10
            elif "date" in param_name.lower():
                sample_body[param_name] = "2024-01-01"
            else:
                sample_body[param_name] = f"<{param_name}>"
        
        return sample_body
    
    async def test_endpoint(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific API endpoint"""
        try:
            service_name = request_data.get("service")
            endpoint_path = request_data.get("endpoint")
            method = request_data.get("method", "GET")
            test_data = request_data.get("data", {})
            
            if not service_name or not endpoint_path:
                return {
                    "error": "Missing service or endpoint information",
                    "required": ["service", "endpoint"]
                }
            
            if service_name not in self.services:
                return {
                    "error": f"Service '{service_name}' not found",
                    "available_services": list(self.services.keys())
                }
            
            # Find the endpoint
            endpoint = None
            for ep in self.services[service_name]["endpoints"]:
                if ep["path"] == endpoint_path:
                    endpoint = ep
                    break
            
            if not endpoint:
                return {
                    "error": f"Endpoint '{endpoint_path}' not found in {service_name}",
                    "available_endpoints": [ep["path"] for ep in self.services[service_name]["endpoints"]]
                }
            
            # Simulate endpoint testing
            test_result = {
                "service": service_name,
                "endpoint": endpoint_path,
                "method": method,
                "test_data": test_data,
                "expected_parameters": endpoint["parameters"],
                "expected_response": endpoint["response"],
                "test_status": "simulated",
                "message": "This is a simulated test. In production, this would make actual API calls."
            }
            
            return test_result
            
        except Exception as e:
            return {
                "error": f"Failed to test endpoint: {str(e)}"
            }
    
    async def search_documentation(self, query: str) -> Dict[str, Any]:
        """Search through API documentation"""
        try:
            results = []
            query_lower = query.lower()
            
            for service_id, service in self.services.items():
                # Search in service name and description
                if query_lower in service["name"].lower() or query_lower in service["description"].lower():
                    results.append({
                        "type": "service",
                        "service_id": service_id,
                        "name": service["name"],
                        "description": service["description"],
                        "relevance": "high"
                    })
                
                # Search in endpoints
                for endpoint in service["endpoints"]:
                    if (query_lower in endpoint["path"].lower() or 
                        query_lower in endpoint["description"].lower()):
                        results.append({
                            "type": "endpoint",
                            "service_id": service_id,
                            "service_name": service["name"],
                            "path": endpoint["path"],
                            "method": endpoint["method"],
                            "description": endpoint["description"],
                            "relevance": "medium"
                        })
            
            return {
                "query": query,
                "total_results": len(results),
                "results": results
            }
            
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "query": query,
                "results": []
            }

