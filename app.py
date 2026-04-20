"""
Aplicación Gradio para Hugging Face Spaces
Clasificador de imágenes usando los modelos CNN entrenados
"""

import gradio as gr
import torch
import torchvision.transforms as transforms
from PIL import Image
import os
from pathlib import Path

# Modelo por defecto
DEFAULT_MODEL = "fashion_mnist"

MODELS_INFO = {
    "fashion_mnist": {
        "name": "Fashion-MNIST",
        "classes": ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot'],
        "input_size": (1, 28, 28),
        "transform": transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
    },
    "cifar10": {
        "name": "CIFAR-10",
        "classes": ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck'],
        "input_size": (3, 32, 32),
        "transform": transforms.Compose([
            transforms.Resize((32, 32)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
    },
    "svhn": {
        "name": "SVHN",
        "classes": ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        "input_size": (3, 32, 32),
        "transform": transforms.Compose([
            transforms.Resize((32, 32)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
    },
    "emnist": {
        "name": "EMNIST",
        "classes": ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                   'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                   'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                   'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                   'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
        "input_size": (1, 28, 28),
        "transform": transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
    },
    "tiny_imagenet": {
        "name": "Tiny ImageNet",
        "classes": [f'class_{i}' for i in range(200)],
        "input_size": (3, 64, 64),
        "transform": transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
        ])
    }
}

def load_model(model_name):
    """Carga el modelo desde Hugging Face Hub o local"""
    checkpoint_path = f"checkpoints/{model_name}/best_model.pth"
    
    if os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
            
        # Crear modelo básico según el dataset
        if model_name == "tiny_imagenet":
            from torchvision.models import resnet18, ResNet18_Weights
            model = resnet18(weights=None)
            model.fc = torch.nn.Linear(512, 200)
        else:
            from models.cnn_builder import get_model_for_dataset
            model = get_model_for_dataset(model_name)
            
        model.load_state_dict(state_dict)
        model.eval()
        return model
    else:
        return None

def predict(image, model_name):
    """Hace predicción en una imagen"""
    if image is None:
        return "Por favor sube una imagen"
    
    info = MODELS_INFO[model_name]
    
    # Convertir imagen PIL
    if isinstance(image, Image.Image):
        img = image
    else:
        img = Image.open(image)
    
    # Transformar
    img_tensor = info["transform"](img).unsqueeze(0)
    
    # Cargar modelo
    model = load_model(model_name)
    
    if model is None:
        return f"Modelo {model_name} no disponible"
    
    # Predicción
    with torch.no_grad():
        output = model(img_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)
        top_prob, top_class = torch.max(probabilities, 1)
        predicted_class = info["classes"][top_class.item()]
        confidence = top_prob.item() * 100
    
    # Top 3 predicciones
    top3_prob, top3_class = torch.topk(probabilities, 3, dim=1)
    predictions = []
    for i in range(3):
        pred_class = info["classes"][top3_class[0][i].item()]
        pred_prob = top3_prob[0][i].item() * 100
        predictions.append(f"{pred_class}: {pred_prob:.1f}%")
    
    result = f"🎯 **Predicción:** {predicted_class}\n"
    result += f"📊 **Confianza:** {confidence:.1f}%\n\n"
    result += "**Top 3 predicciones:**\n" + "\n".join(predictions)
    
    return result

# Crear interfaz Gradio
def create_app():
    with gr.Blocks(title="Clasificador CNN") as demo:
        gr.Markdown("# 🧠 Clasificador de Imágenes CNN")
        gr.Markdown("Selecciona un modelo y sube una imagen para clasificar")
        
        with gr.Row():
            with gr.Column():
                model_choice = gr.Dropdown(
                    choices=list(MODELS_INFO.keys()),
                    value=DEFAULT_MODEL,
                    label="Seleccionar Modelo",
                    info="Elige el dataset para clasificar"
                )
                
                input_image = gr.Image(type="pil", label="Subir Imagen")
                
                submit_btn = gr.Button("Clasificar 🎯", variant="primary")
            
            with gr.Column():
                output = gr.Markdown(label="Resultado")
        
        submit_btn.click(
            fn=predict,
            inputs=[input_image, model_choice],
            outputs=output
        )
        
        gr.Examples([
            ["fashion_mnist", "examples/fashion.jpg"],
            ["cifar10", "examples/cifar.jpg"],
        ], inputs=[model_choice, input_image])
    
    return demo

# Crear y lanzar app
if __name__ == "__main__":
    demo = create_app()
    demo.launch(server_name="0.0.0.0", server_port=7860)