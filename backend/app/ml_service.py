import random
import pandas as pd
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FraudDetectionService:
    """
    Simplified fraud detection service for demo purposes.
    Uses dummy predictions to demonstrate the SaaS functionality.
    """
    
    def __init__(self):
        logger.info("Initializing demo fraud detection service with dummy predictions")
    
    def predict_single(self, transaction_data: Dict) -> Dict:
        """Generate a dummy prediction for a single transaction."""
        fraud_prob = random.random() * 0.3  # Random probability between 0-0.3
        return {
            "fraud_probability": fraud_prob,
            "is_fraud": fraud_prob > 0.5,
            "confidence": self._get_confidence_level(fraud_prob)
        }
    
    def predict_batch(self, df: pd.DataFrame) -> Tuple[List[float], Dict]:
        """Generate dummy batch predictions for demo purposes."""
        n = len(df)
        fraud_probs = [random.random() * 0.3 for _ in range(n)]
        
        fraud_count = sum(1 for prob in fraud_probs if prob > 0.5)
        fraud_rate = fraud_count / n if n > 0 else 0
        avg_fraud_score = sum(fraud_probs) / n if n > 0 else 0
        
        metrics = {
            "total_transactions": n,
            "fraud_count": fraud_count,
            "fraud_rate": fraud_rate,
            "avg_fraud_score": avg_fraud_score
        }
        
        return fraud_probs, metrics
    
    def get_shap_explanation(self, transaction_data: Dict, top_n: int = 10) -> Dict:
        """Generate dummy SHAP explanation for demo purposes."""
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
