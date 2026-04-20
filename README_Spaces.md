# CNN Image Classifier - Hugging Face Spaces

Web app para probar los modelos CNN entrenados en el taller.

## Modelos Disponibles

| Modelo | Accuracy | Clases |
|--------|----------|--------|
| Fashion-MNIST | 93.11% | 10 |
| CIFAR-10 | 84.91% | 10 |
| SVHN | 95.33% | 10 |
| EMNIST | 87.92% | 62 |
| Tiny ImageNet | 44.51% | 200 |

## Cómo usar

1. Selecciona un modelo del dropdown
2. Sube una imagen
3. Click en "Clasificar"
4. Ve el resultado

## Ejemplo de uso local

```bash
pip install -r requirements_spaces.txt
python app.py
```

## Despliegue en Hugging Face Spaces

1. Ve a https://huggingface.co/spaces
2. Crea un nuevo Space (Gradio)
3. Sube los archivos:
   - app.py
   - requirements_spaces.txt
   - checkpoints/ (modelos entrenados)
   - models/
   - dataset_loaders/
   - training/
   - evaluation/
   - utils/
4. ¡Listo!