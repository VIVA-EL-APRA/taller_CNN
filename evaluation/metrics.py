import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support
from sklearn.metrics import roc_auc_score, average_precision_score

class MetricsCalculator:
    @staticmethod
    def calculate_accuracy(predictions: np.ndarray, targets: np.ndarray) -> float:
        return float(accuracy_score(targets, predictions))
    
    @staticmethod
    def calculate_precision_recall_f1(
        predictions: np.ndarray,
        targets: np.ndarray,
        average: str = 'weighted'
    ) -> Tuple[float, float, float]:
        precision, recall, f1, _ = precision_recall_fscore_support(
            targets, predictions, average=average, zero_division=0
        )
        return float(precision), float(recall), float(f1)
    
    @staticmethod
    def calculate_per_class_accuracy(cm: np.ndarray) -> np.ndarray:
        return cm.diagonal() / cm.sum(axis=1)
    
    @staticmethod
    def calculate_top_k_accuracy(
        probabilities: np.ndarray,
        targets: np.ndarray,
        k: int = 5
    ) -> float:
        top_k_preds = np.argsort(probabilities, axis=1)[:, -k:]
        correct = 0
        for i, target in enumerate(targets):
            if target in top_k_preds[i]:
                correct += 1
        return correct / len(targets)
    
    @staticmethod
    def calculate_confidence_metrics(probabilities: np.ndarray, predictions: np.ndarray, targets: np.ndarray) -> Dict:
        confidences = np.max(probabilities, axis=1)
        correct_mask = predictions == targets
        
        return {
            'mean_confidence': float(np.mean(confidences)),
            'mean_confidence_correct': float(np.mean(confidences[correct_mask])) if correct_mask.sum() > 0 else 0.0,
            'mean_confidence_incorrect': float(np.mean(confidences[~correct_mask])) if (~correct_mask).sum() > 0 else 0.0,
            'confidence_std': float(np.std(confidences)),
        }
    
    @staticmethod
    def calculate_all_metrics(
        predictions: np.ndarray,
        targets: np.ndarray,
        probabilities: np.ndarray,
        classes: List[str]
    ) -> Dict:
        cm = confusion_matrix(targets, predictions)
        
        metrics = {
            'accuracy': MetricsCalculator.calculate_accuracy(predictions, targets),
            'precision_weighted': 0,
            'recall_weighted': 0,
            'f1_weighted': 0,
            'per_class_accuracy': {},
            'top_1_accuracy': float(np.mean(predictions == targets)),
            'top_5_accuracy': MetricsCalculator.calculate_top_k_accuracy(probabilities, targets, k=5) if probabilities.shape[1] >= 5 else 0,
        }
        
        precision, recall, f1 = MetricsCalculator.calculate_precision_recall_f1(
            predictions, targets, average='weighted'
        )
        metrics['precision_weighted'] = precision
        metrics['recall_weighted'] = recall
        metrics['f1_weighted'] = f1
        
        per_class_acc = MetricsCalculator.calculate_per_class_accuracy(cm)
        for i, cls in enumerate(classes):
            if i < len(per_class_acc):
                metrics['per_class_accuracy'][cls] = float(per_class_acc[i])
        
        metrics.update(
            MetricsCalculator.calculate_confidence_metrics(probabilities, predictions, targets)
        )
        
        return metrics
