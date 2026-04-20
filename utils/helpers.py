import torch
import numpy as np
import random
import os

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ['PYTHONHASHSEED'] = str(seed)

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def get_device():
    if torch.cuda.is_available():
        print(f'GPU: {torch.cuda.get_device_name(0)}')
        return torch.device('cuda')
    print('Usando CPU')
    return torch.device('cpu')

def print_model_summary(model):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print('='*60)
    print(f'MODELO: {model.__class__.__name__}')
    print(f'Parametros totales: {total:,}')
    print(f'Parametros entrenables: {trainable:,}')
    print('='*60)
    print(model)
    print('='*60)
