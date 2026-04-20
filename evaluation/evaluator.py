import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_recall_fscore_support
import os
import json

class Evaluator:
    def __init__(
        self,
        model: nn.Module,
        test_loader: DataLoader,
        classes: List[str],
        device: Optional[torch.device] = None
    ):
        self.model = model.to(device or torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
        self.device = self.model.device if hasattr(self.model, 'device') else device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.test_loader = test_loader
        self.classes = classes
        self.all_predictions = []
        self.all_targets = []
        self.all_probs = []
    
    def predict(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        self.model.eval()
        all_preds = []
        all_targets = []
        all_probs = []
        
        with torch.no_grad():
            for inputs, targets in self.test_loader:
                inputs = inputs.to(self.device)
                outputs = self.model(inputs)
                probs = torch.softmax(outputs, dim=1)
                _, predicted = outputs.max(1)
                
                all_preds.extend(predicted.cpu().numpy())
                all_targets.extend(targets.numpy())
                all_probs.extend(probs.cpu().numpy())
        
        self.all_predictions = np.array(all_preds)
        self.all_targets = np.array(all_targets)
        self.all_probs = np.array(all_probs)
        
        return self.all_predictions, self.all_targets, self.all_probs
    
    def calculate_metrics(self) -> Dict:
        if len(self.all_predictions) == 0:
            self.predict()
        
        accuracy = accuracy_score(self.all_targets, self.all_predictions)
        precision, recall, f1, support = precision_recall_fscore_support(
            self.all_targets, self.all_predictions, average='weighted'
        )
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'num_samples': len(self.all_predictions)
        }
        
        return metrics
    
    def get_classification_report(self) -> str:
        if len(self.all_predictions) == 0:
            self.predict()
        
        return classification_report(
            self.all_targets,
            self.all_predictions,
            target_names=self.classes,
            digits=4
        )
    
    def get_confusion_matrix(self) -> np.ndarray:
        if len(self.all_predictions) == 0:
            self.predict()
        
        return confusion_matrix(self.all_targets, self.all_predictions)
    
    def plot_confusion_matrix(self, save_path: Optional[str] = None, figsize: Tuple[int, int] = (12, 10)):
        cm = self.get_confusion_matrix()
        
        plt.figure(figsize=figsize)
        sns.heatmap(
            cm,
            annot=False,
            fmt='d',
            cmap='Blues',
            xticklabels=self.classes,
            yticklabels=self.classes,
            cbar_kws={'label': 'Cantidad'}
        )
        plt.xlabel('Predicción', fontsize=12)
        plt.ylabel('Real', fontsize=12)
        plt.title('Matriz de Confusión', fontsize=14)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f'Matriz de confusión guardada en: {save_path}')
        else:
            plt.show()
        plt.close()
    
    def plot_per_class_accuracy(self, save_path: Optional[str] = None, figsize: Tuple[int, int] = (14, 6)):
        if len(self.all_predictions) == 0:
            self.predict()
        
        cm = self.get_confusion_matrix()
        class_accuracies = cm.diagonal() / cm.sum(axis=1)
        
        plt.figure(figsize=figsize)
        bars = plt.bar(range(len(self.classes)), class_accuracies, color='steelblue', edgecolor='black')
        
        for i, (bar, acc) in enumerate(zip(bars, class_accuracies)):
            if acc < 0.7:
                bar.set_color('coral')
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{acc:.2%}', ha='center', va='bottom', fontsize=8)
        
        plt.xlabel('Clase', fontsize=12)
        plt.ylabel('Accuracy', fontsize=12)
        plt.title('Accuracy por Clase', fontsize=14)
        plt.xticks(range(len(self.classes)), self.classes, rotation=45, ha='right')
        plt.ylim(0, 1.1)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
        plt.close()
    
    def plot_top_errors(self, n: int = 20, save_path: Optional[str] = None):
        if len(self.all_predictions) == 0:
            self.predict()
        
        errors_idx = np.where(self.all_predictions != self.all_targets)[0]
        
        if len(errors_idx) == 0:
            print('No se encontraron errores!')
            return
        
        error_confidences = self.all_probs[errors_idx]
        error_confidence = np.array([error_confidences[i][self.all_predictions[errors_idx[i]]] for i in range(len(errors_idx))])
        
        top_errors = np.argsort(error_confidence)[::-1][:n]
        
        print(f'\nTop {n} errores con mayor confianza:')
        print('-' * 60)
        for i, idx in enumerate(top_errors[:10]):
            error_idx = errors_idx[idx]
            print(f'{i+1}. Predicción: {self.classes[self.all_predictions[error_idx]]} '
                  f'(Conf: {error_confidence[idx]:.2%}) | '
                  f'Real: {self.classes[self.all_targets[error_idx]]}')
    
    def save_results(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        
        metrics = self.calculate_metrics()
        with open(os.path.join(output_dir, 'metrics.json'), 'w') as f:
            json.dump(metrics, f, indent=2)
        
        report = self.get_classification_report()
        with open(os.path.join(output_dir, 'classification_report.txt'), 'w') as f:
            f.write(report)
        
        np.save(os.path.join(output_dir, 'predictions.npy'), self.all_predictions)
        np.save(os.path.join(output_dir, 'targets.npy'), self.all_targets)
        np.save(os.path.join(output_dir, 'probabilities.npy'), self.all_probs)
        
        self.plot_confusion_matrix(os.path.join(output_dir, 'confusion_matrix.png'))
        self.plot_per_class_accuracy(os.path.join(output_dir, 'per_class_accuracy.png'))
        
        print(f'\nResultados guardados en: {output_dir}')
    
    def print_summary(self):
        metrics = self.calculate_metrics()
        print('\n' + '=' * 60)
        print('RESUMEN DE EVALUACION')
        print('=' * 60)
        acc = metrics["accuracy"]
        prec = metrics["precision"]
        rec = metrics["recall"]
        f1 = metrics["f1_score"]
        num = metrics["num_samples"]
        print(f'Accuracy: {acc:.4f} ({acc*100:.2f}%)')
        print(f'Precision (weighted): {prec:.4f}')
        print(f'Recall (weighted): {rec:.4f}')
        print(f'F1-Score (weighted): {f1:.4f}')
        print(f'Muestras evaluadas: {num}')
        print('=' * 60)
