"""
Check if the project is fully ready for Render deployment.
This validates all configurations, files, and settings needed for Render.
"""
import os
import sys
import yaml
from pathlib import Path

# Set output encoding to UTF-8 for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_render_readiness():
    print("=" * 70)
    print("RENDER DEPLOYMENT READINESS CHECK")
    print("=" * 70)
    print()
    
    all_checks_passed = True
    warnings = []
    
    # 1. Check render.yaml exists and is valid
    print("1. Render Configuration (render.yaml)")
    print("-" * 70)
    if os.path.exists("render.yaml"):
        try:
            with open("render.yaml", 'r') as f:
                render_config = yaml.safe_load(f)
            print("[OK] render.yaml exists and is valid YAML")
            
            # Check services
            if 'services' in render_config:
                services = render_config['services']
                print(f"[OK] Found {len(services)} service(s) defined")
                
                service_names = [s.get('name', 'unnamed') for s in services]
                print(f"     Services: {', '.join(service_names)}")
                
                # Check for required services
                has_db = any('db' in s.get('name', '').lower() for s in services)
                has_redis = any('redis' in s.get('name', '').lower() for s in services)
                has_backend = any('backend' in s.get('name', '').lower() for s in services)
                has_frontend = any('frontend' in s.get('name', '').lower() for s in services)
                
                print(f"[OK] Database service: {'Yes' if has_db else 'No'}")
                print(f"[OK] Redis service: {'Yes' if has_redis else 'No'}")
                print(f"[OK] Backend service: {'Yes' if has_backend else 'No'}")
                print(f"[OK] Frontend service: {'Yes' if has_frontend else 'No'}")
                
                if not has_backend or not has_frontend:
                    warnings.append("Missing backend or frontend service in render.yaml")
            else:
                print("[FAIL] No services defined in render.yaml")
                all_checks_passed = False
        except Exception as e:
            print(f"[FAIL] Error parsing render.yaml: {e}")
            all_checks_passed = False
    else:
        print("[FAIL] render.yaml not found")
        all_checks_passed = False
    print()
    
    # 2. Check backend structure
    print("2. Backend Structure")
    print("-" * 70)
    backend_files = [
        "backend/requirements.txt",
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/database.py",
        "backend/app/models.py",
        "backend/app/schemas.py",
        "backend/app/auth.py",
        "backend/app/ml_service.py",
    ]
    
    for file in backend_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[FAIL] {file} missing")
            all_checks_passed = False
    print()
    
    # 3. Check frontend structure
    print("3. Frontend Structure")
    print("-" * 70)
    frontend_files = [
        "frontend/package.json",
        "frontend/vite.config.ts",
        "frontend/index.html",
        "frontend/src/main.tsx",
        "frontend/src/App.tsx",
    ]
    
    for file in frontend_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[FAIL] {file} missing")
            all_checks_passed = False
    print()
    
    # 4. Check backend requirements
    print("4. Backend Requirements")
    print("-" * 70)
    if os.path.exists("backend/requirements.txt"):
        with open("backend/requirements.txt", 'r') as f:
            requirements = f.read()
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "psycopg2-binary",
            "pydantic",
            "python-jose",
            "passlib",
        ]
        
        for package in required_packages:
            if package.lower() in requirements.lower():
                print(f"[OK] {package}")
            else:
                print(f"[WARN] {package} might be missing")
                warnings.append(f"{package} might be missing from requirements.txt")
    else:
        print("[FAIL] requirements.txt not found")
        all_checks_passed = False
    print()
    
    # 5. Check frontend package.json
    print("5. Frontend Package Configuration")
    print("-" * 70)
    if os.path.exists("frontend/package.json"):
        try:
            import json
            with open("frontend/package.json", 'r') as f:
                package_config = json.load(f)
            
            print(f"[OK] package.json is valid JSON")
            print(f"[OK] Project name: {package_config.get('name', 'N/A')}")
            
            # Check for build script
            scripts = package_config.get('scripts', {})
            if 'build' in scripts:
                print(f"[OK] Build script found: {scripts['build']}")
            else:
                print("[FAIL] No build script in package.json")
                all_checks_passed = False
            
            # Check for dependencies
            deps = package_config.get('dependencies', {})
            print(f"[OK] Found {len(deps)} dependencies")
            
            required_deps = ['react', 'react-dom', 'react-router-dom']
            for dep in required_deps:
                if dep in deps:
                    print(f"[OK] {dep}")
                else:
                    print(f"[WARN] {dep} might be missing")
                    warnings.append(f"{dep} might be missing from package.json")
                    
        except Exception as e:
            print(f"[FAIL] Error parsing package.json: {e}")
            all_checks_passed = False
    else:
        print("[FAIL] package.json not found")
        all_checks_passed = False
    print()
    
    # 6. Check .gitignore
    print("6. Git Configuration")
    print("-" * 70)
    if os.path.exists(".gitignore"):
        print("[OK] .gitignore exists")
        
        with open(".gitignore", 'r') as f:
            gitignore = f.read()
        
        important_excludes = [
            "node_modules/",
            ".env",
            "__pycache__/",
            "*.pyc",
            "dist/",
        ]
        
        for item in important_excludes:
            if item in gitignore:
                print(f"[OK] {item} is in .gitignore")
            else:
                print(f"[WARN] {item} might not be in .gitignore")
    else:
        print("[WARN] .gitignore not found (recommended)")
        warnings.append(".gitignore not found")
    print()
    
    # 7. Check for README
    print("7. Documentation")
    print("-" * 70)
    if os.path.exists("README.md") or os.path.exists("SAAS_README.md"):
        print("[OK] README file exists")
    else:
        print("[WARN] No README file found (recommended)")
        warnings.append("No README file found")
    print()
    
    # 8. Check for environment example
    print("8. Environment Configuration")
    print("-" * 70)
    if os.path.exists(".env.example"):
        print("[OK] .env.example exists")
        with open(".env.example", 'r') as f:
            env_example = f.read()
        
        important_vars = ["DATABASE_URL", "SECRET_KEY", "REDIS_URL"]
        for var in important_vars:
            if var in env_example:
                print(f"[OK] {var} documented")
            else:
                print(f"[WARN] {var} might not be documented")
    else:
        print("[WARN] .env.example not found (recommended)")
        warnings.append(".env.example not found")
    print()
    
    # 9. Check database configuration
    print("9. Database Configuration")
    print("-" * 70)
    if os.path.exists("backend/app/database.py"):
        with open("backend/app/database.py", 'r') as f:
            db_config = f.read()
        
        if "sqlite" in db_config.lower():
            print("[OK] SQLite support configured (good for fallback)")
        if "postgresql" in db_config.lower() or "postgres" in db_config.lower():
            print("[OK] PostgreSQL support configured")
    else:
        print("[FAIL] database.py not found")
        all_checks_passed = False
    print()
    
    # 10. Final summary
    print("=" * 70)
    print("DEPLOYMENT READINESS SUMMARY")
    print("=" * 70)
    
    if all_checks_passed and not warnings:
        print("[SUCCESS] Project is fully ready for Render deployment!")
        print()
        print("Next steps:")
        print("1. Initialize git repository: git init")
        print("2. Add all files: git add .")
        print("3. Commit: git commit -m 'Initial commit'")
        print("4. Push to GitHub")
        print("5. Go to render.com and create Blueprint")
        print("6. Connect your GitHub repository")
        print("7. Deploy automatically from render.yaml")
    elif all_checks_passed and warnings:
        print("[SUCCESS] Project is ready for deployment with minor warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
        print("You can proceed with deployment, but consider addressing warnings.")
    else:
        print("[FAILED] Project needs fixes before deployment:")
        print("Please address the [FAIL] items above.")
    
    print("=" * 70)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(check_render_readiness())
