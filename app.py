"""
Gradio App para Hugging Face Spaces
Clasificador de imágenes CNN
"""

import gradio as gr
import torch
import torchvision.transforms as transforms
from PIL import Image
import os
from pathlib import Path

MODELS_INFO = {
    "fashion_mnist": {
        "name": "Fashion-MNIST",
        "classes": ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot'],
    },
    "cifar10": {
        "name": "CIFAR-10", 
        "classes": ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck'],
    },
    "svhn": {
        "name": "SVHN",
        "classes": ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
    },
    "emnist": {
        "name": "EMNIST",
        "classes": [str(i) for i in range(10)] + [chr(c) for c in range(65, 91)] + [chr(c) for c in range(97, 123)],
    },
    "tiny_imagenet": {
        "name": "Tiny ImageNet",
        "classes": [f'class_{i}' for i in range(200)],
    }
}

# Cargar modelo desde archivo local
loaded_models = {}

def get_transform(model_name):
    """Obtiene transformaciones según el modelo"""
    if model_name == "fashion_mnist":
        return transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
    elif model_name == "emnist":
        return transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
    elif model_name == "cifar10" or model_name == "svhn":
        return transforms.Compose([
            transforms.Resize((32, 32)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
    else:  # tiny_imagenet
        return transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
        ])

def load_model(model_name):
    """Carga el modelo"""
    if model_name in loaded_models:
        return loaded_models[model_name]
    
    checkpoint_path = f"checkpoints/{model_name}/best_model.pth"
    
    if not os.path.exists(checkpoint_path):
        return None
    
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
        
        # Crear modelo según el tipo
        if model_name == "tiny_imagenet":
            from torchvision.models import resnet18
            model = resnet18(weights=None)
            model.fc = torch.nn.Linear(512, 200)
        elif model_name == "fashion_mnist":
            from models.cnn_builder import FashionCNN
            model = FashionCNN(num_classes=10)
        elif model_name == "cifar10":
            from models.cnn_builder import CIFAR10CNN
            model = CIFAR10CNN(num_classes=10)
        elif model_name == "svhn":
            from models.cnn_builder import SVHNNet
            model = SVHNNet(num_classes=10)
        elif model_name == "emnist":
            from models.cnn_builder import EMNISTNet
            model = EMNISTNet(num_classes=62)
        else:
            return None
        
        model.load_state_dict(state_dict)
        model.eval()
        loaded_models[model_name] = model
        return model
    except Exception as e:
        print(f"Error cargando modelo {model_name}: {e}")
        return None

def predict(image, model_name):
    """Hace predicción"""
    if image is None:
        return "Por favor sube una imagen"
    
    model = load_model(model_name)
    
    if model is None:
        return f"Modelo {model_name} no disponible aún"
    
    info = MODELS_INFO[model_name]
    transform = get_transform(model_name)
    
    # Convertir y transformar
    img = image.convert('RGB') if image.mode == 'RGBA' else image
    img_tensor = transform(img).unsqueeze(0)
    
    # Predicción
    with torch.no_grad():
        output = model(img_tensor)
        probs = torch.nn.functional.softmax(output, dim=1)
        top_prob, top_class = torch.max(probs, 1)
        pred = info["classes"][top_class.item()]
        conf = top_prob.item() * 100
    
    # Top 3
    top3 = torch.topk(probs, 3, dim=1)
    results = []
    for i in range(3):
        cls = info["classes"][top3.indices[0][i].item()]
        prob = top3.values[0][i].item() * 100
        results.append(f"**{cls}**: {prob:.1f}%")
    
    return f"## 🎯 Predicción: **{pred}**\n\n**Confianza:** {conf:.1f}%\n\n### Top 3:\n" + "\n".join(results)

# Interfaz Gradio
with gr.Blocks(title="Clasificador CNN") as demo:
    gr.Markdown("# 🧠 Clasificador de Imágenes CNN")
    gr.Markdown("Selecciona un modelo y sube una imagen para clasificar")
    
    with gr.Row():
        with gr.Column():
            model_choice = gr.Dropdown(
                choices=list(MODELS_INFO.keys()),
                value="fashion_mnist",
                label="Modelo",
            )
            input_image = gr.Image(type="pil", label="Sube una imagen")
            btn = gr.Button("Clasificar 🎯", variant="primary")
        
        with gr.Column():
            output = gr.Markdown()
    
    btn.click(fn=predict, inputs=[input_image, model_choice], outputs=output)
    
    gr.Examples(
        examples=[["fashion_mNIST"], ["cifar10"], ["svhn"], ["emnist"], ["tiny_imagenet"]],
        inputs=model_choice,
    )

demo.launch()