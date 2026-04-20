import argparse
import torch
import torch.optim as optim
import os
import sys

from dataset_loaders import get_loader
from models import FashionCNN, CIFAR10CNN, SVHNNet, EMNISTNet, TinyImageNetNet, ResNetBuilder
from training import Trainer, get_scheduler
from evaluation import Evaluator
from utils import set_seed, get_device, print_model_summary, Visualizer, ExperimentLogger

DATASET_MODELS = {
    'fashion_mnist': FashionCNN,
    'cifar10': CIFAR10CNN,
    'svhn': SVHNNet,
    'emnist': EMNISTNet,
    'tiny_imagenet': TinyImageNetNet,
}

def parse_args():
    parser = argparse.ArgumentParser(description='Entrenamiento de CNNs para clasificacion de imagenes')
    parser.add_argument('--dataset', type=str, default='fashion_mnist',
                        choices=['fashion_mnist', 'cifar10', 'svhn', 'emnist', 'tiny_imagenet', 'all'],
                        help='Dataset a utilizar')
    parser.add_argument('--epochs', type=int, default=30, help='Numero de epocas')
    parser.add_argument('--batch_size', type=int, default=64, help='Tamano del batch')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--seed', type=int, default=42, help='Semilla aleatoria')
    parser.add_argument('--device', type=str, default='auto', choices=['auto', 'cuda', 'cpu'])
    parser.add_argument('--data_dir', type=str, default='./data')
    parser.add_argument('--checkpoint_dir', type=str, default='./checkpoints')
    parser.add_argument('--log_dir', type=str, default='./logs')
    parser.add_argument('--results_dir', type=str, default='./results')
    parser.add_argument('--no_augment', action='store_true')
    parser.add_argument('--scheduler', type=str, default='cosine', choices=['step', 'cosine', 'plateau', 'onecycle', 'none'])
    parser.add_argument('--evaluate_only', action='store_true')
    parser.add_argument('--checkpoint', type=str, default=None)
    parser.add_argument('--resnet', action='store_true')
    return parser.parse_args()

def train_dataset(args, dataset_name, logger):
    print('\n' + '='*70)
    print(f'DATASET: {dataset_name.upper()}')
    print('='*70)
    
    set_seed(args.seed)
    device = get_device() if args.device == 'auto' else torch.device(args.device)
    
    data_loader = get_loader(dataset_name)(
        batch_size=args.batch_size, data_dir=args.data_dir, augment=not args.no_augment
    )
    
    print(f'\nDataset Summary:')
    for key, value in data_loader.summary().items():
        print(f'  {key}: {value}')
    
    model_class = ResNetBuilder.build_resnet18 if args.resnet else DATASET_MODELS[dataset_name]
    model = model_class(num_classes=data_loader.num_classes)
    print_model_summary(model)
    
    logger.log_config({
        'dataset': dataset_name, 'epochs': args.epochs, 'batch_size': args.batch_size,
        'learning_rate': args.lr, 'model': model.__class__.__name__,
        'augmentation': not args.no_augment, 'scheduler': args.scheduler
    })
    
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    scheduler = get_scheduler(args.scheduler, optimizer, T_max=args.epochs) if args.scheduler != 'none' else None
    
    trainer = Trainer(
        model=model, train_loader=data_loader.train_loader(), test_loader=data_loader.test_loader(),
        optimizer=optimizer, scheduler=scheduler, device=device,
        checkpoint_dir=os.path.join(args.checkpoint_dir, dataset_name),
        log_dir=os.path.join(args.log_dir, dataset_name)
    )
    
    if args.evaluate_only and args.checkpoint:
        trainer.load_checkpoint(args.checkpoint)
    else:
        history = trainer.train(epochs=args.epochs, early_stopping_patience=10)
        Visualizer.plot_training_history(history, save_path=os.path.join(args.results_dir, f'{dataset_name}_training_history.png'))
    
    evaluator = Evaluator(model=trainer.model, test_loader=data_loader.test_loader(), classes=data_loader.classes, device=device)
    evaluator.print_summary()
    evaluator.save_results(os.path.join(args.results_dir, dataset_name))
    metrics = evaluator.calculate_metrics()
    logger.log_metrics(epoch=args.epochs, metrics=metrics)
    return metrics

def main():
    args = parse_args()
    print('='*70)
    print('TALLER DE REDES NEURONALES CONVOLUCIONALES (CNNs)')
    print('='*70)
    print(f'Argumentos: {vars(args)}')
    
    logger = ExperimentLogger(log_dir=args.log_dir, experiment_name=f'cnn_training_{args.dataset}_{args.seed}')
    os.makedirs(args.results_dir, exist_ok=True)
    
    datasets = ['fashion_mnist', 'cifar10', 'svhn', 'emnist', 'tiny_imagenet'] if args.dataset == 'all' else [args.dataset]
    all_results = {}
    
    for dataset_name in datasets:
        try:
            metrics = train_dataset(args, dataset_name, logger)
            all_results[dataset_name] = metrics
        except Exception as e:
            print(f'Error entrenando {dataset_name}: {e}')
            import traceback; traceback.print_exc()
    
    if len(all_results) > 1:
        print('\n' + '='*70)
        print('RESUMEN COMPARATIVO')
        print('='*70)
        for name, m in all_results.items():
            acc = m["accuracy"] * 100
            f1 = m["f1_score"]
            print(f'{name.upper()}: Acc={acc:.2f}% F1={f1:.4f}')
    
    logger.finalize()
    print('\nENTRENAMIENTO COMPLETADO')

if __name__ == '__main__':
    main()
