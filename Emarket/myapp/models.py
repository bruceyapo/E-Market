from django.db import models
from django.utils import timezone
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from authentifications.models import Vendeur, client
from boutique.models import Produit
 
    
class Vente(models.Model):
    IdVendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE)
    IdClient = models.ForeignKey(client, on_delete=models.CASCADE)
    IdProduit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    QuantiteVendu = models.IntegerField()
    MontantTotal = models.DecimalField(max_digits=10, decimal_places=2)
    # DateVente = models.DateTimeField()
    DateVente = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.IdVendeur.nom
    
    # def __unicode__(self):
    #     return f"Vente {self.MontantTotal}"
    # def __str__(self):
    #     return f"Vente {self.Idvente}"

class Recu(models.Model):
    IdVente = models.ManyToManyField(Vente)  # Ajoutez cette ligne
    DateCreation = models.DateTimeField(auto_now_add=True)
    



    
class Notification(models.Model):
    message = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    est_lu = models.BooleanField(default=False)

    def __str__(self):
        return self.message
    