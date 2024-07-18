from django.db import models
from django.urls import reverse

# Create your models here.
class CategorieProduit(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    cat_image = models.ImageField(blank=True, upload_to=('Categories'))
        
    def get_url(self):
        return reverse('product_by_category', args=[self.slug])
    def __str__(self):
        return self.nom
