import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from typing import Tuple, Optional, List, Dict, Any
import torchvision.transforms as transforms
from abc import ABC, abstractmethod

class BaseDataLoader(ABC):
    def __init__(
        self,
batch_size: int = 64,
        num_workers: int = 0,
        data_dir: str = './data',
        augment: bool = True
    ):
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.data_dir = data_dir
        self.augment = augment
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._train_loader = None
        self._test_loader = None
        self._classes = None
        
    @property
    @abstractmethod
    def input_size(self) -> Tuple[int, int, int]:
        pass
    
    @property
    @abstractmethod
    def num_classes(self) -> int:
        pass
    
    @property
    @abstractmethod
    def classes(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_transforms(self, train: bool = True) -> transforms.Compose:
        pass
    
    @abstractmethod
    def load_dataset(self) -> Tuple[Dataset, Dataset]:
        pass
    
    def train_loader(self) -> DataLoader:
        if self._train_loader is None:
            train_dataset, _ = self.load_dataset()
            self._train_loader = DataLoader(
                train_dataset,
                batch_size=self.batch_size,
                shuffle=True,
                num_workers=self.num_workers,
                pin_memory=True if torch.cuda.is_available() else False
            )
        return self._train_loader
    
    def test_loader(self) -> DataLoader:
        if self._test_loader is None:
            _, test_dataset = self.load_dataset()
            self._test_loader = DataLoader(
                test_dataset,
                batch_size=self.batch_size,
                shuffle=False,
                num_workers=self.num_workers,
                pin_memory=True if torch.cuda.is_available() else False
            )
        return self._test_loader
    
    def summary(self) -> Dict[str, Any]:
        return {
            'dataset': self.__class__.__name__,
            'input_size': self.input_size,
            'num_classes': self.num_classes,
            'classes': self.classes,
            'batch_size': self.batch_size,
            'device': str(self.device)
        }
