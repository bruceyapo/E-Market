from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models import Avg, Count


from authentifications.models import Utilisateur, client
from categorie.models import CategorieProduit



# Create your models here.
class Produit(models.Model):
    Nom             = models.CharField(max_length=100)
    PrixUnitaire    = models.FloatField()
    slug            = models.SlugField(max_length=100, unique=True)
    description     = models.TextField(blank=True)
    image           = models.ImageField(blank=True, upload_to=('Product'))
    is_available    = models.BooleanField(default=True)
    IdCategorie     = models.ForeignKey(CategorieProduit, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)
    def get_url(self):
        return reverse('product_detail', args=[self.IdCategorie.slug, self.slug])
    
    def __str__(self):
        return self.Nom
    
    def AverageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    def CountReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('rating'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    

class Negotiation(models.Model):
    product = models.ForeignKey(Produit, on_delete=models.CASCADE)
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, null=True)
    PrixUnitaire    = models.FloatField(default=0)
    # PrixNegocie = models.FloatField()

    def __str__(self):
        return self.product.Nom
    
    # def __str__(self):
    #     return f"Negotiation pour {self.product.Nom} par {self.user.username}"
    
    
class ReviewRating(models.Model):
    product         = models.ForeignKey(Produit, on_delete=models.CASCADE)
    user            = models.ForeignKey(client, on_delete=models.CASCADE)
    subject         = models.CharField(max_length=100, blank=True)
    review          = models.TextField(max_length=500,blank=True)
    rating          = models.FloatField()
    ip              = models.CharField(max_length=20, blank=True)
    status          = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.subject

    
class Stock(models.Model):
    IdProduit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    QuantiteStock = models.IntegerField()
    Date = models.DateTimeField(default=timezone.now)
    
    # def __str__(self):
    #     return f"Stock {self.IdStock}"
    def __unicode__(self):
        return self.IdProduit.Nom