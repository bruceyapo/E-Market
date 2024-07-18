from django.shortcuts import get_object_or_404, redirect, render

# from carts.models import Cart, CartItem
# from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from authentifications.models import Utilisateur, client
from boutique.models import Negotiation, Produit
from panier.models import Cart, CartItem

# Create your views here.

def _cart_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


# def add_to_cart(request, product_id):
#     current_user = request.user
#     utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
#     products = Produit.objects.get(id=product_id)  # retrieve the product
#     prix_convenu = request.GET.get('price', products.PrixUnitaire)  # Obtenir le prix convenu
#     prix_convenu= float(prix_convenu)
#     if current_user.is_authenticated:
#         try:
#             negotiation = Negotiation.objects.get(product = products, user = utilisateur, PrixUnitaire = products.PrixUnitaire, PrixNegocie = 0)
#             if negotiation:
#                 negotiation.PrixNegocie = prix_convenu
#                 negotiation.save()
#             cart = Cart.objects.get(cart_id=_cart_id(request))
#         except Cart.DoesNotExist:
#             cart = Cart.objects.create(
#                 cart_id=_cart_id(request),
#             )
#             cart.save()
#         # Get the current cart item or create a new one
        
#         try:
#             cart_item = CartItem.objects.get(product=products, user=current_user, cart=cart)
#             cart_item.quantity += 1
#             cart_item.save()
#         except CartItem.DoesNotExist:
#             cart_item = CartItem.objects.create(
#                 product=products,
#                 user=current_user,
#                 cart=cart,
#                 quantity=1  # Ensure quantity is set to 1 for new items
#             )
#             cart_item.save()
#         return redirect('cart')
#     else:
#         try:
#             cart = Cart.objects.get(cart_id=_cart_id(request))
#         except Cart.DoesNotExist:
#             cart = Cart.objects.create(
#                 cart_id=_cart_id(request),
#             )
#             cart.save()
            
#         try:
#             cart_item = CartItem.objects.get(product=products, cart=cart)
#             cart_item.quantity += 1
#             cart_item.save()
#         except CartItem.DoesNotExist:
#             cart_item = CartItem.objects.create(
#                 product=products,
#                 cart=cart,
#                 quantity=1  # Ensure quantity is set to 1 for new items
#             )
#             cart_item.save()
#         return redirect('cart')

def add_to_cart(request, product_id):
    current_user = request.user
    products = Produit.objects.get(id=product_id)  # retrieve the product
    if current_user.is_authenticated:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request),
            )
            cart.save()
        # Get the current cart item or create a new one
        
        try:
            cart_item = CartItem.objects.get(product=products, user=current_user, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=products,
                user=current_user,
                cart=cart,
                quantity=1  # Ensure quantity is set to 1 for new items
            )
            cart_item.save()
        return redirect('cart')
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request),
            )
            cart.save()
            
        try:
            cart_item = CartItem.objects.get(product=products, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=products,
                cart=cart,
                quantity=1  # Ensure quantity is set to 1 for new items
            )
            cart_item.save()
        return redirect('cart')

@login_required(login_url='connexion')
def add_to_cart_neg(request, product_id):
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    produit = get_object_or_404(Produit, id=product_id)  # Récupérer le produit
    current_user = request.user
    prix_convenu = request.GET.get('price', produit.PrixUnitaire)  # Obtenir le prix convenu
    prix_convenu= float(prix_convenu)
    if current_user.is_authenticated:
        negotiation = Negotiation.objects.get(product = produit, user = utilisateur, PrixUnitaire = 0)
        if negotiation :
            negotiation.PrixUnitaire = prix_convenu
            negotiation.save()
            
        else:
            print("ERREUR")
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        # Ajouter l'article au panier
        cart_item, created = CartItem.objects.get_or_create(
            product=produit,
            negotiation= negotiation,
            user=current_user,
            cart=cart,
            defaults={'quantity': 1,}  # Assurez-vous d'ajouter 'price' à votre modèle CartItem
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()

    else:
        negotiation = Negotiation.objects.get(product = produit, PrixUnitaire = 0)
        if negotiation:
            negotiation.PrixUnitaire = prix_convenu
            negotiation.save()
        else:
            print("ERREUR")  
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        cart_item, created = CartItem.objects.get_or_create(
            product=produit,
            negotiation= negotiation,
            cart=cart,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()

    # messages.success(request, "Produit ajouté au panier avec succès.")
    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    products = get_object_or_404(Produit, id=product_id)
   
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=products, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))  
            cart_item = CartItem.objects.get(product=products, cart=cart, id=cart_item_id) 
        # cart_item = CartItem.objects.get(product=products, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    products = get_object_or_404(Produit, id=product_id)
    
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=products, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=products, cart=cart, id= cart_item_id)
    cart_item.delete()
    return redirect('cart')


