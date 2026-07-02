"""
Test script to validate backend Python imports.
This checks if all required packages can be imported.
"""
import sys

def test_imports():
    print("=" * 60)
    print("Backend Python Imports Test")
    print("=" * 60)
    print()
    
    packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("jose", "python-jose"),
        ("passlib", "Passlib"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
    ]
    
    failed_imports = []
    
    for package, display_name in packages:
        try:
            __import__(package)
            print(f"[OK] {display_name}")
        except ImportError as e:
            print(f"[FAIL] {display_name} - {e}")
            failed_imports.append(display_name)
    
    print()
    print("=" * 60)
    if not failed_imports:
        print("[SUCCESS] All core packages can be imported!")
        print()
        print("Note: ML packages (torch, torch-geometric, xgboost, shap)")
        print("are optional for the demo version and will use dummy predictions.")
    else:
        print(f"[FAILED] {len(failed_imports)} packages failed to import:")
        for pkg in failed_imports:
            print(f"  - {pkg}")
        print()
        print("Install missing packages:")
        print("pip install -r backend/requirements.txt")
    print("=" * 60)
    
    return 0 if not failed_imports else 1

if __name__ == "__main__":
    sys.exit(test_imports())
