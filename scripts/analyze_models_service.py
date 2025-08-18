#!/usr/bin/env python3
"""
MantraPath Models Service - Code Analysis and Structure Report
============================================================

This script analyzes the Models Service codebase structure, dependencies,
and generates a comprehensive report of the service architecture.

Usage:
    python analyze_models_service.py                 # Basic analysis
    python analyze_models_service.py --detailed      # Detailed analysis
    python analyze_models_service.py --export json   # Export to JSON
    python analyze_models_service.py --dependencies  # Analyze dependencies
"""

import os
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Analyzes Python code structure and metrics"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.tree = None
        self.content = ""
        self.lines = []
        
    def parse_file(self) -> bool:
        """Parse Python file and extract AST"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.lines = self.content.split('\n')
            
            self.tree = ast.parse(self.content)
            return True
        except Exception as e:
            logger.warning(f"Could not parse {self.file_path}: {e}")
            return False
    
    def get_imports(self) -> List[Dict[str, Any]]:
        """Extract imports from the file"""
        imports = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append({
                        "type": "from_import",
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno
                    })
        
        return imports
    
    def get_classes(self) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            "name": item.name,
                            "line": item.lineno,
                            "is_async": isinstance(item, ast.AsyncFunctionDef),
                            "args": len(item.args.args),
                            "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in item.decorator_list]
                        })
                
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                    "methods": methods,
                    "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node)
                })
        
        return classes
    
    def get_functions(self) -> List[Dict[str, Any]]:
        """Extract function definitions (not inside classes)"""
        functions = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip methods inside classes
                parent = getattr(node, 'parent', None)
                if any(isinstance(p, ast.ClassDef) for p in ast.walk(self.tree) 
                       if hasattr(p, 'body') and node in p.body):
                    continue
                
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "args": len(node.args.args),
                    "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node)
                })
        
        return functions
    
    def get_complexity_metrics(self) -> Dict[str, int]:
        """Calculate basic complexity metrics"""
        metrics = {
            "total_lines": len(self.lines),
            "code_lines": len([line for line in self.lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in self.lines if line.strip().startswith('#')]),
            "blank_lines": len([line for line in self.lines if not line.strip()]),
            "docstring_lines": self.content.count('"""') + self.content.count("'''"),
            "if_statements": len([node for node in ast.walk(self.tree) if isinstance(node, ast.If)]),
            "for_loops": len([node for node in ast.walk(self.tree) if isinstance(node, ast.For)]),
            "while_loops": len([node for node in ast.walk(self.tree) if isinstance(node, ast.While)]),
            "try_blocks": len([node for node in ast.walk(self.tree) if isinstance(node, ast.Try)]),
        }
        
        return metrics

