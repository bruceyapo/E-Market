import datetime
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from authentifications.models import Utilisateur, client
from boutique.models import Produit
from commande.forms import OrderForm
from commande.models import Order, OrderProduct, Payment
from panier.models import CartItem

# Create your views here.

# 

def payments(request):
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer le client associé
    clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    body = json.loads(request.body)
    order = Order.objects.get(user=clients, is_ordered=False, order_number=body['orderID'])
    payment = Payment(
        user=clients,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = clients.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        if item.negotiation:
            orderproduct.product_price = item.negotiation.PrixUnitaire
        else:
            orderproduct.product_price = item.product.PrixUnitaire
        orderproduct.ordered = True
        orderproduct.save()
    
        # orderproduct.save()

        # product = Produit.objects.get(id=item.product_id)
        # # product.stock -= item.quantity
        # product.save()

    # After processing all items, delete the cart items
    CartItem.objects.filter(user=request.user).delete()

    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)
def place_order(request, quantity= 0,):
    
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer le client associé
    clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user, is_active=True)
    
    
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    totales = []
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        if cart_item.negotiation:
            totale = (cart_item.negotiation.PrixUnitaire * cart_item.quantity)
            totales.append(totale)
        else:
            totale = (cart_item.product.PrixUnitaire * cart_item.quantity)
            totales.append(totale)
        quantity += cart_item.quantity
        total = sum(totales)
    tax = (2* total)/100
    grand_total = total + tax 
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = clients
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            # généer un numéro de commande
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(order_number=order_number, user=clients, is_ordered=False)
            context = {
                        'order': order,
                    'cart_items': cart_items,
                    'grand_total': grand_total,
                    'tax': tax,
                    'total': total,
                    'clients': clients,
                    'utilisateur': utilisateur,
                    
                    }
            return render(request, 'shopping/Orders/payments.html', context)
    else:
        return redirect('checkout')
    
def order_complete(request):
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer le client associé
    clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)
        
        subTotal = 0
        for i in ordered_products:
            subTotal += i.product_price * i.quantity 
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subTotal': subTotal,
            'clients': clients,
            'utilisateur': utilisateur,
        }
        return render(request, 'shopping/Orders/order_complete.html', context)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')
