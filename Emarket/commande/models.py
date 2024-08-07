from django.db import models

from authentifications.models import Utilisateur, client
from boutique.models import Negotiation, Produit

# Create your models here.
class Payment(models.Model):
    user            = models.ForeignKey(client, on_delete= models.CASCADE)
    payment_id      = models.CharField(max_length=100)
    payment_method  = models.CharField(max_length=100)
    amount_paid    = models.CharField(max_length=100)
    status          = models.CharField(max_length=100)
    created_at      = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id

class Order(models.Model):
    STATUS = (
        ('En attente','En attente'),
        ('Complet','Complet'),
    )
    
    
    user            = models.ForeignKey(client, on_delete= models.SET_NULL, null=True)
    payment         = models.ForeignKey(Payment, on_delete= models.SET_NULL, null=True, blank=True)
    order_number    = models.CharField(max_length=20)
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    email           = models.EmailField(max_length=50)
    phone           = models.CharField(max_length=50)
    address_line_1  = models.CharField(max_length=50)
    address_line_2  = models.CharField(max_length=50, blank=True)
    country         = models.CharField(max_length=50)
    state           = models.CharField(max_length=50)
    city            = models.CharField(max_length=50)
    order_note      = models.CharField(max_length=100, blank=True)
    order_total     = models.FloatField()
    tax             = models.FloatField()
    status          = models.CharField(max_length=15, choices=STATUS, default='En attente')
    ip              = models.CharField(max_length=20, blank=True)
    is_ordered      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    upload_at       = models.DateTimeField(auto_now=True)
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    def __str__(self):
        return self.order_number
    
    
class OrderProduct(models.Model):
    order          = models.ForeignKey(Order, on_delete= models.CASCADE)
    payment        = models.ForeignKey(Payment, on_delete= models.SET_NULL, blank=True, null=True)
    user           = models.ForeignKey(client, on_delete= models.CASCADE)
    product        = models.ForeignKey(Produit, on_delete= models.CASCADE)
    negotiation    = models.ForeignKey(Negotiation, on_delete=models.CASCADE, null=True)
    quantity       = models.IntegerField()
    product_price  = models.FloatField()
    ordered        = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)
    upload_at      = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product.Nom
       
