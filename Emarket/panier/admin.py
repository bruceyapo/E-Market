from django.contrib import admin

# Register your models here.
from .models import Cart, CartItem

# Register your models here.

# Register your models here.
class CartModelAdmin(admin.ModelAdmin):
    # list_display_links = ('cart_id')
    list_display = ('id','cart_id', 'date_added')
admin.site.register(Cart, CartModelAdmin)

class CartItemModelAdmin(admin.ModelAdmin):
    # list_display_links = ('product','cart')
    list_display = ('id','product', 'cart','quantity','is_active', 'user','negotiation')
admin.site.register(CartItem, CartItemModelAdmin)