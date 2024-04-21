from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.http import require_POST
from .forms import AdminForm, AjoutCategorieForm, AjoutProduitForm, GestStockUpdateForm, StockUpdateForm, UploadFileForm, VendeurForm,ClientForm,LoginForm, VendeurUpdateForm, VenteForm, GesteionnaireStockForm, VerifClientForm
from .models import Adminitrateur, Notification, Recu, Utilisateur, Vendeur, client, CategorieProduit, Produit, Vente, Stock, GesteionnaireStock
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
from datetime import datetime






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
    context = {
        'utilisateur': utilisateur,
        'administrateur': administrateur,
        'best_product': best_product,
        'best_employee': best_employee,
        'top_clients': top_clients,
    }
    
    return render(request, 'app/admin/accueiladmin.html',locals())

@login_required(login_url='connexion')
def liste_vendeur(request):
    vendeurs = Vendeur.objects.all().select_related('IdUtilisateur')
    nombre_total_vendeur = vendeurs.count()
    paginator = Paginator(vendeurs, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    vendeurs = paginator.get_page(page_number)
    return render(request, 'app/admin/liste_vendeur.html',locals())

def supprimer_vendeur(request, vendeur_id):
    vendeur = Vendeur.objects.get(id=vendeur_id)
    vendeur.delete()
    messages.success(request, f'Le Vendeur {vendeur.nom} a été supprimée avec succès.')
    return redirect('liste_vendeur')

@login_required(login_url='connexion')
def modif_vendeur(request, vendeur_id):
    vendeur = get_object_or_404(Vendeur, pk=vendeur_id)
    if request.method == 'POST':
        form = VendeurUpdateForm(request.POST, request.FILES, instance=vendeur)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Utilisateur.objects.filter(email=email).exists():
                messages.warning(request, "Un utilisateur avec cet email existe déjà.")
                return render(request, 'app/authentification/modif_vendeur.html', {'form': form})
            elif form.is_valid():
                form.save()
                messages.success(request, 'Les informations du vendeur ont été mises à jour avec succès.')
                return redirect('liste_vendeur')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = VendeurUpdateForm(instance=vendeur)
    return render(request, 'app/authentification/modif_vendeur.html', {'form': form,'vendeur': vendeur})


@login_required(login_url='connexion')
def liste_client(request):
    # vendeurs = client.objects.all().select_related('IdUtilisateur')
    clients = client.objects.all()
    nombre_total_client = clients.count()
    paginator = Paginator(clients, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)
    return render(request, 'app/admin/liste_client.html',locals())


def liste_produit_categorie(request):
    # liste des produits
    produits = Produit.objects.all().select_related('IdCategorie')
    nombre_total_produit = produits.count()
    paginator = Paginator(produits, 10)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)
    
    # liste des categories de produit
    categories_produit = CategorieProduit.objects.all()
    nombre_total_categorie_produit = categories_produit.count()
    paginator = Paginator(categories_produit, 10)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    categories_produit = paginator.get_page(page_number)
    return render(request, 'app/admin/liste_produit.html',locals())

@login_required(login_url='connexion')
def AjoutCategoriet(request):
    # if request.method == 'POST':
    form = AjoutCategorieForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request,"Categorie produit enregistré avec success")
        form = AjoutCategorieForm()
        return redirect('liste_produit_categorie')
        # Redirection ou autres actions
    else:
        form = AjoutCategorieForm()
    return render(request, 'app/admin/AjoutCategoriet.html', {'form': form})

def supprimer_categorie(request, categorie_id):
    Categorie = CategorieProduit.objects.get(id=categorie_id)
    Categorie.delete()
    messages.success(request, f'La Categorie {Categorie.nom} a été supprimée avec succès.')
    return redirect('liste_produit_categorie')

