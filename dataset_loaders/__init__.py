from .fashion_mnist import FashionMNISTLoader
from .cifar10 import CIFAR10Loader
from .svhn import SVHNLoader
from .emnist import EMNISTLoader
from .tiny_imagenet import TinyImageNetLoader
from .base import BaseDataLoader

DATASET_LOADERS = {'fashion_mnist': FashionMNISTLoader, 'cifar10': CIFAR10Loader, 'svhn': SVHNLoader, 'emnist': EMNISTLoader, 'tiny_imagenet': TinyImageNetLoader}

def get_loader(name): return DATASET_LOADERS[name]
