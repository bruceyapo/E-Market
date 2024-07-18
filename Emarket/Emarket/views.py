from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from authentifications.models import Utilisateur, client
from boutique.models import Produit

# from store.models import Product


def home(request):
    # Récupérer l'utilisateur connecté
    if request.user.is_authenticated:
        utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
        # Utiliser la clé étrangère pour récupérer le client associé
        clients = get_object_or_404(client, IdUtilisateur=utilisateur)
        products = Produit.objects.all().filter(is_available=True)
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        context ={
            "products": paged_products,
            "clients": clients,
            "utilisateur": utilisateur,
            }
        return render(request, 'shopping/home.html', context)
    else:
        products = Produit.objects.all().filter(is_available=True)
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        context ={
            "products": paged_products,
            }
        return render(request, 'shopping/home.html', context)