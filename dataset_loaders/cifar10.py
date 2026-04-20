import torchvision.datasets as datasets
from .base import BaseDataLoader
from typing import Tuple, List
import torchvision.transforms as transforms

class CIFAR10Loader(BaseDataLoader):
    CIFAR10_CLASSES = [
        'airplane', 'automobile', 'bird', 'cat', 'deer',
        'dog', 'frog', 'horse', 'ship', 'truck'
    ]
    
    @property
    def input_size(self) -> Tuple[int, int, int]:
        return (3, 32, 32)
    
    @property
    def num_classes(self) -> int:
        return 10
    
    @property
    def classes(self) -> List[str]:
        return self.CIFAR10_CLASSES
    
    def get_transforms(self, train: bool = True) -> transforms.Compose:
        if train and self.augment:
            return transforms.Compose([
                transforms.RandomCrop(32, padding=4),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.RandomRotation(degrees=15),
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.4914, 0.4822, 0.4465),
                    (0.2470, 0.2435, 0.2616)
                )
            ])
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                (0.4914, 0.4822, 0.4465),
                (0.2470, 0.2435, 0.2616)
            )
        ])
    
    def load_dataset(self) -> Tuple[object, object]:
        train_transform = self.get_transforms(train=True)
        test_transform = self.get_transforms(train=False)
        
        train_dataset = datasets.CIFAR10(
            root=self.data_dir,
            train=True,
            download=True,
            transform=train_transform
        )
        
        test_dataset = datasets.CIFAR10(
            root=self.data_dir,
            train=False,
            download=True,
            transform=test_transform
        )
        
        return train_dataset, test_dataset
