import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Optional, Callable, Tuple, Any
import time
from tqdm import tqdm
import numpy as np
import os
import json
from datetime import datetime

class Trainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        criterion: Optional[nn.Module] = None,
        optimizer: Optional[optim.Optimizer] = None,
        device: Optional[torch.device] = None,
        scheduler: Optional[Any] = None,
        checkpoint_dir: str = './checkpoints',
        log_dir: str = './logs'
    ):
        self.model = model.to(device or torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
        self.device = self.model.device if hasattr(self.model, 'device') else device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.criterion = criterion or nn.CrossEntropyLoss()
        self.optimizer = optimizer or optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
        self.scheduler = scheduler
        self.checkpoint_dir = checkpoint_dir
        self.log_dir = log_dir
        
        os.makedirs(checkpoint_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        self.train_losses = []
        self.train_accs = []
        self.test_losses = []
        self.test_accs = []
        self.best_test_acc = 0.0
        self.training_history = {
            'epoch': [],
            'train_loss': [],
            'train_acc': [],
            'test_loss': [],
            'test_acc': [],
            'learning_rate': [],
            'time': []
        }
    
    def train_epoch(self) -> Tuple[float, float]:
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc='Entrenando')
        for inputs, targets in pbar:
            inputs, targets = inputs.to(self.device), targets.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
        
        epoch_loss = running_loss / total
        epoch_acc = 100. * correct / total
        return epoch_loss, epoch_acc
    
    def evaluate(self) -> Tuple[float, float]:
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, targets in self.test_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                
                running_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
        
        epoch_loss = running_loss / total
        epoch_acc = 100. * correct / total
        return epoch_loss, epoch_acc
    
    def train(
        self,
        epochs: int,
        early_stopping_patience: int = 10,
        save_best_only: bool = True
    ) -> Dict:
        print(f'Iniciando entrenamiento en {self.device}')
        print(f'Modelo: {self.model.__class__.__name__}')
        print(f'Épocas: {epochs}')
        print('-' * 60)
        
        patience_counter = 0
        
        for epoch in range(epochs):
            start_time = time.time()
            
            train_loss, train_acc = self.train_epoch()
            test_loss, test_acc = self.evaluate()
            
            if self.scheduler is not None:
                self.scheduler.step()
                current_lr = self.optimizer.param_groups[0]['lr']
            else:
                current_lr = self.optimizer.param_groups[0]['lr']
            
            epoch_time = time.time() - start_time
            
            self.train_losses.append(train_loss)
            self.train_accs.append(train_acc)
            self.test_losses.append(test_loss)
            self.test_accs.append(test_acc)
            
            self.training_history['epoch'].append(epoch + 1)
            self.training_history['train_loss'].append(train_loss)
            self.training_history['train_acc'].append(train_acc)
            self.training_history['test_loss'].append(test_loss)
            self.training_history['test_acc'].append(test_acc)
            self.training_history['learning_rate'].append(current_lr)
            self.training_history['time'].append(epoch_time)
            
            print(f'Epoch {epoch+1}/{epochs} | '
                  f'Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | '
                  f'Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.2f}% | '
                  f'Time: {epoch_time:.1f}s')
            
            if test_acc > self.best_test_acc:
                self.best_test_acc = test_acc
                patience_counter = 0
                
                if save_best_only:
                    self.save_checkpoint(f'best_model.pth', epoch, test_acc)
                    print(f'  -> Nuevo mejor modelo guardado! Acc: {test_acc:.2f}%')
            else:
                patience_counter += 1
            
            if (epoch + 1) % 5 == 0:
                self.save_checkpoint(f'checkpoint_epoch_{epoch+1}.pth', epoch, test_acc)
            
            if patience_counter >= early_stopping_patience:
                print(f'\nEarly stopping activado en epoch {epoch+1}')
                break
        
        self.save_training_history()
        self.print_summary()
        
        return self.training_history
    
    def save_checkpoint(self, filename: str, epoch: int, accuracy: float):
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'accuracy': accuracy,
            'training_history': self.training_history
        }
        filepath = os.path.join(self.checkpoint_dir, filename)
        torch.save(checkpoint, filepath)
    
    def load_checkpoint(self, filepath: str):
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        return checkpoint.get('epoch', 0), checkpoint.get('accuracy', 0.0)
    
    def save_training_history(self):
        filepath = os.path.join(self.log_dir, 'training_history.json')
        with open(filepath, 'w') as f:
            json.dump(self.training_history, f, indent=2)
    
    def print_summary(self):
        print('\n' + '=' * 60)
        print('RESUMEN DEL ENTRENAMIENTO')
        print('=' * 60)
        print(f'Mejor accuracy de test: {self.best_test_acc:.2f}%')
        total_epochs = len(self.train_losses)
        total_time = sum(self.training_history['time'])
        print(f'Total de epocas entrenadas: {total_epochs}')
        print(f'Tiempo total: {total_time:.1f}s')
        print(f'Checkpoints guardados en: {self.checkpoint_dir}')
        print(f'Historial guardado en: {self.log_dir}')
        print('=' * 60)
