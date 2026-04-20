import torchvision.datasets as datasets
from .base import BaseDataLoader
from typing import Tuple, List
import torchvision.transforms as transforms

class SVHNLoader(BaseDataLoader):
    SVHN_CLASSES = [str(i) for i in range(10)]
    
    @property
    def input_size(self) -> Tuple[int, int, int]:
        return (3, 32, 32)
    
    @property
    def num_classes(self) -> int:
        return 10
    
    @property
    def classes(self) -> List[str]:
        return self.SVHN_CLASSES
    
    def get_transforms(self, train: bool = True) -> transforms.Compose:
        if train and self.augment:
            return transforms.Compose([
                transforms.RandomCrop(32, padding=4),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.ColorJitter(brightness=0.2, contrast=0.2),
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.4377, 0.4438, 0.4728),
                    (0.1980, 0.2010, 0.1970)
                )
            ])
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                (0.4377, 0.4438, 0.4728),
                (0.1980, 0.2010, 0.1970)
            )
        ])
    
    def load_dataset(self) -> Tuple[object, object]:
        train_transform = self.get_transforms(train=True)
        test_transform = self.get_transforms(train=False)
        
        train_dataset = datasets.SVHN(
            root=self.data_dir,
            split='train',
            download=True,
            transform=train_transform
        )
        
        test_dataset = datasets.SVHN(
            root=self.data_dir,
            split='test',
            download=True,
            transform=test_transform
        )
        
        return train_dataset, test_dataset
