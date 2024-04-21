from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Notification, Vente, Stock

@receiver(post_save, sender=Vente)
def update_stock(sender, instance, **kwargs):
    # Vérifiez si l'instance est nouvellement créée ou mise à jour
    if kwargs.get('created', False):
        # Si la vente est nouvellement créée, déduisez la quantité vendue du stock
        
        produit = instance.IdProduit
        produit_stock, created = Stock.objects.get_or_create(IdProduit=produit)
        # Mettez à jour la quantité en stock
        produit_stock.QuantiteStock -= instance.QuantiteVendu
        produit_stock.save()

        if produit_stock.QuantiteStock < 250:
            message = f"Attention : Le stock du produit {instance.IdProduit.Nom} est faible ({produit_stock.QuantiteStock} restants)."
            Notification.objects.create(message=message)
            