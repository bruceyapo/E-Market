from django.contrib import admin

from boutique.models import Negotiation, Produit, ReviewRating, Stock

class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('id','Nom', 'slug','PrixUnitaire','IdCategorie', 'modified_date','is_available')
    prepopulated_fields ={'slug': ('Nom',)}
    list_display_links = ('slug','Nom')
admin.site.register(Produit, ProductModelAdmin)

admin.site.register(ReviewRating)

class StockModelAdmin(admin.ModelAdmin):
    list_display = ('IdProduit', 'QuantiteStock','Date')
admin.site.register(Stock,StockModelAdmin)

class NegotiationModelAdmin(admin.ModelAdmin):
    list_display = ('id','product', 'user', 'PrixUnitaire')
admin.site.register(Negotiation,NegotiationModelAdmin)
