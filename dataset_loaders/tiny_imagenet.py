import torch
from .base import BaseDataLoader
from typing import Tuple, List
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader as TorchDataLoader
import os

class TinyImageNetLoader(BaseDataLoader):
    TINY_IMAGENET_CLASSES = [f'class_{i}' for i in range(200)]
    
    _huggingface_dataset = None
    
    @property
    def input_size(self) -> Tuple[int, int, int]:
        return (3, 64, 64)
    
    @property
    def num_classes(self) -> int:
        return 200
    
    @property
    def classes(self) -> List[str]:
        return self.TINY_IMAGENET_CLASSES
    
    def get_transforms(self, train: bool = True) -> transforms.Compose:
        if train and self.augment:
            return transforms.Compose([
                transforms.RandomCrop(64, padding=8),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
                transforms.RandomRotation(degrees=15),
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.485, 0.456, 0.406),
                    (0.229, 0.224, 0.225)
                )
            ])
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                (0.485, 0.456, 0.406),
                (0.229, 0.224, 0.225)
            )
        ])
    
    @classmethod
    def load_from_huggingface(cls):
        if cls._huggingface_dataset is None:
            print("Cargando Tiny ImageNet desde Hugging Face...")
            import sys
            if '' in sys.path:
                sys.path.remove('')
            import importlib
            hf_datasets = importlib.import_module('datasets')
            hf_load_dataset = getattr(hf_datasets, 'load_dataset')
            cls._huggingface_dataset = hf_load_dataset("zh-plus/tiny-imagenet")
            print("Dataset cargado exitosamente!")
        return cls._huggingface_dataset
    
    def load_dataset(self) -> Tuple[Dataset, Dataset]:
        try:
            hf_dataset = self.load_from_huggingface()
            
            class HFDatasetWrapper(Dataset):
                def __init__(self, hf_split, transform=None):
                    self.hf_split = hf_split
                    self.transform = transform
                
                def __len__(self):
                    return len(self.hf_split)
                
                def __getitem__(self, idx):
                    item = self.hf_split[idx]
                    image = item['image']
                    label = item['label']
                    
                    if hasattr(image, 'mode') and image.mode != 'RGB':
                        image = image.convert('RGB')
                    elif not isinstance(image, torch.Tensor):
                        image = image.convert('RGB')
                    
                    if self.transform:
                        image = self.transform(image)
                    
                    return image, label
            
            train_dataset = HFDatasetWrapper(
                hf_dataset['train'],
                transform=self.get_transforms(train=True)
            )
            
            val_dataset = HFDatasetWrapper(
                hf_dataset['valid'],
                transform=self.get_transforms(train=False)
            )
            
            return train_dataset, val_dataset
            
        except Exception as e:
            print(f"Error cargando dataset: {e}")
            import traceback
            traceback.print_exc()
            raise