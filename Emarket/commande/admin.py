from django.contrib import admin

from .models import Payment, Order, OrderProduct

# Register your models here.

# Register your models here.
# class PaymentModelAdmin(admin.ModelAdmin):
    # list_display_links = ('cart_id')
    # list_display = ('order_number','cart_id', 'date_added')
admin.site.register(Payment)


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields =('payment', 'user','product', 'quantity', 'product_price', 'ordered')
    extra = 0
    
class OrderModelAdmin(admin.ModelAdmin):
    # list_display_links = ('product','cart')
    list_display = ('order_number','full_name', 'user', 'phone','email','city', 'order_total','tax','status','is_ordered', 'created_at')
    list_filter  = ('status','is_ordered')
    search_fields= ('order_number', 'first_name','last_name','phone','email')
    list_per_page = 20
    inlines = [OrderProductInline]
admin.site.register(Order, OrderModelAdmin)


    # list_display_links = ('product','cart')
    # list_display = ('id','product', 'cart','quantity','is_active', 'user')
admin.site.register(OrderProduct)
