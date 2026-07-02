"""
Test script to validate the Fraud Detection SaaS project configuration.
This script checks if all necessary files and configurations are in place.
"""
import os
import sys
from pathlib import Path

# Set output encoding to UTF-8 for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_file_exists(filepath, description):
    """Check if a file exists and print the result."""
    exists = os.path.exists(filepath)
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {description}: {filepath}")
    return exists

def check_directory_exists(dirpath, description):
    """Check if a directory exists and print the result."""
    exists = os.path.isdir(dirpath)
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {description}: {dirpath}")
    return exists

def main():
    print("=" * 60)
    print("Fraud Detection SaaS - Project Validation")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check backend structure
    print("Backend Structure:")
    print("-" * 60)
    backend_dir = "backend"
    if check_directory_exists(backend_dir, "Backend directory"):
        backend_files = [
            f"{backend_dir}/requirements.txt",
            f"{backend_dir}/Dockerfile",
            f"{backend_dir}/app/__init__.py",
            f"{backend_dir}/app/main.py",
            f"{backend_dir}/app/config.py",
            f"{backend_dir}/app/database.py",
            f"{backend_dir}/app/models.py",
            f"{backend_dir}/app/schemas.py",
            f"{backend_dir}/app/auth.py",
            f"{backend_dir}/app/ml_service.py",
        ]
        for file in backend_files:
            if not check_file_exists(file, f"  - {Path(file).name}"):
                all_checks_passed = False
    else:
        all_checks_passed = False
    print()
    
    # Check frontend structure
    print("Frontend Structure:")
    print("-" * 60)
    frontend_dir = "frontend"
    if check_directory_exists(frontend_dir, "Frontend directory"):
        frontend_files = [
            f"{frontend_dir}/package.json",
            f"{frontend_dir}/vite.config.ts",
            f"{frontend_dir}/tsconfig.json",
            f"{frontend_dir}/Dockerfile",
            f"{frontend_dir}/nginx.conf",
            f"{frontend_dir}/index.html",
            f"{frontend_dir}/src/main.tsx",
            f"{frontend_dir}/src/App.tsx",
            f"{frontend_dir}/src/index.css",
        ]
        for file in frontend_files:
            if not check_file_exists(file, f"  - {Path(file).name}"):
                all_checks_passed = False
        
        # Check frontend subdirectories
        frontend_dirs = [
            f"{frontend_dir}/src/pages",
            f"{frontend_dir}/src/components",
            f"{frontend_dir}/src/api",
            f"{frontend_dir}/src/contexts",
        ]
        for dirpath in frontend_dirs:
            if not check_directory_exists(dirpath, f"  - {Path(dirpath).name}/"):
                all_checks_passed = False
    else:
        all_checks_passed = False
    print()
    
    # Check configuration files
    print("Configuration Files:")
    print("-" * 60)
    config_files = [
        "docker-compose.yml",
        "render.yaml",
        ".env.example",
        ".gitignore",
        "SAAS_README.md",
    ]
    for file in config_files:
        if not check_file_exists(file, f"  - {file}"):
            all_checks_passed = False
    print()
    
    # Check scripts
    print("Scripts:")
    print("-" * 60)
    script_files = [
        "scripts/generate_demo_data.py",
        "start_local.sh",
        "start_local.bat",
    ]
    for file in script_files:
        if not check_file_exists(file, f"  - {Path(file).name}"):
            all_checks_passed = False
    print()
    
    # Check demo data
    print("Demo Data:")
    print("-" * 60)
    demo_file = "demo_transactions.csv"
    if check_file_exists(demo_file, "Demo transactions file"):
        try:
            import pandas as pd
            df = pd.read_csv(demo_file)
            print(f"   [OK] Contains {len(df)} rows and {len(df.columns)} columns")
        except Exception as e:
            print(f"   [WARN] Could not read CSV: {e}")
    print()
    
    # Summary
    print("=" * 60)
    if all_checks_passed:
        print("[SUCCESS] All checks passed! Project is ready for deployment.")
        print()
        print("Next Steps:")
        print("1. For local testing with Docker:")
        print("   - Install Docker Desktop")
        print("   - Run: docker-compose up -d")
        print("   - Access: http://localhost")
        print()
        print("2. For deployment to Render:")
        print("   - Push code to GitHub")
        print("   - Create new Blueprint on render.com")
        print("   - Connect your repository")
        print("   - Deploy automatically from render.yaml")
        print()
        print("See SAAS_README.md for detailed instructions.")
    else:
        print("[FAILED] Some checks failed. Please review the output above.")
        print("Missing files or directories need to be created.")
    print("=" * 60)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