@login_required(login_url='connexion')
def modif_categorie(request, categorie_id):
    categorie = get_object_or_404(CategorieProduit, pk=categorie_id)  # Assurez-vous que le vendeur appartient à l'utilisateur connecté
    form = AjoutCategorieForm(request.POST or None, instance=categorie)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"La categorie {categorie.nom} ont été mises à jour avec succès.")
            return redirect('liste_produit_categorie')  # Remplacez 'liste_vendeur' par le nom réel de votre vue qui affiche la liste des vendeurs
    else:
        # Le formulaire est pré-rempli avec les informations existantes du vendeur
        form = AjoutCategorieForm(instance=categorie)
    return render(request, 'app/admin/modif_categorie.html', {'form': form, 'categorie': categorie})

@login_required(login_url='connexion')
def AjoutProduit(request):
    # if request.method == 'POST':
    form = AjoutProduitForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request,"Produit enregistré avec success")
        form = AjoutProduitForm()
        return redirect('liste_produit_categorie')
        # Redirection ou autres actions
    else:
        form = AjoutProduitForm()
    return render(request, 'app/admin/AjoutProduit.html', {'form': form})


@login_required(login_url='connexion')
def modif_produit(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id,)  # Assurez-vous que le vendeur appartient à l'utilisateur connecté
    form = AjoutProduitForm(request.POST or None, instance=produit)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Produit a été mises à jour avec succès.")
            return redirect('liste_produit_categorie')  # Remplacez 'liste_vendeur' par le nom réel de votre vue qui affiche la liste des vendeurs
    else:
        # Le formulaire est pré-rempli avec les informations existantes du vendeur
        form = AjoutProduitForm(instance=produit)
    return render(request, 'app/admin/modif_produit.html', {'form': form, 'produit': produit})

def supprimer_produit(request, produit_id):
    produit = Produit.objects.get(id=produit_id)
    produit.delete()
    messages.success(request, f'Le produit {produit.Nom} a été supprimée avec succès.')
    return redirect('liste_produit_categorie')


