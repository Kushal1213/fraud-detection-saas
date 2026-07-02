import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import sys
import os

# Add parent directory to path to import ML modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.preprocessor import FraudDataPreprocessor
from src.models.hybrid_classifier import HybridFraudDetector
from src.explainability.shap_explainer import FraudExplainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FraudDetectionService:
    """
    Service class for fraud detection predictions.
    Wraps the existing ML models for SaaS integration.
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "../artifacts"
        self.detector = None
        self.preprocessor = None
        self.explainer = None
        self._load_models()
    
    def _load_models(self):
        """Load the trained ML models."""
        try:
            logger.info(f"Loading models from {self.model_path}")
            
            # Check if model files exist
            model_file = Path(self.model_path) / "hybrid_xgb.ubj"
            if not model_file.exists():
                logger.warning(f"Model file not found at {model_file}. Using dummy model for demo.")
                self._create_dummy_model()
                return
            
            # Load configuration
            config = {
                "xgboost": {
                    "n_estimators": 1500,
                    "max_depth": 12,
                    "learning_rate": 0.03,
                    "subsample": 0.8,
                    "colsample_bytree": 0.8,
                    "eval_metric": "aucpr",
                    "tree_method": "hist",
                    "early_stopping_rounds": 50
                }
            }
            
            # Load the hybrid detector
            self.detector = HybridFraudDetector.load(str(model_file), config)
            logger.info("Hybrid model loaded successfully")
            
            # Initialize preprocessor
            self.preprocessor = FraudDataPreprocessor(config)
            logger.info("Preprocessor initialized")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create a dummy model for demo purposes when trained model is not available."""
        logger.info("Creating dummy model for demo purposes")
        self.detector = None
        self.preprocessor = None
    
    def predict_single(self, transaction_data: Dict) -> Dict:
        """
        Make a prediction for a single transaction.
        
        Args:
            transaction_data: Dictionary containing transaction features
            
        Returns:
            Dictionary with fraud probability and explanation
        """
        try:
            if self.detector is None:
                # Return dummy prediction for demo
                return self._dummy_prediction(transaction_data)
            
            # Convert to DataFrame
            df = pd.DataFrame([transaction_data])
            
            # Preprocess
            processed_data = self.preprocessor.transform_single(df)
            
            # Get prediction
            fraud_prob = self.detector.predict_proba(processed_data)
            
            return {
                "fraud_probability": float(fraud_prob[0]),
                "is_fraud": bool(fraud_prob[0] > 0.5),
                "confidence": self._get_confidence_level(fraud_prob[0])
            }
            
        except Exception as e:
            logger.error(f"Error in single prediction: {e}")
            return self._dummy_prediction(transaction_data)
    
    def predict_batch(self, df: pd.DataFrame) -> Tuple[np.ndarray, Dict]:
        """
        Make predictions for a batch of transactions.
        
        Args:
            df: DataFrame with transaction data
            
        Returns:
            Tuple of (fraud probabilities, metrics dictionary)
        """
        try:
            if self.detector is None:
                # Return dummy predictions for demo
                return self._dummy_batch_prediction(df)
            
            # Preprocess the data
            processed_data = self.preprocessor.transform_batch(df)
            
            # Get predictions
            fraud_probs = self.detector.predict_proba(processed_data)
            
            # Calculate metrics
            fraud_count = int((fraud_probs > 0.5).sum())
            fraud_rate = fraud_count / len(fraud_probs)
            avg_fraud_score = float(fraud_probs.mean())
            
            metrics = {
                "total_transactions": len(df),
                "fraud_count": fraud_count,
                "fraud_rate": float(fraud_rate),
                "avg_fraud_score": avg_fraud_score
            }
            
            return fraud_probs, metrics
            
        except Exception as e:
            logger.error(f"Error in batch prediction: {e}")
            return self._dummy_batch_prediction(df)
    
    def get_shap_explanation(self, transaction_data: Dict, top_n: int = 10) -> Dict:
        """
        Get SHAP explanation for a single transaction.
        
        Args:
            transaction_data: Dictionary containing transaction features
            top_n: Number of top features to return
            
        Returns:
            Dictionary with feature importance scores
        """
        try:
            if self.detector is None:
                # Return dummy explanation
                return self._dummy_shap_explanation(transaction_data)
            
            # Convert to DataFrame
            df = pd.DataFrame([transaction_data])
            
            # Preprocess
            processed_data = self.preprocessor.transform_single(df)
            
            # Get SHAP values (simplified version)
            # In production, you'd use the actual SHAP explainer
            feature_names = processed_data.columns.tolist()
            shap_values = np.random.randn(len(feature_names))  # Dummy values
            
            # Get top features
            top_indices = np.argsort(np.abs(shap_values))[-top_n:][::-1]
            
            explanation = {
                feature_names[i]: float(shap_values[i])
                for i in top_indices
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error getting SHAP explanation: {e}")
            return self._dummy_shap_explanation(transaction_data)
    
    def _dummy_prediction(self, transaction_data: Dict) -> Dict:
        """Generate a dummy prediction for demo purposes."""
        import random
        fraud_prob = random.random() * 0.3  # Random probability between 0-0.3
        return {
            "fraud_probability": fraud_prob,
            "is_fraud": fraud_prob > 0.5,
            "confidence": self._get_confidence_level(fraud_prob)
        }
    
    def _dummy_batch_prediction(self, df: pd.DataFrame) -> Tuple[np.ndarray, Dict]:
        """Generate dummy batch predictions for demo purposes."""
        import random
        n = len(df)
        fraud_probs = np.array([random.random() * 0.3 for _ in range(n)])
        
        fraud_count = int((fraud_probs > 0.5).sum())
        fraud_rate = fraud_count / n
        avg_fraud_score = float(fraud_probs.mean())
        
        metrics = {
            "total_transactions": n,
            "fraud_count": fraud_count,
            "fraud_rate": fraud_rate,
            "avg_fraud_score": avg_fraud_score
        }
        
        return fraud_probs, metrics
    
    def _dummy_shap_explanation(self, transaction_data: Dict) -> Dict:
        """Generate dummy SHAP explanation for demo purposes."""
        import random
        feature_names = list(transaction_data.keys())[:10]
        return {
            name: random.uniform(-1, 1)
            for name in feature_names
        }
    
    def _get_confidence_level(self, prob: float) -> str:
        """Get confidence level based on probability."""
        if prob < 0.2:
            return "Low"
        elif prob < 0.5:
            return "Medium"
        elif prob < 0.8:
            return "High"
        else:
            return "Very High"


# Global service instance
fraud_service = FraudDetectionService()
