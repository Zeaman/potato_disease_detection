from django.shortcuts import render, redirect
from .forms import PotatoImageForm
from .models import PotatoImage
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os

# Load the trained model
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best_model.pth")
model = models.resnet18(pretrained=False)
num_ftrs = model.fc.in_features
model.fc = nn.Sequential(
    nn.Linear(num_ftrs, 256),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(256, 3)  # Assuming 3 output classes
)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

# Define transformations for inference
inference_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def predict_disease(image_path):
    """
    Predicts the disease from the uploaded image.
    """
    image = Image.open(image_path).convert('RGB')
    image_tensor = inference_transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        _, predicted_class = torch.max(output, 1)
    class_names = ['Potato_Early_blight', 'Potato_healthy', 'Potato_Late_blight']
    return class_names[predicted_class.item()], probabilities.tolist()

def upload_image(request):
    if request.method == 'POST':
        form = PotatoImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Delete old images if more than 10 exist
            images = PotatoImage.objects.order_by('-uploaded_at')
            if images.count() >= 10:  # Keep only the latest 10 images
                oldest_images = images[10:]  # Get all images beyond the 10th
                for old_image in oldest_images:
                    if old_image.image:  # Check if the image field is not empty
                        if os.path.isfile(old_image.image.path):  # Check if the file exists
                            os.remove(old_image.image.path)  # Delete the file
                    old_image.delete()  # Delete the database record

            # Save the new uploaded image
            potato_image = form.save()
            image_path = potato_image.image.path

            # Predict the disease
            disease, probabilities = predict_disease(image_path)

            # Render the result page with prediction
            return render(request, 'result.html', {
                'disease': disease,
                'probabilities': probabilities,
                'image_url': potato_image.image.url
            })
    else:
        form = PotatoImageForm()
    return render(request, 'upload.html', {'form': form})

def about_us(request):
    return render(request, 'about.html')