def liste_geststock(request):
    GestStocks = GesteionnaireStock.objects.all().select_related('IdUtilisateur')
    nombre_total_GestStock = GestStocks.count()
    paginator = Paginator(GestStocks, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    GestStocks = paginator.get_page(page_number)
    return render(request, 'app/admin/liste_geststock.html',locals())

@login_required(login_url='connexion')
def modif_geststock(request, geststock_id):
    geststock = get_object_or_404(GesteionnaireStock, pk=geststock_id)
    if request.method == 'POST':
        form = GestStockUpdateForm(request.POST, request.FILES, instance=geststock)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Utilisateur.objects.filter(email=email).exists():
                messages.warning(request, "Un utilisateur avec cet email existe déjà.")
                return render(request, 'app/authentification/modif_geststock.html', {'form': form})
            elif form.is_valid():
                form.save()
                messages.success(request, 'Les informations du gestionnaire de stock ont été mises à jour avec succès.')
                return redirect('liste_geststock')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = GestStockUpdateForm(instance=geststock)
    return render(request, 'app/authentification/modif_geststock.html', {'form': form,'geststock': geststock})

def supprimer_geststock(request, geststock_id):
    geststock = GesteionnaireStock.objects.get(id=geststock_id)
    geststock.delete()
    messages.success(request, f'Le Gesteionnaire de Stock {geststock.nom} a été supprimée avec succès.')
    return redirect('liste_geststock')


@login_required(login_url='connexion')
def accueilvendeur(request):
    user = request.user
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    
    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    vendeur = get_object_or_404(Vendeur, IdUtilisateur=utilisateur)
    
    context = {
        'utilisateur': utilisateur,
        'vendeur': vendeur,
    }
    print(vendeur.image)
    print(context['utilisateur'])
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
    return render(request, 'app/GestionnaireStock/accueilGesteionnaireStock.html',locals())

# Fonction de vue de connexion

@csrf_exempt
def connexion(request):
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
                    # return redirect('ventes')  # Remplacez 'seller_dashboard' par le nom de l'URL de votre tableau de bord Vendeur
            else:
                messages.warning(request,"Adresse email ou mot de passe incorrect")
    else:
        form = LoginForm()
    return render(request, 'app/authentification/connexion.html', {'form': form})

# Vue de déconnexion
def deconnexion(request):
    logout(request)
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
    return render(request, 'app/authentification/inscription_admin.html', {'form': form})

@login_required(login_url='connexion')
def inscription_GestionnaireStock(request):
    form = GesteionnaireStockForm(request.POST, request.FILES)
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
            messages.success(request,"Gesteionnaire de Stock enregistré avec success")
            form = GesteionnaireStockForm()
    return render(request, 'app/authentification/inscription_GesteionnaireStock.html', {'form': form})

@login_required(login_url='connexion')
def visuels(request):
    user = request.user
    
    # Convertir DateVente en DateField
    # Vente.objects.update(DateVente=Cast('DateVente', output_field=DateField()))

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
    
    # Agrégation pour obtenir le nombre total de ventes par mois/année
    sales_by_date = Vente.objects.annotate(
        month=ExtractMonth('DateVente'),
        year=ExtractYear('DateVente')
    ).values('year', 'month').annotate(
        total_sales=Count('id'),
    ).order_by('year', 'month')
    
    ventes = Vente.objects.annotate(
    mois=ExtractMonth('DateVente'),
    annee=ExtractYear('DateVente')
    ).values('mois', 'annee').annotate(
        chiffre_affaires=Sum('MontantTotal')
    ).order_by('annee', 'mois')
    years_months = [f"{sale['year']}-{sale['month']}" for sale in sales_by_date]
    total_sales = [sale['total_sales'] for sale in sales_by_date]

    # Calculer le chiffre d'affaires total de toutes les ventes
    total_chiffre_affaires = Vente.objects.aggregate(total_chiffre_affaires=Sum('MontantTotal'))['total_chiffre_affaires']
    
    labels = [f"{vente['mois']}/{vente['annee']}" for vente in ventes]
    data = [vente['chiffre_affaires'] for vente in ventes]
    data = [float(vente['chiffre_affaires']) for vente in ventes]
    
    Listeventes = Vente.objects.all().select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
    nombre_total_ventes = Listeventes.count()
    
    liste_client = client.objects.all()
    nombre_total_client = liste_client.count()
  
    context = {
        'utilisateur': utilisateur,
        'administrateur': administrateur,
        'best_product': best_product,
        'best_employee': best_employee,
        'top_clients': top_clients,
        'years_months': years_months,
        'total_sales': total_sales,
        'ventes':ventes,
        'labels': labels,
        'data': data,
    }
    return render(request, 'app/admin/visuels.html', locals())

@login_required(login_url='connexion')
def calendier_admin(request):
    return render(request, 'app/admin/calendier.html')

@login_required(login_url='connexion')
def calendier_vendeur(request):
    return render(request, 'app/Vendeur/calendier.html')

@login_required(login_url='connexion')
def calendier_gestionnaireStock(request):
    return render(request, 'app/GestionnaireStock/calendier.html')

def handle_uploaded_file(file, user_id):
    # IdVendeur=request.user.id
    if file.name.endswith('.csv'):
        data = pd.read_csv(file, sep=";")
    elif file.name.endswith('.xlsx'):
        data = pd.read_excel(file)
    else:
        raise ValueError("Le fichier n'est pas un format supporté. Seuls CSV et Excel sont acceptés.")
    
    df=data.copy()   
    for index, row in df.iterrows():
        # Split le nom pour obtenir prenoms et nom
        name_parts = row['Name'].split(' ', 1)
        prenoms = name_parts[0]
        nom = name_parts[1] if len(name_parts) > 1 else ''  # Gère les noms sans prénom

        # Créer ou récupérer le client
        client_instance, created = client.objects.get_or_create(
            prenoms=prenoms, 
            nom=nom, 
            defaults={'genre': row['Gender']}
        )
        
        vendeur_instance = Vendeur.objects.get(id=user_id)
        # Créer ou récupérer la catégorie de produit
        categorie, _ = CategorieProduit.objects.get_or_create(nom=row['Type'])
        
        # Créer ou récupérer le produit
        produit, created_produit = Produit.objects.get_or_create(
            Nom=row['Produit'],
            PrixUnitaire=row['Prix'],
            IdCategorie=categorie
        )
        # stock, created_stock = Stock.objects.get_or_create(
        #     IdProduit=produit,
        #     QuantiteStock=250,
        # )
        
         # Créer la vente si le produit, le client et la catégorie n'existent pas déjà
        
        Vente.objects.create(
            IdVendeur=vendeur_instance,  # Vous devez définir l'ID du vendeur approprié
            IdClient=client_instance,
            IdProduit=produit,
            QuantiteVendu=1,  # Vous devez définir la quantité vendue appropriée
            MontantTotal=row['Prix'],
            DateVente=row['Date']
        )


@login_required(login_url='connexion')
def ventes(request):
    user = request.user.id
    vendeur = get_object_or_404(Vendeur, IdUtilisateur=user)
    # form = UploadFileForm(request.POST, request.FILES)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith('.csv'):
                # Traitement du fichier CSV avec Pandas
                handle_uploaded_file(file, vendeur.id)
                messages.success(request, "Vente enregistrée avec succès.")
                return render(request, 'app/Vendeur/ventes.html', {'form': form})

            elif file.name.endswith(('.xlsx', '.xls')):
                # Traitement du fichier Excel avec Pandas
                handle_uploaded_file(file, vendeur.id)
                messages.success(request, "Vente enregistrée avec succès.")
                return render(request, 'app/Vendeur/ventes.html', {'form': form})

            else:
                messages.warning(request, 'Le fichier doit être au format CSV ou excel')
    else:
        form = UploadFileForm()
    # Filtrer les ventes en fonction du vendeur
    ventes = Vente.objects.filter(IdVendeur=vendeur.id).select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
    nombre_total_ventes = ventes.count()
    paginator = Paginator(ventes, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    ventes = paginator.get_page(page_number)
    return render(request, 'app/Vendeur/ventes.html', {'form': form, 'ventes':ventes, 'nombre_total_ventes':nombre_total_ventes})


def get_client_details(request, client_id):
    try:
        client_obj = client.objects.get(pk=client_id)
        data = {
            'nom': client_obj.nom,
            'prenoms': client_obj.prenoms,
            'genre': client_obj.genre,
        }
        return JsonResponse(data)
    except client.DoesNotExist:
        return JsonResponse({'error': 'Client Non Trouver'}, status=404)

ProduitFormSet = inlineformset_factory(client, Vente, form=VenteForm, extra=1)
def ajout_vente(request):  
    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        
        if client_form.is_valid():
            # Vérifier si le client existe déjà
            nom = client_form.cleaned_data['nom']
            prenoms = client_form.cleaned_data['prenoms']
            genre = client_form.cleaned_data['genre']
            
            existing_client = client.objects.filter(nom=nom, prenoms=prenoms, genre=genre).first()
            
            if existing_client:
                new_client = existing_client
            else:
                new_client = client_form.save()
            
            id_user = request.user.id
            vendeur = get_object_or_404(Vendeur, IdUtilisateur=id_user)
            produit_formset = ProduitFormSet(request.POST, instance=new_client)
            if produit_formset.is_valid():
                instances = produit_formset.save(commit=False)
                error_flag = False
                
                for instance in instances:
                    produit = instance.IdProduit
                    instance.MontantTotal = produit.PrixUnitaire * instance.QuantiteVendu
                    # date_et_heure = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    # instance.DateVente = timezone.now
                    instance.IdVendeur_id = vendeur.id

                    # Vérification de la quantité en stock
                    produit_stock, _ = Stock.objects.get_or_create(IdProduit=produit)
                    if produit_stock.QuantiteStock < instance.QuantiteVendu:
                        messages.warning(request, f"La quantité en stock ({produit_stock.QuantiteStock}) est insuffisante pour la vente.")
                        error_flag = True
                        continue

                    # Vérifiez si la soustraction ne résulte pas en un nombre négatif
                    if produit_stock.QuantiteStock - instance.QuantiteVendu < 0:
                        messages.warning(request, "La quantité en stock ne peut pas être négative après la vente.")
                        error_flag = True
                        continue

                    instance.save()

                if not error_flag:
                    return redirect('recu_vente', client_id=new_client.id)

    else:
        client_form = ClientForm()
        produit_formset = ProduitFormSet()

    return render(request, 'app/Vendeur/ajout_vente.html', {'client_form': client_form, 'produit_formset': produit_formset})

def recu_vente(request, client_id):
    clients = get_object_or_404(client, id=client_id)
    # Création de l'objet datetime pour la date et l'heure actuelles
    date_et_heure = datetime.now()  # Format jour/mois/année heure:minute:seconde
    print(date_et_heure)
    ventes = Vente.objects.filter(IdClient=clients, DateVente__date=date_et_heure.date(), DateVente__time__hour=date_et_heure.hour, DateVente__time__minute=date_et_heure.minute)
    total_vente = sum(vente.MontantTotal for vente in ventes)
    # Créer une instance Recu après avoir enregistré les ventes
    recu = Recu.objects.create()
    for vente in ventes:
        vente.DateVente = date_et_heure
        vente.save()
        
        # Associer la vente au recu
        recu.IdVente.add(vente)
    
    return render(request, 'app/Vendeur/recu.html', {'client': clients, 'ventes': ventes, 'total_vente': total_vente})

def list_recu(request):
    # recu_instance = Recu.objects.all()
    # Récupère tous les reçus et filtre ceux ayant au moins une vente associée
    recu_instance = Recu.objects.annotate(vente_count=Count('IdVente')).filter(vente_count__gt=0)
    paginator = Paginator(recu_instance, 10)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    recu_instance = paginator.get_page(page_number)
    return render(request, 'app/Vendeur/list_recu.html', {'recu_instance': recu_instance})
    
    
def details_vente(request, recu_id):
    # recu_instance = Recu.objects.get(id=id)
    # ventes_associees = recu_instance.IdVente.all()
    
    recu_instance = get_object_or_404(Recu, id=recu_id)
    ventes_associees = recu_instance.IdVente.all()
    total_vente = sum(vente.MontantTotal for vente in ventes_associees)
    # Le reste de votre code...
    return render(request, 'app/Vendeur/details_vente.html', {'recu': recu_instance, 'ventes': ventes_associees, 'total_vente':total_vente})
    
    
    
# def imprimer_recu(request, vente_id):
#     vente = get_object_or_404(Vente, id=vente_id)
#     html = render_to_string('app/recu.html', {'vente': vente})  # Créez un template HTML pour le reçu
#     options = {
#         'page-size': 'Letter',
#         'encoding': 'UTF-8',
#     }
#     pdf = pdfkit.from_string(html, False, options=options)  # Génère le PDF à partir du template HTML

#     response = HttpResponse(pdf, content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="recu_vente_{vente_id}.pdf"'
#     return response
def supprimer_vente(request, vente_id):
    vente = Vente.objects.get(id=vente_id)
    vente.delete()
    messages.success(request, 'La vente a été supprimée avec succès.')
    return redirect('ventes')

# def get_product_details(request, product_id):
#     product = Produit.objects.get(id=product_id)
#     return JsonResponse({
#         'id': product.id,
#         'category': product.IdCategorie.nom,
#         'price': product.PrixUnitaire
#     })

def get_product_details(request, product_id):
    try:
        product = Produit.objects.get(id=product_id)
        stock, _ = Stock.objects.get_or_create(IdProduit=product)
        
        data = {
            'id': product.id,
            'nom': product.Nom,
            'category': product.IdCategorie.nom,
            'price': product.PrixUnitaire,
            'stock': stock.QuantiteStock
        }
        
        return JsonResponse(data)
    
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Produit non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def liste_stock(request):
    stocks = Stock.objects.all().select_related('IdProduit', 'IdProduit__IdCategorie').order_by('QuantiteStock')
    notifications = Notification.objects.filter(est_lu=False)
    paginator = Paginator(stocks, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    stocks = paginator.get_page(page_number)
    return render(request, 'app/GestionnaireStock/liste_stock.html', {'stocks': stocks, 'notifications':notifications})



@require_POST
def mark_notification_as_read(request, notification_id):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    notification = get_object_or_404(Notification, id=notification_id)  # Assurez-vous que la notification appartient à l'utilisateur
    notification.est_lu = True
    notification.save()
    
    return JsonResponse({'success': True})

# def modif_stock(request):
#     if request.method == 'POST':
#         form = StockUpdateForm(request.POST)
#         if form.is_valid():
#             # for produit in form.cleaned_data:
#             #     quantity = form.cleaned_data[produit]
#             #     produit_id = produit.split('_')[1]
                
#             #     stock_item = Stock.objects.get(IdProduit=produit_id)
#             #     stock_item.QuantiteStock = quantity
#             form.save()
            
#             return redirect('liste_stock')  # Remplacez 'home' par l'URL de votre page d'accueil
#     else:
#         form = StockUpdateForm()
    
#     return render(request, 'app/modif_stock.html', {'form': form})



# def modif_stock(request):
#     # if request.method == 'POST':
#     #     formset = StockFormSet(request.POST)
#     #     if formset.is_valid():
#     #         formset.save()
#     #         messages.success(request, "Le stock à été mies à jour avec succès.")
#     #         # Rediriger vers une page de confirmation ou vers la liste des stocks
#     #         return redirect('liste_stock')  # Assurez-vous d'avoir une URL nommée 'liste_stock'
#     # else:
#     #     formset = StockFormSet()
#     if request.method == "POST":
#         form = StockUpdateForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('liste_stock')
#     else:
#         form = StockUpdateForm()
    
#     # context = {
#     #     'formset': formset,
#     # }
#     return render(request, 'app/modif_stock.html', {'form': form})

def modif_stock(request):
    if request.method == 'POST':
        form_data = request.POST
        produit_keys = [key for key in form_data.keys() if key.startswith('produit_')]
        
        for key in produit_keys:
            produit_id = form_data[key]
            quantite_key = key.replace('produit_', 'quantite_')
            quantite = form_data[quantite_key]
            
            if produit_id and quantite:
                produit = Produit.objects.get(pk=produit_id)
                try:
                    stock = Stock.objects.get(IdProduit=produit)
                    nouvelle_quantite = stock.QuantiteStock + int(quantite)  # Addition de l'ancienne et de la nouvelle quantité
                    stock.QuantiteStock = nouvelle_quantite
                    stock.Date = timezone.now()
                    stock.save()
                except Stock.DoesNotExist:
                    Stock.objects.create(
                        IdProduit=produit,
                        QuantiteStock=quantite,
                        Date=timezone.now()
                    )
                    
        messages.success(request, f"Stock mise à jour avec succès.")
        return redirect('liste_stock')
    else:
        form = StockUpdateForm()
    return render(request, 'app/GestionnaireStock/modif_stock.html', {'form': form})

def get_quantite(request, produitId):
    try:
        produit = Stock.objects.get(pk=produitId)
        quantite = produit.QuantiteStock
        return JsonResponse({'quantite': quantite})
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Produit not found'}, status=404)
    
# def get_all_products(request):
#     products = Produit.objects.all().values('id', 'Nom')
#     return JsonResponse(list(products), safe=False)