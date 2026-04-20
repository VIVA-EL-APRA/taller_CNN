import os
import json
from datetime import datetime

class ExperimentLogger:
    def __init__(self, log_dir='./logs', experiment_name=None):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.experiment_name = experiment_name or datetime.now().strftime('%Y%m%d_%H%M%S')
        self.experiment_dir = os.path.join(log_dir, self.experiment_name)
        os.makedirs(self.experiment_dir, exist_ok=True)
        self.metrics_history = []
        self.config = {}

    def log_config(self, config):
        self.config = config
        with open(os.path.join(self.experiment_dir, 'config.json'), 'w') as f:
            json.dump(config, f, indent=2)

    def log_metrics(self, epoch, metrics):
        metrics['epoch'] = epoch
        metrics['timestamp'] = datetime.now().isoformat()
        self.metrics_history.append(metrics)
        with open(os.path.join(self.experiment_dir, 'metrics.jsonl'), 'a') as f:
            f.write(json.dumps(metrics) + '\n')

    def log_message(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(os.path.join(self.experiment_dir, 'log.txt'), 'a') as f:
            f.write(f'[{timestamp}] {message}\n')
        print(f'[{timestamp}] {message}')

    def finalize(self):
        with open(os.path.join(self.experiment_dir, 'metrics_history.json'), 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
        print(f'Experimento finalizado: {self.experiment_dir}')
