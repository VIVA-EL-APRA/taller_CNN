# Taller de Redes Neuronales Convolucionales (CNNs)

Implementacion robusta de CNNs para los 5 datasets del taller de Inteligencia Artificial.

## Estructura del Proyecto

`
proyecto_CNN/
├── datasets/          # Cargadores de datos
├── models/            # Arquitecturas CNN
├── training/           # Pipeline de entrenamiento
├── evaluation/        # Evaluacion y metricas
├── utils/             # Visualizacion y utilidades
├── checkpoints/       # Modelos guardados
├── results/           # Resultados y graficos
├── main.py            # Punto de entrada
└── requirements.txt   # Dependencias
`

## Datasets Soportados

1. **Fashion-MNIST** (Nivel Facil) - 10 clases de moda
2. **CIFAR-10** (Nivel Intermedio-Bajo) - 10 clases de objetos
3. **SVHN** (Nivel Intermedio) - Digitos de calles
4. **EMNIST** (Nivel Intermedio-Alto) - 62 clases
5. **Tiny ImageNet** (Nivel Avanzado) - 200 clases

## Instalacion

`ash
pip install -r requirements.txt
`

## Uso

### Entrenar todos los datasets
`ash
python main.py --dataset all --epochs 30
`

### Entrenar un dataset especifico
`ash
python main.py --dataset fashion_mnist --epochs 30 --batch_size 64
`

### Opciones disponibles

| Parametro | Descripcion | Valor por defecto |
|-----------|-------------|------------------|
| --dataset | Dataset a usar | fashion_mnist |
| --epochs | Numero de epocas | 30 |
| --batch_size | Tamano del batch | 64 |
| --lr | Learning rate | 0.001 |
| --scheduler | LR scheduler | cosine |
| --resnet | Usar ResNet18 | False |

## Modelos Implementados

- **FashionCNN**: Para MNIST/Fashion-MNIST
- **CIFAR10CNN**: Para CIFAR-10/SVHN
- **EMNISTNet**: Para EMNIST
- **TinyImageNetNet**: Para Tiny ImageNet
- **ResNet18**: Arquitectura profunda opcional

## Caracteristicas Robustas

- Data Augmentation completo
- Batch Normalization
- Dropout regularization
- Early Stopping
- Learning Rate Scheduling
- Checkpointing automatico
- Visualizacion de metricas
- Matriz de confusion