# def cart(request, total=0, quantity=0, cart_items=None):
#     if request.user.is_authenticated:
#     # Récupérer l'utilisateur connecté
#         utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
#         # Utiliser la clé étrangère pour récupérer le client associé
#         clients = get_object_or_404(client, IdUtilisateur=utilisateur)
#         try:
#             tax = 0
#             grand_total = 0
#             if request.user.is_authenticated:
#                 cart_items = CartItem.objects.filter(user=request.user, is_active=True)
#             else:
#                 cart = Cart.objects.get(cart_id=_cart_id(request))
#                 cart_items = CartItem.objects.filter(cart=cart, is_active=True)
#                 if cart_items.negotiation is not None:
#                     for cart_item in cart_items:
#                         total += (cart_item.negotiation.PrixUnitaire * cart_item.quantity)
#                         quantity += cart_item.quantity
#                         sub_total += cart_item.negotiation.PrixUnitaire *cart_item.quantity
#                 else:
#                     for cart_item in cart_items:
#                         total += (cart_item.product.PrixUnitaire * cart_item.quantity)
#                         quantity += cart_item.quantity
#                         sub_total = cart_item.product.PrixUnitaire * cart_item.quantity
#                 tax = (2* total)/100
#                 grand_total = total + tax
#                 # cart_item.total = (cart_item.product.price * cart_item.quantity)
#         except ObjectDoesNotExist:
#             pass
#         context ={
#             "sub_total":sub_total,
#             "total": total, 
#             "quantity": quantity,
#             "cart_items": cart_items,
#             "grand_total":grand_total,
#             "tax": tax,
#             "clients": clients,
#             "utilisateur": utilisateur,
#             }
        
#         return render(request, 'shopping/store/cart.html',context)
#     else:
#         # utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
#         # # Utiliser la clé étrangère pour récupérer le client associé
#         # clients = get_object_or_404(client, IdUtilisateur=utilisateur)
#         try:
#             tax = 0
#             grand_total = 0
#             if request.user.is_authenticated:
#                 cart_items = CartItem.objects.filter(user=request.user, is_active=True)
#             else:
#                 cart = Cart.objects.get(cart_id=_cart_id(request))
#                 cart_items = CartItem.objects.filter(cart=cart, is_active=True)
#             for cart_item in cart_items:
#                 total += (cart_item.negotiation.PrixNegocie * cart_item.quantity)
#                 quantity += cart_item.quantity
#             tax = (2* total)/100
#             grand_total = total + tax
#                 # cart_item.total = (cart_item.product.price * cart_item.quantity)
#         except ObjectDoesNotExist:
#             pass
#         context ={
#             "total": total, 
#             "quantity": quantity,
#             "cart_items": cart_items,
#             "grand_total":grand_total,
#             "tax": tax,
#             # "clients": clients,
#             # "utilisateur": utilisateur,
#             }
        
#         return render(request, 'shopping/store/cart.html',context)

def cart(request, total=0, quantity=0, cart_items=None):
    # sub_total = 0  # Initialisation de sub_total

    if request.user.is_authenticated:
        # Récupérer l'utilisateur connecté
        utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
        # Utiliser la clé étrangère pour récupérer le client associé
        clients = get_object_or_404(client, IdUtilisateur=utilisateur)

        try:
            tax = 0
            grand_total = 0
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            
            for cart_item in cart_items:
                if cart_item.negotiation:
                    total += (cart_item.negotiation.PrixUnitaire * cart_item.quantity)
                    # sub_total += (cart_item.negotiation.PrixUnitaire * cart_item.quantity)
                else:
                    total += (cart_item.product.PrixUnitaire * cart_item.quantity)
                    # sub_total += (cart_item.product.PrixUnitaire * cart_item.quantity)
                quantity += cart_item.quantity

            tax = (2 * total) / 100
            grand_total = total + tax

        except ObjectDoesNotExist:
            pass

        context = {
            # "sub_total": sub_total,
            "total": total,
            "quantity": quantity,
            "cart_items": cart_items,
            "grand_total": grand_total,
            "tax": tax,
            "clients": clients,
            "utilisateur": utilisateur,
        }
        
        return render(request, 'shopping/store/cart.html', context)
    else:
        try:
            tax = 0
            grand_total = 0
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
            for cart_item in cart_items:
                if cart_item.negotiation:
                    total += (cart_item.negotiation.PrixNegocie * cart_item.quantity)
                    # sub_total += (cart_item.negotiation.PrixNegocie * cart_item.quantity)
                else:
                    total += (cart_item.product.PrixUnitaire * cart_item.quantity)
                    # sub_total += (cart_item.product.PrixUnitaire * cart_item.quantity)
                quantity += cart_item.quantity

            tax = (2 * total) / 100
            grand_total = total + tax

        except ObjectDoesNotExist:
            pass

        context = {
            # "sub_total": sub_total,
            "total": total,
            "quantity": quantity,
            "cart_items": cart_items,
            "grand_total": grand_total,
            "tax": tax,
        }
        
        return render(request, 'shopping/store/cart.html', context)

@login_required(login_url='connexion')
def checkout(request, total=0, quantity=0, cart_items=None):
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer le client associé
    clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            if cart_item.negotiation:
                total += (cart_item.negotiation.PrixUnitaire * cart_item.quantity)
            else:
                total += (cart_item.product.PrixUnitaire * cart_item.quantity)    
            quantity += cart_item.quantity
        tax = (2* total)/100
        grand_total = total + tax
            # cart_item.total = (cart_item.product.price * cart_item.quantity)
    except ObjectDoesNotExist:
        pass
    context ={
        "total": total, 
        "quantity": quantity,
        "cart_items": cart_items,
        "grand_total":grand_total,
        "tax": tax,
        "clients": clients,
        "utilisateur": utilisateur,
        }
    return render(request, 'shopping/store/checkout.html', context)