class ModelsServiceAnalyzer:
    """Comprehensive analyzer for Models Service"""
    
    def __init__(self, service_path: Path):
        self.service_path = service_path
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "service_path": str(service_path),
            "overview": {},
            "directory_structure": {},
            "file_analysis": {},
            "dependencies": {},
            "architecture": {},
            "api_endpoints": {},
            "test_coverage": {},
            "recommendations": []
        }
    
    def analyze_directory_structure(self):
        """Analyze the directory structure"""
        logger.info("📂 Analyzing directory structure...")
        
        def build_tree(path: Path, max_depth: int = 4, current_depth: int = 0) -> Dict:
            if current_depth >= max_depth:
                return {}
            
            tree = {}
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_dir():
                        tree[item.name + "/"] = build_tree(item, max_depth, current_depth + 1)
                    else:
                        tree[item.name] = {
                            "size": item.stat().st_size,
                            "extension": item.suffix,
                            "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        }
            except PermissionError:
                pass
            
            return tree
        
        self.analysis_results["directory_structure"] = build_tree(self.service_path)
    
    def analyze_python_files(self):
        """Analyze all Python files in the service"""
        logger.info("🐍 Analyzing Python files...")
        
        python_files = list(self.service_path.rglob("*.py"))
        
        total_metrics = {
            "files": 0,
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "classes": 0,
            "functions": 0,
            "async_functions": 0,
            "imports": 0
        }
        
        for py_file in python_files:
            try:
                rel_path = py_file.relative_to(self.service_path)
                analyzer = CodeAnalyzer(py_file)
                
                if not analyzer.parse_file():
                    continue
                
                imports = analyzer.get_imports()
                classes = analyzer.get_classes()
                functions = analyzer.get_functions()
                metrics = analyzer.get_complexity_metrics()
                
                file_info = {
                    "path": str(rel_path),
                    "size": py_file.stat().st_size,
                    "imports": imports,
                    "classes": classes,
                    "functions": functions,
                    "metrics": metrics,
                    "complexity_score": self._calculate_complexity_score(metrics, classes, functions)
                }
                
                self.analysis_results["file_analysis"][str(rel_path)] = file_info
                
                # Update totals
                total_metrics["files"] += 1
                total_metrics["total_lines"] += metrics["total_lines"]
                total_metrics["code_lines"] += metrics["code_lines"]
                total_metrics["comment_lines"] += metrics["comment_lines"]
                total_metrics["classes"] += len(classes)
                total_metrics["functions"] += len(functions)
                total_metrics["async_functions"] += len([f for f in functions if f["is_async"]])
                total_metrics["imports"] += len(imports)
                
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
        
        self.analysis_results["overview"]["code_metrics"] = total_metrics
    
    def _calculate_complexity_score(self, metrics: Dict, classes: List, functions: List) -> float:
        """Calculate a simple complexity score for a file"""
        base_score = metrics["total_lines"] / 100.0
        complexity_factor = (metrics["if_statements"] + metrics["for_loops"] + 
                           metrics["while_loops"] + metrics["try_blocks"]) / 10.0
        structure_factor = (len(classes) + len(functions)) / 5.0
        
        return base_score + complexity_factor + structure_factor
    
    def analyze_dependencies(self):
        """Analyze project dependencies"""
        logger.info("📦 Analyzing dependencies...")
        
        # Analyze requirements.txt
        req_file = self.service_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    requirements = f.read().strip().split('\n')
                
                deps = []
                for req in requirements:
                    req = req.strip()
                    if req and not req.startswith('#'):
                        if '==' in req:
                            name, version = req.split('==', 1)
                            deps.append({"name": name, "version": version, "constraint": "exact"})
                        elif '>=' in req:
                            name, version = req.split('>=', 1)
                            deps.append({"name": name, "version": version, "constraint": "minimum"})
                        else:
                            deps.append({"name": req, "version": None, "constraint": "any"})
                
                self.analysis_results["dependencies"]["requirements"] = {
                    "total": len(deps),
                    "packages": deps
                }
                
            except Exception as e:
                logger.warning(f"Error analyzing requirements.txt: {e}")
        
        # Analyze imports to find internal vs external dependencies
        all_imports = set()
        for file_analysis in self.analysis_results["file_analysis"].values():
            for imp in file_analysis["imports"]:
                module = imp.get("module", "")
                if module:
                    all_imports.add(module.split('.')[0])
        
        # Categorize imports
        internal_modules = set()
        external_modules = set()
        
        for module in all_imports:
            if any(file_path.startswith(module) for file_path in self.analysis_results["file_analysis"].keys()):
                internal_modules.add(module)
            else:
                external_modules.add(module)
        
        self.analysis_results["dependencies"]["imports"] = {
            "total_unique_imports": len(all_imports),
            "internal_modules": sorted(list(internal_modules)),
            "external_modules": sorted(list(external_modules))
        }
    
    def analyze_architecture(self):
        """Analyze service architecture patterns"""
        logger.info("🏗️ Analyzing architecture patterns...")
        
        architecture = {
            "service_type": "FastAPI Microservice",
            "patterns": [],
            "components": {},
            "api_structure": {},
            "async_usage": 0,
            "database_usage": False,
            "caching_usage": False,
            "monitoring_usage": False
        }
        
        # Analyze main components
        main_file = self.service_path / "main.py"
        if main_file.exists():
            main_analysis = self.analysis_results["file_analysis"].get("main.py", {})
            architecture["components"]["main"] = {
                "classes": len(main_analysis.get("classes", [])),
                "functions": len(main_analysis.get("functions", [])),
                "lines": main_analysis.get("metrics", {}).get("total_lines", 0)
            }
        
        # Count async functions
        total_async = 0
        for file_analysis in self.analysis_results["file_analysis"].values():
            total_async += len([f for f in file_analysis.get("functions", []) if f.get("is_async")])
        architecture["async_usage"] = total_async
        
        # Check for common patterns
        all_imports = []
        for file_analysis in self.analysis_results["file_analysis"].values():
            all_imports.extend([imp.get("module", "") for imp in file_analysis.get("imports", [])])
        
        if "fastapi" in all_imports:
            architecture["patterns"].append("FastAPI REST API")
        if "asyncio" in all_imports:
            architecture["patterns"].append("Asynchronous Programming")
        if "pydantic" in all_imports:
            architecture["patterns"].append("Data Validation")
        if "sqlalchemy" in all_imports or "sqlite" in all_imports:
            architecture["database_usage"] = True
            architecture["patterns"].append("Database Integration")
        if "redis" in all_imports or "cache" in " ".join(all_imports).lower():
            architecture["caching_usage"] = True
            architecture["patterns"].append("Caching")
        if "prometheus" in all_imports or "logging" in all_imports:
            architecture["monitoring_usage"] = True
            architecture["patterns"].append("Monitoring/Logging")
        
        self.analysis_results["architecture"] = architecture
    
    def analyze_api_endpoints(self):
        """Analyze API endpoints structure"""
        logger.info("🌐 Analyzing API endpoints...")
        
        endpoints = {
            "total_routes": 0,
            "route_methods": {},
            "route_patterns": [],
            "documented_routes": 0
        }
        
        # Look for route definitions
        for file_path, file_analysis in self.analysis_results["file_analysis"].items():
            if "route" in file_path.lower() or "api" in file_path.lower():
                functions = file_analysis.get("functions", [])
                for func in functions:
                    if func.get("decorators"):
                        for decorator in func["decorators"]:
                            if "router." in str(decorator) or "app." in str(decorator):
                                endpoints["total_routes"] += 1
                                if func.get("docstring"):
                                    endpoints["documented_routes"] += 1
        
        self.analysis_results["api_endpoints"] = endpoints
    
    def analyze_test_coverage(self):
        """Analyze test files and coverage"""
        logger.info("🧪 Analyzing test coverage...")
        
        test_dir = self.service_path / "tests"
        test_files = []
        
        if test_dir.exists():
            test_files = list(test_dir.glob("test_*.py"))
        
        coverage = {
            "test_files_count": len(test_files),
            "test_functions": 0,
            "test_classes": 0,
            "coverage_files": []
        }
        
        for test_file in test_files:
            rel_path = test_file.relative_to(self.service_path)
            if str(rel_path) in self.analysis_results["file_analysis"]:
                file_analysis = self.analysis_results["file_analysis"][str(rel_path)]
                coverage["test_functions"] += len([f for f in file_analysis.get("functions", []) 
                                                 if f["name"].startswith("test_")])
                coverage["test_classes"] += len([c for c in file_analysis.get("classes", [])
                                               if c["name"].startswith("Test")])
                coverage["coverage_files"].append(str(rel_path))
        
        # Look for coverage reports
        coverage_files = list(self.service_path.glob("*coverage*")) + list(self.service_path.glob("htmlcov/"))
        coverage["has_coverage_reports"] = len(coverage_files) > 0
        
        self.analysis_results["test_coverage"] = coverage
    
    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        logger.info("💡 Generating recommendations...")
        
        recommendations = []
        
        # Code quality recommendations
        total_lines = self.analysis_results["overview"]["code_metrics"]["total_lines"]
        total_functions = self.analysis_results["overview"]["code_metrics"]["functions"]
        
        if total_lines > 5000:
            recommendations.append({
                "type": "code_organization",
                "priority": "medium",
                "message": f"Large codebase ({total_lines} lines). Consider modularization."
            })
        
        if total_functions > 100:
            recommendations.append({
                "type": "code_organization", 
                "priority": "low",
                "message": f"Many functions ({total_functions}). Ensure good organization."
            })
        
        # Test coverage recommendations
        test_functions = self.analysis_results["test_coverage"]["test_functions"]
        if test_functions < 10:
            recommendations.append({
                "type": "testing",
                "priority": "high", 
                "message": f"Low test coverage ({test_functions} test functions). Add more tests."
            })
        
        # Documentation recommendations
        documented_routes = self.analysis_results["api_endpoints"].get("documented_routes", 0)
        total_routes = self.analysis_results["api_endpoints"].get("total_routes", 0)
        
        if total_routes > 0 and documented_routes / total_routes < 0.8:
            recommendations.append({
                "type": "documentation",
                "priority": "medium",
                "message": f"API documentation incomplete ({documented_routes}/{total_routes} routes documented)."
            })
        
        # Architecture recommendations
        async_usage = self.analysis_results["architecture"]["async_usage"]
        if async_usage > 0:
            recommendations.append({
                "type": "performance",
                "priority": "info",
                "message": f"Good use of async programming ({async_usage} async functions)."
            })
        
        self.analysis_results["recommendations"] = recommendations
    
    def run_full_analysis(self):
        """Run complete analysis"""
        logger.info(f"🔍 Starting comprehensive analysis of Models Service: {self.service_path}")
        
        self.analyze_directory_structure()
        self.analyze_python_files()
        self.analyze_dependencies()
        self.analyze_architecture() 
        self.analyze_api_endpoints()
        self.analyze_test_coverage()
        self.generate_recommendations()
        
        logger.info("✅ Analysis complete!")
        return self.analysis_results
    
    def print_summary(self):
        """Print analysis summary"""
        results = self.analysis_results
        
        print("\n" + "=" * 60)
        print("📊 MODELS SERVICE ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Overview
        metrics = results["overview"]["code_metrics"]
        print(f"\n📈 CODE METRICS:")
        print(f"   Files: {metrics['files']}")
        print(f"   Total Lines: {metrics['total_lines']}")
        print(f"   Code Lines: {metrics['code_lines']}")
        print(f"   Classes: {metrics['classes']}")
        print(f"   Functions: {metrics['functions']}")
        print(f"   Async Functions: {metrics['async_functions']}")
        
        # Dependencies
        deps = results["dependencies"]
        if "requirements" in deps:
            print(f"\n📦 DEPENDENCIES:")
            print(f"   Required Packages: {deps['requirements']['total']}")
        
        imports = deps.get("imports", {})
        print(f"   External Modules: {len(imports.get('external_modules', []))}")
        print(f"   Internal Modules: {len(imports.get('internal_modules', []))}")
        
        # Architecture
        arch = results["architecture"]
        print(f"\n🏗️ ARCHITECTURE:")
        print(f"   Service Type: {arch['service_type']}")
        print(f"   Patterns: {', '.join(arch['patterns'])}")
        print(f"   Async Functions: {arch['async_usage']}")
        print(f"   Database: {'Yes' if arch['database_usage'] else 'No'}")
        print(f"   Caching: {'Yes' if arch['caching_usage'] else 'No'}")
        
        # API
        api = results["api_endpoints"]
        print(f"\n🌐 API ENDPOINTS:")
        print(f"   Total Routes: {api['total_routes']}")
        print(f"   Documented: {api['documented_routes']}")
        
        # Tests
        tests = results["test_coverage"]
        print(f"\n🧪 TESTING:")
        print(f"   Test Files: {tests['test_files_count']}")
        print(f"   Test Functions: {tests['test_functions']}")
        print(f"   Coverage Reports: {'Yes' if tests['has_coverage_reports'] else 'No'}")
        
        # Recommendations
        recommendations = results["recommendations"]
        print(f"\n💡 RECOMMENDATIONS:")
        if recommendations:
            for rec in recommendations:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢", "info": "ℹ️"}
                icon = priority_icon.get(rec["priority"], "•")
                print(f"   {icon} {rec['message']}")
        else:
            print("   ✅ No major issues found!")

def main():
    parser = argparse.ArgumentParser(description="Analyze Models Service code structure")
    parser.add_argument("--path", help="Path to models service directory")
    parser.add_argument("--detailed", action="store_true", help="Show detailed analysis")
    parser.add_argument("--export", choices=["json"], help="Export format")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--dependencies", action="store_true", help="Focus on dependency analysis")
    
    args = parser.parse_args()
    
    # Find models service directory
    if args.path:
        service_path = Path(args.path)
    else:
        # Try to find it relative to script location
        script_dir = Path(__file__).parent
        service_path = script_dir.parent / "backend" / "services" / "models_service"
        
        if not service_path.exists():
            logger.error(f"Models service directory not found: {service_path}")
            logger.info("Please specify path with --path argument")
            return 1
    
    if not service_path.exists():
        logger.error(f"Directory does not exist: {service_path}")
        return 1
    
    try:
        analyzer = ModelsServiceAnalyzer(service_path)
        results = analyzer.run_full_analysis()
        
        if args.export == "json":
            output_file = args.output or f"models_service_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"📄 Analysis exported to: {output_file}")
        
        analyzer.print_summary()
        
        if args.detailed:
            print("\n" + "=" * 60)
            print("📋 DETAILED ANALYSIS")
            print("=" * 60)
            print(json.dumps(results, indent=2, default=str))
        
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
