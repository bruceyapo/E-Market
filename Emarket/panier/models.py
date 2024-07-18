from django.db import models

from authentifications.models import Utilisateur
from boutique.models import Negotiation, Produit

# Create your models here.
class Cart(models.Model):
    cart_id     = models.CharField(max_length=250, blank=True)
    date_added  = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    user        = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, null=True)
    product     = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True)
    cart        = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    negotiation = models.ForeignKey(Negotiation, on_delete=models.CASCADE, null=True)
    quantity    = models.IntegerField()
    is_active   = models.BooleanField(default=True)

    
    def sub_total(self):
        if self.negotiation:
            return self.negotiation.PrixUnitaire * self.quantity
        else:
            return self.product.PrixUnitaire * self.quantity
       
    def __unicode__(self):
        return self.negotiation.product.Nom