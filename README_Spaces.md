# Taller CNN - Hugging Face Space

Web app interactiva para clasificar imágenes usando modelos CNN entrenados.

## 🎯 Modelos Disponibles

| Dataset | Accuracy | Clases | Descripción |
|---------|----------|--------|------------|
| Fashion-MNIST | 93.11% | 10 | Ropa y accesorios |
| CIFAR-10 | 84.91% | 10 | Objetos cotidianos |
| SVHN | 95.33% | 10 | Números de casas |
| EMNIST | 87.92% | 62 | Letras y dígitos |
| Tiny ImageNet | 44.51% | 200 | Imágenes diversas |

## 🚀 Cómo usar

1. Selecciona un modelo del dropdown
2. Sube una imagen
3. Click en "Clasificar"
4. ¡Ve el resultado!

## 💻 Uso local

```bash
pip install -r requirements_spaces.txt
python app.py
```

## 📝 Requisitos

- torch
- torchvision  
- gradio
- pillow
- numpy