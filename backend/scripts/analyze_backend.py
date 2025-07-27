"""
Backend Utilization Report Generator
Analyzes the MantraPath backend implementation and generates a comprehensive report
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class BackendAnalyzer:
    def __init__(self, backend_root: str):
        self.backend_root = Path(backend_root)
        self.services_dir = self.backend_root / "services"
        self.shared_dir = self.backend_root / "shared"
        
    def analyze_services(self) -> Dict[str, Any]:
        """Analyze all microservices"""
        services = {}
        
        for service_dir in self.services_dir.iterdir():
            if service_dir.is_dir() and (service_dir / "main.py").exists():
                service_name = service_dir.name
                services[service_name] = self.analyze_service(service_dir)
        
        return services
    
    def analyze_service(self, service_dir: Path) -> Dict[str, Any]:
        """Analyze individual service"""
        main_file = service_dir / "main.py"
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Count endpoints
        endpoints = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('@app.') and any(method in line for method in ['get', 'post', 'put', 'delete', 'patch']):
                endpoints.append(line)
        
        # Count lines of code
        loc = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
        
        # Check for key features
        features = {
            'authentication': 'get_current_user' in content or 'verify_token' in content,
            'database': 'Session = Depends(get_db)' in content,
            'caching': 'redis_client' in content,
            'background_tasks': 'BackgroundTasks' in content,
            'validation': 'BaseModel' in content,
            'error_handling': 'HTTPException' in content,
            'cors': 'CORSMiddleware' in content,
            'health_check': '/health' in content,
            'websockets': 'WebSocket' in content,
            'file_upload': 'UploadFile' in content
        }
        
        return {
            'endpoints_count': len(endpoints),
            'endpoints': endpoints[:10],  # Show first 10
            'lines_of_code': loc,
            'features': features,
            'has_dockerfile': (service_dir / "Dockerfile").exists(),
            'main_file_size': main_file.stat().st_size
        }
    
    def analyze_shared_modules(self) -> Dict[str, Any]:
        """Analyze shared modules"""
        shared_analysis = {}
        
        for module_file in self.shared_dir.glob("*.py"):
            if module_file.name == "__init__.py":
                continue
                
            with open(module_file, 'r') as f:
                content = f.read()
            
            loc = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
            
            shared_analysis[module_file.stem] = {
                'lines_of_code': loc,
                'file_size': module_file.stat().st_size,
                'exports': self.extract_exports(content)
            }
        
        return shared_analysis
    
    def extract_exports(self, content: str) -> List[str]:
        """Extract key exports from a module"""
        exports = []
        
        # Look for class definitions
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('class ') and '(' in line:
                class_name = line.split('class ')[1].split('(')[0].strip()
                exports.append(f"class {class_name}")
            elif line.startswith('def ') and not line.startswith('def _'):
                func_name = line.split('def ')[1].split('(')[0].strip()
                exports.append(f"function {func_name}")
        
        return exports[:10]  # Limit to first 10
    
    def check_route_utilization(self) -> Dict[str, Any]:
        """Check which documented routes are implemented"""
        
        # This would ideally parse the API documentation
        # For now, we'll check key routes manually
        documented_routes = {
            'auth_service': [
                'POST /register', 'POST /login', 'POST /logout',
                'POST /refresh-token', 'GET /me', 'POST /change-password'
            ],
            'mood_service': [
                'POST /api/v1/mood/', 'GET /api/v1/mood/',
                'POST /api/v1/journal/', 'GET /api/v1/journal/',
                'POST /api/v1/habits/', 'GET /api/v1/habits/',
                'GET /api/v1/analytics/overview'
            ],
            'community_service': [
                'GET /forums', 'POST /forums/thread',
                'POST /forums/like', 'GET /forums/search'
            ],
            'content_service': [
                'GET /content/feed', 'GET /affirmations/random',
                'POST /bookmark/{content_id}', 'GET /bookmarks'
            ],
            'chatbot_service': [
                'POST /api/chatbot/chat', 'GET /api/chatbot/chat/sessions',
                'GET /api/chatbot/chat/history'
            ],
            'notification_service': [
                'POST /notify/send', 'GET /notify/recent',
                'PUT /notify/preferences'
            ],
            'media_service': [
                'POST /api/v1/media/upload', 'GET /api/v1/media/',
                'GET /api/v1/media/{media_id}/file'
            ]
        }
        
        implementation_status = {}
        services = self.analyze_services()
        
        for service_name, routes in documented_routes.items():
            if service_name in services:
                implemented = services[service_name]['endpoints']
                implementation_status[service_name] = {
                    'total_documented': len(routes),
                    'estimated_implemented': len(implemented),
                    'sample_routes': routes[:5],
                    'sample_implemented': implemented[:5]
                }
            else:
                implementation_status[service_name] = {
                    'status': 'not_found'
                }
        
        return implementation_status
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive backend analysis report"""
        
        services = self.analyze_services()
        shared = self.analyze_shared_modules()
        utilization = self.check_route_utilization()
        
        # Calculate totals
        total_endpoints = sum(service['endpoints_count'] for service in services.values())
        total_loc = sum(service['lines_of_code'] for service in services.values())
        total_loc += sum(module['lines_of_code'] for module in shared.values())
        
        # Architecture assessment
        architecture_score = self.assess_architecture(services)
        
        return {
            'analysis_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_services': len(services),
                'total_endpoints': total_endpoints,
                'total_lines_of_code': total_loc,
                'architecture_score': architecture_score
            },
            'services': services,
            'shared_modules': shared,
            'route_utilization': utilization,
            'architecture_assessment': self.get_architecture_assessment(services),
            'recommendations': self.get_recommendations(services, utilization)
        }
    
    def assess_architecture(self, services: Dict[str, Any]) -> float:
        """Assess architecture quality (0-100)"""
        score = 0
        max_score = 0
        
        for service_name, service in services.items():
            # Check essential features
            features = service['features']
            
            # Essential features (10 points each)
            essential = ['authentication', 'database', 'error_handling', 'health_check', 'cors']
            for feature in essential:
                max_score += 10
                if features.get(feature, False):
                    score += 10
            
            # Good practices (5 points each)
            good_practices = ['caching', 'validation', 'background_tasks']
            for feature in good_practices:
                max_score += 5
                if features.get(feature, False):
                    score += 5
            
            # Deployment readiness
            max_score += 10
            if service.get('has_dockerfile', False):
                score += 10
        
        return round((score / max_score * 100) if max_score > 0 else 0, 1)
    
    def get_architecture_assessment(self, services: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed architecture assessment"""
        
        assessments = {}
        
        for service_name, service in services.items():
            features = service['features']
            
            strengths = []
            weaknesses = []
            
            # Check strengths
            if features.get('authentication'):
                strengths.append("Proper authentication integration")
            if features.get('caching'):
                strengths.append("Redis caching implemented")
            if features.get('background_tasks'):
                strengths.append("Background task processing")
            if features.get('validation'):
                strengths.append("Input validation with Pydantic")
            if service.get('has_dockerfile'):
                strengths.append("Docker containerization ready")
            
            # Check weaknesses
            if not features.get('health_check'):
                weaknesses.append("Missing health check endpoint")
            if not features.get('error_handling'):
                weaknesses.append("Limited error handling")
            if service['lines_of_code'] > 1000:
                weaknesses.append("Large service file - consider splitting")
            
            assessments[service_name] = {
                'strengths': strengths,
                'weaknesses': weaknesses,
                'complexity': 'High' if service['lines_of_code'] > 800 else 'Medium' if service['lines_of_code'] > 400 else 'Low'
            }
        
        return assessments
    
    def get_recommendations(self, services: Dict[str, Any], utilization: Dict[str, Any]) -> List[str]:
        """Get recommendations for improvement"""
        
        recommendations = []
        
        # Service-specific recommendations
        for service_name, service in services.items():
            if service['lines_of_code'] > 1000:
                recommendations.append(f"Consider splitting {service_name} into smaller modules")
            
            if not service['features'].get('caching'):
                recommendations.append(f"Add Redis caching to {service_name} for better performance")
        
        # General recommendations
        total_endpoints = sum(service['endpoints_count'] for service in services.values())
        if total_endpoints > 50:
            recommendations.append("Consider implementing API versioning for future scalability")
        
        recommendations.extend([
            "Add comprehensive API documentation with OpenAPI/Swagger",
            "Implement rate limiting on all endpoints",
            "Add monitoring and logging middleware",
            "Set up automated testing for all services",
            "Consider implementing circuit breakers for inter-service communication",
            "Add database connection pooling optimization",
            "Implement graceful shutdown handling"
        ])
        
        return recommendations[:10]  # Limit to top 10


def main():
    """Generate and save the backend utilization report"""
    
    backend_root = "/workspaces/spark-template/backend"
    analyzer = BackendAnalyzer(backend_root)
    
    print("🔍 Analyzing MantraPath Backend Implementation...")
    
    report = analyzer.generate_report()
    
    # Save report
    report_path = Path(backend_root) / "backend_utilization_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n📊 MANTRAPATH BACKEND UTILIZATION REPORT")
    print("=" * 50)
    
    summary = report['summary']
    print(f"🏗️  Total Services: {summary['total_services']}")
    print(f"🔗 Total Endpoints: {summary['total_endpoints']}")
    print(f"📝 Total Lines of Code: {summary['total_lines_of_code']:,}")
    print(f"🏆 Architecture Score: {summary['architecture_score']}/100")
    
    print("\n🚀 SERVICES OVERVIEW")
    print("-" * 30)
    for service_name, service in report['services'].items():
        print(f"{service_name.replace('_', ' ').title()}: {service['endpoints_count']} endpoints, {service['lines_of_code']} LOC")
    
    print("\n📋 ROUTE UTILIZATION")
    print("-" * 30)
    for service_name, util in report['route_utilization'].items():
        if 'total_documented' in util:
            print(f"{service_name}: ~{util['estimated_implemented']}/{util['total_documented']} routes implemented")
    
    print("\n🔧 TOP RECOMMENDATIONS")
    print("-" * 30)
    for i, rec in enumerate(report['recommendations'][:5], 1):
        print(f"{i}. {rec}")
    
    print(f"\n📄 Full report saved to: {report_path}")
    print("✅ Analysis complete!")

if __name__ == "__main__":
    main()