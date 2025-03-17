# Create your models here.
from django.db import models

class PotatoImage(models.Model):
    image = models.ImageField(upload_to='uploads/')  # Stores uploaded images
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp of upload

    def __str__(self):
        return f"Image uploaded at {self.uploaded_at}"