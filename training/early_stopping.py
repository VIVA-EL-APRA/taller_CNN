import torch
import numpy as np
import os

class EarlyStopping:
    def __init__(
        self,
        patience: int = 10,
        min_delta: float = 0.0,
        mode: str = 'max',
        save_path: str = 'best_model.pth'
    ):
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.save_path = save_path
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.best_model_state = None
        
        if mode not in ['min', 'max']:
            raise ValueError("mode debe ser 'min' o 'max'")
    
    def __call__(self, score: float, model: torch.nn.Module) -> bool:
        if self.best_score is None:
            self.best_score = score
            self.best_model_state = model.state_dict().copy()
            return False
        
        if self.mode == 'max':
            if score > self.best_score + self.min_delta:
                self.best_score = score
                self.best_model_state = model.state_dict().copy()
                self.counter = 0
            else:
                self.counter += 1
        else:
            if score < self.best_score - self.min_delta:
                self.best_score = score
                self.best_model_state = model.state_dict().copy()
                self.counter = 0
            else:
                self.counter += 1
        
        if self.counter >= self.patience:
            self.early_stop = True
            return True
        return False
    
    def save_best_model(self, model: torch.nn.Module):
        if self.best_model_state is not None:
            os.makedirs(os.path.dirname(self.save_path) if os.path.dirname(self.save_path) else '.', exist_ok=True)
            torch.save(self.best_model_state, self.save_path)
            print(f'Mejor modelo guardado en: {self.save_path}')
    
    def load_best_model(self, model: torch.nn.Module):
        if self.best_model_state is not None:
            model.load_state_dict(self.best_model_state)
        return model
