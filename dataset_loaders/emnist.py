import torch
from .base import BaseDataLoader
from typing import Tuple, List
import torchvision.transforms as transforms
from torch.utils.data import Dataset
import os

class EMNISTLoader(BaseDataLoader):
    EMNIST_CLASSES = [str(i) for i in range(10)] + [chr(c) for c in range(65, 91)] + [chr(c) for c in range(97, 123)]
    
    @property
    def input_size(self) -> Tuple[int, int, int]:
        return (1, 28, 28)
    
    @property
    def num_classes(self) -> int:
        return 62
    
    @property
    def classes(self) -> List[str]:
        return self.EMNIST_CLASSES[:62]
    
    def get_transforms(self, train: bool = True) -> transforms.Compose:
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
    
    def load_dataset(self) -> Tuple[Dataset, Dataset]:
        try:
            import torchvision.datasets as datasets
            train_dataset = datasets.EMNIST(
                root=self.data_dir,
                train=True,
                split='byclass',
                download=True,
                transform=self.get_transforms(train=True)
            )
            
            test_dataset = datasets.EMNIST(
                root=self.data_dir,
                train=False,
                split='byclass',
                download=True,
                transform=self.get_transforms(train=False)
            )
            
            return train_dataset, test_dataset
        except Exception as e:
            print(f"Nota: EMNIST requiere configuracion adicional. Error: {e}")
            raise