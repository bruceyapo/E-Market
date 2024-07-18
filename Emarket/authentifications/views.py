

from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.http import require_POST
import requests

from commande.models import Order, OrderProduct
from myapp.models import Vente
from panier.models import Cart, CartItem
from panier.views import _cart_id
from .forms import AdminForm,GestStockUpdateForm, UserForm, UserProfileForm, VendeurForm, ClientRegisterForm,LoginForm, VendeurUpdateForm, GesteionnaireStockForm
from .models import Adminitrateur, UserProfile, Utilisateur, Vendeur, client, GesteionnaireStock
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
import pdfkit
from reportlab.pdfgen import canvas
from django.db.models import Sum, Count,F
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
import csv
from django.db.models import QuerySet
import pandas as pd
from django.forms import inlineformset_factory
from django.utils import timezone
from django.db.models.functions import ExtractMonth, ExtractYear, Cast
from django.db.models.fields import DateField
from datetime import datetime,timedelta
from django.db import IntegrityError

@login_required(login_url='connexion')
def accueiladmin(request):
    user = request.user
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)

    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    administrateur = get_object_or_404(Adminitrateur, IdUtilisateur=utilisateur)
    # Meilleur produit vendu
    best_product = Vente.objects.values('IdProduit__Nom').annotate(total_sold=Sum('QuantiteVendu')).order_by('-total_sold').first()

    # Meilleur employé
    best_employee = Vente.objects.values('IdVendeur__nom', 'IdVendeur__prenoms').annotate(total_sales=Sum('MontantTotal')).order_by('-total_sales').first()

    # Top 5 des meilleurs clients
    top_clients = Vente.objects.values('IdClient__nom', 'IdClient__prenoms').annotate(total_purchases=Count('IdClient')).order_by('-total_purchases')[:5]
    # Récupérer la date et l'heure actuelles
    now = timezone.now()
    
    ventes = Vente.objects.filter().order_by('-DateVente')[:20]
    # Filtrer les ventes en fonction du vendeur
    # ventes = Vente.objects.filter(IdVendeur=vendeur.id).select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
    nombre_total_ventes = ventes.count()
    
    total_ventes = Vente.objects.all()
    nombre_total_vente = total_ventes.count()
    # Calculer la date et l'heure il y a 24 heures
    twenty_four_hours_ago = now - timedelta(hours=24)

    # Récupérer les ventes réalisées en moins de 24 heures
    ventes_par_jour = Vente.objects.filter(DateVente__gte=twenty_four_hours_ago)
    nombre_ventes_par_jour = ventes_par_jour.count()
    # Calcul du pourcentage de ventes par jour, arrondi à deux chiffres après la virgule
    pourc_ventes_par_jour = round((nombre_ventes_par_jour * 100) / nombre_total_vente, 2)
    
    paginator = Paginator(ventes, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    ventes = paginator.get_page(page_number)
    context = {
        'utilisateur': utilisateur,
        'administrateur': administrateur,
        'best_product': best_product,
        'best_employee': best_employee,
        'top_clients': top_clients,
        'pourc_ventes_par_jour':pourc_ventes_par_jour
    }
    messages.success(request,f"Heureux de vous revoir M/Mme/Mlle {administrateur.prenoms} {administrateur.nom}")
    return render(request, 'app/admin/accueiladmin.html',locals())



@login_required(login_url='connexion')
def accueilvendeur(request):
    user = request.user
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    vendeur = get_object_or_404(Vendeur, IdUtilisateur=utilisateur)
    now = timezone.now()
    # Calculer la date et l'heure il y a 24 heures
    twenty_four_hours_ago = now - timedelta(hours=24)
    # Récupérer les ventes réalisées en moins de 24 heures en fonction du vendeur
    ventes = Vente.objects.filter(IdVendeur=vendeur.id).order_by('-DateVente')[:20].select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
    # ventes = Vente.objects.filter(IdVendeur=vendeur.id, DateVente__gte=twenty_four_hours_ago).select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
    nombre_total_ventes = ventes.count()
    status_code = 'En attente'
    orders_status = Order.objects.filter(status=status_code)
    orders_status_count = orders_status.count()
    
    paginator = Paginator(ventes, 25)  # Affiche 25 ventes par page
    page_number = request.GET.get('page')
    ventes = paginator.get_page(page_number)
    context = {
        'utilisateur': utilisateur,
        'vendeur': vendeur,
        
    }
    messages.success(request,f"Heureux de vous revoir M/Mme/Mlle {vendeur.prenoms} {vendeur.nom}")
    return render(request, 'app/Vendeur/accueilvendeur.html',locals())

@login_required(login_url='connexion')
def accueilGestionnaireStock(request):
    user = request.user
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    gestionnaireStock = get_object_or_404(GesteionnaireStock, IdUtilisateur=utilisateur)
    context = {
        'utilisateur': utilisateur,
        'gestionnaireStock': gestionnaireStock,
    }
    messages.success(request,f"Heureux de vous revoir M/Mme/Mlle {gestionnaireStock.prenoms} {gestionnaireStock.nom}")
    return render(request, 'app/GestionnaireStock/accueilGesteionnaireStock.html',locals())

@login_required(login_url='connexion')
def dashboard(request):
    user = request.user
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    orders = Order.objects.order_by('-created_at').filter(user_id=clients.id, is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user=clients) 
   
    context = {
        'utilisateur': utilisateur,
        'clients': clients,
        'orders_count': orders_count,
        'userprofile':userprofile
    }
    messages.success(request,f"Heureux de vous revoir M/Mme/Mlle {clients.prenoms} {clients.nom}")
    return render(request, 'shopping/accounts/dashboard.html', context)

# @login_required(login_url='connexion')
# @csrf_exempt
# def inscription_Client(request):
#     # if request.method == 'POST':
#     form = ClientRegisterForm(request.POST, request.FILES)
#     if form.is_valid():
#         email = form.cleaned_data['email']
#         password = form.cleaned_data['password']
#         confirm_password = form.cleaned_data['confirm_password']
#         # Vérification de l'existence de l'email
#         if password and confirm_password and password != confirm_password:
#             messages.warning(request,"Les mots de passe ne correspondent pas.")
#             return render(request, 'shopping/accounts/register.html', {'form': form})
#         elif Utilisateur.objects.filter(email=email).exists():
#             messages.warning(request, "Un utilisateur avec cet email existe déjà.")
#             return render(request, 'shopping/accounts/register.html', {'form': form})
#         elif form.is_valid():
#             form.save()
#             messages.success(request,"Inscription réussi")
#             form = ClientRegisterForm()
#             return redirect('connexion')
#         # Redirection ou autres actions
#         # else:
#         #     messages.warning(request,"Données d'entrée invalides")
#             # form = VendeurForm()
#     return render(request, 'shopping/accounts/register.html', {'form': form})

@csrf_exempt
def inscription_Client(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Inscription réussie")
            return redirect('connexion')
        else:
            messages.warning(request, "Données d'entrée invalides")
    else:
        form = ClientRegisterForm()
    return render(request, 'shopping/accounts/register.html', {'form': form})
# Fonction de vue de connexion

# @csrf_exempt
# def connexion(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                 # Redirection en fonction du rôle de l'utilisateur
                if user.roles == 'Administratuer':
                    next_url = request.GET.get('next', reverse('accueiladmin'))  # 'home' est le nom de l'URL de la page d'accueil
                    return redirect(next_url)
                    # return redirect('')  # Redirigez vers la page d'accueil après la connexion
                elif user.roles == 'Vendeur':
                    next_url = request.GET.get('next', reverse('accueilvendeur'))  # 'home' est le nom de l'URL de la page d'accueil
                    return redirect(next_url)
                elif user.roles == 'GesteionnaireStock':
                    next_url = request.GET.get('next', reverse('accueilGestionnaireStock'))  # 'home' est le nom de l'URL de la page d'accueil
                    return redirect(next_url)
                elif user.roles == 'Client':
                    next_url = request.GET.get('next', reverse('dashboard'))  # 'home' est le nom de l'URL de la page d'accueil
                    return redirect(next_url)
                    # return redirect('ventes')  # Remplacez 'seller_dashboard' par le nom de l'URL de votre tableau de bord Vendeur
            else:
                messages.warning(request,"Adresse email ou mot de passe incorrect")
    else:
        form = LoginForm()
    return render(request, 'shopping/accounts/login.html', {'form': form})
# Vue de déconnexion

@csrf_exempt
def connexion(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                

                # Récupérer le panier actuel (non connecté) de la session
                cart_id = _cart_id(request)
                try:
                    cart = Cart.objects.get(cart_id=cart_id)
                except Cart.DoesNotExist:
                    cart = None

                # Si un panier existe pour la session, attribuez-le à l'utilisateur connecté
                if cart:
                    cart_items = CartItem.objects.filter(cart=cart)
                    for item in cart_items:
                        # Vérifier si l'utilisateur a déjà cet article dans son panier
                        try:
                            user_cart_item = CartItem.objects.get(product=item.product, user=user)
                            user_cart_item.quantity += item.quantity
                            user_cart_item.save()
                        except CartItem.DoesNotExist:
                            item.user = user
                            item.cart = None  # Retirer la référence de l'ancien panier de session
                            item.save()

                    # Supprimer le panier de session après l'attribution des articles
                    # cart.delete()
                login(request, user)
                # Redirection en fonction du rôle de l'utilisateur
                if user.roles == 'Administrateur':
                    next_url = request.GET.get('next', reverse('accueiladmin'))
                    return redirect(next_url)
                elif user.roles == 'Vendeur':
                    next_url = request.GET.get('next', reverse('accueilvendeur'))
                    return redirect(next_url)
                elif user.roles == 'GestionnaireStock':
                    next_url = request.GET.get('next', reverse('accueilGestionnaireStock'))
                    return redirect(next_url)
                elif user.roles == 'Client':
                        url = request.META.get('HTTP_REFERER')
                        try:
                            query = requests.utils.urlparse(url).query
                            params = dict(x.split('=') for x in query.split('&'))
                            print(params)
                            if 'next' in params:
                                nextPage = params['next']
                            return redirect(nextPage)
                        except:
                            next_url = request.GET.get('next', reverse('dashboard'))
                            return redirect(next_url)
            else:
                messages.warning(request, "Adresse email ou mot de passe incorrect")
    else:
        form = LoginForm()
    return render(request, 'shopping/accounts/login.html', {'form': form})

def deconnexion(request):
    logout(request)
    messages.success(request,f"vous êtes déconnecté")
    return redirect('connexion')  # Redirige vers la page de connexion après la déconnexion

@login_required(login_url='connexion')
def inscription_vendeur(request):
    # if request.method == 'POST':
    form = VendeurForm(request.POST, request.FILES)
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']
        # Vérification de l'existence de l'email
        if password and confirm_password and password != confirm_password:
            messages.warning(request,"Les mots de passe ne correspondent pas.")
            return render(request, 'app/authentification/inscription_vendeur.html', {'form': form})
        elif Utilisateur.objects.filter(email=email).exists():
            messages.warning(request, "Un utilisateur avec cet email existe déjà.")
            return render(request, 'app/authentification/inscription_vendeur.html', {'form': form})
        elif form.is_valid():
            form.save()
            messages.success(request,"Vendeur enregistré avec success")
            form = VendeurForm()
            return redirect('liste_vendeur')
        # Redirection ou autres actions
        # else:
        #     messages.warning(request,"Données d'entrée invalides")
            # form = VendeurForm()
    return render(request, 'app/authentification/inscription_vendeur.html', {'form': form})

@login_required(login_url='connexion')
def inscription_GestionnaireStock(request):
    if request.method == 'POST':
        form = VendeurForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Inscription réussie")
            return redirect('liste_vendeur')
        else:
            messages.warning(request, "Données d'entrée invalides")
    else:
        form = VendeurForm()
    return render(request, 'app/authentification/inscription_vendeur.html', {'form': form})
 
def inscription_admin(request):
    form = AdminForm(request.POST, request.FILES)
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']
        # Vérification de l'existence de l'email
        if password and confirm_password and password != confirm_password:
            messages.warning(request,"Les mots de passe ne correspondent pas.")
        elif Utilisateur.objects.filter(email=email).exists():
            messages.warning(request, "Un utilisateur avec cet email existe déjà.")
    
        elif form.is_valid():
            form.save()
            messages.success(request,"Adminitrateur enregistré avec success")
            form = AdminForm()
            return redirect ('connexion')
    return render(request, 'app/authentification/inscription_admin.html', {'form': form})

# @login_required(login_url='connexion')
# def inscription_GestionnaireStock(request):
#     form = GesteionnaireStockForm(request.POST, request.FILES)
#     if form.is_valid():
#         email = form.cleaned_data['email']
#         password = form.cleaned_data['password']
#         confirm_password = form.cleaned_data['confirm_password']
#         # Vérification de l'existence de l'email
#         if password and confirm_password and password != confirm_password:
#             messages.warning(request,"Les mots de passe ne correspondent pas.")
#         elif Utilisateur.objects.filter(email=email).exists():
#             messages.warning(request, "Un utilisateur avec cet email existe déjà.")
    
#         elif form.is_valid():
#             form.save()
#             messages.success(request,"Gesteionnaire de Stock enregistré avec success")
#             form = GesteionnaireStockForm()
#     return render(request, 'app/authentification/inscription_GesteionnaireStock.html', {'form': form})

# @csrf_exempt
@login_required(login_url='connexion')
def inscription_GestionnaireStock(request):
    if request.method == 'POST':
        form = GesteionnaireStockForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Inscription réussie")
            return redirect('liste_geststock')
        else:
            messages.warning(request, "Données d'entrée invalides")
    else:
        form = GesteionnaireStockForm()
    return render(request, 'app/authentification/inscription_GesteionnaireStock.html', {'form': form})
 


@login_required(login_url='connexion')
def my_orders(request):
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    orders = Order.objects.order_by('-created_at').filter(user_id=clients.id, is_ordered=True)
    context = {
        'orders': orders,
        'clients': clients,
        'utilisateur': utilisateur,
    }
    return render(request, 'shopping/accounts/my_orders.html', context)


# @login_required(login_url='connexion')
# def edit_profile(request):
#     userprofile = get_object_or_404(UserProfile, user=request.user)
#     if request.method == 'POST':
#         user_form = UserForm(request.POST, instance=request.user)
#         profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, 'Profile updated successfully')
#             return redirect('edit_profile')
#         else:
#             messages.error(request, 'Error updating profile')
#     else:
#         user_form = UserForm(instance=request.user)
#         profile_form = UserProfileForm(instance=userprofile)
    
#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'userprofile': userprofile
#     }
#     return render(request, 'shopping/accounts/edit_profile.html', context)

@login_required(login_url='connexion')
def edit_profile(request):
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer le client associé
    clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    
    # Récupérer ou créer le UserProfile associé au client
    userprofile, created = UserProfile.objects.get_or_create(user=clients)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=clients)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Error updating profile')
    else:
        user_form = UserForm(instance=clients)
        profile_form = UserProfileForm(instance=userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
        'clients': clients,
        'utilisateur': utilisateur,
    }
    return render(request, 'shopping/accounts/edit_profile.html', context)


@login_required(login_url='connexion')
def orders_detail(request, order_id):
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    orders_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subTotal = 0
    for i in orders_detail:
        subTotal += i.product_price * i.quantity 
    context = {
        'orders_detail': orders_detail,
        'order': order,
        'subTotal': subTotal,
        'clients': clients,
        'utilisateur': utilisateur,
    }
    return render(request, 'shopping/accounts/orders_detail.html', context)