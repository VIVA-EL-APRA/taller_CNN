import torchvision.datasets as datasets
from .base import BaseDataLoader
from typing import Tuple, List
import torchvision.transforms as transforms

class FashionMNISTLoader(BaseDataLoader):
    FASHION_CLASSES = [
        'T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
        'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot'
    ]
    
    @property
    def input_size(self) -> Tuple[int, int, int]:
        return (1, 28, 28)
    
    @property
    def num_classes(self) -> int:
        return 10
    
    @property
    def classes(self) -> List[str]:
        return self.FASHION_CLASSES
    
    def get_transforms(self, train: bool = True) -> transforms.Compose:
        if train and self.augment:
            return transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(degrees=10),
                transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
                transforms.ToTensor(),
                transforms.Normalize((0.2860,), (0.3530,))
            ])
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.2860,), (0.3530,))
        ])
    
    def load_dataset(self) -> Tuple[object, object]:
        train_transform = self.get_transforms(train=True)
        test_transform = self.get_transforms(train=False)
        
        train_dataset = datasets.FashionMNIST(
            root=self.data_dir,
            train=True,
            download=True,
            transform=train_transform
        )
        
        test_dataset = datasets.FashionMNIST(
            root=self.data_dir,
            train=False,
            download=True,
            transform=test_transform
        )
        
        return train_dataset, test_dataset
