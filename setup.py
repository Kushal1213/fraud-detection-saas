from setuptools import setup, find_packages

setup(
    name="fraud-detection",
    version="1.0.0",
    description="Temporal Motif-Aware Fraud Detection System",
    author="Kushal",
    url="https://github.com/Kushal1213/fraud-detection",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "torch>=2.0.0",
        "torch-geometric>=2.3.0",
        "torch-geometric-temporal>=0.54.0",
        "xgboost>=1.7.0",
        "shap>=0.42.0",
        "scikit-learn>=1.2.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "pyyaml>=6.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
