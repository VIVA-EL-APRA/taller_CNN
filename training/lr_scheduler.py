import torch.optim as optim
from torch.optim.lr_scheduler import StepLR, CosineAnnealingLR, ReduceLROnPlateau, OneCycleLR

def get_scheduler(scheduler_name: str, optimizer, **kwargs):
    schedulers = {
        'step': StepLR,
        'cosine': CosineAnnealingLR,
        'plateau': ReduceLROnPlateau,
        'onecycle': OneCycleLR,
    }
    
    if scheduler_name not in schedulers:
        raise ValueError(f'Scheduler no encontrado. Opciones: {list(schedulers.keys())}')
    
    scheduler_class = schedulers[scheduler_name]
    
    if scheduler_name == 'step':
        return scheduler_class(optimizer, step_size=kwargs.get('step_size', 10), gamma=kwargs.get('gamma', 0.1))
    elif scheduler_name == 'cosine':
        return scheduler_class(optimizer, T_max=kwargs.get('T_max', 50), eta_min=kwargs.get('eta_min', 0))
    elif scheduler_name == 'plateau':
        return scheduler_class(optimizer, mode=kwargs.get('mode', 'max'), factor=kwargs.get('factor', 0.1), patience=kwargs.get('patience', 5))
    elif scheduler_name == 'onecycle':
        return scheduler_class(optimizer, max_lr=kwargs.get('max_lr', 0.01), epochs=kwargs.get('epochs', 50), steps_per_epoch=kwargs.get('steps_per_epoch', 100))
    
    return None
