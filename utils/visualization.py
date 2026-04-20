import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import torch
from typing import List, Optional, Tuple
import os

class Visualizer:
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        try:
            plt.style.use(style)
        except:
            plt.style.use('ggplot')
        sns.set_palette('husl')
    
    @staticmethod
    def plot_training_history(
        history: dict,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (15, 5)
    ):
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        epochs = history['epoch']
        
        axes[0].plot(epochs, history['train_loss'], 'b-', label='Train Loss', linewidth=2)
        axes[0].plot(epochs, history['test_loss'], 'r-', label='Test Loss', linewidth=2)
        axes[0].set_xlabel('Época')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Loss durante Entrenamiento')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        axes[1].plot(epochs, history['train_acc'], 'b-', label='Train Acc', linewidth=2)
        axes[1].plot(epochs, history['test_acc'], 'r-', label='Test Acc', linewidth=2)
        axes[1].set_xlabel('Época')
        axes[1].set_ylabel('Accuracy (%)')
        axes[1].set_title('Accuracy durante Entrenamiento')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        axes[2].plot(epochs, history['learning_rate'], 'g-', linewidth=2)
        axes[2].set_xlabel('Época')
        axes[2].set_ylabel('Learning Rate')
        axes[2].set_title('Learning Rate Schedule')
        axes[2].set_yscale('log')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f'Gráfico guardado en: {save_path}')
        else:
            plt.show()
        plt.close()
    
    @staticmethod
    def plot_sample_predictions(
        images: torch.Tensor,
        predictions: np.ndarray,
        targets: np.ndarray,
        classes: List[str],
        num_samples: int = 16,
        save_path: Optional[str] = None
    ):
        num_samples = min(num_samples, len(images))
        rows = int(np.sqrt(num_samples))
        cols = (num_samples + rows - 1) // rows
        
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.5, rows * 2.5))
        axes = axes.flatten() if num_samples > 1 else [axes]
        
        for i in range(num_samples):
            img = images[i].cpu().numpy()
            if img.shape[0] == 1:
                img = img.squeeze()
                axes[i].imshow(img, cmap='gray')
            else:
                img = np.transpose(img, (1, 2, 0))
                img = (img - img.min()) / (img.max() - img.min())
                axes[i].imshow(img)
            
            pred_class = classes[predictions[i]]
            true_class = classes[targets[i]]
            color = 'green' if predictions[i] == targets[i] else 'red'
            
            axes[i].set_title(f'P: {pred_class}\nR: {true_class}', color=color, fontsize=9)
            axes[i].axis('off')
        
        for i in range(num_samples, len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
        plt.close()
    
    @staticmethod
    def plot_class_distribution(
        targets: np.ndarray,
        classes: List[str],
        title: str = 'Distribución de Clases',
        save_path: Optional[str] = None
    ):
        unique, counts = np.unique(targets, return_counts=True)
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(classes)), [0] * len(classes), color='lightgray')
        
        for i, u in enumerate(unique):
            if u < len(classes):
                bars[u].set_height(counts[i])
                bars[u].set_color('steelblue')
        
        plt.xlabel('Clase')
        plt.ylabel('Cantidad')
        plt.title(title)
        plt.xticks(range(len(classes)), [classes[i] for i in range(len(classes))], rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
        plt.close()
    
    @staticmethod
    def plot_loss_comparison(
        results: dict,
        save_path: Optional[str] = None
    ):
        datasets = list(results.keys())
        train_losses = [results[d]['train_loss'] for d in datasets]
        test_losses = [results[d]['test_loss'] for d in datasets]
        
        x = np.arange(len(datasets))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width/2, train_losses, width, label='Train Loss', color='steelblue')
        bars2 = ax.bar(x + width/2, test_losses, width, label='Test Loss', color='coral')
        
        ax.set_xlabel('Dataset')
        ax.set_ylabel('Loss')
        ax.set_title('Comparación de Loss entre Datasets')
        ax.set_xticks(x)
        ax.set_xticklabels(datasets)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
        plt.close()
    
    @staticmethod
    def plot_accuracy_comparison(
        results: dict,
        save_path: Optional[str] = None
    ):
        datasets = list(results.keys())
        train_accs = [results[d]['train_acc'] for d in datasets]
        test_accs = [results[d]['test_acc'] for d in datasets]
        
        x = np.arange(len(datasets))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width/2, train_accs, width, label='Train Acc', color='steelblue')
        bars2 = ax.bar(x + width/2, test_accs, width, label='Test Acc', color='coral')
        
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
        
        ax.set_xlabel('Dataset')
        ax.set_ylabel('Accuracy (%)')
        ax.set_title('Comparación de Accuracy entre Datasets')
        ax.set_xticks(x)
        ax.set_xticklabels(datasets)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 110)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
        plt.close()
    
    @staticmethod
    def plot_filters(model: torch.nn.Module, layer_name: str = 'features.0', save_path: Optional[str] = None):
        try:
            layer = dict(model.named_modules())[layer_name]
            if isinstance(layer, torch.nn.Conv2d):
                filters = layer.weight.data.cpu().numpy()
                
                num_filters = min(32, filters.shape[0])
                fig, axes = plt.subplots(4, 8, figsize=(16, 8))
                axes = axes.flatten()
                
                for i in range(num_filters):
                    if filters.shape[1] == 3:
                        f = filters[i].transpose(1, 2, 0)
                        f = (f - f.min()) / (f.max() - f.min())
                    else:
                        f = filters[i, 0]
                    axes[i].imshow(f, cmap='gray')
                    axes[i].axis('off')
                
                for i in range(num_filters, len(axes)):
                    axes[i].axis('off')
                
                plt.suptitle(f'Filtros de la capa: {layer_name}')
                plt.tight_layout()
                
                if save_path:
                    plt.savefig(save_path, dpi=150, bbox_inches='tight')
                else:
                    plt.show()
                plt.close()
        except Exception as e:
            print(f'No se pudieron visualizar los filtros: {e}')
